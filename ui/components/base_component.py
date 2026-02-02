"""
基础组件类
提供通用UI组件功能
"""
import cv2
import numpy as np


class BaseComponent:
    """基础UI组件"""
    
    def __init__(self, x=0, y=0, width=100, height=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        
        # 默认颜色
        self.bg_color = (70, 130, 180)  # 钢蓝色
        self.text_color = (255, 255, 255)  # 白色
        self.border_color = (255, 255, 255)  # 白色边框
        
    def contains_point(self, x, y):
        """检查点是否在组件内"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def draw(self, canvas):
        """绘制组件（子类需要重写）"""
        raise NotImplementedError("子类必须实现draw方法")
    
    def handle_click(self, x, y):
        """处理点击事件"""
        if self.contains_point(x, y):
            self.on_click()
            return True
        return False
    
    def on_click(self):
        """点击回调（子类可以重写）"""
        pass
    
    def draw_rect(self, canvas, color=None, border_color=None, thickness=-1):
        """绘制矩形"""
        if not self.visible:
            return
            
        color = color or self.bg_color
        border_color = border_color or self.border_color
        
        # 绘制背景
        cv2.rectangle(canvas, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height), 
                     color, thickness)
        
        # 绘制边框
        if thickness == -1:  # 只有填充时才绘制边框
            cv2.rectangle(canvas, (self.x, self.y), 
                         (self.x + self.width, self.y + self.height), 
                         border_color, 2)
    
    def draw_text(self, canvas, text, font_scale=0.7, thickness=2):
        """绘制居中文本"""
        if not self.visible:
            return
            
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 
                                   font_scale, thickness)[0]
        text_x = self.x + (self.width - text_size[0]) // 2
        text_y = self.y + (self.height + text_size[1]) // 2
        
        cv2.putText(canvas, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                   self.text_color, thickness)