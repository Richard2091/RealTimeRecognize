"""
MediaPipe渲染器模块
负责MediaPipe检测结果的渲染（姿态、表情、手势）
"""
import cv2
import mediapipe as mp

# 导入MediaPipe官方绘图工具
try:
    from mediapipe.tasks.python.vision import drawing_utils
    from mediapipe.tasks.python.vision import drawing_styles
    HAS_DRAWING_UTILS = True
except ImportError:
    drawing_utils = None
    drawing_styles = None
    HAS_DRAWING_UTILS = False
    print("Warning: MediaPipe drawing_utils not available, using custom rendering")


class MediaPipeRenderer:
    """MediaPipe统一渲染器"""

    def __init__(self, show_skeleton=True):
        """
        初始化渲染器

        Args:
            show_skeleton: 是否显示骨骼连接
        """
        self.show_skeleton = show_skeleton

        # 颜色配置
        self.pose_landmark_color = (0, 255, 255)  # 黄色关键点
        self.pose_connection_color = (0, 255, 0)  # 绿色连接线
        self.face_box_color = (255, 0, 0)  # 蓝色框
        self.face_text_color = (0, 0, 255)  # 红色文本
        self.hand_landmark_color = (0, 255, 0)  # 绿色关键点
        self.hand_connection_color = (255, 255, 0)  # 黄色连接线
        self.gesture_text_color = (0, 165, 255)  # 橙色文本

        # 字体配置
        self.text_font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.7
        self.font_thickness = 2

        # 姿态连接定义（MediaPipe Pose 33个关键点）
        self.pose_connections = [
            (11, 13), (13, 15),  # 左臂
            (12, 14), (14, 16),  # 右臂
            (11, 12),  # 肩膀
            (5, 7), (7, 9),  # 左眼-左耳-左肩
            (6, 8), (8, 10),  # 右眼-右耳-右肩
            (5, 6),  # 鼻子
            (5, 11), (6, 12),  # 肩膀到眼睛
            (11, 23), (12, 24),  # 肩膀到臀部
            (23, 24),  # 臀部
            (23, 25), (25, 27),  # 左腿
            (24, 26), (26, 28)  # 右腿
        ]

    def render_pose(self, frame, pose_results, bbox=None):
        """
        渲染姿态检测结果

        Args:
            frame: 输入帧
            pose_results: MediaPipe姿态检测结果
            bbox: 可选，边界框信息 (x1, y1, x2, y2)
        """
        if not pose_results.pose_landmarks or len(pose_results.pose_landmarks) == 0:
            return

        # 使用MediaPipe官方绘图工具（如果可用）
        if HAS_DRAWING_UTILS and not bbox:
            mp_pose_connections = mp.tasks.vision.PoseLandmarksConnections
            for pose_landmarks in pose_results.pose_landmarks:
                # 姿态检测始终显示连接线
                drawing_utils.draw_landmarks(
                    frame,
                    pose_landmarks,
                    mp_pose_connections.POSE_CONNECTIONS,
                    drawing_styles.get_default_pose_landmarks_style(),
                    None
                )
        else:
            # 回退到自定义绘制（特别是当有bbox时）
            for pose_landmarks in pose_results.pose_landmarks:
                landmarks = self._normalize_landmarks(
                    pose_landmarks,
                    frame.shape,
                    bbox
                )

                # 绘制关键点
                self._draw_pose_landmarks(frame, landmarks)

                # 姿态检测始终显示连接线
                self._draw_pose_connections(frame, landmarks)

    def render_emotion(self, frame, emotion, face_rect):
        """
        渲染表情检测结果

        Args:
            frame: 输入帧
            emotion: 表情标签
            face_rect: 面部区域 (x1, y1, x2, y2)
        """
        x1, y1, x2, y2 = face_rect
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        # 绘制面部框
        cv2.rectangle(frame, (x1, y1), (x2, y2), self.face_box_color, 2)

        # 绘制表情标签
        label = f"Emotion: {emotion}"
        cv2.putText(frame, label, (x1, y1 - 10),
                   self.text_font, self.font_scale, self.face_text_color, self.font_thickness)

    def render_gesture(self, frame, gesture_results):
        """
        渲染手势识别结果
        根据官方文档，GestureRecognizer 返回 hand_landmarks 和 gestures
        参考: https://github.com/google-ai-edge/mediapipe-samples/blob/main/examples/gesture_recognizer/python/gesture_recognizer.ipynb

        Args:
            frame: 输入帧
            gesture_results: MediaPipe手势识别结果 (包含 hand_landmarks 和 gestures)
        """
        if not gesture_results.hand_landmarks or len(gesture_results.hand_landmarks) == 0:
            return

        # 使用MediaPipe官方绘图工具绘制手部关键点和连接线
        if HAS_DRAWING_UTILS:
            mp_hands_connections = mp.tasks.vision.HandLandmarksConnections
            for idx, hand_landmarks in enumerate(gesture_results.hand_landmarks):
                # 绘制手部关键点和连接线
                drawing_utils.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands_connections.HAND_CONNECTIONS,
                    drawing_styles.get_default_hand_landmarks_style(),
                    drawing_styles.get_default_hand_connections_style()
                )

                # 绘制手势标签和得分
                if gesture_results.gestures and idx < len(gesture_results.gestures):
                    top_gesture = gesture_results.gestures[idx][0]
                    gesture_name = top_gesture.category_name
                    gesture_score = top_gesture.score

                    # 获取手腕位置用于显示标签
                    wrist = hand_landmarks[0]
                    h, w = frame.shape[:2]
                    text_x = int(wrist.x * w) - 20
                    text_y = int(wrist.y * h) - 20

                    # 显示手势名称和置信度
                    label = f"{gesture_name} ({gesture_score:.2f})"
                    cv2.putText(frame, label, (text_x, text_y),
                               self.text_font, self.font_scale * 0.6, self.gesture_text_color, 2)

                    # 绘制手部类型标签（如果有）
                    if gesture_results.handedness and idx < len(gesture_results.handedness):
                        handedness = gesture_results.handedness[idx][0].category_name
                        label = f"{handedness}"
                        cv2.putText(frame, label, (text_x, text_y - 25),
                                   self.text_font, self.font_scale * 0.5, (255, 255, 0), 2)
        else:
            # 回退到自定义绘制
            for idx, hand_landmarks in enumerate(gesture_results.hand_landmarks):
                landmarks = self._normalize_landmarks(hand_landmarks, frame.shape)

                # 绘制关键点
                self._draw_hand_landmarks(frame, landmarks)

                # 绘制连接线
                self._draw_hand_connections(frame, landmarks)

                # 绘制手势标签
                if gesture_results.gestures and idx < len(gesture_results.gestures):
                    top_gesture = gesture_results.gestures[idx][0]
                    gesture_name = top_gesture.category_name
                    gesture_score = top_gesture.score

                    wrist = landmarks[0]
                    label = f"{gesture_name} ({gesture_score:.2f})"
                    cv2.putText(frame, label, (wrist['x'] - 20, wrist['y'] - 20),
                               self.text_font, self.font_scale * 0.6, self.gesture_text_color, 2)

    @staticmethod
    def _normalize_landmarks(landmarks, frame_shape, bbox=None):
        """
        将归一化坐标转换为图像坐标

        Args:
            landmarks: MediaPipe关键点
            frame_shape: 帧形状
            bbox: 边界框 (x1, y1, x2, y2)

        Returns:
            normalized_landmarks: 标准化的关键点列表
        """
        height, width = frame_shape[:2]
        normalized_landmarks = []

        for landmark in landmarks:
            if bbox:
                x1, y1, x2, y2 = bbox
                abs_x = int((landmark.x * (x2 - x1)) + x1)
                abs_y = int((landmark.y * (y2 - y1)) + y1)
            else:
                abs_x = int(landmark.x * width)
                abs_y = int(landmark.y * height)

            # 检查是否有 visibility 属性（姿态检测有，手部检测没有）
            visibility = 1.0
            if hasattr(landmark, 'visibility'):
                visibility = float(landmark.visibility) if landmark.visibility is not None else 1.0

            normalized_landmarks.append({
                'x': abs_x,
                'y': abs_y,
                'visibility': visibility
            })

        return normalized_landmarks

    def _draw_pose_landmarks(self, frame, landmarks):
        """绘制姿态关键点"""
        for lm in landmarks:
            if lm['visibility'] > 0.5:
                cv2.circle(frame, (lm['x'], lm['y']), 4,
                         self.pose_landmark_color, -1)

    def _draw_pose_connections(self, frame, landmarks):
        """绘制姿态骨骼连接"""
        for start_idx, end_idx in self.pose_connections:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                pt1 = landmarks[start_idx]
                pt2 = landmarks[end_idx]
                if pt1['visibility'] > 0.5 and pt2['visibility'] > 0.5:
                    cv2.line(frame, (pt1['x'], pt1['y']), (pt2['x'], pt2['y']),
                            self.pose_connection_color, 2)

    def _draw_hand_landmarks(self, frame, landmarks):
        """绘制手部关键点"""
        for lm in landmarks:
            cv2.circle(frame, (lm['x'], lm['y']), 3, (0, 255, 0), -1)

    def _draw_hand_connections(self, frame, landmarks):
        """绘制手部连接线"""
        # 手部连接定义（MediaPipe Hands 21个关键点）
        hand_connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # 拇指
            (0, 5), (5, 6), (6, 7), (7, 8),  # 食指
            (0, 9), (9, 10), (10, 11), (11, 12),  # 中指
            (0, 13), (13, 14), (14, 15), (15, 16),  # 无名指
            (0, 17), (17, 18), (18, 19), (19, 20),  # 小指
            (5, 9), (9, 13), (13, 17)  # 手掌
        ]
        for start_idx, end_idx in hand_connections:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                pt1 = landmarks[start_idx]
                pt2 = landmarks[end_idx]
                cv2.line(frame, (pt1['x'], pt1['y']), (pt2['x'], pt2['y']),
                        (255, 255, 0), 2)
