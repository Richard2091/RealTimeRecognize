"""
组件化配置窗口
使用组件化架构重构配置界面
"""
import cv2
import numpy as np
from pathlib import Path
from utils.config import Config
from .components.model_selector import ModelSelector
from .components.display_selector import DisplaySelector
from .components.feature_selector import FeatureSelector
from .components.start_button import StartButton


class ConfigWindowComponent:
    """组件化配置窗口"""
    
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.window_name = "YOLO配置向导"
        
        # 选择状态
        self.selected_model = None
        self.use_opencv = True
        self.use_pose = False
        self.use_emotion = False
        self.config_complete = False
        self.mediapipe_available = True
        
        # 颜色定义
        self.bg_color = (30, 30, 40)  # 深蓝灰背景
        self.title_color = (0, 200, 255)  # 青色标题
        self.text_color = (220, 220, 220)  # 浅灰色文本
        
        # 创建组件
        self._create_components()
        
    def _create_components(self):
        """创建UI组件"""
        # 模型选择器
        self.model_selector = ModelSelector()
        self.model_selector.on_model_selected = self._on_model_selected
        
        # 显示方式选择器
        self.display_selector = DisplaySelector()
        self.display_selector.on_display_changed = self._on_display_changed
        
        # 功能选择器
        self.feature_selector = FeatureSelector()
        self.feature_selector.on_feature_changed = self._on_feature_changed
        
        # 开始按钮
        self.start_button = StartButton(self.width, self.height)
        self.start_button.on_start_clicked = self._start_detection
        
        # 组件列表（用于事件处理）
        self.components = [
            self.model_selector,
            self.display_selector,
            self.feature_selector,
            self.start_button
        ]
    
    def _on_model_selected(self, model_key):
        """模型选择回调"""
        self.selected_model = model_key
        self._update_config_complete()
    
    def _on_display_changed(self, use_opencv):
        """显示方式选择回调"""
        self.use_opencv = use_opencv
    
    def _on_feature_changed(self, use_pose, use_emotion):
        """功能选择回调"""
        self.use_pose = use_pose
        self.use_emotion = use_emotion
    
    def _update_config_complete(self):
        """更新配置完成状态"""
        self.config_complete = self.selected_model is not None
        self.start_button.set_config_complete(self.config_complete)
    
    def _start_detection(self):
        """开始检测"""
        if self.config_complete:
            self.config_complete = True
    
    def create_window(self):
        """创建配置窗口"""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.width, self.height)
        
    def draw_background(self):
        """绘制背景"""
        canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        canvas[:, :] = self.bg_color
        
        # 添加渐变效果
        for i in range(self.height):
            alpha = i / self.height
            color = tuple(int(c * (0.7 + 0.3 * alpha)) for c in self.bg_color)
            cv2.line(canvas, (0, i), (self.width, i), color, 1)
        
        return canvas
    
    def draw_title(self, canvas, title):
        """绘制标题"""
        text_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = 80
        
        # 标题阴影
        cv2.putText(canvas, title, (text_x + 2, text_y + 2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
        
        # 标题
        cv2.putText(canvas, title, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, self.title_color, 3)
        
        return canvas
    
    def draw_components(self, canvas):
        """绘制所有组件"""
        for component in self.components:
            component.draw(canvas)
    
    def handle_click(self, x, y):
        """处理点击事件"""
        for component in self.components:
            if component.handle_click(x, y):
                return True
        return False
    
    def show(self, mediapipe_available=True):
        """
        显示配置窗口
        
        Args:
            mediapipe_available: MediaPipe是否可用
            
        Returns:
            config_complete: 配置是否完成
            selected_model: 选择的模型键
            use_opencv: 是否使用OpenCV显示
            use_pose: 是否使用姿态检测
            use_emotion: 是否使用表情检测
        """
        self.mediapipe_available = mediapipe_available
        self.feature_selector.set_mediapipe_available(mediapipe_available)
        
        self.create_window()
        
        while not self.config_complete:
            # 绘制界面
            canvas = self.draw_background()
            canvas = self.draw_title(canvas, "YOLO实时检测系统 - 配置向导")
            canvas = self.draw_components(canvas)
            
            # 显示界面
            cv2.imshow(self.window_name, canvas)
            
            # 处理鼠标事件
            def mouse_callback(event, x, y, flags, param):
                if event == cv2.EVENT_LBUTTONDOWN:
                    self.handle_click(x, y)
            
            cv2.setMouseCallback(self.window_name, mouse_callback)
            
            # 键盘控制
            key = cv2.waitKey(30) & 0xFF
            if key == 27 or key == ord('q'):  # ESC键或Q键退出
                break
        
        # 关闭配置窗口
        cv2.destroyWindow(self.window_name)
        
        if self.config_complete:
            model_info = Config.ALL_MODELS.get(self.selected_model)
            if model_info:
                return True, model_info['file'], self.use_opencv, self.use_pose, self.use_emotion
        
        return False, None, True, False, False