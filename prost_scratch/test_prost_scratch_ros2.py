#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for ProstScratch ROS2 implementation
This script tests the basic functionality of the ROS2 migration
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import time
import sys


class ProstScratchTester(Node):
    
    def __init__(self):
        super().__init__('prost_scratch_tester')
        self.get_logger().info("ProstScratch ROS2 Tester Started")
        
        # Publishers for testing
        self.pub_scratch_ros = self.create_publisher(String, '/scratch_ros', 10)
        
        # Subscribers for validation
        self.sub_ros_scratch = self.create_subscription(
            String, '/ros_scratch', self.cb_ros_scratch, 10)
        self.sub_cmd_vel = self.create_subscription(
            Twist, '/cmd_vel', self.cb_cmd_vel, 10)
        
        # Test data storage
        self.received_responses = []
        self.received_cmd_vels = []
        
        # Wait for connections
        time.sleep(1.0)
        
    def cb_ros_scratch(self, msg):
        """Receive responses from the connector"""
        self.received_responses.append(msg.data)
        self.get_logger().info(f"Received response: {msg.data}")
        
    def cb_cmd_vel(self, msg):
        """Monitor cmd_vel commands"""
        self.received_cmd_vels.append((msg.linear.x, msg.angular.z))
        self.get_logger().info(f"Received cmd_vel: linear={msg.linear.x}, angular={msg.angular.z}")
        
    def test_basic_commands(self):
        """Test basic Scratch commands"""
        self.get_logger().info("Starting basic command tests...")
        
        test_commands = [
            "motion_stop:",
            "turtlebot_cmd_vel:10,5",  # 10 cm/s linear, 5 deg/s angular
            "motion_stop:",
            "move_speed:20,second:1",  # 20 cm/s for 1 second
            "rotation_speed:30,second:1",  # 30 deg/s for 1 second
            "motion_stop:",
            "LED:green",
            "sound:1",
            "speech:Hello from ROS2",
        ]
        
        for cmd in test_commands:
            self.get_logger().info(f"Sending command: {cmd}")
            msg = String()
            msg.data = cmd
            self.pub_scratch_ros.publish(msg)
            
            # Allow time for processing
            rclpy.spin_once(self, timeout_sec=0.1)
            time.sleep(0.5)
            
        self.get_logger().info("Basic command tests completed")
        
    def test_controller_commands(self):
        """Test controller-specific commands"""
        self.get_logger().info("Starting controller command tests...")
        
        controller_commands = [
            "S:100",  # Move 100cm straight
            "T:90",   # Turn 90 degrees
            "S:-50",  # Move 50cm backward
            "T:-45",  # Turn -45 degrees
        ]
        
        for cmd in controller_commands:
            self.get_logger().info(f"Sending controller command: {cmd}")
            msg = String()
            msg.data = cmd
            self.pub_scratch_ros.publish(msg)
            
            # Allow time for processing
            rclpy.spin_once(self, timeout_sec=0.1)
            time.sleep(1.0)  # Longer wait for movement commands
            
        self.get_logger().info("Controller command tests completed")
        
    def run_tests(self):
        """Run all tests"""
        try:
            self.test_basic_commands()
            time.sleep(2.0)
            self.test_controller_commands()
            
            # Summary
            self.get_logger().info("=== Test Summary ===")
            self.get_logger().info(f"Total responses received: {len(self.received_responses)}")
            self.get_logger().info(f"Total cmd_vel commands: {len(self.received_cmd_vels)}")
            
            if self.received_cmd_vels:
                self.get_logger().info("✓ Movement commands are being published")
            else:
                self.get_logger().warn("✗ No movement commands detected")
                
            if self.received_responses:
                self.get_logger().info("✓ Responses are being received")
            else:
                self.get_logger().warn("✗ No responses received")
                
            self.get_logger().info("Tests completed successfully!")
            
        except Exception as e:
            self.get_logger().error(f"Test failed with error: {e}")


def main(args=None):
    rclpy.init(args=args)
    
    tester = ProstScratchTester()
    
    try:
        # Give some time for other nodes to start
        tester.get_logger().info("Waiting for other nodes to start...")
        time.sleep(3.0)
        
        # Run the tests
        tester.run_tests()
        
        # Keep spinning for a bit to catch any delayed responses
        end_time = time.time() + 5.0
        while time.time() < end_time and rclpy.ok():
            rclpy.spin_once(tester, timeout_sec=0.1)
            
    except KeyboardInterrupt:
        tester.get_logger().info("Test interrupted by user")
    finally:
        tester.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()