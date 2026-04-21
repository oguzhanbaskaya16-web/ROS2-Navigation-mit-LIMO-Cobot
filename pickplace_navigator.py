import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus


class PickPlaceNavigator(Node):
    def __init__(self):
        super().__init__('pick_place_navigator')

        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.start_pose = None

        self.pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.amcl_callback,
            10
        )

        # Zielpunkt für "Pick" oder "Place"
        self.target_x = -0.49
        self.target_y = 0.00
        self.target_yaw = 0.0

    def amcl_callback(self, msg):
        if self.start_pose is None:
            self.start_pose = (
                msg.pose.pose.position.x,
                msg.pose.pose.position.y,
                self.get_yaw_from_quaternion(msg.pose.pose.orientation)
            )
            self.get_logger().info(
                f'Startposition gespeichert: '
                f'x={self.start_pose[0]:.2f}, '
                f'y={self.start_pose[1]:.2f}, '
                f'yaw={self.start_pose[2]:.2f}'
            )

    def get_yaw_from_quaternion(self, q):
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny_cosp, cosy_cosp)

    def create_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0

        pose.pose.orientation.x = 0.0
        pose.pose.orientation.y = 0.0
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)

        return pose

    def send_goal(self, x, y, yaw):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = self.create_pose(x, y, yaw)

        self.get_logger().info(f'Fahre zu: x={x:.2f}, y={y:.2f}, yaw={yaw:.2f}')

        self.client.wait_for_server()

        future = self.client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Ziel wurde abgelehnt!')
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result()

        if result is None:
            self.get_logger().error('Kein Ergebnis erhalten.')
            return False

        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Ziel erreicht!')
            return True
        else:
            self.get_logger().error(f'Navigation fehlgeschlagen, Status: {result.status}')
            return False

    def run(self):
        self.get_logger().info('Warte auf Startposition aus /amcl_pose ...')

        while rclpy.ok() and self.start_pose is None:
            rclpy.spin_once(self, timeout_sec=0.5)

        if self.start_pose is None:
            self.get_logger().error('Startposition konnte nicht gelesen werden.')
            return

        # 1. Zum Ziel fahren
        success = self.send_goal(self.target_x, self.target_y, self.target_yaw)
        if not success:
            return

        # Hier könnte später Pick/Place-Aktion kommen
        self.get_logger().info('Am Ziel angekommen. Simuliere Pick/Place ...')

        # 2. Zurück zur Startposition
        sx, sy, syaw = self.start_pose
        self.get_logger().info('Fahre zurück zur Startposition ...')
        self.send_goal(sx, sy, syaw)


def main(args=None):
    rclpy.init(args=args)
    node = PickPlaceNavigator()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()