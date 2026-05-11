#!/usr/bin/env python3
import math
import time

import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


TURN_ANGLE_DEG = 65.0
ANGULAR_SPEED_RAD_S = 0.25
SLOWDOWN_ERROR_DEG = 20.0
ANGLE_TOLERANCE_DEG = 2.0
CMD_VEL_TOPIC = "/cmd_vel"
ODOM_TOPIC = "/odom"


current_yaw = None


def normalize_angle(angle):
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def yaw_from_quaternion(q):
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


def odom_callback(msg):
    global current_yaw
    current_yaw = yaw_from_quaternion(msg.pose.pose.orientation)


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
    rospy.init_node("turn_right_90_odom_ros1")

    turn_angle_deg = float(rospy.get_param("~turn_angle_deg", TURN_ANGLE_DEG))
    angular_speed = abs(float(rospy.get_param("~angular_speed_rad_s", ANGULAR_SPEED_RAD_S)))
    tolerance_deg = float(rospy.get_param("~angle_tolerance_deg", ANGLE_TOLERANCE_DEG))
    slowdown_error_deg = float(rospy.get_param("~slowdown_error_deg", SLOWDOWN_ERROR_DEG))
    cmd_vel_topic = rospy.get_param("~cmd_vel_topic", CMD_VEL_TOPIC)
    odom_topic = rospy.get_param("~odom_topic", ODOM_TOPIC)

    if angular_speed <= 0.0:
        rospy.logerr("angular_speed_rad_s muss groesser als 0 sein.")
        return

    pub = rospy.Publisher(cmd_vel_topic, Twist, queue_size=10)
    rospy.Subscriber(odom_topic, Odometry, odom_callback)

    rospy.loginfo("Warte auf Odometrie von %s ...", odom_topic)
    timeout_time = time.time() + 5.0
    while not rospy.is_shutdown() and current_yaw is None and time.time() < timeout_time:
        rospy.sleep(0.05)

    if current_yaw is None:
        rospy.logerr("Keine Odometrie empfangen. Drehung abgebrochen.")
        return

    start_yaw = current_yaw
    target_yaw = normalize_angle(start_yaw - math.radians(turn_angle_deg))
    tolerance = math.radians(tolerance_deg)
    slowdown_error = math.radians(slowdown_error_deg)

    rospy.loginfo(
        "Drehe nach rechts: Start %.1f Grad, Ziel %.1f Grad.",
        math.degrees(start_yaw),
        math.degrees(target_yaw),
    )

    rate = rospy.Rate(20)
    try:
        while not rospy.is_shutdown():
            error = normalize_angle(target_yaw - current_yaw)

            if abs(error) <= tolerance:
                break

            speed = angular_speed
            if abs(error) < slowdown_error:
                speed = max(0.08, angular_speed * abs(error) / slowdown_error)

            publish_velocity(pub, 0.0, -speed)
            rate.sleep()
    finally:
        stop_robot(pub)

    rospy.loginfo(
        "Drehung beendet. Aktueller Winkel %.1f Grad, Fehler %.1f Grad.",
        math.degrees(current_yaw),
        math.degrees(normalize_angle(target_yaw - current_yaw)),
    )


if __name__ == "__main__":
    main()
