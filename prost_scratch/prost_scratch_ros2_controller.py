#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
import math
import time
from geometry_msgs.msg import Pose, Point, Quaternion, Twist
from std_msgs.msg import String, Empty
from nav_msgs.msg import Odometry
import tf2_ros
from tf2_ros import Buffer, TransformListener
import tf2_py as tf2
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import numpy as np


class ProstScratchROS2Controller(Node):
    """
    ROS2 version of the TurtleBot2/Kobuki controller for precise movement control
    Supports:
    - S:1000 (1000cm straight movement)
    - T:90 (90 degree rotation, counter-clockwise positive)
    """

    def __init__(self):
        super().__init__('prost_scratch_ros2_controller')
        self.get_logger().info("ProstScratch ROS2 Controller Started")

        # QoS settings for reliable communication
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # TF2 setup
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Control parameters for rotation
        self.turn_acs = 1  # acceleration (initial: 0.5)
        self.turn_speed_max = 150  # max speed (initial: 20)
        self.turn_speed_min = 0
        self.turn_ki = 0.15

        # Control parameters for straight movement
        self.stlight_acs = 0.01  # acceleration (default: 0.01)
        self.stlight_speed_max = 0.4  # max speed (default: 0.2m/s)
        self.stlight_speed_min = 0  # min speed (default: 0m/s)
        self.stlight_ki = 0.1  # integral coefficient

        # Loop cycle setting
        self.sleep_vale = 0.030

        # Speed update time measurement
        self.start_measurement_time = 0
        self.speed_update_time = 0
        self.period_time = 0
        self.speed_start_flag = False

        # Variable initialization
        self.speed = 0
        self.speed_max = 0
        self.speed_min = 0
        self.before_speed = 0
        self.current_speed = 0
        self.current_pose_x = 0
        self.current_pose_y = 0
        self.current_angle = 0
        self.before_pose_x = 0
        self.before_pose_y = 0
        self.before_angle = 0
        self.order_vale = 0
        self.moved_vale = 0
        self.error_P = 0
        self.error_I = 0
        self.move_order_T = False
        self.move_order_S = False
        self.stop_flag = False

        # Publishers - Updated for ROS2
        self.pub_cmd_vel = self.create_publisher(Twist, '/cmd_vel', qos_profile)
        self.pub_output_log = self.create_publisher(String, '/odom_base/output_log', qos_profile)
        self.pub_return_arrive = self.create_publisher(String, '/return_arrive', qos_profile)

        # Subscribers
        self.sub_motion_stop = self.create_subscription(
            String, '/motion_stop', self.motion_stop, qos_profile)
        self.sub_odom_base_ctrl = self.create_subscription(
            String, '/odom_base_ctrl', self.odom_base_ctrl, qos_profile)

        self.get_logger().info("ProstScratch ROS2 Controller is ready.")

    def check_command(self, line):
        """Check if command format is valid"""
        cmd_line = line.data[0:2]
        value_line = line.data[2:len(line.data)]
        
        for i in range(len(cmd_line)):
            key = cmd_line[i]
            if key == 'T' or key == 'S' or key == ':':
                pass
            else:
                self.get_logger().error(f"check_command cmd error: {line.data}")
                return False
                
        for i in range(len(value_line)):
            key = value_line[i]
            if key >= '0' and key <= '9' or key == '-' or key == '.':
                pass
            else:
                self.get_logger().error(f"check_command cmd error: {line.data}")
                return False
        return True

    def read_value(self, line):
        """Read value from command string"""
        value_str = line.data[2:len(line.data)]
        value = float(value_str)
        return value

    def motion_stop(self, data):
        """Handle motion stop command"""
        self.get_logger().info("Motion stop flag received")
        self.stop_flag = True

    def get_current_transform(self):
        """Get current transform using TF2"""
        try:
            # Use time(0) for latest available transform
            transform = self.tf_buffer.lookup_transform(
                'odom', 'base_link', rclpy.time.Time())
            return transform
        except Exception as ex:
            self.get_logger().warn(f'Could not get transform: {ex}')
            return None

    def quaternion_to_euler(self, x, y, z, w):
        """Convert quaternion to euler angles"""
        # Roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # Pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)  # use 90 degrees if out of range
        else:
            pitch = math.asin(sinp)

        # Yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return [roll, pitch, yaw]

    def odom_base_ctrl(self, motion):
        """Main control function for handling movement commands"""
        if self.move_order_T or self.move_order_S:
            self.get_logger().warn("Sorry, the action is not registered.")
            return "False"
            
        check = self.check_command(motion)
        if not check:
            self.get_logger().warn("The command cannot be carried out.")
            return "False"
        
        if "T" in motion.data:
            self.order_vale = self.read_value(motion)
            self.move_order_T = True
            self.get_logger().info(f"Order: Turn: {self.order_vale} (deg)")
            
        elif "S" in motion.data:
            self.order_vale = self.read_value(motion)  # cm
            self.move_order_S = True
            self.get_logger().info(f"Order: Straight: {self.order_vale} (cm)")

        if self.move_order_T and not self.move_order_S:
            # Rotation control parameters
            self.speed_acs = self.turn_acs
            self.speed_max = self.turn_speed_max
            self.speed_min = self.turn_speed_min
            self.ki = self.turn_ki
        elif not self.move_order_T and self.move_order_S:
            # Straight movement control parameters
            self.speed_acs = self.stlight_acs
            self.speed_max = self.stlight_speed_max
            self.speed_min = self.stlight_speed_min
            self.ki = self.stlight_ki

        # Get current encoder values
        transform = self.get_current_transform()
        if transform is None:
            self.get_logger().error("Cannot get current transform")
            return "False"

        trans = transform.transform.translation
        rot = transform.transform.rotation
        euler = self.quaternion_to_euler(rot.x, rot.y, rot.z, rot.w)
        
        # Save current position
        self.before_pose_x = trans.x * 100  # [cm]
        self.before_pose_y = trans.y * 100  # [cm]
        self.before_angle = math.degrees(euler[2])  # [deg]
        
        self.get_logger().info(f"Starting position - x:{self.before_pose_x} y:{self.before_pose_y} angle:{self.before_angle}")

        # Main control loop
        while rclpy.ok():
            time.sleep(self.sleep_vale)
            send_cmd = Twist()

            if not self.move_order_T and not self.move_order_S:
                self.pub_cmd_vel.publish(Twist())  # Stop
                break
            elif self.stop_flag:
                self.stop_flag = False
                self.reset_control_variables()
                self.pub_cmd_vel.publish(Twist())  # Stop
                self.get_logger().info("Motion stopped by stop flag")
                break
            else:
                # Acceleration phase
                if self.moved_vale < abs(self.order_vale) / 5:
                    self.speed += self.speed_acs
                    self.current_speed = self.speed
                # Deceleration phase
                elif self.moved_vale > abs(self.order_vale) * 4 / 5:
                    # PI control
                    self.before_speed = self.speed
                    if self.speed > self.error_I:
                        self.error_P = (abs(self.order_vale) - self.moved_vale) / (abs(self.order_vale) / 5)
                        self.speed = self.current_speed * self.error_P + self.error_I
                        self.error_I += (self.before_speed - self.speed) * self.ki
                    elif self.speed <= self.error_I:
                        self.speed = self.error_I
                # Constant speed phase
                else:
                    pass

                # Max speed correction
                if self.speed >= self.speed_max:
                    self.speed = self.speed_max
                # Prevent reverse movement
                if self.speed < self.speed_min:
                    self.speed = self.speed_min

                # Handle rotation
                if self.move_order_T and not self.move_order_S:
                    if self.order_vale > 0:
                        send_cmd.angular.z = math.radians(-self.speed)
                    else:  # clockwise
                        send_cmd.angular.z = math.radians(self.speed)

                    if self.moved_vale < abs(self.order_vale):
                        self.pub_cmd_vel.publish(send_cmd)
                        self.update_position_rotation()
                    else:
                        self.finish_movement("rotation")

                # Handle straight movement
                elif not self.move_order_T and self.move_order_S:
                    if self.order_vale > 0:
                        send_cmd.linear.x = self.speed  # m/sec
                    else:
                        send_cmd.linear.x = -self.speed  # m/sec

                    if self.moved_vale < abs(self.order_vale):
                        self.pub_cmd_vel.publish(send_cmd)
                        self.update_position_straight()
                    else:
                        self.finish_movement("straight")

            # Allow other callbacks to be processed
            rclpy.spin_once(self, timeout_sec=0.001)

    def update_position_rotation(self):
        """Update position for rotation movement"""
        transform = self.get_current_transform()
        if transform is None:
            return

        trans = transform.transform.translation
        rot = transform.transform.rotation
        euler = self.quaternion_to_euler(rot.x, rot.y, rot.z, rot.w)
        
        self.current_pose_x = trans.x * 100  # [cm]
        self.current_pose_y = trans.y * 100  # [cm]
        self.current_angle = math.degrees(euler[2])  # [deg]
        
        # Calculate rotation movement
        sub_point = abs(self.current_angle - self.before_angle)
        if sub_point > 180:
            sub_point = abs(sub_point - 360)
        self.moved_vale += sub_point
        
        self.get_logger().info(f"Current rotation angle: {self.moved_vale} [deg]")
        
        # Update reference position
        self.before_pose_x = self.current_pose_x
        self.before_pose_y = self.current_pose_y
        self.before_angle = self.current_angle

    def update_position_straight(self):
        """Update position for straight movement"""
        transform = self.get_current_transform()
        if transform is None:
            return

        trans = transform.transform.translation
        rot = transform.transform.rotation
        euler = self.quaternion_to_euler(rot.x, rot.y, rot.z, rot.w)
        
        self.current_pose_x = trans.x * 100  # [cm]
        self.current_pose_y = trans.y * 100  # [cm]
        self.current_angle = math.degrees(euler[2])  # [deg]
        
        # Calculate distance moved
        sub_x = self.before_pose_x - self.current_pose_x
        sub_y = self.before_pose_y - self.current_pose_y
        self.moved_vale = math.hypot(sub_x, sub_y)
        
        self.get_logger().info(f"Current distance moved: {self.moved_vale} [cm]")

    def finish_movement(self, movement_type):
        """Finish movement and cleanup"""
        self.pub_cmd_vel.publish(Twist())  # Stop
        self.get_logger().info(f"Movement completed: {movement_type}")
        
        # Reset control variables
        self.reset_control_variables()
        
        # Send completion signal
        end_msg = String()
        end_msg.data = "move end"
        self.pub_return_arrive.publish(end_msg)
        
        self.get_logger().info("Moving Finished")

    def reset_control_variables(self):
        """Reset control variables to initial state"""
        self.speed = 0
        self.current_speed = 0
        self.order_vale = 0
        self.moved_vale = 0
        self.error_P = 0
        self.error_I = 0
        self.move_order_T = False
        self.move_order_S = False
        self.speed_start_flag = False


def main(args=None):
    rclpy.init(args=args)
    
    prost_scratch_controller = ProstScratchROS2Controller()
    
    try:
        rclpy.spin(prost_scratch_controller)
    except KeyboardInterrupt:
        pass
    finally:
        prost_scratch_controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()