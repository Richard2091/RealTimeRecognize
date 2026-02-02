"""
控制面板组件
包含左侧控制面板的所有UI组件
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QGroupBox, QLabel, 
                             QComboBox, QCheckBox, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt
from utils.config import Config


class ControlPanel:
    """控制面板组件管理器"""
    
    def __init__(self):
        self.panel = None
        self.components = {}
        
    def create_panel(self):
        """创建完整的控制面板"""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout()
        
        # 添加各个组件
        layout.addWidget(self.create_model_selector())
        layout.addWidget(self.create_camera_selector())
        layout.addWidget(self.create_feature_selector())
        layout.addWidget(self.create_display_settings())
        layout.addWidget(self.create_control_buttons())
        
        # 添加弹性空间
        layout.addStretch()
        
        panel.setLayout(layout)
        self.panel = panel
        return panel
    
    def create_model_selector(self):
        """创建模型选择器组件"""
        group = QGroupBox("模型选择")
        layout = QVBoxLayout()
        
        # 模型下拉框
        model_combo = QComboBox()
        for key, model_info in Config.ALL_MODELS.items():
            model_combo.addItem(model_info['display'], key)
        
        layout.addWidget(model_combo)
        group.setLayout(layout)
        
        self.components['model_combo'] = model_combo
        return group
    
    def create_camera_selector(self):
        """创建摄像头选择器组件"""
        from PyQt5.QtWidgets import QLineEdit
        
        group = QGroupBox("摄像头设置")
        layout = QVBoxLayout()

        # 摄像头源选择
        layout.addWidget(QLabel("摄像头源:"))
        camera_source_combo = QComboBox()
        camera_source_combo.addItem("本地摄像头", 'local')
        camera_source_combo.addItem("RTSP网络摄像头", 'rtsp')
        layout.addWidget(camera_source_combo)

        # RTSP地址输入
        rtsp_label = QLabel("RTSP摄像头IP:")
        rtsp_label.setVisible(False)
        layout.addWidget(rtsp_label)

        rtsp_url_input = QLineEdit()
        rtsp_url_input.setPlaceholderText("192.168.1.100 (默认端口8554)")
        rtsp_url_input.setVisible(False)
        layout.addWidget(rtsp_url_input)

        # 常用RTSP地址提示
        rtsp_hint_label = QLabel("格式: IP[:端口] (例如: 192.168.1.100 或 192.168.1.100:554)")
        rtsp_hint_label.setStyleSheet("color: gray; font-size: 10px;")
        rtsp_hint_label.setVisible(False)
        layout.addWidget(rtsp_hint_label)

        group.setLayout(layout)
        
        # 保存组件引用
        self.components.update({
            'camera_source_combo': camera_source_combo,
            'rtsp_label': rtsp_label,
            'rtsp_url_input': rtsp_url_input,
            'rtsp_hint_label': rtsp_hint_label
        })
        
        return group
    
    def create_feature_selector(self):
        """创建功能选择器组件"""
        group = QGroupBox("检测功能")
        layout = QVBoxLayout()

        # 姿态检测
        pose_checkbox = QCheckBox("姿态检测")
        pose_checkbox.setChecked(False)
        layout.addWidget(pose_checkbox)

        # 骨骼显示
        skeleton_checkbox = QCheckBox("显示骨骼连接")
        skeleton_checkbox.setChecked(False)
        skeleton_checkbox.setEnabled(False)
        layout.addWidget(skeleton_checkbox)

        # 表情检测
        emotion_checkbox = QCheckBox("表情检测")
        emotion_checkbox.setChecked(False)
        emotion_checkbox.setEnabled(False)
        layout.addWidget(emotion_checkbox)

        group.setLayout(layout)
        
        self.components.update({
            'pose_checkbox': pose_checkbox,
            'skeleton_checkbox': skeleton_checkbox,
            'emotion_checkbox': emotion_checkbox
        })
        
        return group
    
    def create_display_settings(self):
        """创建显示设置组件"""
        group = QGroupBox("显示设置")
        layout = QVBoxLayout()

        # 镜像模式
        mirror_checkbox = QCheckBox("镜像模式")
        mirror_checkbox.setChecked(False)
        layout.addWidget(mirror_checkbox)

        # 镜头控制
        zoom_label = QLabel("镜头缩放:")
        layout.addWidget(zoom_label)

        zoom_layout = QHBoxLayout()
        zoom_out_button = QPushButton("-")
        zoom_out_button.setEnabled(False)
        zoom_layout.addWidget(zoom_out_button)

        zoom_value_label = QLabel("100%")
        zoom_value_label.setAlignment(Qt.AlignCenter)
        zoom_layout.addWidget(zoom_value_label)

        zoom_in_button = QPushButton("+")
        zoom_in_button.setEnabled(False)
        zoom_layout.addWidget(zoom_in_button)

        layout.addLayout(zoom_layout)

        group.setLayout(layout)
        
        self.components.update({
            'mirror_checkbox': mirror_checkbox,
            'zoom_out_button': zoom_out_button,
            'zoom_value_label': zoom_value_label,
            'zoom_in_button': zoom_in_button
        })
        
        return group
    
    def create_control_buttons(self):
        """创建控制按钮组件"""
        group = QGroupBox("控制")
        layout = QVBoxLayout()
        
        # 启动按钮
        start_button = QPushButton("启动检测")
        layout.addWidget(start_button)
        
        # 停止按钮
        stop_button = QPushButton("停止检测")
        stop_button.setEnabled(False)
        layout.addWidget(stop_button)
        
        # 退出按钮
        exit_button = QPushButton("退出")
        layout.addWidget(exit_button)
        
        group.setLayout(layout)
        
        self.components.update({
            'start_button': start_button,
            'stop_button': stop_button,
            'exit_button': exit_button
        })
        
        return group
    
    def get_component(self, name):
        """获取指定组件"""
        return self.components.get(name)
    
    def get_all_components(self):
        """获取所有组件"""
        return self.components