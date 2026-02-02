"""
检测流水线
整合多个检测器，提供统一的检测接口
"""
import cv2


class DetectionPipeline:
    """检测流水线"""
    
    def __init__(self, yolo_detector, pose_detector=None, emotion_detector=None):
        """
        初始化检测流水线
        
        Args:
            yolo_detector: YOLO检测器
            pose_detector: 姿态检测器（可选）
            emotion_detector: 表情检测器（可选）
        """
        self.yolo_detector = yolo_detector
        self.pose_detector = pose_detector
        self.emotion_detector = emotion_detector
        
        # 配置
        self.use_pose = pose_detector is not None
        self.use_emotion = emotion_detector is not None
    
    def process(self, frame, use_pose=True, use_emotion=True):
        """
        处理帧，执行完整的检测流程
        
        Args:
            frame: 输入帧
            use_pose: 是否使用姿态检测
            use_emotion: 是否使用表情检测
        
        Returns:
            results: 检测结果字典
        """
        results = {
            'frame': frame,
            'yolo_results': None,
            'pose_results': [],
            'emotions': []
        }
        
        # YOLO目标检测
        if self.yolo_detector:
            results['yolo_results'] = self.yolo_detector.detect(frame, verbose=False)
        
        # 对检测到的人进行姿态和表情检测
        if (use_pose and self.use_pose and self.pose_detector and 
            results['yolo_results']):
            for result in results['yolo_results']:
                if result.boxes is not None:
                    boxes = result.boxes
                    for idx, box in enumerate(boxes):
                        # 只对类别为"人"（class_id=0）的目标进行检测
                        if int(box.cls[0]) == 0:
                            # 获取检测框
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                            x1, y1 = max(0, x1), max(0, y1)
                            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                            
                            # 裁剪人体区域（扩大一点边界以包含完整身体）
                            margin = 50
                            x1_crop = max(0, x1 - margin)
                            y1_crop = max(0, y1 - margin)
                            x2_crop = min(frame.shape[1], x2 + margin)
                            y2_crop = min(frame.shape[0], y2 + margin)
                            
                            person_img = frame[y1_crop:y2_crop, x1_crop:x2_crop]
                            
                            if person_img.size > 0:
                                # 姿态检测
                                pose_result = self.pose_detector.detect(person_img)
                                results['pose_results'].append({
                                    'bbox': (x1, y1, x2, y2),
                                    'pose_result': pose_result
                                })
                                
                                # 表情检测（基于鼻子位置）
                                if (use_emotion and self.use_emotion and 
                                    self.emotion_detector and pose_result.pose_landmarks):
                                    # 鼻子是索引0
                                    landmarks = pose_result.pose_landmarks.landmark
                                    if len(landmarks) > 0:
                                        nose = landmarks[0]
                                        if nose.visibility > 0.5:
                                            # 计算在原图中的绝对坐标
                                            nose_x = int((nose.x * (x2_crop - x1_crop)) + x1_crop)
                                            nose_y = int((nose.y * (y2_crop - y1_crop)) + y1_crop)
                                            
                                            face_size = 80
                                            x1_face = int(max(0, nose_x - face_size))
                                            y1_face = int(max(0, nose_y - face_size))
                                            x2_face = int(min(frame.shape[1], nose_x + face_size))
                                            y2_face = int(min(frame.shape[0], nose_y + face_size * 1.2))
                                            
                                            emotion = self.emotion_detector.detect_emotion(
                                                frame, (x1_face, y1_face, x2_face, y2_face)
                                            )
                                            
                                            results['emotions'].append({
                                                'emotion': emotion,
                                                'face_rect': (x1_face, y1_face, x2_face, y2_face)
                                            })
        
        return results
    
    def set_pose_enabled(self, enabled):
        """启用/禁用姿态检测"""
        self.use_pose = enabled and self.pose_detector is not None
    
    def set_emotion_enabled(self, enabled):
        """启用/禁用表情检测"""
        self.use_emotion = enabled and self.emotion_detector is not None
    
    def get_detector_info(self):
        """获取检测器信息"""
        info = {
            'yolo': self.yolo_detector.get_info() if self.yolo_detector else None,
            'pose': {
                'enabled': self.use_pose,
                'available': self.pose_detector is not None
            },
            'emotion': {
                'enabled': self.use_emotion,
                'available': self.emotion_detector is not None
            }
        }
        return info