#! /usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Bool, String
from std_srvs.srv import Empty, EmptyResponse
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose2D,PoseStamped
import tf
import math

class OdomPublisher:
    def __init__(self):
        rospy.init_node('odom_publisher')
        self.pub_pose2d = rospy.Publisher('/odom_publisher/scratch_base_footprint', Pose2D, queue_size = 1)        
        self.scratch_pose = Pose2D()
        self.listener = tf.TransformListener()
        while not rospy.is_shutdown():
            #scratch_initialからみたbase_footprintの座標を取得
            if self.listener.frameExists("scratch_initialpose") and self.listener.frameExists("base_footprint"):
                try:
                    (trans,rot) = self.listener.lookupTransform('base_footprint', 'scratch_initialpose', rospy.Time(0))
                except (self.listener.LookupException, self.listener.ConnectivityException, self.listener.ExtrapolationException):
                    pass

                rad = math.atan2(trans[1], trans[0])
                #deg = math.degrees(rad)

                #print ("x:"+ str(trans[0]))
                #print ("y:" + str(trans[1]))
                #print ("theta:" + str(deg))
            
                self.scratch_pose.x = trans[1]
                self.scratch_pose.y = trans[0]
                self.scratch_pose.theta = rad

                self.pub_pose2d.publish(self.scratch_pose)

if __name__ == '__main__':
    try:
        os = OdomPublisher()
        rospy.spin()
    except rospy.ROSInterruptException: pass