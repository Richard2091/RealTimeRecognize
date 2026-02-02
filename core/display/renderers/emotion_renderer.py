"""
表情渲染器
负责表情检测结果的绘制
"""
import cv2


class EmotionRenderer:
    """表情渲染器"""
    
    def __init__(self):
        # 表情颜色配置
        self.box_color = (255, 0, 0)  # 蓝色框
        self.text_color = (0, 0, 255)  # 红色文本
        self.text_font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.7
        self.font_thickness = 2
    
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
        cv2.rectangle(frame, (x1, y1), (x2, y2), self.box_color, 2)
        
        # 绘制表情标签
        label = f"Person: {emotion}"
        cv2.putText(frame, label, (x1, y1 - 10),
                   self.text_font, self.font_scale, self.text_color, self.font_thickness)
    
    def render_emotion_list(self, frame, emotions_list):
        """
        渲染多个表情检测结果
        
        Args:
            frame: 输入帧
            emotions_list: 表情列表 [(emotion, face_rect), ...]
        """
        for emotion, face_rect in emotions_list:
            self.render_emotion(frame, emotion, face_rect)