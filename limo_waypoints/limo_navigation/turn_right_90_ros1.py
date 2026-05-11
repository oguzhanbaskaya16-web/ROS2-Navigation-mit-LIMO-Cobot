#!/usr/bin/env python3
import math
import time

import rospy
from geometry_msgs.msg import Twist


TURN_ANGLE_DEG = 90.0
ANGULAR_SPEED_RAD_S = 0.4
CMD_VEL_TOPIC = "/cmd_vel"


def publish_velocity(pub, linear_x=0.0, angular_z=0.0):
    msg = Twist()
    msg.linear.x = float(linear_x)
    msg.angular.z = float(angular_z)
    pub.publish(msg)


def stop_robot(pub):
    rate = rospy.Rate(20)
    for _ in range(10):
        publish_velocity(pub, 0.0, 0.0)
        rate.sleep()


def main():
    rospy.init_node("turn_right_90_ros1")

    turn_angle_deg = float(rospy.get_param("~turn_angle_deg", TURN_ANGLE_DEG))
    angular_speed = abs(float(rospy.get_param("~angular_speed_rad_s", ANGULAR_SPEED_RAD_S)))
    cmd_vel_topic = rospy.get_param("~cmd_vel_topic", CMD_VEL_TOPIC)

    if angular_speed <= 0.0:
        rospy.logerr("angular_speed_rad_s muss groesser als 0 sein.")
        return

    pub = rospy.Publisher(cmd_vel_topic, Twist, queue_size=10)
    rospy.sleep(1.0)

    turn_time_s = math.radians(turn_angle_deg) / angular_speed
    rospy.loginfo(
        "Drehe %.1f Grad nach rechts mit %.2f rad/s fuer ca. %.2f s.",
        turn_angle_deg,
        angular_speed,
        turn_time_s,
    )

    start_time = time.time()
    rate = rospy.Rate(10)

    try:
        while not rospy.is_shutdown() and time.time() - start_time < turn_time_s:
            publish_velocity(pub, 0.0, -angular_speed)
            rate.sleep()
    finally:
        stop_robot(pub)
        rospy.loginfo("Drehung beendet, Roboter gestoppt.")


if __name__ == "__main__":
    main()
