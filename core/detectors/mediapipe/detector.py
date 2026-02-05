"""
MediaPipe统一检测器模块
整合姿态检测、表情检测和手势识别功能
"""
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import (
    PoseLandmarker,
    FaceLandmarker,
    GestureRecognizer
)


class MediaPipeDetector:
    """MediaPipe统一检测器"""

    def __init__(self, model_path=None, detection_type="pose"):
        """
        初始化MediaPipe检测器

        Args:
            model_path: 模型文件路径（如果为None，使用默认路径）
            detection_type: 检测类型
                - "pose": 姿态检测
                - "face": 表情检测
                - "gesture": 手势识别
        """
        self.detection_type = detection_type
        self.model_path = model_path or self._get_default_model_path(detection_type)
        self.detector = None
        self._init_mediapipe()

    @staticmethod
    def _get_default_model_path(detection_type):
        """获取默认模型路径"""
        model_paths = {
            "pose": "model/mediapipe/pose_landmarker_lite.task",
            "face": "model/mediapipe/face_landmarker.task",
            "gesture": "model/mediapipe/gesture_recognizer.task"
        }
        return model_paths.get(detection_type, "")

    def _init_mediapipe(self):
        """初始化MediaPipe检测器"""
        import os

        # 检查模型文件是否存在
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"模型文件不存在: {self.model_path}")

        try:
            base_options = python.BaseOptions(
                model_asset_path=self.model_path,
                delegate=python.BaseOptions.Delegate.CPU
            )

            if self.detection_type == "pose":
                options = vision.PoseLandmarkerOptions(
                    base_options=base_options,
                    output_segmentation_masks=False,
                    num_poses=5,
                    min_pose_detection_confidence=0.5,
                    min_pose_presence_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                self.detector = PoseLandmarker.create_from_options(options)
                print(f"✓ 初始化MediaPipe姿态检测器")

            elif self.detection_type == "face":
                options = vision.FaceLandmarkerOptions(
                    base_options=base_options,
                    output_face_blendshapes=True,
                    output_facial_transformation_matrixes=True,
                    num_faces=5
                )
                self.detector = FaceLandmarker.create_from_options(options)
                print(f"✓ 初始化MediaPipe表情检测器")

            elif self.detection_type == "gesture":
                options = vision.GestureRecognizerOptions(
                    base_options=base_options,
                    num_hands=2,
                    min_hand_detection_confidence=0.5,
                    min_hand_presence_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                self.detector = GestureRecognizer.create_from_options(options)
                print(f"✓ 初始化MediaPipe手势识别器")

            else:
                raise ValueError(f"不支持的检测类型: {self.detection_type}")

        except Exception as e:
            raise RuntimeError(f"MediaPipe初始化失败: {e}")

    def load_model(self):
        """加载模型（MediaPipe不需要）"""
        pass

    def detect(self, frame, verbose=True):
        """
        检测图像

        Args:
            frame: 输入图像 (BGR格式)
            verbose: 是否显示详细信息（未使用，保留用于接口兼容性）

        Returns:
            results: 检测结果
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        return self.detector.detect(mp_image)

    def get_classes(self):
        """获取支持的类别"""
        if self.detection_type == "pose":
            return []
        elif self.detection_type == "face":
            return ['开心😊', '平静😐', '眨眼😉', '中性😌', '未知']
        elif self.detection_type == "gesture":
            return ['Thumb_Up', 'Thumb_Down', 'Victory', 'Closed_Fist', 'Pointing_Up', 'Unknown']
        else:
            return []

    def detect_pose(self, frame):
        """姿态检测"""
        if self.detection_type != "pose":
            raise ValueError("检测器类型不是姿态检测")
        return self.detect(frame)

    def detect_emotion(self, frame, face_rect=None):
        """表情检测"""
        if self.detection_type != "face":
            raise ValueError("检测器类型不是表情检测")

        if face_rect:
            x1, y1, x2, y2 = face_rect
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            face_img = frame[y1:y2, x1:x2]
        else:
            face_img = frame

        if face_img.size == 0:
            return "未知"

        results = self.detect(face_img)

        if not results.face_landmarks:
            return "未知"

        # 表情识别逻辑
        landmarks = results.face_landmarks[0]
        emotion = self._analyze_emotion(landmarks)
        return emotion

    def recognize_gesture(self, frame):
        """
        手势识别
        根据官方文档，GestureRecognizer 返回 hand_landmarks 和 gestures
        参考: https://github.com/google-ai-edge/mediapipe-samples/blob/main/examples/gesture_recognizer/python/gesture_recognizer.ipynb
        """
        if self.detection_type != "gesture":
            raise ValueError("检测器类型不是手势识别")

        # Gesture Recognizer使用recognize方法而不是detect方法
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # 使用recognize方法
        results = self.detector.recognize(mp_image)

        return results

    @staticmethod
    def _analyze_emotion(landmarks):
        """分析表情"""
        # 嘴部开合度
        upper_lip = landmarks[13]
        lower_lip = landmarks[14]
        mouth_distance = ((upper_lip.x - lower_lip.x)**2 +
                         (upper_lip.y - lower_lip.y)**2)**0.5

        # 眼睛开合度
        left_eye_top = landmarks[159]
        left_eye_bottom = landmarks[145]
        right_eye_top = landmarks[386]
        right_eye_bottom = landmarks[374]

        left_eye_open = ((left_eye_top.x - left_eye_bottom.x)**2 +
                        (left_eye_top.y - left_eye_bottom.y)**2)**0.5
        right_eye_open = ((right_eye_top.x - right_eye_bottom.x)**2 +
                         (right_eye_top.y - right_eye_bottom.y)**2)**0.5
        avg_eye_open = (left_eye_open + right_eye_open) / 2

        # 表情判断
        if mouth_distance > 0.1:
            return "开心😊"
        elif mouth_distance < 0.02:
            return "平静😐"
        elif avg_eye_open < 0.015:
            return "眨眼😉"
        else:
            return "中性😌"

    def get_keypoints(self, results, person_id=0):
        """
        获取关键点（姿态检测专用）

        Args:
            results: MediaPipe检测结果
            person_id: 人体ID（默认0）

        Returns:
            keypoints: 关键点列表 [[x, y, conf], ...]
        """
        if self.detection_type != "pose":
            return []

        if not results.pose_landmarks or person_id >= len(results.pose_landmarks):
            return []

        keypoints = []
        for landmark in results.pose_landmarks[person_id]:
            x = float(landmark.x)
            y = float(landmark.y)
            conf = float(landmark.visibility) if hasattr(landmark, 'visibility') and landmark.visibility is not None else 1.0
            keypoints.append([x, y, conf])

        return keypoints

    def close(self):
        """释放资源"""
        if hasattr(self, 'detector') and self.detector:
            self.detector.close()
