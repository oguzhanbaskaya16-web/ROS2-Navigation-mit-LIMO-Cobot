#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import Bool, Float32
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2

MODEL_PATH = "/home/agilex/best.pt"
IMAGE_TOPIC = "/camera/color/image_raw"
CONFIDENCE_THRESHOLD = 0.5

class BausteinDetector:
    def __init__(self):
        rospy.init_node("baustein_detector", anonymous=True)

        self.bridge = CvBridge()
        self.model = YOLO(MODEL_PATH)

        self.detected_pub = rospy.Publisher("/baustein_detected", Bool, queue_size=10)
        self.center_pub = rospy.Publisher("/baustein_center", Point, queue_size=10)
        self.conf_pub = rospy.Publisher("/baustein_confidence", Float32, queue_size=10)

        self.sub = rospy.Subscriber(
            IMAGE_TOPIC,
            Image,
            self.image_callback,
            queue_size=1,
            buff_size=2**24
        )

        rospy.loginfo("Baustein-Detektor gestartet.")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            results = self.model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, verbose=False)

            detected = False
            best_conf = 0.0
            best_center = None

            if results and len(results) > 0:
                boxes = results[0].boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        conf = float(box.conf[0].item())
                        xyxy = box.xyxy[0].tolist()
                        x1, y1, x2, y2 = xyxy

                        cx = (x1 + x2) / 2.0
                        cy = (y1 + y2) / 2.0

                        if conf > best_conf:
                            best_conf = conf
                            best_center = (cx, cy)

                    if best_center is not None:
                        detected = True

            self.detected_pub.publish(Bool(data=detected))

            if detected:
                p = Point()
                p.x = best_center[0]
                p.y = best_center[1]
                p.z = 0.0
                self.center_pub.publish(p)
                self.conf_pub.publish(Float32(data=best_conf))
            else:
                self.conf_pub.publish(Float32(data=0.0))

        except Exception as e:
            rospy.logerr(f"Fehler in image_callback: {e}")

if __name__ == "__main__":
    BausteinDetector()
    rospy.spin()