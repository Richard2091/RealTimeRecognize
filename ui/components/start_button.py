"""
开始按钮组件
"""
import cv2
from .button import Button


class StartButton:
    """开始按钮组件"""
    
    def __init__(self, window_width=800, window_height=600):
        self.width = 200
        self.height = 60
        self.x = (window_width - self.width) // 2
        self.y = window_height - 100
        self.config_complete = False
        self.on_start_clicked = None
        
        # 创建开始按钮
        self.button = Button(
            text="开始检测",
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height
        )
        self.button.set_callback(self._on_click)
    
    def set_config_complete(self, complete):
        """设置配置完成状态"""
        self.config_complete = complete
        # 更新按钮颜色
        if complete:
            self.button.bg_color = (50, 205, 50)  # 绿色激活
            self.button.border_color = (255, 255, 255)  # 白色边框
        else:
            self.button.bg_color = (100, 100, 100)  # 灰色非激活
            self.button.border_color = (100, 100, 100)  # 灰色边框
    
    def _on_click(self, button):
        """开始按钮点击处理"""
        if self.config_complete and self.on_start_clicked:
            self.on_start_clicked()
    
    def draw(self, canvas):
        """绘制组件"""
        self.button.draw(canvas)
    
    def handle_click(self, x, y):
        """处理点击事件"""
        return self.button.handle_click(x, y)