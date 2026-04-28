#!/usr/bin/env python3
import rospy
import cv2

from ultralytics import YOLO
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import Bool, Float32
from geometry_msgs.msg import Point


class BausteinDetection:
    def __init__(self):
        rospy.init_node("baustein_detection", anonymous=True)

        self.bridge = CvBridge()

        self.detected_pub = rospy.Publisher("/baustein_detected", Bool, queue_size=10)
        self.center_pub = rospy.Publisher("/baustein_center", Point, queue_size=10)
        self.size_pub = rospy.Publisher("/baustein_size", Float32, queue_size=10)

        # Pfad ggf. anpassen
        self.model = YOLO("/home/agilex/best.pt")

        rospy.Subscriber(
            "/camera/color/image_raw",
            Image,
            self.image_callback,
            queue_size=1,
            buff_size=2**24
        )

        rospy.loginfo("Baustein-Detection ueber /camera/color/image_raw gestartet.")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            rospy.logerr("Fehler bei Bildumwandlung: %s", str(e))
            return

        results = self.model(frame, verbose=False)

        best_width = 0.0
        best_center_x = None
        best_center_y = None

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                bbox_width = float(x2 - x1)
                center_x = float((x1 + x2) / 2.0)
                center_y = float((y1 + y2) / 2.0)

                if bbox_width > best_width:
                    best_width = bbox_width
                    best_center_x = center_x
                    best_center_y = center_y

        if best_center_x is not None:
            self.detected_pub.publish(Bool(data=True))

            point = Point()
            point.x = best_center_x
            point.y = best_center_y
            point.z = 0.0
            self.center_pub.publish(point)

            self.size_pub.publish(Float32(data=best_width))

            rospy.loginfo(
                "Baustein erkannt | center_x: %.1f | size: %.1f",
                best_center_x,
                best_width
            )
        else:
            self.detected_pub.publish(Bool(data=False))
            self.size_pub.publish(Float32(data=0.0))


if __name__ == "__main__":
    try:
        node = BausteinDetection()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass