"""
姿态渲染器
负责姿态关键点和骨骼连接的绘制
"""
import cv2


class PoseRenderer:
    """姿态渲染器"""
    
    def __init__(self, show_skeleton=True):
        self.show_skeleton = show_skeleton
        
        # 关键点颜色配置
        self.landmark_color = (0, 255, 255)  # 黄色关键点
        self.connection_color = (0, 255, 255)  # 黄色连接线
        
        # MediaPipe POSE_CONNECTIONS
        self.connections = [
            (11, 13), (13, 15),  # 左臂
            (12, 14), (14, 16),  # 右臂
            (11, 12),           # 肩膀
            (5, 7), (7, 9),     # 左眼-左耳-左肩
            (6, 8), (8, 10),    # 右眼-右耳-右肩
            (5, 6),             # 鼻子
            (5, 11), (6, 12),   # 肩膀到眼睛
            (11, 23), (12, 24), # 肩膀到臀部
            (23, 24),           # 臀部
            (23, 25), (25, 27), # 左腿
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
        if not pose_results.pose_landmarks:
            return
        
        # 转换关键点到图像坐标
        landmarks = self._normalize_landmarks(pose_results.pose_landmarks.landmark, 
                                             frame.shape, bbox)
        
        # 绘制关键点
        self._draw_landmarks(frame, landmarks)
        
        # 绘制骨骼连接
        if self.show_skeleton:
            self._draw_connections(frame, landmarks)
    
    def _normalize_landmarks(self, landmarks, frame_shape, bbox=None):
        """将归一化坐标转换为图像坐标"""
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
            
            normalized_landmarks.append({
                'x': abs_x,
                'y': abs_y,
                'visibility': float(landmark.visibility)
            })
        
        return normalized_landmarks
    
    def _draw_landmarks(self, frame, landmarks):
        """绘制关键点"""
        for lm in landmarks:
            if lm['visibility'] > 0.5:
                cv2.circle(frame, (lm['x'], lm['y']), 3, 
                         self.landmark_color, -1)
    
    def _draw_connections(self, frame, landmarks):
        """绘制骨骼连接"""
        for start_idx, end_idx in self.connections:
            if (start_idx < len(landmarks) and end_idx < len(landmarks)):
                pt1 = landmarks[start_idx]
                pt2 = landmarks[end_idx]
                if pt1['visibility'] > 0.5 and pt2['visibility'] > 0.5:
                    cv2.line(frame, (pt1['x'], pt1['y']), (pt2['x'], pt2['y']),
                            self.connection_color, 2)
    
    def set_skeleton_visibility(self, visible):
        """设置骨骼显示状态"""
        self.show_skeleton = visible