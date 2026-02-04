"""
信号管理器
管理MainWindow的信号连接和事件处理
"""
from PyQt5.QtCore import QObject


class SignalManager(QObject):
    """信号管理器，负责连接UI组件的信号和处理UI事件"""

    def __init__(self, main_window):
        """
        初始化信号管理器

        Args:
            main_window: 主窗口实例
        """
        super().__init__()
        self.main_window = main_window

    def connect_all_signals(self):
        """连接所有信号"""
        self._connect_control_signals()
        self._connect_camera_signals()

    def _connect_control_signals(self):
        """连接控制面板信号"""
        control_panel = self.main_window.control_panel

        # 获取组件引用
        pose_checkbox = control_panel.get_component('pose_checkbox')
        skeleton_checkbox = control_panel.get_component('skeleton_checkbox')
        emotion_checkbox = control_panel.get_component('emotion_checkbox')
        mirror_checkbox = control_panel.get_component('mirror_checkbox')
        start_button = control_panel.get_component('start_button')
        stop_button = control_panel.get_component('stop_button')
        exit_button = control_panel.get_component('exit_button')

        # 连接信号
        pose_checkbox.toggled.connect(self._on_pose_toggled)
        skeleton_checkbox.toggled.connect(self._on_skeleton_toggled)
        emotion_checkbox.toggled.connect(self._on_emotion_toggled)
        mirror_checkbox.toggled.connect(self._on_mirror_toggled)
        start_button.clicked.connect(self._start_detection)
        stop_button.clicked.connect(self._stop_detection)
        exit_button.clicked.connect(self.main_window.close)

    def _connect_camera_signals(self):
        """连接摄像头相关信号"""
        control_panel = self.main_window.control_panel
        camera_source_combo = control_panel.get_component('camera_source_combo')

        # 连接摄像头源选择信号
        if camera_source_combo:
            camera_source_combo.currentTextChanged.connect(self._on_camera_source_changed)

    def _on_pose_toggled(self, checked):
        """姿态检测切换"""
        self.main_window.use_pose = checked
        control_panel = self.main_window.control_panel
        skeleton_checkbox = control_panel.get_component('skeleton_checkbox')
        emotion_checkbox = control_panel.get_component('emotion_checkbox')

        skeleton_checkbox.setEnabled(checked)
        emotion_checkbox.setEnabled(checked)

    def _on_skeleton_toggled(self, checked):
        """骨骼显示切换"""
        self.main_window.show_skeleton = checked

    def _on_emotion_toggled(self, checked):
        """表情检测切换"""
        self.main_window.use_emotion = checked

    def _on_mirror_toggled(self, checked):
        """镜像模式切换"""
        self.main_window.mirror_mode = checked

    def _on_camera_source_changed(self, source_name: str):
        """摄像头源切换事件"""
        try:
            control_panel = self.main_window.control_panel
            camera_source_combo = control_panel.get_component('camera_source_combo')
            camera_type = camera_source_combo.currentData() if camera_source_combo else 'local'

            # 委托给MainWindow的UI更新方法
            self.main_window.toggle_camera_ui(camera_type)

        except Exception as e:
            print(f"❌ 切换摄像头源失败: {e}")

    def _start_detection(self):
        """启动检测"""
        self.main_window.detection_manager.start_detection()

    def _stop_detection(self):
        """停止检测"""
        self.main_window.detection_manager.stop_detection()
