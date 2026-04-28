#!/usr/bin/env python3
import numpy as np
import rospy
from cv_bridge import CvBridge
from geometry_msgs.msg import Point, Twist
from sensor_msgs.msg import Image
from std_msgs.msg import Bool


COLOR_IMAGE_WIDTH = 640.0
COLOR_IMAGE_HEIGHT = 480.0
IMAGE_CENTER_X = COLOR_IMAGE_WIDTH / 2.0

CENTER_TOLERANCE = 40.0
CONFIRM_CENTER_TOLERANCE = 70.0
ANGULAR_SPEED = 0.25

TARGET_DISTANCE_M = 0.55
STOP_DISTANCE_MIN_M = 0.55
STOP_DISTANCE_MAX_M = 0.63
GRASP_CONFIRMATION_S = 3.0
MAX_LINEAR_SPEED = 0.06
MIN_LINEAR_SPEED = 0.02

DEPTH_WINDOW_SIZE = 31
LAST_DEPTH_TIMEOUT_S = 0.8
MAX_VALID_DISTANCE_M = 2.0
MAX_DISTANCE_JUMP_M = 0.45
BOTTOM_STOP_Y = 465.0


class BausteinDepthFollower:
    def __init__(self):
        rospy.init_node("baustein_depth_follower", anonymous=True)

        self.bridge = CvBridge()
        self.detected = False
        self.center_x = None
        self.center_y = None
        self.depth_image = None
        self.last_valid_distance_m = None
        self.last_valid_distance_time = rospy.Time(0)
        self.grasp_requested = False
        self.grasp_candidate_since = None

        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        self.grasp_pub = rospy.Publisher("/greif_start", Bool, queue_size=1, latch=True)

        rospy.Subscriber("/baustein_detected", Bool, self.detected_callback)
        rospy.Subscriber("/baustein_center", Point, self.center_callback)
        rospy.Subscriber("/camera/depth/image_raw", Image, self.depth_callback, queue_size=1)

        self.rate = rospy.Rate(10)

    def detected_callback(self, msg):
        self.detected = msg.data

    def center_callback(self, msg):
        self.center_x = msg.x
        self.center_y = msg.y

    def depth_callback(self, msg):
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        except Exception as exc:
            rospy.logwarn_throttle(2.0, "Depth-Bild konnte nicht gelesen werden: %s", exc)

    def stop_robot(self):
        self.cmd_pub.publish(Twist())

    def reset_grasp_confirmation(self):
        if self.grasp_candidate_since is not None:
            rospy.loginfo("Greifbestaetigung abgebrochen.")
        self.grasp_candidate_since = None

    def get_depth_at_baustein(self):
        if self.depth_image is None or self.center_x is None or self.center_y is None:
            return None

        height, width = self.depth_image.shape[:2]
        depth_x = int(self.center_x * width / COLOR_IMAGE_WIDTH)
        depth_y = int(self.center_y * height / COLOR_IMAGE_HEIGHT)

        half_window = DEPTH_WINDOW_SIZE // 2
        x1 = max(0, depth_x - half_window)
        x2 = min(width, depth_x + half_window + 1)
        y1 = max(0, depth_y - half_window)
        y2 = min(height, depth_y + half_window + 1)

        depth_values = self.depth_image[y1:y2, x1:x2].astype(np.float32)

        if self.depth_image.dtype == np.uint16:
            depth_values = depth_values / 1000.0

        valid = depth_values[np.isfinite(depth_values)]
        valid = valid[(valid > 0.05) & (valid < MAX_VALID_DISTANCE_M)]

        if valid.size == 0:
            if self.last_valid_distance_m is None:
                return None

            age = (rospy.Time.now() - self.last_valid_distance_time).to_sec()
            if age <= LAST_DEPTH_TIMEOUT_S:
                return self.last_valid_distance_m

            return None

        distance_m = float(np.median(valid))

        if (
            self.last_valid_distance_m is not None
            and self.last_valid_distance_m < 0.9
            and distance_m - self.last_valid_distance_m > MAX_DISTANCE_JUMP_M
        ):
            return self.last_valid_distance_m

        self.last_valid_distance_m = distance_m
        self.last_valid_distance_time = rospy.Time.now()
        return distance_m

    def run(self):
        rospy.loginfo("Baustein-Depth-Follower gestartet. Zielabstand: %.2f m", TARGET_DISTANCE_M)

        while not rospy.is_shutdown():
            cmd = Twist()

            if self.grasp_requested:
                self.stop_robot()
                self.rate.sleep()
                continue

            if not self.detected or self.center_x is None:
                self.reset_grasp_confirmation()
                self.stop_robot()
                self.rate.sleep()
                continue

            distance_m = self.get_depth_at_baustein()
            if distance_m is None:
                self.reset_grasp_confirmation()
                rospy.logwarn_throttle(2.0, "Kein gueltiger Depth-Abstand am Baustein.")
                self.stop_robot()
                self.rate.sleep()
                continue

            error_x = self.center_x - IMAGE_CENTER_X

            rospy.loginfo_throttle(
                1.0,
                "Baustein: x=%.0f px, y=%.0f px, Abstand=%.2f m",
                self.center_x,
                self.center_y,
                distance_m,
            )

            if self.center_y is not None and self.center_y >= BOTTOM_STOP_Y:
                self.reset_grasp_confirmation()
                rospy.loginfo_throttle(
                    2.0,
                    "Baustein ist am unteren Bildrand. Stoppe bei %.2f m.",
                    distance_m,
                )
                self.stop_robot()
                self.rate.sleep()
                continue

            active_center_tolerance = (
                CONFIRM_CENTER_TOLERANCE
                if self.grasp_candidate_since is not None
                else CENTER_TOLERANCE
            )

            if abs(error_x) > active_center_tolerance:
                self.reset_grasp_confirmation()
                cmd.angular.z = ANGULAR_SPEED if error_x < 0 else -ANGULAR_SPEED
                cmd.linear.x = 0.0
            else:
                if STOP_DISTANCE_MIN_M <= distance_m <= STOP_DISTANCE_MAX_M:
                    self.stop_robot()

                    now = rospy.Time.now()
                    if self.grasp_candidate_since is None:
                        self.grasp_candidate_since = now
                        rospy.loginfo(
                            "Greiffenster erreicht bei %.2f m. Warte %.1f s zur Bestaetigung.",
                            distance_m,
                            GRASP_CONFIRMATION_S,
                        )

                    confirmation_age = (now - self.grasp_candidate_since).to_sec()
                    rospy.loginfo_throttle(
                        1.0,
                        "Greifabstand wird bestaetigt: %.1f/%.1f s",
                        confirmation_age,
                        GRASP_CONFIRMATION_S,
                    )

                    if confirmation_age >= GRASP_CONFIRMATION_S and not self.grasp_requested:
                        self.grasp_pub.publish(Bool(data=True))
                        self.grasp_requested = True
                        rospy.loginfo("Greifsignal auf /greif_start gesendet.")

                    self.rate.sleep()
                    continue

                if distance_m > STOP_DISTANCE_MAX_M:
                    self.reset_grasp_confirmation()
                    cmd.angular.z = 0.0
                    cmd.linear.x = min(
                        MAX_LINEAR_SPEED,
                        max(MIN_LINEAR_SPEED, (distance_m - STOP_DISTANCE_MAX_M) * 0.25),
                    )
                else:
                    self.stop_robot()
                    rospy.logwarn_throttle(
                        2.0,
                        "Baustein ist naeher als das Greiffenster: %.2f m < %.2f m.",
                        distance_m,
                        STOP_DISTANCE_MIN_M,
                    )
                    self.rate.sleep()
                    continue

            self.cmd_pub.publish(cmd)
            self.rate.sleep()


if __name__ == "__main__":
    try:
        BausteinDepthFollower().run()
    except rospy.ROSInterruptException:
        pass
