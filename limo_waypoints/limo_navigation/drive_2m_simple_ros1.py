#!/usr/bin/env python3
import math
import time

import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from pymycobot.mycobot import MyCobot


SPEED_M_S = 0.2
DRIVE_TIME_S = 3.0
DRIVE_MULTIPLIER = 3.0
CMD_VEL_TOPIC = "/cmd_vel"
ODOM_TOPIC = "/odom"
TURN_ANGLE_DEG = 65.0
ANGULAR_SPEED_RAD_S = 0.25
SLOWDOWN_ERROR_DEG = 20.0
ANGLE_TOLERANCE_DEG = 2.0
PORT = "/dev/ttyACM0"
BAUD = 115200
MOVE_SPEED = 25
GRIPPER_SPEED = 50
COORD_MODE = 1
HOME_ANGLES = [0, -20, 20, 0, 0, 0]
POSE_1_ANGLES = [-0.96, -74.17, 16.43, -15.02, 0.43, -0.61]
POSE_2_ANGLES = [4.04, -83.84, -30.05, 27.07, 0.61, -7.82]
GRASP_COORDS = [278.7, -43.3, 10.0, -176.78, 0.17, -78.11]
COMPACT_HOLD_ANGLES = [-90, -45, 65, -20, 0, 0]


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


def publish_velocity(pub, linear_x, angular_z=0.0):
    msg = Twist()
    msg.linear.x = float(linear_x)
    msg.angular.z = float(angular_z)
    pub.publish(msg)


def stop_robot(pub):
    rate = rospy.Rate(20)
    for _ in range(10):
        publish_velocity(pub, 0.0, 0.0)
        rate.sleep()


def drive_straight_for_time(pub, speed, drive_time_s, label="Geradeausfahrt"):
    rospy.loginfo(
        "%s: fahre geradeaus mit %.2f m/s fuer %.1f s.",
        label,
        speed,
        drive_time_s,
    )

    start_time = time.time()
    rate = rospy.Rate(10)

    try:
        while not rospy.is_shutdown() and time.time() - start_time < drive_time_s:
            publish_velocity(pub, speed, 0.0)
            rate.sleep()
    finally:
        stop_robot(pub)
        rospy.loginfo("%s beendet. Roboter gestoppt.", label)


def init_mycobot():
    port = rospy.get_param("~mycobot_port", PORT)
    baud = int(rospy.get_param("~mycobot_baud", BAUD))

    rospy.loginfo("Verbinde MyCobot auf %s mit %d Baud.", port, baud)
    mc = MyCobot(port, baud)
    time.sleep(2)

    rospy.loginfo("Initialisiere MyCobot.")
    mc.power_on()
    time.sleep(2)
    mc.set_fresh_mode(1)
    time.sleep(1)
    return mc


def move_to_angles(mc, label, angles, wait_s=4.0):
    move_speed = int(rospy.get_param("~move_speed", MOVE_SPEED))

    rospy.loginfo("%s: fahre Winkel %s", label, angles)
    mc.send_angles(angles, move_speed)
    time.sleep(wait_s)


def move_to_coords(mc, label, coords, wait_s=4.0):
    move_speed = int(rospy.get_param("~move_speed", MOVE_SPEED))

    rospy.loginfo("%s: fahre Koordinaten %s", label, coords)
    mc.send_coords(coords, move_speed, COORD_MODE)
    time.sleep(wait_s)


def open_gripper(mc):
    rospy.loginfo("Greifer oeffnen.")
    mc.set_gripper_state(0, GRIPPER_SPEED, 1)
    time.sleep(2)


def close_gripper(mc):
    rospy.loginfo("Greifer schliessen.")
    mc.set_gripper_state(1, GRIPPER_SPEED, 1)
    time.sleep(2)


def run_standing_pick():
    mc = init_mycobot()

    open_gripper(mc)
    move_to_angles(mc, "Home", HOME_ANGLES)
    move_to_angles(mc, "Pose 1", POSE_1_ANGLES)
    move_to_angles(mc, "Pose 2", POSE_2_ANGLES)
    move_to_coords(mc, "Grasp", GRASP_COORDS)
    close_gripper(mc)
    move_to_angles(mc, "Kompakte Halteposition", COMPACT_HOLD_ANGLES)

    rospy.loginfo("Standing-Pick beendet.")
    return mc


def run_standing_place(mc):
    move_to_coords(mc, "Place", GRASP_COORDS)
    open_gripper(mc)

    rospy.loginfo("Standing-Place beendet.")


def turn_right_with_odom(pub):
    turn_angle_deg = float(rospy.get_param("~turn_angle_deg", TURN_ANGLE_DEG))
    angular_speed = abs(float(rospy.get_param("~angular_speed_rad_s", ANGULAR_SPEED_RAD_S)))
    tolerance_deg = float(rospy.get_param("~angle_tolerance_deg", ANGLE_TOLERANCE_DEG))
    slowdown_error_deg = float(rospy.get_param("~slowdown_error_deg", SLOWDOWN_ERROR_DEG))

    if angular_speed <= 0.0:
        rospy.logerr("angular_speed_rad_s muss groesser als 0 sein.")
        return

    rospy.loginfo("Warte auf Odometrie von %s ...", ODOM_TOPIC)
    timeout_time = time.time() + 5.0
    while not rospy.is_shutdown() and current_yaw is None and time.time() < timeout_time:
        rospy.sleep(0.05)

    if current_yaw is None:
        rospy.logerr("Keine Odometrie empfangen. Rechtsdrehung abgebrochen.")
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
        "Rechtsdrehung beendet. Aktueller Winkel %.1f Grad, Fehler %.1f Grad.",
        math.degrees(current_yaw),
        math.degrees(normalize_angle(target_yaw - current_yaw)),
    )


def move_arm_home(mc):
    move_to_angles(mc, "Home-Position", HOME_ANGLES)
    rospy.loginfo("Home-Position erreicht.")


def main():
    rospy.init_node("drive_2m_simple_ros1")

    speed = float(rospy.get_param("~speed_m_s", SPEED_M_S))
    drive_time_s = float(rospy.get_param("~drive_time_s", DRIVE_TIME_S))
    drive_multiplier = float(rospy.get_param("~drive_multiplier", DRIVE_MULTIPLIER))
    cmd_vel_topic = rospy.get_param("~cmd_vel_topic", CMD_VEL_TOPIC)
    odom_topic = rospy.get_param("~odom_topic", ODOM_TOPIC)

    if speed <= 0.0:
        rospy.logerr("speed_m_s muss groesser als 0 sein.")
        return

    if drive_multiplier <= 0.0:
        rospy.logerr("drive_multiplier muss groesser als 0 sein.")
        return

    pub = rospy.Publisher(cmd_vel_topic, Twist, queue_size=10)
    rospy.Subscriber(odom_topic, Odometry, odom_callback)
    rospy.sleep(1.0)

    drive_straight_for_time(
        pub,
        speed,
        drive_time_s * drive_multiplier,
        "Erste Geradeausfahrt",
    )

    mc = run_standing_pick()
    turn_right_with_odom(pub)
    drive_straight_for_time(
        pub,
        speed,
        drive_time_s * drive_multiplier / 2.0,
        "Zweite Geradeausfahrt",
    )
    turn_right_with_odom(pub)
    drive_straight_for_time(
        pub,
        speed,
        drive_time_s * drive_multiplier / 2.0,
        "Dritte Geradeausfahrt",
    )
    run_standing_place(mc)
    move_arm_home(mc)


if __name__ == "__main__":
    main()
