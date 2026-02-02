"""
重构后的主窗口类
使用模块化架构，代码更清晰易维护
"""
import sys
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer, QRect

from ui.components.control_panel import ControlPanel
from ui.components.display_area import DisplayArea
from ui.handlers.camera_handler import CameraHandler
from ui.handlers.detection_handler import DetectionHandler
from utils.config_manager import config_manager


class MainWindow(QMainWindow):
    """重构后的主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO实时检测识别")

        # 配置参数
        self.selected_model = None
        self.use_pose = False
        self.use_emotion = False
        self.mirror_mode = False
        self.show_skeleton = False

        # 摄像头配置
        self.camera_source = 'local'  # 'local' 或 'rtsp'
        self.rtsp_url = ''
        self.camera_width = 1280
        self.camera_height = 720

        # 模块化组件
        self.control_panel = ControlPanel()
        self.display_area = DisplayArea()
        self.camera_handler = CameraHandler(self)
        self.detection_handler = DetectionHandler(self)
        
        # 加载配置
        self._load_configuration()

        # 初始化UI
        self._init_ui()
        self._connect_signals()
        
        # 应用配置到UI
        self._apply_configuration()
    
    def _apply_configuration(self):
        """将配置应用到UI组件"""
        try:
            # 应用RTSP地址
            if self.rtsp_url:
                rtsp_url_input = self.control_panel.get_component('rtsp_url_input')
                rtsp_url_input.setText(self.rtsp_url)
            
            # 应用摄像头源选择
            camera_source_combo = self.control_panel.get_component('camera_source_combo')
            index = camera_source_combo.findData(self.camera_source)
            if index >= 0:
                camera_source_combo.setCurrentIndex(index)
            
            # 应用功能开关
            pose_checkbox = self.control_panel.get_component('pose_checkbox')
            emotion_checkbox = self.control_panel.get_component('emotion_checkbox')
            skeleton_checkbox = self.control_panel.get_component('skeleton_checkbox')
            mirror_checkbox = self.control_panel.get_component('mirror_checkbox')
            
            pose_checkbox.setChecked(self.use_pose)
            emotion_checkbox.setChecked(self.use_emotion)
            skeleton_checkbox.setChecked(self.show_skeleton)
            mirror_checkbox.setChecked(self.mirror_mode)
            
            # 应用窗口几何
            geometry = config_manager.get_config_value(self.current_config, 'window_geometry', {})
            if geometry:
                self.setGeometry(QRect(
                    geometry.get('x', 100),
                    geometry.get('y', 100),
                    geometry.get('width', 1400),
                    geometry.get('height', 900)
                ))
                
        except Exception as e:
            print(f"应用配置失败: {e}")
    
    def _load_configuration(self):
        """加载配置文件"""
        config = config_manager.load_config()
        
        # 应用配置值
        self.selected_model = config_manager.get_config_value(config, 'selected_model')
        self.use_pose = config_manager.get_config_value(config, 'use_pose', False)
        self.use_emotion = config_manager.get_config_value(config, 'use_emotion', False)
        self.mirror_mode = config_manager.get_config_value(config, 'mirror_mode', False)
        self.show_skeleton = config_manager.get_config_value(config, 'show_skeleton', False)
        self.camera_source = config_manager.get_config_value(config, 'camera_source', 'local')
        self.rtsp_url = config_manager.get_config_value(config, 'rtsp_url', '')
        
        # 摄像头设置
        camera_settings = config_manager.get_config_value(config, 'camera_settings', {})
        self.camera_width = camera_settings.get('width', 1280)
        self.camera_height = camera_settings.get('height', 720)
        
        # 保存配置引用
        self.current_config = config
    
    def _save_configuration(self):
        """保存当前配置"""
        try:
            # 从UI获取当前状态
            model_combo = self.control_panel.get_component('model_combo')
            pose_checkbox = self.control_panel.get_component('pose_checkbox')
            emotion_checkbox = self.control_panel.get_component('emotion_checkbox')
            skeleton_checkbox = self.control_panel.get_component('skeleton_checkbox')
            mirror_checkbox = self.control_panel.get_component('mirror_checkbox')
            camera_source_combo = self.control_panel.get_component('camera_source_combo')
            rtsp_url_input = self.control_panel.get_component('rtsp_url_input')
            
            # 更新配置字典
            self.current_config['selected_model'] = model_combo.currentData() if model_combo.currentData() else None
            self.current_config['use_pose'] = pose_checkbox.isChecked()
            self.current_config['use_emotion'] = emotion_checkbox.isChecked()
            self.current_config['show_skeleton'] = skeleton_checkbox.isChecked()
            self.current_config['mirror_mode'] = mirror_checkbox.isChecked()
            self.current_config['camera_source'] = camera_source_combo.currentData()
            self.current_config['rtsp_url'] = rtsp_url_input.text()
            
            # 保存窗口几何信息
            geometry = self.geometry()
            self.current_config['window_geometry'] = {
                'x': geometry.x(),
                'y': geometry.y(),
                'width': geometry.width(),
                'height': geometry.height()
            }
            
            # 保存配置
            config_manager.save_config(self.current_config)
            
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建主部件和布局
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # 左侧控制面板
        control_panel = self.control_panel.create_panel()
        main_layout.addWidget(control_panel, 1)
        
        # 右侧显示区域
        display_area = self.display_area.create_display_area()
        main_layout.addWidget(display_area, 3)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 获取组件引用
        camera_source_combo = self.control_panel.get_component('camera_source_combo')
        rtsp_url_input = self.control_panel.get_component('rtsp_url_input')
        pose_checkbox = self.control_panel.get_component('pose_checkbox')
        skeleton_checkbox = self.control_panel.get_component('skeleton_checkbox')
        emotion_checkbox = self.control_panel.get_component('emotion_checkbox')
        mirror_checkbox = self.control_panel.get_component('mirror_checkbox')
        zoom_out_button = self.control_panel.get_component('zoom_out_button')
        zoom_in_button = self.control_panel.get_component('zoom_in_button')
        start_button = self.control_panel.get_component('start_button')
        stop_button = self.control_panel.get_component('stop_button')
        exit_button = self.control_panel.get_component('exit_button')

        # 连接信号
        camera_source_combo.currentIndexChanged.connect(self._on_camera_source_changed)
        rtsp_url_input.textChanged.connect(self._on_rtsp_url_changed)
        pose_checkbox.toggled.connect(self._on_pose_toggled)
        skeleton_checkbox.toggled.connect(self._on_skeleton_toggled)
        emotion_checkbox.toggled.connect(self._on_emotion_toggled)
        mirror_checkbox.toggled.connect(self._on_mirror_toggled)
        zoom_out_button.clicked.connect(self._on_zoom_out)
        zoom_in_button.clicked.connect(self._on_zoom_in)
        start_button.clicked.connect(self._start_detection)
        stop_button.clicked.connect(self._stop_detection)
        exit_button.clicked.connect(self.close)
    
    def _on_pose_toggled(self, checked):
        """姿态检测切换"""
        self.use_pose = checked
        skeleton_checkbox = self.control_panel.get_component('skeleton_checkbox')
        emotion_checkbox = self.control_panel.get_component('emotion_checkbox')
        zoom_out_button = self.control_panel.get_component('zoom_out_button')
        zoom_in_button = self.control_panel.get_component('zoom_in_button')
        
        skeleton_checkbox.setEnabled(checked)
        emotion_checkbox.setEnabled(checked)
        zoom_out_button.setEnabled(checked)
        zoom_in_button.setEnabled(checked)

    def _on_skeleton_toggled(self, checked):
        """骨骼显示切换"""
        self.show_skeleton = checked

    def _on_emotion_toggled(self, checked):
        """表情检测切换"""
        self.use_emotion = checked

    def _on_mirror_toggled(self, checked):
        """镜像模式切换"""
        self.mirror_mode = checked

    def _on_zoom_in(self):
        """镜头放大"""
        if (self.camera_handler.camera and 
            hasattr(self.camera_handler.camera, 'zoom_level')):
            self.camera_handler.camera.zoom_level = min(3.0, self.camera_handler.camera.zoom_level + 0.2)
            zoom_value_label = self.control_panel.get_component('zoom_value_label')
            zoom_value_label.setText(f"{int(self.camera_handler.camera.zoom_level * 100)}%")

    def _on_zoom_out(self):
        """镜头缩小"""
        if (self.camera_handler.camera and 
            hasattr(self.camera_handler.camera, 'zoom_level')):
            self.camera_handler.camera.zoom_level = max(0.5, self.camera_handler.camera.zoom_level - 0.2)
            zoom_value_label = self.control_panel.get_component('zoom_value_label')
            zoom_value_label.setText(f"{int(self.camera_handler.camera.zoom_level * 100)}%")
    
    def _on_rtsp_url_changed(self, text):
        """RTSP地址变化"""
        self.camera_handler.handle_rtsp_url_change(text)

    def _on_camera_source_changed(self, index):
        """摄像头源切换"""
        camera_source_combo = self.control_panel.get_component('camera_source_combo')
        self.camera_source = camera_source_combo.itemData(index)
        self.camera_handler.handle_camera_selection(self.camera_source)
    
    def _start_detection(self):
        """启动检测"""
        if self.camera_handler.start_detection():
            # 如果成功启动检测，连接定时器处理帧
            self._setup_frame_processing()

    def _setup_frame_processing(self):
        """设置帧处理定时器"""
        # 使用单独的定时器来处理帧，避免阻塞主线程
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self._process_frame)
        self.frame_timer.start(30)  # 30ms间隔，约33FPS

    def _process_frame(self):
        """处理视频帧"""
        self.detection_handler.process_frame()

    def _stop_detection(self):
        """停止检测"""
        self.camera_handler.stop_detection()
        self.camera_handler.update_ui_state()
        
        # 停止帧处理定时器
        if hasattr(self, 'frame_timer'):
            self.frame_timer.stop()
    
    def closeEvent(self, event):
        """关闭事件"""
        self._stop_detection()
        # 保存配置
        self._save_configuration()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()