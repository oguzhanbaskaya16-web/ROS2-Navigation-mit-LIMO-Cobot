#!/usr/bin/env python3
import math
import time
from collections import deque

import numpy as np
import rospy
from cv_bridge import CvBridge
from geometry_msgs.msg import Point
from pymycobot.mycobot import MyCobot
from sensor_msgs.msg import CameraInfo, Image
from std_msgs.msg import Bool


PORT = "/dev/ttyACM0"
BAUD = 115200

MOVE_SPEED = 25
GRIPPER_SPEED = 50

HOME_COORDS = [180, 0, 120, 180, 0, 0]

DEPTH_WINDOW_SIZE = 31
MIN_DEPTH_M = 0.08
MAX_DEPTH_M = 1.50
MAX_TARGET_AGE_S = 1.0
MIN_STABLE_SAMPLES = 5
MAX_SAMPLE_SPREAD_MM = 35.0


class BausteinAutoGrabber:
    def __init__(self):
        rospy.init_node("baustein_auto_grabber", anonymous=True)

        self.port = rospy.get_param("~port", PORT)
        self.baud = int(rospy.get_param("~baud", BAUD))
        self.move_speed = int(rospy.get_param("~move_speed", MOVE_SPEED))
        self.gripper_speed = int(rospy.get_param("~gripper_speed", GRIPPER_SPEED))

        self.detected_topic = rospy.get_param("~detected_topic", "/baustein_detected")
        self.center_topic = rospy.get_param("~center_topic", "/baustein_center")
        self.depth_topic = rospy.get_param("~depth_topic", "/camera/depth/image_raw")
        self.camera_info_topic = rospy.get_param("~camera_info_topic", "/camera/depth/camera_info")
        self.grasp_start_topic = rospy.get_param("~grasp_start_topic", "/greif_start")

        self.image_width = float(rospy.get_param("~image_width", 640.0))
        self.image_height = float(rospy.get_param("~image_height", 480.0))

        # Kalibrierwerte: so wird Kamera-3D in MyCobot-Koordinaten gemappt.
        self.camera_to_arm_x_mm = float(rospy.get_param("~camera_to_arm_x_mm", -400.0))
        self.camera_to_arm_y_mm = float(rospy.get_param("~camera_to_arm_y_mm", 0.0))
        self.fixed_grasp_z_mm = float(rospy.get_param("~fixed_grasp_z_mm", 45.0))

        self.approach_height_mm = float(rospy.get_param("~approach_height_mm", 75.0))
        self.lift_height_mm = float(rospy.get_param("~lift_height_mm", 120.0))
        self.rx = float(rospy.get_param("~rx", 180.0))
        self.ry = float(rospy.get_param("~ry", 0.0))
        self.rz = float(rospy.get_param("~rz", 0.0))

        self.x_min = float(rospy.get_param("~x_min", 100.0))
        self.x_max = float(rospy.get_param("~x_max", 280.0))
        self.y_min = float(rospy.get_param("~y_min", -130.0))
        self.y_max = float(rospy.get_param("~y_max", 130.0))
        self.z_min = float(rospy.get_param("~z_min", 25.0))
        self.z_max = float(rospy.get_param("~z_max", 180.0))

        self.bridge = CvBridge()
        self.detected = False
        self.center = None
        self.depth_image = None
        self.camera_info = None
        self.busy = False
        self.samples = deque(maxlen=12)
        self.last_target = None
        self.last_target_time = rospy.Time(0)

        rospy.Subscriber(self.detected_topic, Bool, self.detected_callback)
        rospy.Subscriber(self.center_topic, Point, self.center_callback)
        rospy.Subscriber(self.depth_topic, Image, self.depth_callback, queue_size=1)
        rospy.Subscriber(self.camera_info_topic, CameraInfo, self.camera_info_callback, queue_size=1)
        rospy.Subscriber(self.grasp_start_topic, Bool, self.grasp_start_callback)

        rospy.loginfo("Verbinde MyCobot auf %s mit %d Baud.", self.port, self.baud)
        self.mc = MyCobot(self.port, self.baud)
        time.sleep(2)
        self.prepare_arm()

        self.timer = rospy.Timer(rospy.Duration(0.1), self.update_target)
        rospy.loginfo("Baustein-Auto-Grabber wartet auf stabile Bausteinposition und /greif_start.")

    def prepare_arm(self):
        self.mc.release_all_servos()
        time.sleep(2)
        self.mc.power_on()
        time.sleep(2)
        self.mc.set_fresh_mode(1)
        time.sleep(1)
        self.open_gripper()
        self.move_to_coords(HOME_COORDS, 4.0)

    def detected_callback(self, msg):
        self.detected = bool(msg.data)
        if not self.detected:
            self.samples.clear()

    def center_callback(self, msg):
        self.center = msg

    def depth_callback(self, msg):
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        except Exception as exc:
            rospy.logwarn_throttle(2.0, "Depth-Bild konnte nicht gelesen werden: %s", exc)

    def camera_info_callback(self, msg):
        self.camera_info = msg

    def grasp_start_callback(self, msg):
        if not msg.data or self.busy:
            return

        target = self.get_stable_target()
        if target is None:
            rospy.logwarn("Kein stabiler Baustein-Zielpunkt vorhanden. Greifen abgebrochen.")
            return

        self.execute_grasp(target)

    def update_target(self, _event):
        if self.busy or not self.detected or self.center is None:
            return

        target = self.calculate_arm_target()
        if target is None:
            return

        if not self.is_target_safe(target):
            rospy.logwarn_throttle(2.0, "Berechnete Greifposition ist ausserhalb des Arbeitsbereichs: %s", target)
            return

        self.samples.append(target)
        stable_target = self.get_stable_target()
        if stable_target is not None:
            self.last_target = stable_target
            self.last_target_time = rospy.Time.now()
            rospy.loginfo_throttle(
                1.0,
                "Stabile Greifposition: x=%.0f y=%.0f z=%.0f mm",
                stable_target[0],
                stable_target[1],
                stable_target[2],
            )

    def calculate_arm_target(self):
        if self.depth_image is None or self.center is None:
            return None

        depth_m = self.get_depth_at_center()
        if depth_m is None:
            return None

        camera_matrix = self.get_camera_matrix()
        if camera_matrix is not None and camera_matrix[0] > 0 and camera_matrix[4] > 0:
            fx = camera_matrix[0]
            fy = camera_matrix[4]
            cx = camera_matrix[2]
            cy = camera_matrix[5]
            px = self.center.x * self.depth_image.shape[1] / self.image_width
            py = self.center.y * self.depth_image.shape[0] / self.image_height
        else:
            fx = float(rospy.get_param("~fallback_fx", 580.0))
            fy = float(rospy.get_param("~fallback_fy", 580.0))
            cx = self.depth_image.shape[1] / 2.0
            cy = self.depth_image.shape[0] / 2.0
            px = self.center.x * self.depth_image.shape[1] / self.image_width
            py = self.center.y * self.depth_image.shape[0] / self.image_height

        camera_x_m = (px - cx) * depth_m / fx
        camera_y_m = (py - cy) * depth_m / fy
        camera_z_m = depth_m

        arm_x_mm = camera_z_m * 1000.0 + self.camera_to_arm_x_mm
        arm_y_mm = -camera_x_m * 1000.0 + self.camera_to_arm_y_mm
        arm_z_mm = self.fixed_grasp_z_mm

        if not all(math.isfinite(v) for v in (arm_x_mm, arm_y_mm, arm_z_mm, camera_y_m)):
            return None

        return [arm_x_mm, arm_y_mm, arm_z_mm, self.rx, self.ry, self.rz]

    def get_camera_matrix(self):
        if self.camera_info is None:
            return None

        # ROS1 nutzt CameraInfo.K, ROS2 nutzt je nach Python-API oft camera_info.k.
        return getattr(self.camera_info, "K", None) or getattr(self.camera_info, "k", None)

    def get_depth_at_center(self):
        if self.depth_image is None:
            return None

        height, width = self.depth_image.shape[:2]
        x = int(self.center.x * width / self.image_width)
        y = int(self.center.y * height / self.image_height)

        half_window = DEPTH_WINDOW_SIZE // 2
        x1 = max(0, x - half_window)
        x2 = min(width, x + half_window + 1)
        y1 = max(0, y - half_window)
        y2 = min(height, y + half_window + 1)

        values = self.depth_image[y1:y2, x1:x2].astype(np.float32)
        if self.depth_image.dtype == np.uint16:
            values = values / 1000.0

        valid = values[np.isfinite(values)]
        valid = valid[(valid >= MIN_DEPTH_M) & (valid <= MAX_DEPTH_M)]
        if valid.size == 0:
            rospy.logwarn_throttle(2.0, "Kein gueltiger Depth-Wert am Baustein.")
            return None

        return float(np.median(valid))

    def get_stable_target(self):
        if len(self.samples) < MIN_STABLE_SAMPLES:
            if self.last_target is not None:
                age = (rospy.Time.now() - self.last_target_time).to_sec()
                if age <= MAX_TARGET_AGE_S:
                    return self.last_target
            return None

        xyz = np.array([sample[:3] for sample in self.samples], dtype=np.float32)
        spread = np.max(np.ptp(xyz, axis=0))
        if spread > MAX_SAMPLE_SPREAD_MM:
            rospy.logwarn_throttle(2.0, "Bausteinposition schwankt noch zu stark: %.0f mm.", spread)
            return None

        median_xyz = np.median(xyz, axis=0)
        return [float(median_xyz[0]), float(median_xyz[1]), float(median_xyz[2]), self.rx, self.ry, self.rz]

    def is_target_safe(self, target):
        x, y, z = target[:3]
        return (
            self.x_min <= x <= self.x_max
            and self.y_min <= y <= self.y_max
            and self.z_min <= z <= self.z_max
        )

    def move_to_coords(self, coords, wait_s):
        rospy.loginfo("Fahre MyCobot zu Koordinaten: %s", [round(v, 1) for v in coords])
        self.mc.send_coords(coords, self.move_speed, 1)
        time.sleep(wait_s)

    def open_gripper(self):
        rospy.loginfo("Greifer oeffnen.")
        self.mc.set_gripper_state(0, self.gripper_speed, 1)
        time.sleep(2)

    def close_gripper(self):
        rospy.loginfo("Greifer schliessen.")
        self.mc.set_gripper_state(1, self.gripper_speed, 1)
        time.sleep(2)

    def execute_grasp(self, target):
        self.busy = True
        try:
            grasp = list(target)
            pre_grasp = list(target)
            lift = list(target)
            pre_grasp[2] = min(self.z_max, grasp[2] + self.approach_height_mm)
            lift[2] = min(self.z_max, self.lift_height_mm)

            rospy.loginfo("Starte automatisches Greifen bei: %s", [round(v, 1) for v in grasp])
            self.open_gripper()
            self.move_to_coords(pre_grasp, 4.0)
            self.move_to_coords(grasp, 4.0)
            self.close_gripper()
            self.move_to_coords(lift, 4.0)
            rospy.loginfo("Automatisches Greifen beendet.")
        except Exception as exc:
            rospy.logerr("Fehler beim automatischen Greifen: %s", exc)
        finally:
            self.busy = False


def main():
    try:
        BausteinAutoGrabber()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass


if __name__ == "__main__":
    main()
