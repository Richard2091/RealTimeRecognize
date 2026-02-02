"""
姿态检测器
基于MediaPipe的Pose进行人体姿态检测
"""
import cv2
import mediapipe as mp
from ..base import BaseDetector


class PoseDetector(BaseDetector):
    """MediaPipe姿态检测器"""

    def __init__(self, model_complexity=1, min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):
        """
        初始化姿态检测器

        Args:
            model_complexity: 模型复杂度 (0=快速, 1=标准, 2=高精度)
            min_detection_confidence: 最小检测置信度
            min_tracking_confidence: 最小跟踪置信度
        """
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.pose = None
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        
        # 不需要加载模型路径，使用MediaPipe内置模型
        self._init_mediapipe()
    
    def _init_mediapipe(self):
        """初始化MediaPipe"""
        try:
            self.pose = mp.solutions.pose.Pose(
                model_complexity=self.model_complexity,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            )
            print("✓ 初始化MediaPipe姿态检测器")
        except Exception as e:
            raise RuntimeError(f"MediaPipe初始化失败: {e}\n\n请安装正确的版本: pip install mediapipe==0.10.9")
    
    def load_model(self):
        """加载模型（MediaPipe不需要）"""
        # MediaPipe模型在初始化时加载
        pass

    def detect(self, frame, verbose=True):
        """
        检测姿态

        Args:
            frame: 输入图像 (BGR格式)
            verbose: 是否显示详细信息（不使用）

        Returns:
            results: MediaPipe检测结果
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.pose.process(rgb_frame)

    def get_classes(self):
        """获取支持的类别（姿态检测无类别）"""
        return {}

    def get_keypoints(self, results, person_id=0):
        """
        获取关键点（统一格式：[[x, y, conf], ...]）

        Args:
            results: MediaPipe检测结果
            person_id: 人员ID（目前MediaPipe只支持单人）

        Returns:
            keypoints: 关键点列表 [[x, y, conf], ...]
        """
        if results.pose_landmarks is None:
            return []

        keypoints = []
        for landmark in results.pose_landmarks.landmark:
            x = float(landmark.x)
            y = float(landmark.y)
            conf = float(landmark.visibility)
            keypoints.append([x, y, conf])

        return keypoints

    def draw_landmarks(self, frame, results, draw_connections=True):
        """
        绘制关键点和连接线

        Args:
            frame: 输入图像
            results: MediaPipe检测结果
            draw_connections: 是否绘制连接线

        Returns:
            frame: 绘制后的图像
        """
        if results.pose_landmarks:
            if draw_connections:
                self.mp_draw.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                )
            else:
                self.mp_draw.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    None,
                    self.mp_draw.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2)
                )
        return frame

    def get_specific_keypoints(self, results, keypoint_indices):
        """
        获取特定关键点

        Args:
            results: MediaPipe检测结果
            keypoint_indices: 关键点索引列表

        Returns:
            keypoints: 指定关键点的列表
        """
        if results.pose_landmarks is None:
            return []

        landmarks = results.pose_landmarks.landmark
        keypoints = []
        for idx in keypoint_indices:
            if idx < len(landmarks):
                lm = landmarks[idx]
                keypoints.append([float(lm.x), float(lm.y), float(lm.visibility)])
        return keypoints

    def get_nose_position(self, results):
        """获取鼻子位置（索引0）"""
        return self.get_specific_keypoints(results, [0])

    def get_eye_positions(self, results):
        """获取眼睛位置（左眼:2, 右眼:5）"""
        return self.get_specific_keypoints(results, [2, 5])

    def get_hand_positions(self, results):
        """获取手腕位置（左手:15, 右手:16）"""
        return self.get_specific_keypoints(results, [15, 16])

    def close(self):
        """释放资源"""
        if hasattr(self, 'pose') and self.pose:
            self.pose.close()