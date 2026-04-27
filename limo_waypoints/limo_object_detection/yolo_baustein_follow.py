#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist, Point
from std_msgs.msg import Bool

IMAGE_WIDTH = 640.0
IMAGE_CENTER_X = IMAGE_WIDTH / 2.0

# Toleranzbereich um die Bildmitte
CENTER_TOLERANCE = 40.0

# Drehgeschwindigkeit
ANGULAR_SPEED = 0.25

# Vorwärtsgeschwindigkeit
LINEAR_SPEED = 0.05

class BausteinFollower:
    def __init__(self):
        rospy.init_node("baustein_follower", anonymous=True)

        self.detected = False
        self.center_x = None

        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)

        rospy.Subscriber("/baustein_detected", Bool, self.detected_callback)
        rospy.Subscriber("/baustein_center", Point, self.center_callback)

        self.rate = rospy.Rate(10)

    def detected_callback(self, msg):
        self.detected = msg.data

    def center_callback(self, msg):
        self.center_x = msg.x

    def stop_robot(self):
        cmd = Twist()
        self.cmd_pub.publish(cmd)

    def run(self):
        rospy.loginfo("Baustein-Follower gestartet.")
        while not rospy.is_shutdown():
            cmd = Twist()

            if not self.detected or self.center_x is None:
                # nichts erkannt -> stehen bleiben
                self.stop_robot()
                self.rate.sleep()
                continue

            error_x = self.center_x - IMAGE_CENTER_X

            # Erst nur ausrichten
            if abs(error_x) > CENTER_TOLERANCE:
                if error_x < 0:
                    cmd.angular.z = ANGULAR_SPEED
                else:
                    cmd.angular.z = -ANGULAR_SPEED
                cmd.linear.x = 0.0
            else:
                # mittig -> langsam vorfahren
                cmd.angular.z = 0.0
                cmd.linear.x = LINEAR_SPEED

            self.cmd_pub.publish(cmd)
            self.rate.sleep()

if __name__ == "__main__":
    follower = BausteinFollower()
    follower.run()