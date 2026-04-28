#!/usr/bin/env python3
import time

import rospy
from pymycobot.mycobot import MyCobot
from std_msgs.msg import Bool


PORT = "/dev/ttyACM0"
BAUD = 115200
MOVE_SPEED = 25
GRIPPER_SPEED = 50

HOME_ANGLES = [0, -20, 20, 0, 0, 0]
PRE_GRASP_ANGLES = [0, -35, 45, 0, 0, 0]
GRASP_ANGLES = [0, -45, 55, 0, 0, 0]
LIFT_ANGLES = [0, -20, 35, 0, 0, 0]


class MyCobotGripperNode:
    def __init__(self):
        rospy.init_node("mycobot_gripper_node", anonymous=True)

        self.busy = False
        self.mc = MyCobot(PORT, BAUD)
        time.sleep(2)

        rospy.loginfo("Initialisiere MyCobot.")
        self.mc.release_all_servos()
        time.sleep(2)
        self.mc.power_on()
        time.sleep(2)
        self.mc.set_fresh_mode(1)
        time.sleep(1)

        self.open_gripper()
        self.move_to(HOME_ANGLES, 4.0)

        rospy.Subscriber("/greif_start", Bool, self.grasp_callback)
        rospy.loginfo("MyCobot-Greifnode wartet auf /greif_start.")

    def move_to(self, angles, wait_s):
        rospy.loginfo("Arm bewege zu: %s", angles)
        self.mc.send_angles(angles, MOVE_SPEED)
        time.sleep(wait_s)

    def open_gripper(self):
        rospy.loginfo("Greifer oeffnen.")
        self.mc.set_gripper_state(0, GRIPPER_SPEED, 1)
        time.sleep(2)

    def close_gripper(self):
        rospy.loginfo("Greifer schliessen.")
        self.mc.set_gripper_state(1, GRIPPER_SPEED, 1)
        time.sleep(2)

    def grasp_callback(self, msg):
        if not msg.data or self.busy:
            return

        self.busy = True
        rospy.loginfo("Greifsignal empfangen. Starte Greifsequenz.")

        try:
            self.open_gripper()
            self.move_to(PRE_GRASP_ANGLES, 4.0)
            self.move_to(GRASP_ANGLES, 4.0)
            self.close_gripper()
            self.move_to(LIFT_ANGLES, 4.0)
            rospy.loginfo("Greifsequenz beendet.")
        except Exception as exc:
            rospy.logerr("Fehler in Greifsequenz: %s", exc)


if __name__ == "__main__":
    try:
        MyCobotGripperNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
