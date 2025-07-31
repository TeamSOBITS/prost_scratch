#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
import cv2
import numpy as np
import math
import time
from std_msgs.msg import String, UInt8, Empty, Bool
from geometry_msgs.msg import Twist, Quaternion, PoseStamped
from sensor_msgs.msg import LaserScan, Image
from nav_msgs.msg import Odometry
# from cv_bridge import CvBridge, CvBridgeError
import tf2_ros
from tf2_ros import Buffer, TransformListener
from tf2_geometry_msgs import do_transform_pose
import tf2_py as tf2
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy


class ProstScratchROS2Connector(Node):

    def __init__(self):
        super().__init__('prost_scratch_ros2_connector')
        self.get_logger().info("ProstScratch ROS2 Connector Started")

        # QoS settings for reliable communication
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Initialize variables
        self.save_qr_distance = 0
        self.save_qr_width = 0
        self.save_qr_angle = 0
        self.moving_speed = Twist()
        
        # TF2 setup
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Publishers - Updated for TurtleBot2 in ROS2
        self.pub_ros_scratch = self.create_publisher(String, '/ros_scratch', qos_profile)
        self.pub_ros_scratch_debug = self.create_publisher(String, '/ros_scratch_debug', qos_profile)
        self.pub_cmd_vel = self.create_publisher(Twist, '/cmd_vel', qos_profile)  # Standard ROS2 topic
        self.pub_odom_base_ctrl = self.create_publisher(String, '/odom_base_ctrl', qos_profile)
        self.pub_speech_word = self.create_publisher(String, '/speech_word', qos_profile)

        # Subscribers
        self.sub_scratch_ros = self.create_subscription(
            String, '/scratch_ros', self.cb_scratch_ros, qos_profile)
        self.sub_wifi_connect = self.create_subscription(
            Bool, '/wifi_connect', self.cb_wifi_connect, qos_profile)
        self.sub_odom = self.create_subscription(
            Odometry, '/odom', self.cb_odom, qos_profile)
        self.sub_speech_recognition = self.create_subscription(
            String, '/speech_recognition/word', self.speech_recognition, qos_profile)
        self.sub_qr_position = self.create_subscription(
            PoseStamped, '/visp_auto_tracker/object_position', self.qr_position, qos_profile)

        # For TurtleBot2/Kobuki specific topics (may need to be adapted based on available drivers)
        # Note: In ROS2, these topics might be different or provided by different packages
        # self.sub_bumper = self.create_subscription(
        #     BumperEvent, '/mobile_base/events/bumper', self.bumper_state, qos_profile)
        # self.sub_button = self.create_subscription(
        #     ButtonEvent, '/mobile_base/events/button', self.button_state, qos_profile)
        
        # These publishers might need different message types in ROS2
        # self.pub_led1 = self.create_publisher(Led, '/mobile_base/commands/led1', qos_profile)
        # self.pub_led2 = self.create_publisher(Led, '/mobile_base/commands/led2', qos_profile)
        # self.pub_sound = self.create_publisher(Sound, '/mobile_base/commands/sound', qos_profile)
        # self.pub_reset_odometry = self.create_publisher(Empty, '/mobile_base/commands/reset_odometry', qos_profile)

        # Timer for connection announcement
        self.create_timer(3.0, self.announce_connection)

    def announce_connection(self):
        """Announce connection status after startup"""
        connection_call = String()
        connection_call.data = "みどりいろのUSBを接続した後に、接続ブロックを実行してください"
        self.pub_speech_word.publish(connection_call)
        # Only run once - destroy the timer (no need to store timer reference)

    def cb_wifi_connect(self, state):
        """Handle WiFi connection status"""
        # LED control would need to be adapted for ROS2 TurtleBot2 drivers
        # if state.data:
        #     self.pub_led1.publish(1)  # on--green
        # else:
        #     self.pub_led1.publish(3)  # off--red
        self.get_logger().info(f"WiFi connection status: {state.data}")

    def cb_scratch_ros(self, msg):
        """Handle commands from Scratch"""
        get_msg = msg.data
        self.get_logger().info(f"Received from Scratch: {get_msg}")
        
        if get_msg.find('LED:') >= 0:
            word = get_msg[4:len(get_msg)]
            # LED control would need ROS2 adaptation
            # if word == "off":
            #     self.pub_led2.publish(0)
            # elif word == "green":
            #     self.pub_led2.publish(1)
            # elif word == "yellow":
            #     self.pub_led2.publish(2)
            # elif word == "red":
            #     self.pub_led2.publish(3)
            self.get_logger().info(f"LED command: {word}")
            
        elif get_msg.find('sound:') >= 0:
            word = get_msg[6:len(get_msg)]
            # Sound control would need ROS2 adaptation
            # self.pub_sound.publish(np.uint8(word))
            self.get_logger().info(f"Sound command: {word}")
            
        elif get_msg.find('S:') >= 0:
            self.pub_odom_base_ctrl.publish(msg)
            
        elif get_msg.find('T:') >= 0:
            self.pub_odom_base_ctrl.publish(msg)
            
        elif get_msg.find('move_speed:') >= 0:
            word = get_msg[11:get_msg.find(',')]
            speed = float(word)
            if speed > 50:
                speed = 50
            if speed < -50:
                speed = -50
            self.moving_speed.linear.x = speed * 0.01
            self.moving_speed.angular.z = 0.0
            
            if get_msg.find('second:') >= 0:
                second = get_msg[get_msg.index(',')+8:len(get_msg)]
            else:
                second = 1
                
            begin_time = self.get_clock().now()
            while True:
                current_time = self.get_clock().now()
                check = (current_time - begin_time).nanoseconds / 1e9
                if check >= float(second):
                    self.moving_speed.linear.x = 0.0
                    self.pub_cmd_vel.publish(self.moving_speed)
                    self.get_logger().info(f"Movement completed in {check} seconds")
                    break
                self.pub_cmd_vel.publish(self.moving_speed)
                rclpy.spin_once(self, timeout_sec=0.001)
                
        elif get_msg.find('rotation_speed:') >= 0:
            word = get_msg[15:get_msg.find(',')]
            speed = float(word)
            if speed > 120:
                speed = 120
            if speed < -120:
                speed = -120
            self.moving_speed.linear.x = 0.0
            self.moving_speed.angular.z = math.radians(speed)
            
            if get_msg.find('second:') >= 0:
                second = get_msg[get_msg.index(',')+8:len(get_msg)]
            else:
                second = 1
                
            begin_time = self.get_clock().now()
            while True:
                current_time = self.get_clock().now()
                check = (current_time - begin_time).nanoseconds / 1e9
                if check >= float(second):
                    self.moving_speed.angular.z = 0.0
                    self.pub_cmd_vel.publish(self.moving_speed)
                    self.get_logger().info(f"Rotation completed in {check} seconds")
                    break
                self.pub_cmd_vel.publish(self.moving_speed)
                rclpy.spin_once(self, timeout_sec=0.001)
                
        elif get_msg.find('turtlebot_cmd_vel:') >= 0:
            word = get_msg[18:len(get_msg)]
            num = word.find(',')
            vel = word[0:num]
            rad = word[num+1:len(word)]
            self.moving_speed.linear.x = float(vel) * 0.01
            self.moving_speed.angular.z = math.radians(float(rad))
            self.pub_cmd_vel.publish(self.moving_speed)
            
        elif get_msg.find('motion_stop:') >= 0:
            self.moving_speed.linear.x = 0.0
            self.moving_speed.angular.z = 0.0
            self.pub_cmd_vel.publish(self.moving_speed)
            
        elif get_msg.find('odome_initialize') >= 0:
            # Odometry reset would need to be adapted for ROS2
            # reset_val = Empty()
            # self.pub_reset_odometry.publish(reset_val)
            self.get_logger().info("Odometry reset requested (not implemented in ROS2 version yet)")
            
        elif get_msg.find('speech') >= 0:
            word = get_msg[7:len(get_msg)]
            speech_msg = String()
            speech_msg.data = word
            self.pub_speech_word.publish(speech_msg)

    def cb_odom(self, data):
        """Handle odometry data"""
        robo_pose_x = data.pose.pose.position.x
        robo_pose_y = data.pose.pose.position.y
        
        # Convert quaternion to euler
        quat = data.pose.pose.orientation
        euler = self.quaternion_to_euler(quat.x, quat.y, quat.z, quat.w)
        robo_rad = euler[2]
        robo_deg = math.degrees(robo_rad)

        # Publish robot position data to Scratch
        robo_pose_x_msg = String()
        robo_pose_x_msg.data = f"robot_pose_x:{robo_pose_x}"
        self.pub_ros_scratch.publish(robo_pose_x_msg)
        
        robo_pose_y_msg = String()
        robo_pose_y_msg.data = f"robot_pose_y:{robo_pose_y}"
        self.pub_ros_scratch.publish(robo_pose_y_msg)
        
        robo_angle_msg = String()
        robo_angle_msg.data = f"robot_angle:{robo_deg}"
        self.pub_ros_scratch.publish(robo_angle_msg)

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

    def qr_position(self, data):
        """Handle QR code position data"""
        euler = self.quaternion_to_euler(
            data.pose.orientation.x, data.pose.orientation.y, 
            data.pose.orientation.z, data.pose.orientation.w)

        temp_width = data.pose.position.x * -1
        temp_high = data.pose.position.y * -1
        temp_distance = data.pose.position.z

        get_qr_distance = temp_distance * 100

        # Distance calibration (same formula as original)
        get_qr_distance = (0.00999177789385630000 * get_qr_distance * get_qr_distance + 
                          1.95235227648073000000 * get_qr_distance + 4.00275749637565000000)

        if self.save_qr_distance != get_qr_distance:
            qr_distance_msg = String()
            qr_distance_msg.data = f"qr_distance:{get_qr_distance}"
            self.pub_ros_scratch.publish(qr_distance_msg)
            self.pub_ros_scratch_debug.publish(qr_distance_msg)
            self.save_qr_distance = get_qr_distance

        get_qr_width = int(temp_width * 100)
        if self.save_qr_width != get_qr_width:
            qr_width_msg = String()
            qr_width_msg.data = f"qr_width:{get_qr_width}"
            self.pub_ros_scratch.publish(qr_width_msg)
            self.save_qr_width = get_qr_width

        qr_angle = int(math.degrees(euler[1]))
        if qr_angle == 0:
            return

        if self.save_qr_angle != qr_angle:
            qr_angle_msg = String()
            qr_angle_msg.data = f"qr_angle:{qr_angle}"
            self.pub_ros_scratch.publish(qr_angle_msg)
            self.save_qr_angle = qr_angle

    def speech_recognition(self, data):
        """Handle speech recognition results"""
        word_msg = String()
        word_msg.data = f'recognition_word:{data.data}'
        self.pub_ros_scratch.publish(word_msg)

    # Note: Bumper and button callbacks would need to be adapted 
    # based on available ROS2 TurtleBot2/Kobuki drivers


def main(args=None):
    rclpy.init(args=args)
    
    prost_scratch_connector = ProstScratchROS2Connector()
    
    try:
        rclpy.spin(prost_scratch_connector)
    except KeyboardInterrupt:
        pass
    finally:
        prost_scratch_connector.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()