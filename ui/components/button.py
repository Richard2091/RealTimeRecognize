"""
按钮组件
"""
import cv2
from .base_component import BaseComponent


class Button(BaseComponent):
    """按钮组件"""
    
    def __init__(self, text="按钮", x=0, y=0, width=120, height=40):
        super().__init__(x, y, width, height)
        self.text = text
        self.is_toggle = False
        self.is_active = False
        self.on_click_callback = None
        
        # 状态颜色
        self.active_color = (50, 205, 50)  # 绿色激活
        self.inactive_color = (100, 100, 100)  # 灰色非激活
        self.hover_color = (100, 160, 210)  # 浅钢蓝色悬停
        
    def draw(self, canvas):
        """绘制按钮"""
        if not self.visible:
            return
            
        # 确定颜色
        if self.is_toggle:
            color = self.active_color if self.is_active else self.inactive_color
        else:
            color = self.bg_color
            
        # 绘制背景
        self.draw_rect(canvas, color)
        
        # 绘制文本
        self.draw_text(canvas, self.text)
    
    def on_click(self):
        """按钮点击处理"""
        if self.is_toggle:
            self.is_active = not self.is_active
            
        if self.on_click_callback:
            self.on_click_callback(self)
    
    def set_callback(self, callback):
        """设置点击回调"""
        self.on_click_callback = callback
        return self  # 支持链式调用
    
    def set_toggle(self, is_toggle=True):
        """设置为切换按钮"""
        self.is_toggle = is_toggle
        return self
    
    def set_active(self, active):
        """设置激活状态"""
        self.is_active = active
        return self