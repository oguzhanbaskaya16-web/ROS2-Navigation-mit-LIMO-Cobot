#!/usr/bin/env python3
"""
auto_pick_orchestrator.py

Automatisierter Pick-and-Place-Ablauf für LIMO + MyCobot:

1. Empfängt Startposition (AMCL) und Zielposition (/pick_goal Topic)
2. Fährt mit Nav2 zur Zielposition
3. Dreht sich und sucht den Baustein (YOLO-Erkennung via /baustein_detected)
4. Richtet den Baustein in der Bildmitte aus (Visual Servoing via /cmd_vel)
5. Fährt auf Greifabstand heran (Tiefe via /camera/depth/image_raw)
6. Löst den Greifvorgang aus (/greif_start → baustein_auto_grabber in ROS1)
7. Fährt zur Startposition zurück

Eingang:
  /pick_goal  (geometry_msgs/PoseStamped) – Zielposition in der Map
  ROS-Parameter:
    grasp_wait_s        (float, default 8.0)  – Wartezeit für Armvorgang
    search_timeout_s    (float, default 20.0) – Max. Suchdauer
    target_distance_m   (float, default 0.55) – Greifabstand
    center_tolerance_px (int,   default 40)   – Pixel-Toleranz für Ausrichtung

Ausgang:
  /cmd_vel      (geometry_msgs/Twist)  – Fahrbefehl
  /greif_start  (std_msgs/Bool)        – Greif-Trigger für ROS1-Armknoten
"""

import math

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from action_msgs.msg import GoalStatus
from cv_bridge import CvBridge
from enum import Enum, auto
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped, Twist, Point
from nav2_msgs.action import NavigateToPose
from sensor_msgs.msg import Image
from std_msgs.msg import Bool


class State(Enum):
    IDLE = auto()
    WAIT_FOR_START_POSE = auto()
    NAVIGATE_TO_PICK = auto()
    SEARCH = auto()
    ALIGN = auto()
    APPROACH = auto()
    WAIT_FOR_GRASP = auto()
    NAVIGATE_HOME = auto()


class AutoPickOrchestrator(Node):

    IMAGE_WIDTH = 640

    def __init__(self):
        super().__init__('auto_pick_orchestrator')

        # Parameter
        self.declare_parameter('grasp_wait_s', 8.0)
        self.declare_parameter('search_timeout_s', 20.0)
        self.declare_parameter('target_distance_m', 0.55)
        self.declare_parameter('stop_distance_min_m', 0.50)
        self.declare_parameter('stop_distance_max_m', 0.62)
        self.declare_parameter('center_tolerance_px', 40)
        self.declare_parameter('angular_speed', 0.20)
        self.declare_parameter('linear_speed', 0.05)
        self.declare_parameter('search_angular_speed', 0.25)

        self.grasp_wait_s = self.get_parameter('grasp_wait_s').value
        self.search_timeout_s = self.get_parameter('search_timeout_s').value
        self.target_distance_m = self.get_parameter('target_distance_m').value
        self.stop_min_m = self.get_parameter('stop_distance_min_m').value
        self.stop_max_m = self.get_parameter('stop_distance_max_m').value
        self.center_tol_px = self.get_parameter('center_tolerance_px').value
        self.angular_speed = self.get_parameter('angular_speed').value
        self.linear_speed = self.get_parameter('linear_speed').value
        self.search_ang_speed = self.get_parameter('search_angular_speed').value

        # Interner Zustand
        self.state = State.IDLE
        self.start_pose: PoseStamped | None = None
        self.goal_pose: PoseStamped | None = None
        self.search_started_at = None
        self.grasp_triggered_at = None
        self.bridge = CvBridge()

        # Erkennungsdaten
        self.baustein_detected = False
        self.baustein_center: Point | None = None
        self.depth_image = None
        self.depth_stamp = None

        # --- Publishers ---
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.greif_pub = self.create_publisher(Bool, '/greif_start', 10)

        # --- Subscribers ---
        amcl_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            depth=5,
        )
        self.create_subscription(
            PoseWithCovarianceStamped, '/amcl_pose', self._amcl_cb, amcl_qos
        )
        self.create_subscription(PoseStamped, '/pick_goal', self._goal_cb, 10)
        self.create_subscription(Bool, '/baustein_detected', self._detected_cb, 10)
        self.create_subscription(Point, '/baustein_center', self._center_cb, 10)
        self.create_subscription(Image, '/camera/depth/image_raw', self._depth_cb, 10)

        # Nav2 Action-Client
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Hauptschleife 10 Hz
        self.create_timer(0.1, self._loop)

        self.get_logger().info(
            'AutoPickOrchestrator bereit. Warte auf /pick_goal (geometry_msgs/PoseStamped) ...'
        )

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _amcl_cb(self, msg: PoseWithCovarianceStamped):
        ps = PoseStamped()
        ps.header = msg.header
        ps.pose = msg.pose.pose
        # Startpose nur einmalig speichern wenn Ziel gerade eingegangen
        if self.state == State.WAIT_FOR_START_POSE and self.start_pose is None:
            self.start_pose = ps
            self.get_logger().info(
                f'Startposition gespeichert: '
                f'x={ps.pose.position.x:.2f}  y={ps.pose.position.y:.2f}'
            )
            self.state = State.NAVIGATE_TO_PICK
            self._navigate_to(self.goal_pose)

    def _goal_cb(self, msg: PoseStamped):
        if self.state != State.IDLE:
            self.get_logger().warn('Neues Ziel empfangen, aber Orchestrator ist beschäftigt – ignoriert.')
            return
        self.goal_pose = msg
        self.start_pose = None
        self.state = State.WAIT_FOR_START_POSE
        self.get_logger().info(
            f'Ziel empfangen: x={msg.pose.position.x:.2f}  y={msg.pose.position.y:.2f}'
        )

    def _detected_cb(self, msg: Bool):
        self.baustein_detected = msg.data

    def _center_cb(self, msg: Point):
        self.baustein_center = msg

    def _depth_cb(self, msg: Image):
        self.depth_image = msg
        self.depth_stamp = self.get_clock().now()

    # ------------------------------------------------------------------
    # Hauptschleife (Zustandsmaschine)
    # ------------------------------------------------------------------

    def _loop(self):
        if self.state == State.SEARCH:
            self._do_search()
        elif self.state == State.ALIGN:
            self._do_align()
        elif self.state == State.APPROACH:
            self._do_approach()
        elif self.state == State.WAIT_FOR_GRASP:
            self._do_wait_grasp()

    # ------------------------------------------------------------------
    # Phase 2: Suche
    # ------------------------------------------------------------------

    def _do_search(self):
        elapsed = (self.get_clock().now() - self.search_started_at).nanoseconds / 1e9

        if elapsed > self.search_timeout_s:
            self.get_logger().error(
                f'Suche nach {self.search_timeout_s:.0f}s ohne Ergebnis abgebrochen. Fahre heim.'
            )
            self._stop()
            self.state = State.NAVIGATE_HOME
            self._navigate_to(self.start_pose)
            return

        if self.baustein_detected and self.baustein_center is not None:
            self.get_logger().info('Baustein gefunden! Starte Ausrichtung.')
            self._stop()
            self.state = State.ALIGN
            return

        # Langsam drehen zum Scannen
        cmd = Twist()
        cmd.angular.z = self.search_ang_speed
        self.cmd_vel_pub.publish(cmd)

    # ------------------------------------------------------------------
    # Phase 3: Ausrichten (Baustein in Bildmitte bringen)
    # ------------------------------------------------------------------

    def _do_align(self):
        if not self.baustein_detected or self.baustein_center is None:
            self.get_logger().warn('Baustein verloren – zurück zur Suche.')
            self.state = State.SEARCH
            return

        error_px = self.baustein_center.x - (self.IMAGE_WIDTH / 2.0)

        if abs(error_px) <= self.center_tol_px:
            self.get_logger().info('Ausgerichtet! Starte Annäherung.')
            self._stop()
            self.state = State.APPROACH
            return

        # Proportionale Winkelkorrektur (negativ weil Kamerabild gespiegelt)
        cmd = Twist()
        cmd.angular.z = -float(error_px) / (self.IMAGE_WIDTH / 2.0) * self.angular_speed
        self.cmd_vel_pub.publish(cmd)

    # ------------------------------------------------------------------
    # Phase 4: Annäherung auf Greifabstand
    # ------------------------------------------------------------------

    def _do_approach(self):
        if not self.baustein_detected or self.baustein_center is None:
            self.get_logger().warn('Baustein verloren – zurück zur Suche.')
            self._stop()
            self.state = State.SEARCH
            return

        error_px = self.baustein_center.x - (self.IMAGE_WIDTH / 2.0)

        # Bei starker Abweichung zuerst neu ausrichten
        if abs(error_px) > self.center_tol_px * 2.5:
            self.get_logger().info('Ausrichtung verloren – neu ausrichten.')
            self._stop()
            self.state = State.ALIGN
            return

        depth_m = self._depth_at_center()
        if depth_m is None:
            # Kein valider Tiefenwert → langsam vorwärts schleichen
            cmd = Twist()
            cmd.linear.x = self.linear_speed * 0.4
            self.cmd_vel_pub.publish(cmd)
            return

        self.get_logger().info(
            f'Tiefe zum Baustein: {depth_m:.3f} m', throttle_duration_sec=0.5
        )

        if self.stop_min_m <= depth_m <= self.stop_max_m:
            self.get_logger().info(
                f'Greifabstand erreicht ({depth_m:.3f} m). Löse Greifvorgang aus.'
            )
            self._stop()
            self._trigger_grasp()
            self.state = State.WAIT_FOR_GRASP

        elif depth_m > self.stop_max_m:
            # Vorwärtsfahrt, proportional zur Restdistanz
            speed = max(0.02, min(self.linear_speed, (depth_m - self.target_distance_m) * 0.15))
            cmd = Twist()
            cmd.linear.x = speed
            # Kleine Korrektur während der Annäherung
            cmd.angular.z = -float(error_px) / (self.IMAGE_WIDTH / 2.0) * self.angular_speed * 0.4
            self.cmd_vel_pub.publish(cmd)

        else:
            # Zu nah – kurz zurücksetzen
            self.get_logger().warn(f'Zu nah ({depth_m:.3f} m) – setze zurück.')
            cmd = Twist()
            cmd.linear.x = -0.03
            self.cmd_vel_pub.publish(cmd)

    # ------------------------------------------------------------------
    # Phase 5: Warten bis Greifarm fertig ist
    # ------------------------------------------------------------------

    def _do_wait_grasp(self):
        elapsed = (self.get_clock().now() - self.grasp_triggered_at).nanoseconds / 1e9
        self.get_logger().info(
            f'Warte auf Greifabschluss … {elapsed:.1f} / {self.grasp_wait_s:.0f} s',
            throttle_duration_sec=2.0,
        )
        if elapsed >= self.grasp_wait_s:
            self.get_logger().info('Greifvorgang abgeschlossen. Fahre zur Startposition zurück.')
            self.state = State.NAVIGATE_HOME
            self._navigate_to(self.start_pose)

    # ------------------------------------------------------------------
    # Navigation (Nav2)
    # ------------------------------------------------------------------

    def _navigate_to(self, pose: PoseStamped):
        if not self.nav_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Nav2-Aktionsserver nicht erreichbar!')
            self.state = State.IDLE
            return

        goal = NavigateToPose.Goal()
        goal.pose = pose

        phase = 'Ziel' if self.state == State.NAVIGATE_TO_PICK else 'Start'
        self.get_logger().info(
            f'Navigation zu {phase}position: '
            f'x={pose.pose.position.x:.2f}  y={pose.pose.position.y:.2f}'
        )

        future = self.nav_client.send_goal_async(goal)
        future.add_done_callback(self._nav_goal_response_cb)

    def _nav_goal_response_cb(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().error('Navigationsziel wurde abgelehnt!')
            self.state = State.IDLE
            return
        handle.get_result_async().add_done_callback(self._nav_result_cb)

    def _nav_result_cb(self, future):
        status = future.result().status

        if self.state == State.NAVIGATE_TO_PICK:
            if status == GoalStatus.STATUS_SUCCEEDED:
                self.get_logger().info('Zielposition erreicht. Starte Suche nach Baustein.')
                self.search_started_at = self.get_clock().now()
                self.state = State.SEARCH
            else:
                self.get_logger().error(f'Navigation zur Zielposition fehlgeschlagen (Status {status}).')
                self.state = State.IDLE

        elif self.state == State.NAVIGATE_HOME:
            if status == GoalStatus.STATUS_SUCCEEDED:
                self.get_logger().info('Startposition wieder erreicht. Aufgabe erledigt.')
            else:
                self.get_logger().warn('Rückfahrt fehlgeschlagen – Aufgabe dennoch beendet.')
            self.state = State.IDLE
            self.goal_pose = None
            self.start_pose = None
            self.get_logger().info('Orchestrator bereit. Warte auf nächstes /pick_goal ...')

    # ------------------------------------------------------------------
    # Hilfsmethoden
    # ------------------------------------------------------------------

    def _depth_at_center(self) -> float | None:
        """Median-Tiefe (in Meter) im Fenster um den erkannten Baustein."""
        if self.depth_image is None or self.baustein_center is None:
            return None
        if self.depth_stamp is not None:
            age_s = (self.get_clock().now() - self.depth_stamp).nanoseconds / 1e9
            if age_s > 0.5:
                return None
        try:
            arr = self.bridge.imgmsg_to_cv2(self.depth_image, desired_encoding='passthrough').astype(float)
            cx = int(self.baustein_center.x)
            cy = int(self.baustein_center.y)
            h, w = arr.shape[:2]
            win = 15
            patch = arr[
                max(0, cy - win): min(h, cy + win),
                max(0, cx - win): min(w, cx + win),
            ]
            valid = patch[(patch > 80) & (patch < 2000)]
            if len(valid) == 0:
                return None
            return float(np.median(valid)) / 1000.0
        except Exception as exc:
            self.get_logger().warn(f'Tiefenauswertung fehlgeschlagen: {exc}')
            return None

    def _stop(self):
        self.cmd_vel_pub.publish(Twist())

    def _trigger_grasp(self):
        msg = Bool()
        msg.data = True
        for _ in range(5):
            self.greif_pub.publish(msg)
        self.grasp_triggered_at = self.get_clock().now()
        self.get_logger().info('/greif_start = True gesendet → Armsteuerung übernimmt.')


def main(args=None):
    rclpy.init(args=args)
    node = AutoPickOrchestrator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
