"""
MediaPipe检测管理器
统一管理姿态和表情检测
"""
from .mediapipe_detector import MediaPipeDetector
from core.display.renderers.mediapipe_renderer import MediaPipeRenderer


class MediaPipeManager:
    """MediaPipe检测管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.pose_detector = None
        self.emotion_detector = None
        self.renderer = MediaPipeRenderer()
        
        # 配置状态
        self.use_pose = False
        self.use_emotion = False
        self.show_skeleton = False
    
    def initialize_detectors(self, use_pose=False, use_emotion=False):
        """
        初始化检测器
        
        Args:
            use_pose: 是否使用姿态检测
            use_emotion: 是否使用表情检测
        """
        self.use_pose = use_pose
        self.use_emotion = use_emotion
        
        try:
            if use_pose:
                self.pose_detector = MediaPipeDetector(detection_type="pose")
                print("✓ 姿态检测器初始化成功")
            
            if use_emotion:
                self.emotion_detector = MediaPipeDetector(detection_type="face")
                print("✓ 表情检测器初始化成功")
                
        except Exception as e:
            print(f"❌ 检测器初始化失败: {e}")
            raise
    
    def detect_pose(self, frame):
        """姿态检测"""
        if not self.use_pose or not self.pose_detector:
            return None
        return self.pose_detector.detect(frame)
    
    def detect_emotion(self, frame, face_rect=None):
        """表情检测"""
        if not self.use_emotion or not self.emotion_detector:
            return "未知"
        return self.emotion_detector.detect_emotion(frame, face_rect)
    
    def render_pose(self, frame, pose_results, bbox=None):
        """渲染姿态"""
        if pose_results:
            self.renderer.render_pose(frame, pose_results, bbox)
    
    def render_emotion(self, frame, emotion, face_rect):
        """渲染表情"""
        self.renderer.render_emotion(frame, emotion, face_rect)
    
    def set_skeleton_visibility(self, visible):
        """设置骨骼显示状态"""
        self.show_skeleton = visible
        self.renderer.set_skeleton_visibility(visible)
    
    def get_pose_keypoints(self, pose_results):
        """获取姿态关键点"""
        if self.pose_detector and pose_results:
            return self.pose_detector.get_keypoints(pose_results)
        return []
    
    def get_emotion_classes(self):
        """获取表情类别"""
        if self.emotion_detector:
            return self.emotion_detector.get_classes()
        return []
    
    def close(self):
        """释放资源"""
        if self.pose_detector:
            self.pose_detector.close()
        if self.emotion_detector:
            self.emotion_detector.close()
        print("✓ MediaPipe检测器资源已释放")