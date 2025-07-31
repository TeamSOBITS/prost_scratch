#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    """
    ROS2 launch file for ProstScratch TurtleBot2 control system
    """
    
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    
    return LaunchDescription([
        
        # TurtleBot2 bringup (would need TurtleBot2 ROS2 packages)
        # Note: This may need to be replaced with appropriate TurtleBot2 ROS2 launch files
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource([
        #         PathJoinSubstitution([
        #             FindPackageShare('turtlebot2_bringup'),
        #             'launch',
        #             'minimal.launch.py'
        #         ])
        #     ]),
        #     launch_arguments={'use_sim_time': use_sim_time}.items()
        # ),

        # rosbridge_server for Scratch integration
        # Note: rosbridge_server should be available for ROS2
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('rosbridge_server'),
                    'launch',
                    'rosbridge_websocket_launch.xml'
                ])
            ])
        ),

        # web_video_server for camera streaming
        # Note: web_video_server should be available for ROS2
        Node(
            package='web_video_server',
            executable='web_video_server',
            name='web_video_server',
            output='screen'
        ),

        # ProstScratch ROS2 Connector
        Node(
            package='prost_scratch',
            executable='prost_scratch_ros2_connector',
            name='prost_scratch_ros2_connector',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}]
        ),

        # ProstScratch ROS2 Controller
        Node(
            package='prost_scratch',
            executable='prost_scratch_ros2_controller',
            name='prost_scratch_ros2_controller',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}]
        ),

        # Text to speech (if available for ROS2)
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource([
        #         PathJoinSubstitution([
        #             FindPackageShare('text_to_speech'),
        #             'launch',
        #             'japanese.launch.py'
        #         ])
        #     ])
        # ),

        # Speech recognition (if available for ROS2)
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource([
        #         PathJoinSubstitution([
        #             FindPackageShare('julius_ros'),
        #             'launch',
        #             'speech_recognition.launch.py'
        #         ])
        #     ])
        # ),

        # USB camera (if needed)
        # Node(
        #     package='usb_cam',
        #     executable='usb_cam_node_exe',
        #     name='usb_cam',
        #     output='screen',
        #     parameters=[{
        #         'video_device': '/dev/video0',
        #         'image_width': 640,
        #         'image_height': 480,
        #         'pixel_format': 'yuyv',
        #         'camera_frame_id': 'usb_cam'
        #     }]
        # ),

    ])


if __name__ == '__main__':
    generate_launch_description()