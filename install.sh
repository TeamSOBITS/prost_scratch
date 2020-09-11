#!/bin/sh

cd ~/catkin_ws/src

echo "Install TurtleBot packages"
sudo apt install ros-kinetic-turtlebot ros-kinetic-turtlebot-apps ros-kinetic-turtlebot-interactions ros-kinetic-turtlebot-simulator ros-kinetic-kobuki-ftdi ros-kinetic-ar-track-alvar-msgs

sudo apt install ros-kinetic-usb-cam

sudo apt install ros-kinetic-visp-auto-tracker

sudo pip install zbar

sudo apt install ros-kinetic-rosbridge-server

sudo apt install ros-kinetic-web-video-server

sudo apt install python-zbar

echo "Install Finished"

