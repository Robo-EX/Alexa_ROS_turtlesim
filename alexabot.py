#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math
import time
from std_srvs.srv import Empty
from flask import Flask
from flask_ask import Ask, statement, question, session
import json
import requests
import time
import unidecode


app = Flask(__name__)
ask = Ask(app, "/robot")


def get_headlines():

    titles = 'is this working'
    return titles


@app.route('/')
def homepage():
    return "hi there, how ya doin?"


@ask.launch
def start_skill():
    welcome_message = 'Hello Bhavik, would you like to move the robot?'
    return question(welcome_message)


@ask.intent("YesIntent")
def yes_intent():
    yes_text = 'To move forward say Move Forward and To move Backward say Move Back'
    return question(yes_text)


@ask.intent("MoveForwardIntent")
def move_forward():
    move(1.0, 3.0, True)
    frwd_text = "Robot moved Forward"
    return statement(frwd_text)


@ask.intent("MoveBackIntent")
def move_back():
    move(1.0, 3.0, False)
    back_text = "Robot moved Backward "
    return statement(back_text)


@ask.intent("RotateClockwiseIntent")
def clockwise():
    rotate(10, 30, True)
    clockwise_text = "Robot rotated clockwise 30 degrees "
    return statement(clockwise_text)


@ask.intent("RotateAntiClockwisekIntent")
def anti_clockwise():
    rotate(10, 30, False)
    anti_clockwise_text = "Robot rotated Anti-clockwise 30 degrees "
    return statement(anti_clockwise_text)


x = 0
y = 0
yaw = 0


def poseCallback(pose_message):
    global x, y, yaw
    x = pose_message.x
    y = pose_message.y
    yaw = pose_message.theta


def move(speed, distance, isForward):
    # declare a Twist message to send velocity commands
    velocity_message = Twist()

    # task 1. assign the x coordinate of linear velocity to the speed.

    if(isForward):
        velocity_message.linear.x = abs(speed)
    else:
        velocity_message.linear.x = -abs(speed)
    distance_moved = 0.0
    # we publish the velocity at 10 Hz (10 times a second)
    loop_rate = rospy.Rate(10)
    # task 2. create a publisher for the velocity message on the appropriate topic.

    rospy.loginfo("Turtlesim moves forwards")
    t0 = rospy.Time.now().to_sec()

    while not rospy.is_shutdown():

        # Setting the current time for distance calculus
        t0 = rospy.Time.now().to_sec()
        current_distance = 0

        # Loop to move the turtle in an specified distance
        while(current_distance < distance):
            # Publish the velocity
            velocity_publisher.publish(velocity_message)
            # Takes actual time to velocity calculus
            t1 = rospy.Time.now().to_sec()
            # Calculates distancePoseStamped
            current_distance = speed*(t1-t0)
        # After the loop, stops the robot
        velocity_message.linear.x = 0
        # Force the robot to stop
        velocity_publisher.publish(velocity_message)
        break


def rotate(angular_speed_degree, relative_angle_degree, clockwise):

    global yaw
    velocity_message = Twist()
    velocity_message.linear.x = 0
    velocity_message.linear.y = 0
    velocity_message.linear.z = 0
    velocity_message.angular.x = 0
    velocity_message.angular.y = 0
    velocity_message.angular.z = 0

    # get current location
    theta0 = yaw
    angular_speed = math.radians(abs(angular_speed_degree))

    if (clockwise):
        velocity_message.angular.z = -abs(angular_speed)
    else:
        velocity_message.angular.z = abs(angular_speed)

    angle_moved = 0.0
    # we publish the velocity at 10 Hz (10 times a second)
    loop_rate = rospy.Rate(50)
    t0 = rospy.Time.now().to_sec()

    while True:
        rospy.loginfo("Turtlesim rotates")
        velocity_publisher.publish(velocity_message)
        # print("==> %s" % velocity_message)

        t1 = rospy.Time.now().to_sec()
        current_angle_degree = (t1-t0)*angular_speed_degree
        print(current_angle_degree)
        loop_rate.sleep()

        if (current_angle_degree > relative_angle_degree):
            rospy.loginfo("reached")
            break

    # finally, stop the robot when the distance is moved
    velocity_message.angular.z = 0
    velocity_publisher.publish(velocity_message)



if __name__ == '__main__':
    try:
        rospy.init_node('turtlesim_motion_pose', anonymous=True)
        velocity_publisher = rospy.Publisher(
            '/turtle1/cmd_vel', Twist, queue_size=10)
        app.run(port=5000, debug=True)
        position_topic = "/turtle1/pose"
        pose_subscriber = rospy.Subscriber(position_topic, Pose, poseCallback)
        rospy.spin()

    except rospy.ROSInterruptException:
        rospy.loginfo("node terminated.")
