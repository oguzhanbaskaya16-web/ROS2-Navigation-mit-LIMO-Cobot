#!/usr/bin/env python3
import time

import rospy
from pymycobot.mycobot import MyCobot


PORT = "/dev/ttyACM0"
BAUD = 115200
MOVE_SPEED = 25
GRIPPER_SPEED = 50
COORD_MODE = 1

# Feste Home-Position.
HOME_ANGLES = [0, -20, 20, 0, 0, 0]

# Pose 1.
POSE_1_ANGLES = [-0.96, -74.17, 16.43, -15.02, 0.43, -0.61]
POSE_1_COORDS = [271.4, -67.6, 199.4, -162.76, 0.23, -90.24]

# Pose 2.
POSE_2_ANGLES = [4.04, -83.84, -30.05, 27.07, 0.61, -7.82]
POSE_2_COORDS = [278.7, -43.3, 70.9, -176.78, 0.17, -78.11]

# Greifposition knapp ueber dem Boden.
GRASP_COORDS = [278.7, -43.3, 10.0, -176.78, 0.17, -78.11]
LIFT_COORDS = [278.7, -43.3, 140.0, -176.78, 0.17, -78.11]

# Stein vor dem Roboter halten, Arm moeglichst kompakt eingezogen.
COMPACT_HOLD_ANGLES = [-90, -45, 65, -20, 0, 0]


def move_to_angles(mc, label, angles, wait_s=4.0):
    if angles is None:
        rospy.logwarn("%s ist noch nicht eingetragen und wird uebersprungen.", label)
        return

    rospy.loginfo("%s: fahre Winkel %s", label, angles)
    mc.send_angles(angles, MOVE_SPEED)
    time.sleep(wait_s)


def move_to_coords(mc, label, coords, wait_s=4.0):
    rospy.loginfo("%s: fahre Koordinaten %s", label, coords)
    mc.send_coords(coords, MOVE_SPEED, COORD_MODE)
    time.sleep(wait_s)


def open_gripper(mc):
    rospy.loginfo("Greifer oeffnen.")
    mc.set_gripper_state(0, GRIPPER_SPEED, 1)
    time.sleep(2.0)


def close_gripper(mc):
    rospy.loginfo("Greifer schliessen.")
    mc.set_gripper_state(1, GRIPPER_SPEED, 1)
    time.sleep(2.0)


def main():
    rospy.init_node("standing_pick")

    port = rospy.get_param("~port", PORT)
    baud = int(rospy.get_param("~baud", BAUD))

    rospy.loginfo("Verbinde MyCobot auf %s mit %d Baud.", port, baud)
    mc = MyCobot(port, baud)
    time.sleep(2.0)

    rospy.loginfo("Initialisiere MyCobot.")
    mc.power_on()
    time.sleep(2.0)
    mc.set_fresh_mode(1)
    time.sleep(1.0)

    open_gripper(mc)
    move_to_angles(mc, "Home", HOME_ANGLES)
    move_to_angles(mc, "Pose 1", POSE_1_ANGLES)
    move_to_angles(mc, "Pose 2", POSE_2_ANGLES)
    move_to_coords(mc, "Grasp", GRASP_COORDS)
    close_gripper(mc)
    move_to_angles(mc, "Kompakte Halteposition", COMPACT_HOLD_ANGLES)

    rospy.loginfo("Standing-Pick-Programm beendet.")


if __name__ == "__main__":
    main()
