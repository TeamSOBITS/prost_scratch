# Migration Guide: ROS1 to ROS2 Jazzy

## Overview
This guide explains how to migrate from the ROS1 version of ProstScratch to the new ROS2 Jazzy implementation.

## Before You Start

### Environment Requirements
- **Old System**: ROS1 Kinetic/Melodic + Ubuntu 16.04/18.04
- **New System**: ROS2 Jazzy + Ubuntu 24.04 + Raspberry Pi 5

### Hardware Compatibility
- TurtleBot2 with Kobuki base remains the same
- Raspberry Pi upgrade to version 5 recommended
- USB camera and sensors maintain compatibility

## Migration Steps

### 1. System Backup
```bash
# Backup your existing ROS1 workspace
tar -czf ~/prost_scratch_ros1_backup.tar.gz ~/catkin_ws/src/prost_scratch
```

### 2. Install ROS2 Jazzy
```bash
# Update system
sudo apt update && sudo apt upgrade

# Install ROS2 Jazzy (follow official ROS2 installation guide)
sudo apt install ros-jazzy-desktop

# Install additional dependencies
sudo apt install ros-jazzy-rosbridge-server ros-jazzy-web-video-server
sudo apt install ros-jazzy-tf2-ros ros-jazzy-tf2-geometry-msgs
```

### 3. Setup ROS2 Workspace
```bash
# Create ROS2 workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Clone or copy the migrated package
git clone <repository_url>  # Or copy your updated prost_scratch package

# Build the workspace
cd ~/ros2_ws
colcon build --packages-select prost_scratch

# Source the workspace
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 4. TurtleBot2 Driver Setup
**Note**: TurtleBot2 drivers for ROS2 may not be officially available. You may need to:

#### Option A: Use ROS1-ROS2 Bridge (Temporary Solution)
```bash
# Install ros1_bridge
sudo apt install ros-jazzy-ros1-bridge

# In terminal 1 (ROS1 side):
source /opt/ros/melodic/setup.bash
roslaunch prost_scratch minimal.launch

# In terminal 2 (Bridge):
source /opt/ros/jazzy/setup.bash
source /opt/ros/melodic/setup.bash
ros2 run ros1_bridge dynamic_bridge

# In terminal 3 (ROS2 side):
source ~/ros2_ws/install/setup.bash
ros2 launch prost_scratch prost_scratch_ros2.launch.py
```

#### Option B: Use Generic Mobile Robot Drivers
```bash
# Look for ROS2-compatible mobile robot drivers
sudo apt install ros-jazzy-turtlebot3-*  # Similar base functionality
# Configure remapping to match TurtleBot2 topics
```

#### Option C: Create Custom Driver Wrapper
- Wrap existing TurtleBot2 hardware interface in ROS2 node
- Implement required message conversions
- See `turtlebot2_minimal_ros2.launch.py` for template

### 5. Scratch 3.0 Integration
The Scratch integration remains largely the same:

```bash
# Start the ROS2 system
ros2 launch prost_scratch prost_scratch_ros2.launch.py

# Scratch blocks work identically:
# - Motion control blocks
# - Sensor reading blocks  
# - Status feedback blocks
```

### 6. Testing the Migration
```bash
# Run the test suite
ros2 run prost_scratch test_prost_scratch_ros2

# Check topic communication
ros2 topic list
ros2 topic echo /ros_scratch

# Monitor robot movement
ros2 topic echo /cmd_vel
```

## Key Differences

### Command Line Changes
| ROS1 | ROS2 |
|------|------|
| `roslaunch prost_scratch scratch_connector.launch` | `ros2 launch prost_scratch prost_scratch_ros2.launch.py` |
| `rosrun prost_scratch scratch3_connector.py` | `ros2 run prost_scratch prost_scratch_ros2_connector` |
| `rostopic echo /ros_scratch` | `ros2 topic echo /ros_scratch` |
| `rosnode list` | `ros2 node list` |

### Topic Changes
| Functionality | ROS1 Topic | ROS2 Topic |
|---------------|------------|------------|
| Robot Velocity | `/mobile_base/commands/velocity` | `/cmd_vel` |
| Odometry | `/odom` | `/odom` (same) |
| Scratch Commands | `/scratch_ros` | `/scratch_ros` (same) |
| Robot Status | `/ros_scratch` | `/ros_scratch` (same) |

### Programming Interface
- **Launch Files**: `.launch` → `.launch.py` (Python-based)
- **Node Structure**: Function-based → Class-based inheritance
- **Message Handling**: `rospy` → `rclpy`
- **TF Transforms**: `tf` → `tf2_ros`

## Troubleshooting Migration Issues

### 1. Driver Compatibility
**Problem**: TurtleBot2 drivers not available for ROS2
**Solutions**:
- Use ros1_bridge as temporary solution
- Port existing drivers to ROS2
- Use alternative compatible mobile robot packages

### 2. Scratch Connection Issues
**Problem**: Scratch cannot connect to robot
**Solutions**:
```bash
# Check rosbridge_server
ros2 node list | grep rosbridge

# Check port 9090 is open
netstat -ln | grep 9090

# Test websocket connection
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" \
     http://localhost:9090
```

### 3. Movement Commands Not Working
**Problem**: Robot doesn't respond to movement commands
**Solutions**:
```bash
# Check cmd_vel topic
ros2 topic echo /cmd_vel

# Test manual control
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.1}, angular: {z: 0.0}}'

# Check TF transforms
ros2 run tf2_tools view_frames
```

### 4. Build Errors
**Problem**: Package fails to build
**Solutions**:
```bash
# Clean build
rm -rf ~/ros2_ws/build ~/ros2_ws/install ~/ros2_ws/log

# Install missing dependencies
rosdep install --from-paths src --ignore-src -r -y

# Build with verbose output
colcon build --packages-select prost_scratch --event-handlers console_direct+
```

## Performance Considerations

### ROS2 Benefits
- **Better Real-time Performance**: Improved deterministic behavior
- **Enhanced Security**: Built-in security features
- **Multi-platform Support**: Windows, macOS, Linux
- **Modern Architecture**: Better suited for production use

### Migration Impact
- **Latency**: Slightly improved message passing
- **Resource Usage**: Similar to ROS1
- **Compatibility**: Requires updated drivers and packages

## Rollback Plan

If migration issues arise:

```bash
# Return to ROS1 system
source /opt/ros/melodic/setup.bash
cd ~/catkin_ws
catkin_make
roslaunch prost_scratch scratch_connector.launch
```

## Next Steps

1. **Test Thoroughly**: Validate all Scratch blocks work correctly
2. **Hardware Validation**: Test on actual TurtleBot2 hardware
3. **Performance Tuning**: Optimize for your specific use case
4. **Documentation**: Update any custom Scratch blocks or extensions
5. **Training**: Update user documentation and training materials

## Support

For migration assistance:
- Check ROS2 Jazzy documentation
- Review the README_ROS2.md file
- Test using the provided test scripts
- Report issues with detailed error logs

The migration preserves all existing Scratch programming functionality while providing a modern, maintainable platform for future development.