"""
功能选择组件
"""
import cv2
from .button import Button


class FeatureSelector:
    """功能选择器"""
    
    def __init__(self, x=50, y=430):
        self.x = x
        self.y = y
        self.use_pose = False
        self.use_emotion = False
        self.mediapipe_available = True
        self.buttons = []
        self.on_feature_changed = None
        
    def set_mediapipe_available(self, available):
        """设置MediaPipe可用性"""
        self.mediapipe_available = available
        self._create_buttons()
    
    def _create_buttons(self):
        """创建功能选择按钮"""
        self.buttons = []
        
        if self.mediapipe_available:
            # 姿态检测按钮
            btn_pose = Button(
                text="姿态检测",
                x=self.x,
                y=self.y + 40,
                width=340,
                height=50
            )
            btn_pose.set_toggle(True)
            btn_pose.set_callback(lambda btn: self._select_pose(btn.is_active))
            
            # 表情检测按钮
            btn_emotion = Button(
                text="表情检测",
                x=self.x + 340 + 20,
                y=self.y + 40,
                width=340,
                height=50
            )
            btn_emotion.set_toggle(True)
            btn_emotion.set_callback(lambda btn: self._select_emotion(btn.is_active))
            
            self.buttons = [btn_pose, btn_emotion]
    
    def _select_pose(self, use_pose):
        """选择姿态检测"""
        self.use_pose = use_pose
        
        # 如果关闭姿态检测，也关闭表情检测
        if not use_pose:
            self.use_emotion = False
            # 更新表情检测按钮状态
            for button in self.buttons:
                if button.text == "表情检测":
                    button.set_active(False)
        
        # 更新按钮可用性
        self._update_button_availability()
        
        if self.on_feature_changed:
            self.on_feature_changed(self.use_pose, self.use_emotion)
    
    def _select_emotion(self, use_emotion):
        """选择表情检测"""
        if self.use_pose:  # 只有姿态检测开启时才能开启表情检测
            self.use_emotion = use_emotion
        else:
            self.use_emotion = False
        
        if self.on_feature_changed:
            self.on_feature_changed(self.use_pose, self.use_emotion)
    
    def _update_button_availability(self):
        """更新按钮可用性"""
        for button in self.buttons:
            if button.text == "表情检测":
                # 表情检测按钮只有在姿态检测开启时才可用
                if not self.use_pose:
                    button.bg_color = (100, 100, 100)  # 灰色
                    button.border_color = (100, 100, 100)  # 灰色边框
                    button.visible = False  # 暂时隐藏
                else:
                    button.bg_color = (70, 130, 180)  # 恢复默认颜色
                    button.border_color = (255, 255, 255)  # 白色边框
                    button.visible = True  # 显示
    
    def draw(self, canvas):
        """绘制组件"""
        # 绘制标题
        cv2.putText(canvas, "选择检测功能:", (self.x, self.y),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (220, 220, 220), 2)
        
        if not self.mediapipe_available:
            # MediaPipe不可用时显示提示
            cv2.putText(canvas, "MediaPipe未安装，无法使用姿态和表情检测", 
                       (self.x, self.y + 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 100), 2)
            return
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(canvas)
    
    def handle_click(self, x, y):
        """处理点击事件"""
        if not self.mediapipe_available:
            return False
            
        for button in self.buttons:
            if button.visible and button.handle_click(x, y):
                return True
        return False