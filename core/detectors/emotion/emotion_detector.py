"""
面部表情检测器
基于MediaPipe的FaceMesh进行表情识别
"""
import cv2
import mediapipe as mp
from ..base import BaseDetector


class EmotionDetector(BaseDetector):
    """面部表情检测器"""

    def __init__(self, model_path=None):
        """
        初始化检测器

        Args:
            model_path: 不需要模型路径（使用MediaPipe内置模型）
        """
        self.model_path = model_path
        self.face_mesh = None
        self._init_mediapipe()
    
    def _init_mediapipe(self):
        """初始化MediaPipe"""
        try:
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=5,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            print("✓ 初始化MediaPipe FaceMesh")
        except Exception as e:
            raise RuntimeError(f"MediaPipe初始化失败: {e}\n\n请安装正确的版本: pip install mediapipe==0.10.9")
    
    def load_model(self):
        """加载模型（MediaPipe不需要）"""
        # MediaPipe模型在初始化时加载
        pass

    def detect(self, frame, face_rect=None):
        """
        检测表情

        Args:
            frame: 输入图像
            face_rect: 面部区域 (x1, y1, x2, y2)，如果为None则全图检测

        Returns:
            emotion: 表情标签
        """
        if face_rect:
            x1, y1, x2, y2 = face_rect
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            face_img = frame[y1:y2, x1:x2]
        else:
            face_img = frame

        if face_img.size == 0:
            return "未知"

        rgb_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_face)

        if not results.multi_face_landmarks:
            return "未知"

        landmarks = results.multi_face_landmarks[0]

        # 计算嘴部开合度
        upper_lip = landmarks.landmark[13]
        lower_lip = landmarks.landmark[14]
        mouth_distance = ((upper_lip.x - lower_lip.x)**2 +
                         (upper_lip.y - lower_lip.y)**2)**0.5

        # 计算眼睛开合度
        left_eye_top = landmarks.landmark[159]
        left_eye_bottom = landmarks.landmark[145]
        right_eye_top = landmarks.landmark[386]
        right_eye_bottom = landmarks.landmark[374]

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

    def detect_emotion(self, frame, face_rect):
        """
        检测表情（兼容旧接口）

        Args:
            frame: 输入图像
            face_rect: 面部区域 (x1, y1, x2, y2)

        Returns:
            emotion: 表情标签
        """
        return self.detect(frame, face_rect)

    def get_classes(self):
        """获取支持的类别（表情检测无类别）"""
        return ['开心😊', '平静😐', '眨眼😉', '中性😌', '未知']

    def draw_face_landmarks(self, frame, face_rect):
        """
        绘制面部关键点

        Args:
            frame: 输入图像
            face_rect: 面部区域 (x1, y1, x2, y2)

        Returns:
            frame: 绘制后的图像
        """
        x1, y1, x2, y2 = face_rect
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        face_img = frame[y1:y2, x1:x2]

        if face_img.size == 0:
            return frame

        rgb_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_face)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * (x2 - x1)) + x1
                    y = int(landmark.y * (y2 - y1)) + y1
                    cv2.circle(frame, (x, y), 1, (0, 255, 255), -1)

        return frame

    def close(self):
        """释放资源"""
        if hasattr(self, 'face_mesh') and self.face_mesh:
            self.face_mesh.close()