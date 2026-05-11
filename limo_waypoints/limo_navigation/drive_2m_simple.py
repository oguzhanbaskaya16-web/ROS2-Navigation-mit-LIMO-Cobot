#!/usr/bin/env python3
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class DriveTwoMetersSimple(Node):
    def __init__(self):
        super().__init__("drive_2m_simple")

        self.declare_parameter("distance_m", 2.0)
        self.declare_parameter("speed_m_s", 0.2)
        self.declare_parameter("cmd_vel_topic", "/cmd_vel")

        cmd_vel_topic = self.get_parameter("cmd_vel_topic").value
        self.cmd_vel_pub = self.create_publisher(Twist, cmd_vel_topic, 10)

    def publish_velocity(self, linear_x, angular_z=0.0):
        msg = Twist()
        msg.linear.x = float(linear_x)
        msg.angular.z = float(angular_z)
        self.cmd_vel_pub.publish(msg)

    def stop_robot(self):
        for _ in range(10):
            self.publish_velocity(0.0, 0.0)
            rclpy.spin_once(self, timeout_sec=0.05)

    def run(self):
        distance = float(self.get_parameter("distance_m").value)
        speed = float(self.get_parameter("speed_m_s").value)

        if speed <= 0.0:
            self.get_logger().error("speed_m_s muss groesser als 0 sein.")
            return

        drive_time_s = distance / speed
        self.get_logger().info(
            f"Fahre geradeaus: {distance:.2f} m mit {speed:.2f} m/s "
            f"fuer ca. {drive_time_s:.1f} s."
        )

        start_time = time.monotonic()
        try:
            while rclpy.ok() and time.monotonic() - start_time < drive_time_s:
                self.publish_velocity(speed, 0.0)
                rclpy.spin_once(self, timeout_sec=0.1)
        finally:
            self.stop_robot()
            self.get_logger().info("Roboter gestoppt.")


def main(args=None):
    rclpy.init(args=args)
    node = DriveTwoMetersSimple()
    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
