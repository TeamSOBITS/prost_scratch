#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import roslib
import math
from std_msgs.msg import String,Bool,Int32,Int16,UInt8
import numpy as np
from subprocess import Popen
from kobuki_msgs.msg import *
from text_to_speech.srv import TextToSpeech

class Scratch3Connector:

	def __init__(self):
		rospy.init_node('scratch3_connector')
		rospy.loginfo("Scratch3_Connector Started")

		self.sub_scratch_ros = rospy.Subscriber("/scratch_ros", String, self.cb_scratch_ros)#scratchから受け取るメッセージ
		self.pub_ros_scratch = rospy.Publisher('/ros_scratch', String, queue_size = 10)#scratchへ送るメッセージ

		self.sub_client_count = rospy.Subscriber("/client_count", Int32, self.cb_client_count)#clientの数の保持
		#rospy.Timer(rospy.Duration(1), self.ros_scratch_publisher)#常に情報をpubする

		self.sub_bumper = rospy.Subscriber("/mobile_base/events/bumper", BumperEvent, self.bumper_state)
		self.sub_button = rospy.Subscriber("/mobile_base/events/button", ButtonEvent, self.button_state)
		self.sub_wifi_connect = rospy.Subscriber("/wifi_connect", Bool, self.cb_wifi_connect)
		self.sub_battery = rospy.Subscriber('mobile_base/sensors/core', SensorState, self.battery_state)
		self.pub_led1 = rospy.Publisher('/mobile_base/commands/led1', Led, queue_size = 10)#LED1光らせる
		self.pub_led2 = rospy.Publisher('/mobile_base/commands/led2', Led, queue_size = 10)#LED2光らせる
		self.pub_sound = rospy.Publisher('/mobile_base/commands/sound', Sound, queue_size = 10)
		self.pub_stop_motion = rospy.Publisher('/motion_stop', String, queue_size = 10)

		self.pub_odom_base_ctrl = rospy.Publisher('/odom_base_ctrl', String, queue_size = 10)
		self.sub_retrun_arrive = rospy.Subscriber("/retrun_arrive", String, self.retrun_arrive)

	def cb_wifi_connect(self, state):
		if state.data == True:
			self.pub_led1.publish(1)#on--green
		else:
			self.pub_led1.publish(3)#off--red


	def cb_scratch_ros(self, msg):
		self.get_msg = msg.data

		if(self.get_msg.find('LED:') >= 0):
			word = self.get_msg[4:len(self.get_msg)]
			rospy.loginfo(word)
			if word == "off":
				self.pub_led2.publish(0)
			elif word == "green":
				self.pub_led2.publish(1)
			elif word == "yellow":
				self.pub_led2.publish(2)
			elif word == "red":
				self.pub_led2.publish(3)
		elif(self.get_msg.find('S:') >= 0):
			#self.odom_base_call(self.get_msg)
			self.pub_odom_base_ctrl.publish(self.get_msg)
			#self.pub_ros_scratch.publish('arrive')
		elif(self.get_msg.find('T:') >= 0):
			#self.odom_base_call(self.get_msg)
			self.pub_odom_base_ctrl.publish(self.get_msg)
			#self.pub_ros_scratch.publish('arrive')
		elif(self.get_msg.find('sound:') >= 0):
			word = self.get_msg[6:len(self.get_msg)]
			self.pub_sound.publish(np.uint8(word))
		elif(self.get_msg.find('motion_stop:') >= 0):
			word = self.get_msg[12:len(self.get_msg)]
			self.pub_stop_motion.publish(word)
		elif(self.get_msg.find('speech:') >= 0):
			word = self.get_msg[7:len(self.get_msg)]
			try:
				srv_speech = rospy.ServiceProxy('/speech_word', TextToSpeech)
				resp = srv_speech(word)
			except rospy.ServiceException, e:
				print "Service call failed: %s"%e


	def cb_client_count(self, data):
		self.client_count = data.data
		word = "client_count:" + str(self.client_count)
		self.pub_ros_scratch.publish(word)

	def ros_scratch_publisher(self,event):	#常にscratch側にpubする(使ってない)
		word = "client_count:" + str(self.client_count)
		self.pub_ros_scratch.publish(word)

	def retrun_arrive(self, ret_value):# TurtleBotの位置調整
		self.pub_ros_scratch.publish('arrive')

	def odom_base_call(self, str_x):# TurtleBotの位置調整
		rospy.wait_for_service('odom_base_ctrl')
		print "sending it."
		try:
			service_name = rospy.ServiceProxy('odom_base_ctrl', odom_base)
			resp = service_name(str_x)
			return resp.res_str
		except rospy.ServiceException, e:
			print "Service call failed: %s"%e

	def bumper_state(self, data):
		word = String()
		if(1 == data.state):
			if(0 == data.bumper):
				word.data = 'left_bumper:true'
				self.pub_ros_scratch.publish(word)
			elif(1 == data.bumper):
				word.data = 'front_bumper:true'
				self.pub_ros_scratch.publish(word)
			elif(2 == data.bumper):
				word.data = 'right_bumper:true'
				self.pub_ros_scratch.publish(word)
		elif(0 == data.state):
			if(0 == data.bumper):
				word.data = 'left_bumper:false'
				self.pub_ros_scratch.publish(word)
			elif(1 == data.bumper):
				word.data = 'front_bumper:false'
				self.pub_ros_scratch.publish(word)
			elif(2 == data.bumper):
				word.data = 'right_bumper:false'
				self.pub_ros_scratch.publish(word)

	def button_state(self, data):
		word = String()
		if(0 == data.state):
			if(0 == data.button):
				word.data = 'button_0:false'
				self.pub_ros_scratch.publish(word)
			elif(1 == data.button):
				word.data = 'button_1:false'
				self.pub_ros_scratch.publish(word)
			elif(2 == data.button):
				word.data = 'button_2:false'
				self.pub_ros_scratch.publish(word)
		elif(1 == data.state):
			if(0 == data.button):
				word.data = 'button_0:true'
				self.pub_ros_scratch.publish(word)
			elif(1 == data.button):
				word.data = 'button_1:true'
				self.pub_ros_scratch.publish(word)
			elif(2 == data.button):
				word.data = 'button_2:true'
				self.pub_ros_scratch.publish(word)

	def battery_state(self, data):
		word = 'battery:' + str(data.battery)
		self.pub_ros_scratch.publish(word)

if __name__ == '__main__':
	sc = Scratch3Connector()
	rospy.spin()
