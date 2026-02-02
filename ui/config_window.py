"""
配置窗口模块
提供GUI界面选择启动配置
"""
import cv2
import numpy as np
from pathlib import Path
from utils.config import Config


class ConfigWindow:
    """配置窗口"""
    
    def __init__(self, width=800, height=600):
        """
        初始化配置窗口
        
        Args:
            width: 窗口宽度
            height: 窗口高度
        """
        self.width = width
        self.height = height
        self.window_name = "YOLO配置向导"
        
        # 选择状态
        self.selected_model = None
        self.use_opencv = True
        self.use_pose = False
        self.use_emotion = False
        self.config_complete = False
        
        # 颜色定义
        self.bg_color = (30, 30, 40)  # 深蓝灰背景
        self.title_color = (0, 200, 255)  # 青色标题
        self.text_color = (220, 220, 220)  # 浅灰色文本
        self.button_color = (70, 130, 180)  # 钢蓝色按钮
        self.button_hover_color = (100, 160, 210)  # 浅钢蓝色
        self.active_color = (50, 205, 50)  # 绿色激活状态
        self.inactive_color = (100, 100, 100)  # 灰色非激活
        
        # 按钮定义
        self.buttons = []
        self.hovered_button = None
        
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
    
    def draw_model_selection(self, canvas):
        """绘制模型选择"""
        y_start = 150
        x_start = 50
        
        # 标题
        cv2.putText(canvas, "选择YOLO模型:", (x_start, y_start),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.text_color, 2)
        
        # 模型选项
        y = y_start + 50
        model_index = 1
        
        for key, model_info in Config.ALL_MODELS.items():
            # 按钮位置
            btn_x = x_start
            btn_y = y
            btn_width = 700
            btn_height = 50
            
            # 按钮颜色（选中状态）
            is_selected = (self.selected_model == key)
            color = self.active_color if is_selected else self.button_color
            
            # 绘制按钮背景
            cv2.rectangle(canvas, (btn_x, btn_y), 
                         (btn_x + btn_width, btn_y + btn_height), 
                         color, -1)
            
            # 绘制按钮边框
            border_color = (255, 255, 255) if is_selected else (150, 150, 150)
            cv2.rectangle(canvas, (btn_x, btn_y), 
                         (btn_x + btn_width, btn_y + btn_height), 
                         border_color, 2)
            
            # 按钮文本
            text = f"{model_index}. {model_info['display']}"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            text_x = btn_x + 20
            text_y = btn_y + (btn_height + text_size[1]) // 2
            
            cv2.putText(canvas, text, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.text_color, 2)
            
            # 存储按钮信息
            self.buttons.append({
                'id': f'model_{key}',
                'x': btn_x,
                'y': btn_y,
                'width': btn_width,
                'height': btn_height,
                'action': lambda k=key: self._select_model(k)
            })
            
            y += btn_height + 10
            model_index += 1
        
        return canvas
    
    def draw_display_selection(self, canvas):
        """绘制显示方式选择"""
        y_start = 350
        x_start = 50
        
        # 标题
        cv2.putText(canvas, "选择显示方式:", (x_start, y_start),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.text_color, 2)
        
        # OpenCV显示按钮
        btn1_x = x_start
        btn1_y = y_start + 40
        btn_width = 340
        btn_height = 50
        
        color1 = self.active_color if self.use_opencv else self.button_color
        cv2.rectangle(canvas, (btn1_x, btn1_y), 
                     (btn1_x + btn_width, btn1_y + btn_height), 
                     color1, -1)
        cv2.rectangle(canvas, (btn1_x, btn1_y), 
                     (btn1_x + btn_width, btn1_y + btn_height), 
                     (255, 255, 255) if self.use_opencv else (150, 150, 150), 2)
        
        cv2.putText(canvas, "OpenCV显示 (推荐)", 
                   (btn1_x + 20, btn1_y + 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.text_color, 2)
        
        # YOLO内置显示按钮
        btn2_x = x_start + btn_width + 20
        btn2_y = y_start + 40
        
        color2 = self.active_color if not self.use_opencv else self.button_color
        cv2.rectangle(canvas, (btn2_x, btn2_y), 
                     (btn2_x + btn_width, btn2_y + btn_height), 
                     color2, -1)
        cv2.rectangle(canvas, (btn2_x, btn2_y), 
                     (btn2_x + btn_width, btn2_y + btn_height), 
                     (255, 255, 255) if not self.use_opencv else (150, 150, 150), 2)
        
        cv2.putText(canvas, "YOLO内置显示", 
                   (btn2_x + 20, btn2_y + 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.text_color, 2)
        
        # 存储按钮信息
        self.buttons.append({
            'id': 'display_opencv',
            'x': btn1_x,
            'y': btn1_y,
            'width': btn_width,
            'height': btn_height,
            'action': lambda: self._select_display(True)
        })
        
        self.buttons.append({
            'id': 'display_yolo',
            'x': btn2_x,
            'y': btn2_y,
            'width': btn_width,
            'height': btn_height,
            'action': lambda: self._select_display(False)
        })
        
        return canvas
    
    def draw_feature_selection(self, canvas, mediapipe_available):
        """绘制功能选择"""
        y_start = 430
        x_start = 50
        
        # 标题
        cv2.putText(canvas, "选择检测功能:", (x_start, y_start),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.text_color, 2)
        
        y = y_start + 40
        
        # 姿态检测按钮
        btn_width = 340
        btn_height = 50
        
        if mediapipe_available:
            # 姿态检测按钮
            btn1_x = x_start
            btn1_y = y
            
            color1 = self.active_color if self.use_pose else self.button_color
            cv2.rectangle(canvas, (btn1_x, btn1_y), 
                         (btn1_x + btn_width, btn1_y + btn_height), 
                         color1, -1)
            cv2.rectangle(canvas, (btn1_x, btn1_y), 
                         (btn1_x + btn_width, btn1_y + btn_height), 
                         (255, 255, 255) if self.use_pose else (150, 150, 150), 2)
            
            cv2.putText(canvas, "姿态检测", 
                       (btn1_x + 20, btn1_y + 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.text_color, 2)
            
            # 表情检测按钮（只有在姿态检测开启时才可用）
            btn2_x = x_start + btn_width + 20
            btn2_y = y
            
            color2 = self.active_color if self.use_emotion else self.button_color
            # 如果姿态检测未开启，按钮变灰
            if not self.use_pose:
                color2 = self.inactive_color
            
            cv2.rectangle(canvas, (btn2_x, btn2_y), 
                         (btn2_x + btn_width, btn2_y + btn_height), 
                         color2, -1)
            
            border_color = (255, 255, 255) if self.use_emotion else (150, 150, 150)
            if not self.use_pose:
                border_color = (100, 100, 100)
            
            cv2.rectangle(canvas, (btn2_x, btn2_y), 
                         (btn2_x + btn_width, btn2_y + btn_height), 
                         border_color, 2)
            
            cv2.putText(canvas, "表情检测", 
                       (btn2_x + 20, btn2_y + 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.text_color, 2)
            
            # 存储按钮信息
            self.buttons.append({
                'id': 'feature_pose',
                'x': btn1_x,
                'y': btn1_y,
                'width': btn_width,
                'height': btn_height,
                'action': lambda: self._select_pose(True) if mediapipe_available else None
            })
            
            self.buttons.append({
                'id': 'feature_emotion',
                'x': btn2_x,
                'y': btn2_y,
                'width': btn_width,
                'height': btn_height,
                'action': lambda: self._select_emotion(True) if mediapipe_available and self.use_pose else None
            })
        else:
            # MediaPipe不可用时显示提示
            cv2.putText(canvas, "MediaPipe未安装，无法使用姿态和表情检测", 
                       (x_start, y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 100), 2)
        
        return canvas
    
    def draw_start_button(self, canvas):
        """绘制开始按钮"""
        btn_width = 200
        btn_height = 60
        btn_x = (self.width - btn_width) // 2
        btn_y = self.height - 100
        
        # 按钮颜色（根据配置是否完成）
        color = self.active_color if self._is_config_complete() else self.inactive_color
        
        # 绘制按钮
        cv2.rectangle(canvas, (btn_x, btn_y), 
                     (btn_x + btn_width, btn_y + btn_height), 
                     color, -1)
        
        # 按钮边框
        border_color = (255, 255, 255) if self._is_config_complete() else (100, 100, 100)
        cv2.rectangle(canvas, (btn_x, btn_y), 
                     (btn_x + btn_width, btn_y + btn_height), 
                     border_color, 3)
        
        # 按钮文本
        text = "开始检测"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 3)[0]
        text_x = btn_x + (btn_width - text_size[0]) // 2
        text_y = btn_y + (btn_height + text_size[1]) // 2
        
        cv2.putText(canvas, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.text_color, 2)
        
        # 存储按钮信息
        self.buttons.append({
            'id': 'start',
            'x': btn_x,
            'y': btn_y,
            'width': btn_width,
            'height': btn_height,
            'action': self._start_detection
        })
        
        return canvas
    
    def _is_config_complete(self):
        """检查配置是否完成"""
        return self.selected_model is not None
    
    def _select_model(self, model_key):
        """选择模型"""
        self.selected_model = model_key
    
    def _select_display(self, use_opencv):
        """选择显示方式"""
        self.use_opencv = use_opencv
    
    def _select_pose(self, use_pose):
        """选择姿态检测"""
        self.use_pose = use_pose
        if not use_pose:
            self.use_emotion = False
    
    def _select_emotion(self, use_emotion):
        """选择表情检测"""
        if self.use_pose:  # 只有姿态检测开启时才能开启表情检测
            self.use_emotion = use_emotion
    
    def _start_detection(self):
        """开始检测"""
        if self._is_config_complete():
            self.config_complete = True
    
    def _check_button_click(self, x, y):
        """检查鼠标点击"""
        for button in self.buttons:
            if (button['x'] <= x <= button['x'] + button['width'] and
                button['y'] <= y <= button['y'] + button['height']):
                if button['action']:
                    button['action']()
                return True
        return False
    
    def _update_hover(self, x, y):
        """更新鼠标悬停状态"""
        self.hovered_button = None
        for button in self.buttons:
            if (button['x'] <= x <= button['x'] + button['width'] and
                button['y'] <= y <= button['y'] + button['height']):
                self.hovered_button = button['id']
                break
    
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
        self.create_window()
        
        while not self.config_complete:
            # 绘制界面
            canvas = self.draw_background()
            canvas = self.draw_title(canvas, "YOLO实时检测系统 - 配置向导")
            canvas = self.draw_model_selection(canvas)
            canvas = self.draw_display_selection(canvas)
            canvas = self.draw_feature_selection(canvas, mediapipe_available)
            canvas = self.draw_start_button(canvas)
            
            # 显示界面
            cv2.imshow(self.window_name, canvas)
            
            # 处理鼠标事件
            def mouse_callback(event, x, y, flags, param):
                if event == cv2.EVENT_MOUSEMOVE:
                    self._update_hover(x, y)
                elif event == cv2.EVENT_LBUTTONDOWN:
                    self._check_button_click(x, y)
            
            cv2.setMouseCallback(self.window_name, mouse_callback)
            
            # 键盘控制
            key = cv2.waitKey(30) & 0xFF
            if key == 27:  # ESC键退出
                break
            elif key == ord('q'):  # Q键退出
                break
        
        # 关闭配置窗口
        cv2.destroyWindow(self.window_name)
        
        if self.config_complete:
            model_info = Config.ALL_MODELS.get(self.selected_model)
            if model_info:
                return True, model_info['file'], self.use_opencv, self.use_pose, self.use_emotion
        
        return False, None, True, False, False