"""
模型选择器组件
"""
import cv2
from .button import Button
from utils.config import Config


class ModelSelector:
    """模型选择器组件"""
    
    def __init__(self, x=50, y=150, width=700):
        self.x = x
        self.y = y
        self.width = width
        self.buttons = []
        self.selected_model = None
        self.on_model_selected = None
        
        # 创建模型选择按钮
        self._create_buttons()
    
    def _create_buttons(self):
        """创建模型选择按钮"""
        y_offset = 0
        
        for key, model_info in Config.ALL_MODELS.items():
            button = Button(
                text=f"{model_info['display']}",
                x=self.x,
                y=self.y + y_offset,
                width=self.width,
                height=50
            )
            
            button.set_toggle(True)
            button.set_callback(lambda btn, k=key: self._select_model(k))
            
            self.buttons.append(button)
            y_offset += 60  # 按钮高度 + 间距
    
    def _select_model(self, model_key):
        """选择模型"""
        # 取消其他按钮的选中状态
        for button in self.buttons:
            button.set_active(False)
        
        # 设置当前选中的按钮
        for button in self.buttons:
            if button.text == Config.ALL_MODELS[model_key]['display']:
                button.set_active(True)
                self.selected_model = model_key
                break
        
        if self.on_model_selected:
            self.on_model_selected(model_key)
    
    def draw(self, canvas):
        """绘制组件"""
        # 绘制标题
        cv2.putText(canvas, "选择YOLO模型:", (self.x, self.y - 10),
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