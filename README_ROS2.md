# ProstScratch ROS2 Jazzy Implementation

## Overview
This is the ROS2 Jazzy port of the ProstScratch system for TurtleBot2 (Kobuki) control with Scratch 3.0 integration. The system enables intuitive robot control through Scratch programming blocks.

## Features

### Core Functionality
- **Scratch Integration**: Bidirectional communication with Scratch 3.0 via websockets
- **TurtleBot2 Control**: Motion control for TurtleBot2 with Kobuki base
- **Odometry Tracking**: Real-time position and orientation feedback
- **Sensor Integration**: Support for bumper, button, and QR code detection
- **Speech & Audio**: Text-to-speech and sound control capabilities

### Supported Commands

#### Motion Control
- `motion_stop:` - Stop all movement
- `move_speed:XX,second:YY` - Move at XX cm/s for YY seconds
- `rotation_speed:XX,second:YY` - Rotate at XX deg/s for YY seconds  
- `turtlebot_cmd_vel:XX,YY` - Direct velocity control (linear cm/s, angular deg/s)

#### Precise Movement
- `S:XXX` - Move XXX centimeters straight (positive=forward, negative=backward)
- `T:XXX` - Turn XXX degrees (positive=counter-clockwise, negative=clockwise)

#### System Control
- `odome_initialize` - Reset odometry to origin
- `LED:color` - Control LED (off, green, yellow, red)
- `sound:X` - Play sound X
- `speech:message` - Text-to-speech output

## Installation

### Prerequisites
- ROS2 Jazzy
- Ubuntu 24.04
- Python 3.10+
- TurtleBot2/Kobuki drivers for ROS2

### Dependencies
```bash
# Install ROS2 dependencies
sudo apt install ros-jazzy-geometry-msgs ros-jazzy-std-msgs ros-jazzy-nav-msgs
sudo apt install ros-jazzy-tf2-ros ros-jazzy-tf2-geometry-msgs
sudo apt install ros-jazzy-rosbridge-server ros-jazzy-web-video-server

# Python dependencies
pip3 install opencv-python numpy pillow
```

### Build Instructions
```bash
# Navigate to your ROS2 workspace
cd ~/ros2_ws/src

# Clone or copy the package
# (package should be in ~/ros2_ws/src/prost_scratch)

# Build the package
cd ~/ros2_ws
colcon build --packages-select prost_scratch

# Source the workspace
source ~/ros2_ws/install/setup.bash
```

## Usage

### Basic Launch
```bash
# Launch the complete system
ros2 launch prost_scratch prost_scratch_ros2.launch.py

# Or launch individual components
ros2 run prost_scratch prost_scratch_ros2_connector
ros2 run prost_scratch prost_scratch_ros2_controller
```

### Testing
```bash
# Run the test suite
ros2 run prost_scratch test_prost_scratch_ros2
```

### Integration with Scratch 3.0
1. Ensure rosbridge_server is running (included in launch file)
2. Open Scratch 3.0 with the ProstScratch extension
3. Use the connection block to establish communication
4. Program robot behaviors using Scratch blocks

## Architecture

### ROS2 Nodes

#### prost_scratch_ros2_connector
- **Purpose**: Interface between Scratch and ROS2
- **Subscriptions**: 
  - `/scratch_ros` (String) - Commands from Scratch
  - `/odom` (Odometry) - Robot position feedback
  - `/wifi_connect` (Bool) - WiFi status
- **Publications**:
  - `/ros_scratch` (String) - Status/data to Scratch
  - `/cmd_vel` (Twist) - Robot velocity commands
  - `/odom_base_ctrl` (String) - Precise movement commands

#### prost_scratch_ros2_controller  
- **Purpose**: Precise movement control with trapezoidal velocity profiles
- **Subscriptions**:
  - `/odom_base_ctrl` (String) - Movement commands (S:, T:)
  - `/motion_stop` (String) - Emergency stop
- **Publications**:
  - `/cmd_vel` (Twist) - Velocity commands
  - `/return_arrive` (String) - Movement completion signals

### Topic Mappings (ROS1 → ROS2)
- `/mobile_base/commands/velocity` → `/cmd_vel`
- TF transforms: `tf` → `tf2_ros`
- Message handling: `rospy` → `rclpy`

## Key Changes from ROS1

### API Migration
- **Node Initialization**: `rospy.init_node()` → `Node` class inheritance
- **Publishers**: `rospy.Publisher()` → `self.create_publisher()`
- **Subscribers**: `rospy.Subscriber()` → `self.create_subscription()`
- **Main Loop**: `rospy.spin()` → `rclpy.spin(node)`
- **Transforms**: `tf.TransformListener()` → `tf2_ros.TransformListener()`

### Message & Topic Updates
- Standard velocity topic: `/cmd_vel` (instead of `/mobile_base/commands/velocity`)
- QoS profiles for reliable communication
- Updated time handling with `self.get_clock().now()`

### Build System
- **From**: CMakeLists.txt + catkin
- **To**: setup.py + ament_python

## Configuration

### TurtleBot2/Kobuki Setup
The system expects TurtleBot2 drivers to provide:
- `/odom` topic (nav_msgs/Odometry)
- `/cmd_vel` subscription (geometry_msgs/Twist)
- Base TF transforms (odom → base_link)

### Network Configuration
- Default rosbridge port: 9090
- Default web_video_server port: 8080
- Ensure firewall allows these ports for Scratch communication

## Troubleshooting

### Common Issues
1. **No movement**: Check if `/cmd_vel` topic is being published and subscribed
2. **No odometry**: Verify TurtleBot2 drivers are running and publishing `/odom`
3. **Scratch connection**: Ensure rosbridge_server is running on port 9090
4. **TF errors**: Check that robot description and tf2 transforms are working

### Debug Commands
```bash
# Check topic communication
ros2 topic list
ros2 topic echo /cmd_vel
ros2 topic echo /ros_scratch

# Check TF transforms
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo odom base_link

# Monitor node status
ros2 node list
ros2 node info /prost_scratch_ros2_connector
```

## Known Limitations

1. **Kobuki-specific features**: LED, sound, and button events require additional ROS2 driver packages
2. **Speech recognition**: Requires separate ROS2-compatible speech packages
3. **QR code detection**: Requires visp_auto_tracker or equivalent for ROS2
4. **Camera integration**: web_video_server must be configured for specific camera setup

## Future Enhancements

- [ ] Add support for ROS2 kobuki drivers when available
- [ ] Implement speech recognition integration
- [ ] Add camera and QR code detection
- [ ] Create Docker container for easy deployment
- [ ] Add unit tests and continuous integration
- [ ] Performance optimization for real-time control

## Contributing

When contributing to this ROS2 port:
1. Maintain compatibility with existing Scratch blocks
2. Follow ROS2 best practices and coding standards
3. Test thoroughly on actual TurtleBot2 hardware
4. Update documentation for any API changes

## License

[Same as original ProstScratch project]