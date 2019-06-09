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



class CountTwist:
	def __init__(self):
		sub_odom_base_ctrl = rospy.Subscriber('/mobile_base/commands/velocity',Twist, self.twist_callback)
		self.count = 0

	def twist_callback(self,data):
		self.count+=1
		print " "
		print self.count


if __name__ == '__main__':
	rospy.init_node('count_twist')
	rospy.loginfo("-- OK.")

	CountTwist()
	rospy.spin()
