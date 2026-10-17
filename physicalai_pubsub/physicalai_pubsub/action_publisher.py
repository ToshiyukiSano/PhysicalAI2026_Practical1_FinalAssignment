#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class MultiAIActionPublisher(Node):
    def __init__(self):
        super().__init__('multi_ai_action_publisher')
        self.bridge = CvBridge()
        self.is_executing = False  # 実行中フラグのみ管理

        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/crane_plus_arm_controller/follow_joint_trajectory'
        )

        self.get_logger().info('Multi-AI Trigger Node ready. Waiting for Red/Blue signals...')

    def image_callback(self, msg):
        # アーム動作中は新しい信号を受け付けない（衝突防止）
        if self.is_executing:
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Image conversion failed: {e}')
            return

        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # 赤色領域の抽出
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
        red_pixels = cv2.countNonZero(mask_red)

        # 青色領域の抽出
        lower_blue = np.array([100, 100, 100])
        upper_blue = np.array([140, 255, 255])
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        blue_pixels = cv2.countNonZero(mask_blue)

        self.get_logger().info(f'[AI Inference] Red score: {red_pixels}, Blue score: {blue_pixels}')

        # 条件分岐（赤 vs 青 の判定）
        if red_pixels > blue_pixels and red_pixels > 0:
            self.get_logger().info('AI Condition Met: RED detected! Executing Horizontal Wave Motion (20s)...')
            self.is_executing = True
            self.send_goal_motion_red()
        elif blue_pixels > red_pixels and blue_pixels > 0:
            self.get_logger().info('AI Condition Met: BLUE detected! Executing Vertical Bow Motion (20s)...')
            self.is_executing = True
            self.send_goal_motion_blue()

    def send_goal_motion_red(self):
        """【パターンA】赤色：左右横振りウェーブ（20秒）"""
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = ['crane_plus_joint1', 'crane_plus_joint2', 'crane_plus_joint3', 'crane_plus_joint4']

        p1 = JointTrajectoryPoint(positions=[0.5, 0.3, -0.2, 0.2], time_from_start=Duration(sec=4, nanosec=0))
        p2 = JointTrajectoryPoint(positions=[-0.5, 0.3, -0.2, -0.2], time_from_start=Duration(sec=8, nanosec=0))
        p3 = JointTrajectoryPoint(positions=[0.6, 0.1, -0.1, 0.3], time_from_start=Duration(sec=12, nanosec=0))
        p4 = JointTrajectoryPoint(positions=[0.0, 0.4, -0.3, 0.0], time_from_start=Duration(sec=16, nanosec=0))
        p5 = JointTrajectoryPoint(positions=[0.0, 0.0, 0.0, 0.0], time_from_start=Duration(sec=20, nanosec=0))

        goal_msg.trajectory.points = [p1, p2, p3, p4, p5]
        self.execute_trajectory(goal_msg)

    def send_goal_motion_blue(self):
        """【パターンB】青色：上下お辞儀・うなずき（20秒）"""
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = ['crane_plus_joint1', 'crane_plus_joint2', 'crane_plus_joint3', 'crane_plus_joint4']

        p1 = JointTrajectoryPoint(positions=[0.0, 0.4, -0.3, 0.2], time_from_start=Duration(sec=4, nanosec=0))
        p2 = JointTrajectoryPoint(positions=[0.0, -0.2, 0.3, -0.2], time_from_start=Duration(sec=8, nanosec=0))
        p3 = JointTrajectoryPoint(positions=[0.0, 0.4, -0.3, 0.2], time_from_start=Duration(sec=12, nanosec=0))
        p4 = JointTrajectoryPoint(positions=[0.0, -0.2, 0.3, -0.2], time_from_start=Duration(sec=16, nanosec=0))
        p5 = JointTrajectoryPoint(positions=[0.0, 0.0, 0.0, 0.0], time_from_start=Duration(sec=20, nanosec=0))

        goal_msg.trajectory.points = [p1, p2, p3, p4, p5]
        self.execute_trajectory(goal_msg)

    def execute_trajectory(self, goal_msg):
        self._action_client.wait_for_server()
        self._send_goal_future = self._action_client.send_goal_async(goal_msg)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            self.is_executing = False
            return

        self.get_logger().info('Goal accepted! Executing motion...')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        self.get_logger().info('Motion completed! Ready for next signal.')
        # 動作が終わったらフラグを解除し、次の信号を受け付け可能にする
        self.is_executing = False

def main(args=None):
    rclpy.init(args=args)
    node = MultiAIActionPublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
