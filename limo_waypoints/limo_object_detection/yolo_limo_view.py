#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2

MODEL_PATH = "/home/agilex/best.pt"
IMAGE_TOPIC = "/camera/color/image_raw"
CONFIDENCE = 0.5

class LimoYoloViewer:
    def __init__(self):
        rospy.init_node("limo_yolo_viewer", anonymous=True)
        self.bridge = CvBridge()
        self.model = YOLO(MODEL_PATH)
        self.sub = rospy.Subscriber(
            IMAGE_TOPIC,
            Image,
            self.image_callback,
            queue_size=1,
            buff_size=2**24
        )

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            results = self.model.predict(source=frame, conf=CONFIDENCE, verbose=False)
            annotated = results[0].plot()
            cv2.imshow("LIMO YOLO", annotated)
            cv2.waitKey(1)
        except Exception as e:
            rospy.logerr(f"Fehler in image_callback: {e}")

if __name__ == "__main__":
    LimoYoloViewer()
    rospy.spin()