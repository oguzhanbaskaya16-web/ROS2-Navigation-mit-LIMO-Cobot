import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose


class SimpleNavigator(Node):
    def __init__(self):
        super().__init__('simple_navigator')

        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # 👉 HIER DEINE PUNKTE (erst hin, dann zurück)
        self.goals = [
            (-0.49, 0.00, 0.0),   # Zielpunkt B
            (-0.78, -0.23, 0.0)   # zurück zu A
        ]

    def create_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y

        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)

        return pose

    def send_goal(self, x, y, yaw):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = self.create_pose(x, y, yaw)

        self.get_logger().info(f'Fahre zu: {x}, {y}')

        self.client.wait_for_server()

        future = self.client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Ziel abgelehnt!')
            return

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        self.get_logger().info('Ziel erreicht!')

    def run(self):
        for x, y, yaw in self.goals:
            self.send_goal(x, y, yaw)


def main(args=None):
    rclpy.init(args=args)
    node = SimpleNavigator()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()