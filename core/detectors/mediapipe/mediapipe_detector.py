"""
MediaPipe统一检测器模块
整合姿态检测和表情检测功能
"""
import cv2
import mediapipe as mp
mp_solutions = mp


class MediaPipeDetector:
    """MediaPipe统一检测器"""

    def __init__(self, model_path=None, detection_type="pose"):
        """
        初始化MediaPipe检测器

        Args:
            model_path: 不需要模型路径（使用MediaPipe内置模型）
            detection_type: 检测类型（"pose"姿态检测，"face"表情检测）
        """
        self.detection_type = detection_type
        self.model_path = model_path

        # MediaPipe组件
        self.mp_pose = mp_solutions.pose
        self.mp_face_mesh = mp_solutions.face_mesh
        self.mp_draw = mp_solutions.drawing_utils
        
        # 检测器实例
        self.detector = None
        self._init_mediapipe()
    
    def _init_mediapipe(self):
        """初始化MediaPipe检测器"""
        try:
            if self.detection_type == "pose":
                self.detector = self.mp_pose.Pose(
                    model_complexity=1,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                print("✓ 初始化MediaPipe姿态检测器")
            elif self.detection_type == "face":
                self.detector = self.mp_face_mesh.FaceMesh(
                    max_num_faces=5,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                print("✓ 初始化MediaPipe表情检测器")
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
            verbose: 是否显示详细信息
            
        Returns:
            results: 检测结果
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.detector.process(rgb_frame)
    
    def get_classes(self):
        """获取支持的类别"""
        if self.detection_type == "pose":
            return {}
        else:  # face
            return ['开心😊', '平静😐', '眨眼😉', '中性😌', '未知']
    
    def detect_pose(self, frame):
        """姿态检测（兼容旧接口）"""
        if self.detection_type != "pose":
            raise ValueError("检测器类型不是姿态检测")
        return self.detect(frame)
    
    def detect_emotion(self, frame, face_rect=None):
        """表情检测（兼容旧接口）"""
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
        
        if not results.multi_face_landmarks:
            return "未知"

        # 表情识别逻辑
        landmarks = results.multi_face_landmarks[0]
        emotion = self._analyze_emotion(landmarks)
        return emotion
    
    def _analyze_emotion(self, landmarks):
        """分析表情"""
        # 嘴部开合度
        upper_lip = landmarks.landmark[13]
        lower_lip = landmarks.landmark[14]
        mouth_distance = ((upper_lip.x - lower_lip.x)**2 +
                         (upper_lip.y - lower_lip.y)**2)**0.5

        # 眼睛开合度
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
    
    def get_keypoints(self, results, person_id=0):
        """获取关键点（姿态检测专用）"""
        if self.detection_type != "pose":
            return []
            
        if results.pose_landmarks is None:
            return []

        keypoints = []
        for landmark in results.pose_landmarks.landmark:
            x = float(landmark.x)
            y = float(landmark.y)
            conf = float(landmark.visibility)
            keypoints.append([x, y, conf])

        return keypoints
    
    def close(self):
        """释放资源"""
        if hasattr(self, 'detector') and self.detector:
            self.detector.close()