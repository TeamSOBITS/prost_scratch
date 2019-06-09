#!/usr/bin/env python
# coding: utf-8
import rospy
import tf
import math
import time
from tf.transformations import euler_from_quaternion
from geometry_msgs.msg import Pose, Point, Quaternion, Twist
from std_msgs.msg import String
from nav_msgs.msg import Odometry

import os
import numpy as np
import matplotlib.pyplot as plt
import datetime


#indent = 1 tabs
# S:1000	(1000cm直進)
# T:90		(90度回転、反時計回り正回転)

###############################################################################


if __name__ == '__main__':

	rospy.init_node('twist_test')

	listener = tf.TransformListener()
	rospy.sleep(3)

	rospy.loginfo("-- ok.")

	pub_twist = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=10)

	(trans,rot) = listener.lookupTransform('/base_link', '/odom', rospy.Time(0))
	euler = tf.transformations.euler_from_quaternion((rot[0],rot[1],rot[2],rot[3]))
	#現在位置代入
	before_pose_x = trans[0]# * 100#[cm]
	before_pose_y = trans[1]# * 100#[cm]
	before_pose_z = trans[2]# * 100#[cm]
	before_angle_1 = euler[0]#math.degrees(euler[0])#[deg]
	before_angle_2 = euler[1]#math.degrees(euler[1])#[deg]
	before_angle_3 = euler[2]#math.degrees(euler[2])#[deg]
	rate = rospy.Rate(10) # 100hz
	order = 1.0

	start = time.time()
	while not rospy.is_shutdown():
		cmd_vel = Twist()

		(trans,rot) = listener.lookupTransform('/base_link', '/odom', rospy.Time(0))
		dis = abs(trans[0] - before_pose_x)
		rospy.loginfo("--エンコーダ値:              x:%f y:%f z:%f | A:%f B:%f C:%f", trans[0], trans[1], trans[2], rot[0], rot[1], rot[2])
		rospy.loginfo("--初期位置 x: %f [m] ", before_pose_x)
		rospy.loginfo("--現在位置 x: %f [m] ", trans[0])
		rospy.loginfo("--進んだ距離: %f [m] ", dis)
		if  dis >= order:#0.5m以上進んだらstop
			cmd_vel.linear.x = 0
			pub_twist.publish(cmd_vel)
			timeval = now - start
			rospy.loginfo("--経過時間: %f [sec]", timeval)
			break
		else:
			cmd_vel.linear.x = order
		pub_twist.publish(cmd_vel)
		now = time.time()
		timeval = now - start
		rospy.loginfo("--経過時間: %f [sec]", timeval)
		rospy.loginfo(" ")
		#rate.sleep()
		time.sleep(0.03)
	rospy.loginfo("---終了---")
	rospy.spin()
