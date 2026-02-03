"""
重构后的主窗口类
使用模块化架构，代码更清晰易维护
"""
import sys
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QSplitter, QFrame)
from PyQt5.QtCore import Qt, QRect

from ui.components.control_panel import ControlPanel
from ui.components.display_area import DisplayArea
from ui.components.bottom_info_area import BottomInfoArea
from ui.handlers.detection_handler import DetectionHandler
from ui.handlers.camera_handler import CameraHandler
from utils.config_manager import config_manager


class MainWindow(QMainWindow):
    """重构后的主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO实时检测识别系统")

        # 配置参数
        self.selected_model = None
        self.use_pose = False
        self.use_emotion = False
        self.mirror_mode = False
        self.show_skeleton = False

        # 模块化组件
        self.control_panel = ControlPanel()
        self.display_area = DisplayArea()
        self.bottom_info_area = BottomInfoArea()
        self.detection_handler = DetectionHandler(self)
        self.camera_handler = CameraHandler(self)

        # 加载配置
        self._load_configuration()

        # 初始化UI
        self._init_ui()
        self._connect_signals()

        # 应用配置到UI
        self._apply_configuration()

        # 重定向标准输出到日志
        self._setup_log_redirect()
    
    def _apply_configuration(self):
        """将配置应用到UI组件"""
        try:
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

            # 应用分割器大小
            splitter_sizes = config_manager.get_config_value(self.current_config, 'splitter_sizes', [600, 30])
            if hasattr(self, 'main_splitter'):
                self.main_splitter.setSizes(splitter_sizes)

            # 检测并填充可用摄像头列表
            self._detect_and_populate_cameras()

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

            # 更新配置字典
            self.current_config['selected_model'] = model_combo.currentData() if model_combo.currentData() else None
            self.current_config['use_pose'] = pose_checkbox.isChecked()
            self.current_config['use_emotion'] = emotion_checkbox.isChecked()
            self.current_config['show_skeleton'] = skeleton_checkbox.isChecked()
            self.current_config['mirror_mode'] = mirror_checkbox.isChecked()

            # 保存窗口几何信息
            geometry = self.geometry()
            self.current_config['window_geometry'] = {
                'x': geometry.x(),
                'y': geometry.y(),
                'width': geometry.width(),
                'height': geometry.height()
            }

            # 保存分割器大小
            if hasattr(self, 'main_splitter'):
                self.current_config['splitter_sizes'] = self.main_splitter.sizes()

            # 保存配置
            config_manager.save_config(self.current_config)

        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建主部件和垂直布局
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # 创建统一的边框容器
        border_container = QFrame()
        border_container.setFrameShape(QFrame.StyledPanel)
        border_layout = QVBoxLayout(border_container)
        border_layout.setContentsMargins(0, 0, 0, 0)
        border_layout.setSpacing(0)

        # 上部区域：水平布局（左侧控制面板 + 右侧显示区域）
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(5)

        # 左侧控制面板
        control_panel = self.control_panel.create_panel()
        control_panel.setFrameShape(QFrame.NoFrame)
        top_layout.addWidget(control_panel, 1)

        # 右侧显示区域
        display_area = self.display_area.create_display_area()
        display_area.setFrameShape(QFrame.NoFrame)
        top_layout.addWidget(display_area, 3)

        # 底部信息区域
        bottom_info_area = self.bottom_info_area.create_bottom_info_area()
        bottom_info_area.setFrameShape(QFrame.NoFrame)

        # 创建垂直分割器
        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.setChildrenCollapsible(False)
        vertical_splitter.setHandleWidth(6)

        # 添加上部和下部到分割器
        vertical_splitter.addWidget(top_widget)
        vertical_splitter.addWidget(bottom_info_area)

        # 设置分割器的初始比例
        vertical_splitter.setStretchFactor(0, 1)
        vertical_splitter.setStretchFactor(1, 0)
        vertical_splitter.setSizes([600, 30])

        # 将垂直分割器添加到边框容器
        border_layout.addWidget(vertical_splitter)

        # 将边框容器添加到主布局
        main_layout.addWidget(border_container, 1)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 保存组件引用
        self.main_splitter = vertical_splitter
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 获取组件引用
        pose_checkbox = self.control_panel.get_component('pose_checkbox')
        skeleton_checkbox = self.control_panel.get_component('skeleton_checkbox')
        emotion_checkbox = self.control_panel.get_component('emotion_checkbox')
        mirror_checkbox = self.control_panel.get_component('mirror_checkbox')
        start_button = self.control_panel.get_component('start_button')
        stop_button = self.control_panel.get_component('stop_button')
        exit_button = self.control_panel.get_component('exit_button')
        camera_source_combo = self.control_panel.get_component('camera_source_combo')

        # 连接信号
        pose_checkbox.toggled.connect(self._on_pose_toggled)
        skeleton_checkbox.toggled.connect(self._on_skeleton_toggled)
        emotion_checkbox.toggled.connect(self._on_emotion_toggled)
        mirror_checkbox.toggled.connect(self._on_mirror_toggled)
        start_button.clicked.connect(self._start_detection)
        stop_button.clicked.connect(self._stop_detection)
        exit_button.clicked.connect(self.close)

        # 连接摄像头源选择信号
        if camera_source_combo:
            camera_source_combo.currentTextChanged.connect(self._on_camera_source_changed)
    
    def _on_pose_toggled(self, checked):
        """姿态检测切换"""
        self.use_pose = checked
        skeleton_checkbox = self.control_panel.get_component('skeleton_checkbox')
        emotion_checkbox = self.control_panel.get_component('emotion_checkbox')
        
        skeleton_checkbox.setEnabled(checked)
        emotion_checkbox.setEnabled(checked)
    
    def _on_skeleton_toggled(self, checked):
        """骨骼显示切换"""
        self.show_skeleton = checked
    
    def _on_emotion_toggled(self, checked):
        """表情检测切换"""
        self.use_emotion = checked
    
    def _on_mirror_toggled(self, checked):
        """镜像模式切换"""
        self.mirror_mode = checked

    def _detect_and_populate_cameras(self):
        """检测并填充可用摄像头列表"""
        try:
            print("\n检测可用摄像头...")
            print("-" * 30)

            local_camera_combo = self.control_panel.get_component('local_camera_combo')

            # 清空现有选项
            local_camera_combo.clear()

            # 使用CameraHandler检测摄像头
            cameras = self.camera_handler.detect_cameras(max_id=3)

            print(f"  检测结果: {cameras}")

            if cameras:
                for camera_id, camera_name in cameras.items():
                    local_camera_combo.addItem(camera_name, camera_id)
                    print(f"  ✓ 添加到UI: {camera_name}")
                print(f"✓ 共发现 {len(cameras)} 个摄像头")
            else:
                print("⚠ 未检测到可用摄像头")
                local_camera_combo.addItem("未检测到摄像头", 0)
                print("  ✓ 添加默认选项到UI")

        except Exception as e:
            print(f"❌ 检测摄像头失败: {e}")
            import traceback
            traceback.print_exc()

            # 添加默认选项防止UI为空
            local_camera_combo = self.control_panel.get_component('local_camera_combo')
            if local_camera_combo is not None:
                local_camera_combo.clear()
                local_camera_combo.addItem("检测失败，使用默认摄像头0", 0)

    def _on_camera_source_changed(self, source_name: str):
        """摄像头源切换事件"""
        try:
            camera_source_combo = self.control_panel.get_component('camera_source_combo')
            local_camera_label = self.control_panel.get_component('local_camera_label')
            local_camera_combo = self.control_panel.get_component('local_camera_combo')
            rtsp_label = self.control_panel.get_component('rtsp_label')
            rtsp_url_input = self.control_panel.get_component('rtsp_url_input')
            rtsp_hint_label = self.control_panel.get_component('rtsp_hint_label')

            camera_type = camera_source_combo.currentData() if camera_source_combo else 'local'

            if camera_type == 'local':
                # 显示本地摄像头选择，隐藏RTSP输入
                local_camera_label.setVisible(True)
                local_camera_combo.setVisible(True)
                rtsp_label.setVisible(False)
                rtsp_url_input.setVisible(False)
                rtsp_hint_label.setVisible(False)
                print(f"✓ 切换到本地摄像头")
            elif camera_type == 'rtsp':
                # 显示RTSP输入，隐藏本地摄像头选择
                local_camera_label.setVisible(False)
                local_camera_combo.setVisible(False)
                rtsp_label.setVisible(True)
                rtsp_url_input.setVisible(True)
                rtsp_hint_label.setVisible(True)
                print(f"✓ 切换到RTSP摄像头")

        except Exception as e:
            print(f"❌ 切换摄像头源失败: {e}")
    
    def _setup_log_redirect(self):
        """设置日志重定向"""
        # 重定向标准输出到日志文本框
        class LogRedirector:
            def __init__(self, bottom_info_area):
                self.bottom_info_area = bottom_info_area
                self.terminal = sys.stdout

            def write(self, message):
                self.bottom_info_area.append_log(message)
                self.terminal.write(message)

            def flush(self):
                self.terminal.flush()

        sys.stdout = LogRedirector(self.bottom_info_area)
    
    def _start_detection(self):
        """启动检测"""
        print("=" * 50)
        print("启动检测")
        print("=" * 50)
        
        # 获取模型配置
        model_combo = self.control_panel.get_component('model_combo')
        model_key = model_combo.currentData()
        
        if not model_key:
            print("❌ 错误: 未选择模型")
            self.display_area.get_component('status_label').setText("状态: 请选择模型")
            return
        
        print(f"✓ 选择的模型: {model_key}")
        
        # 获取模型信息
        from utils.config import Config
        model_info = Config.ALL_MODELS.get(model_key)
        if not model_info:
            print(f"❌ 错误: 模型信息不存在: {model_key}")
            self.display_area.get_component('status_label').setText("状态: 模型加载失败")
            return
        
        print(f"✓ 模型路径: {model_info['file']}")
        print(f"✓ 模型描述: {model_info['display']}")
        
        # 加载检测器
        if not self.detection_handler.load_detector(model_info):
            return
        
        # 初始化摄像头
        camera_config = self._get_camera_config()
        if not self.camera_handler.initialize_camera(camera_config):
            self.display_area.get_component('status_label').setText("状态: 摄像头初始化失败")
            return
        
        # 打开摄像头
        if not self.camera_handler.start_camera():
            self.display_area.get_component('status_label').setText("状态: 摄像头打开失败")
            return
        
        # 更新UI状态
        self._update_ui_state(detecting=True)
        print("=" * 50)
        print("✓ 检测已启动")
        print("=" * 50)
    
    def _stop_detection(self):
        """停止检测"""
        print("\n" + "=" * 50)
        print("【停止检测】")
        print("=" * 50)
        
        # 停止摄像头
        self.camera_handler.stop_camera()
        
        # 更新UI状态
        self._update_ui_state(detecting=False)
        
        # 清空显示
        video_label = self.display_area.get_component('video_label')
        video_label.setText("等待启动...")
        video_label.clear()
        
        print("✓ 检测已停止")
        print("=" * 50)
    
    def _get_camera_config(self) -> dict:
        """获取摄像头配置"""
        camera_source_combo = self.control_panel.get_component('camera_source_combo')
        local_camera_combo = self.control_panel.get_component('local_camera_combo')
        rtsp_url_input = self.control_panel.get_component('rtsp_url_input')

        camera_type = camera_source_combo.currentData() if camera_source_combo else 'local'

        config = {
            'type': camera_type,
            'width': 640,
            'height': 480
        }

        if camera_type == 'local':
            camera_id = local_camera_combo.currentData() if local_camera_combo else 0
            config['camera_id'] = camera_id
            print(f"✓ 使用本地摄像头: ID={camera_id}")
        elif camera_type == 'rtsp':
            rtsp_ip = rtsp_url_input.text() if rtsp_url_input else ''
            if rtsp_ip:
                config['rtsp_url'] = rtsp_ip
                print(f"✓ 使用RTSP摄像头: {rtsp_ip}")
            else:
                print("❌ RTSP地址为空，使用默认配置")

        return config
    
    def _update_ui_state(self, detecting: bool):
        """更新UI状态"""
        start_button = self.control_panel.get_component('start_button')
        stop_button = self.control_panel.get_component('stop_button')
        status_label = self.display_area.get_component('status_label')
        
        if detecting:
            start_button.setEnabled(False)
            stop_button.setEnabled(True)
            status_label.setText("状态: 检测中...")
        else:
            start_button.setEnabled(True)
            stop_button.setEnabled(False)
            status_label.setText("状态: 已停止")
    
    def process_camera_frame(self, frame):
        """处理摄像头帧（供CameraHandler调用）"""
        # 将帧传递给检测处理器
        self.detection_handler.process_frame(frame)
    
    def update_camera_status(self, status: str):
        """更新摄像头状态"""
        status_label = self.display_area.get_component('status_label')
        if status_label:
            status_label.setText(f"状态: {status}")
    
    def closeEvent(self, event):
        """关闭事件"""
        self._stop_detection()
        self._save_configuration()
        
        # 恢复标准输出
        if hasattr(sys.stdout, 'terminal'):
            sys.stdout = sys.stdout.terminal
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
