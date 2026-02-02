"""
显示方式选择组件
"""
import cv2
from .button import Button


class DisplaySelector:
    """显示方式选择器"""
    
    def __init__(self, x=50, y=350):
        self.x = x
        self.y = y
        self.use_opencv = True
        self.buttons = []
        self.on_display_changed = None
        
        # 创建显示方式选择按钮
        self._create_buttons()
    
    def _create_buttons(self):
        """创建显示方式选择按钮"""
        # OpenCV显示按钮
        btn_opencv = Button(
            text="OpenCV显示 (推荐)",
            x=self.x,
            y=self.y + 40,
            width=340,
            height=50
        )
        btn_opencv.set_toggle(True)
        btn_opencv.set_active(True)
        btn_opencv.set_callback(lambda btn: self._select_display(True))
        
        # YOLO内置显示按钮
        btn_yolo = Button(
            text="YOLO内置显示",
            x=self.x + 340 + 20,
            y=self.y + 40,
            width=340,
            height=50
        )
        btn_yolo.set_toggle(True)
        btn_yolo.set_callback(lambda btn: self._select_display(False))
        
        self.buttons = [btn_opencv, btn_yolo]
    
    def _select_display(self, use_opencv):
        """选择显示方式"""
        self.use_opencv = use_opencv
        
        # 更新按钮状态
        for button in self.buttons:
            if button.text.startswith("OpenCV") and use_opencv:
                button.set_active(True)
            elif button.text.startswith("YOLO") and not use_opencv:
                button.set_active(True)
            else:
                button.set_active(False)
        
        if self.on_display_changed:
            self.on_display_changed(use_opencv)
    
    def draw(self, canvas):
        """绘制组件"""
        # 绘制标题
        cv2.putText(canvas, "选择显示方式:", (self.x, self.y),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (220, 220, 220), 2)
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(canvas)
    
    def handle_click(self, x, y):
        """处理点击事件"""
        for button in self.buttons:
            if button.handle_click(x, y):
                return True
        return False