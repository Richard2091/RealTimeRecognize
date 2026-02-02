"""
按钮管理模块
负责按钮的绘制和交互
"""
import cv2


class ButtonManager:
    """按钮管理器"""
    
    def __init__(self, display):
        """
        初始化按钮管理器
        
        Args:
            display: OpenCVDisplay实例，用于访问状态和配置
        """
        self.display = display
        self.buttons = []
        
        # 按钮配置
        self.button_height = 40
        self.button_width = 120
        self.button_margin = 10
        self.button_font = cv2.FONT_HERSHEY_SIMPLEX
        self.button_font_scale = 0.7
        self.button_font_thickness = 2
        
        # 按钮状态颜色
        self.button_color_active = (70, 130, 180)  # 钢蓝色
        self.button_color_inactive = (100, 100, 100)  # 灰色
        self.button_text_color = (255, 255, 255)  # 白色
    
    def setup_buttons(self, frame_width, frame_height, use_pose=False, use_emotion=False):
        """
        设置按钮布局
        
        Args:
            frame_width: 帧宽度
            frame_height: 帧高度
            use_pose: 是否启用姿态检测
            use_emotion: 是否启用表情检测
        """
        self.buttons = []
        
        # 按钮定义： (id, label, active_color, is_toggle)
        button_defs = [
            ('quit', '退出', self.button_color_active, False),
            ('mirror', '镜像: 开' if self.display.mirror_mode else '镜像: 关', 
             self.button_color_active if self.display.mirror_mode else self.button_color_inactive, True),
        ]
        
        if use_pose:
            button_defs.append(
                ('skeleton', '骨骼: 开' if self.display.show_skeleton else '骨骼: 关',
                 self.button_color_active if self.display.show_skeleton else self.button_color_inactive, True)
            )
        
        if use_emotion:
            button_defs.append(
                ('emotion', '表情: 开',
                 self.button_color_active, True)
            )
        
        # 添加缩放相关按钮
        button_defs.extend([
            ('zoom_in', '放大 +', self.button_color_active, False),
            ('zoom_out', '缩小 -', self.button_color_active, False),
            ('zoom_reset', '重置缩放', self.button_color_active, False),
            ('center_reset', '重置中心', self.button_color_active, False),
        ])
        
        # 计算按钮位置（底部居中）
        total_width = len(button_defs) * (self.button_width + self.button_margin) - self.button_margin
        start_x = (frame_width - total_width) // 2
        
        for i, (btn_id, label, color, is_toggle) in enumerate(button_defs):
            x = start_x + i * (self.button_width + self.button_margin)
            y = frame_height - self.button_height - 20  # 底部上方
            self.buttons.append({
                'id': btn_id,
                'label': label,
                'x': x,
                'y': y,
                'width': self.button_width,
                'height': self.button_height,
                'color': color,
                'is_toggle': is_toggle,
                'active': True if not is_toggle else (btn_id == 'mirror' and self.display.mirror_mode) or 
                        (btn_id == 'skeleton' and self.display.show_skeleton) or 
                        (btn_id == 'emotion' and use_emotion)
            })
    
    def draw_buttons(self, frame):
        """
        绘制所有按钮
        
        Args:
            frame: 要绘制按钮的帧
        """
        for button in self.buttons:
            self._draw_button(frame, button)
    
    def _draw_button(self, frame, button):
        """绘制单个按钮"""
        x, y = button['x'], button['y']
        width, height = button['width'], button['height']
        
        # 绘制按钮背景
        color = button['color'] if button['active'] else self.button_color_inactive
        cv2.rectangle(frame, (x, y), (x + width, y + height), color, -1)
        
        # 绘制按钮边框
        border_color = (255, 255, 255) if button['active'] else (150, 150, 150)
        cv2.rectangle(frame, (x, y), (x + width, y + height), border_color, 2)
        
        # 计算文字位置（居中）
        text_size = cv2.getTextSize(button['label'], self.button_font, 
                                   self.button_font_scale, self.button_font_thickness)[0]
        text_x = x + (width - text_size[0]) // 2
        text_y = y + (height + text_size[1]) // 2
        
        # 绘制文字
        cv2.putText(frame, button['label'], (text_x, text_y),
                   self.button_font, self.button_font_scale,
                   self.button_text_color, self.button_font_thickness)
    
    def check_button_click(self, x, y, camera=None):
        """
        检查鼠标点击是否在按钮区域内
        
        Args:
            x: 鼠标x坐标
            y: 鼠标y坐标
            camera: CameraController实例（可选）
        
        Returns:
            (button_id, should_exit, update_buttons)
        """
        should_exit = False
        update_buttons = False
        
        for button in self.buttons:
            btn_x, btn_y = button['x'], button['y']
            btn_width, btn_height = button['width'], button['height']
            
            if (btn_x <= x <= btn_x + btn_width and 
                btn_y <= y <= btn_y + btn_height):
                
                button_id = button['id']
                
                if button_id == 'quit':
                    should_exit = True
                    print("点击退出按钮")
                
                elif button_id == 'mirror':
                    self.display.mirror_mode = not self.display.mirror_mode
                    button['label'] = f"镜像: {'开' if self.display.mirror_mode else '关'}"
                    button['active'] = self.display.mirror_mode
                    button['color'] = self.button_color_active if self.display.mirror_mode else self.button_color_inactive
                    update_buttons = True
                    print(f"镜像: {'开' if self.display.mirror_mode else '关'}")
                
                elif button_id == 'skeleton':
                    self.display.show_skeleton = not self.display.show_skeleton
                    button['label'] = f"骨骼: {'开' if self.display.show_skeleton else '关'}"
                    button['active'] = self.display.show_skeleton
                    button['color'] = self.button_color_active if self.display.show_skeleton else self.button_color_inactive
                    update_buttons = True
                    mode = "骨骼连接" if self.display.show_skeleton else "仅关键点"
                    print(f"切换到: {mode}模式")
                
                elif button_id == 'emotion':
                    # 注意：表情检测开关需要外部处理
                    button['active'] = not button['active']
                    button['label'] = f"表情: {'开' if button['active'] else '关'}"
                    button['color'] = self.button_color_active if button['active'] else self.button_color_inactive
                    update_buttons = True
                    print(f"表情检测: {'开' if button['active'] else '关'}")
                
                elif button_id == 'zoom_in' and camera:
                    camera.zoom_in()
                    update_buttons = True
                
                elif button_id == 'zoom_out' and camera:
                    camera.zoom_out()
                    update_buttons = True
                
                elif button_id == 'zoom_reset' and camera:
                    camera.reset_zoom()
                    update_buttons = True
                
                elif button_id == 'center_reset' and camera:
                    camera.reset_zoom_center()
                    print("缩放中心点已重置为图像中心")
                    update_buttons = True
                
                return button_id, should_exit, update_buttons
        
        return None, should_exit, update_buttons
    
    def update_button_states(self, use_pose, use_emotion):
        """
        更新按钮状态（用于外部状态变化时）
        
        Args:
            use_pose: 是否启用姿态检测
            use_emotion: 是否启用表情检测
        """
        for button in self.buttons:
            if button['id'] == 'mirror':
                button['label'] = f"镜像: {'开' if self.display.mirror_mode else '关'}"
                button['active'] = self.display.mirror_mode
                button['color'] = self.button_color_active if self.display.mirror_mode else self.button_color_inactive
            elif button['id'] == 'skeleton' and use_pose:
                button['label'] = f"骨骼: {'开' if self.display.show_skeleton else '关'}"
                button['active'] = self.display.show_skeleton
                button['color'] = self.button_color_active if self.display.show_skeleton else self.button_color_inactive