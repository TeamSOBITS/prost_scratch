#! /usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Bool, String
from std_srvs.srv import Empty, EmptyResponse
from nav_msgs.msg import Odometry
import tf

class InitialposeBroadcaster:
    def __init__(self):
        rospy.init_node('initialpose_broadcaster')
        service = rospy.Service('/initialpose_broadcaster/start', Empty, self.reset_position_server)
        self.sub_odom = rospy.Subscriber('/odom', Odometry, self.odom_callback)
        self.initialize_start = Bool()
        self.broadcast_start = Bool()
        self.scratch_initialpose = Odometry()
        self.br = tf.TransformBroadcaster()
        
    def reset_position_server(self, req):
        self.initialize_start = True
        return EmptyResponse()

    def odom_callback(self, odom):
        if self.initialize_start == True:
            self.scratch_initialpose = odom
            print("######################## saved initialpose ########################")
            print(self.scratch_initialpose)
            print("###################################################################")
            print("initialized odom.")
            self.initialize_start = False
            self.broadcast_start = True
            #print("初期化")
        else:
            pass

        if self.broadcast_start == True:
            #print("broadcasting")
            #base_footprintの位置を初期位置(scratch_initialpose)に設定
            self.br.sendTransform((self.scratch_initialpose.pose.pose.position.x, self.scratch_initialpose.pose.pose.position.y, 0), (0, 0, self.scratch_initialpose.pose.pose.orientation.z, self.scratch_initialpose.pose.pose.orientation.w), rospy.Time.now(), "scratch_initialpose", "odom")
        else:
            pass

if __name__ == '__main__':
    try:
        os = InitialposeBroadcaster()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass