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
        self._connect_bottom_info_signals()

    def _connect_control_signals(self):
        """连接控制面板信号"""
        control_panel = self.main_window.control_panel

        # 获取组件引用
        pose_checkbox = control_panel.get_component('pose_checkbox')
        emotion_checkbox = control_panel.get_component('emotion_checkbox')
        gesture_checkbox = control_panel.get_component('gesture_checkbox')
        mirror_checkbox = control_panel.get_component('mirror_checkbox')
        start_button = control_panel.get_component('start_button')
        stop_button = control_panel.get_component('stop_button')
        exit_button = control_panel.get_component('exit_button')

        # 连接信号
        pose_checkbox.toggled.connect(self._on_pose_toggled)
        emotion_checkbox.toggled.connect(self._on_emotion_toggled)
        gesture_checkbox.toggled.connect(self._on_gesture_toggled)
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

    def _on_emotion_toggled(self, checked):
        """表情检测切换"""
        self.main_window.use_emotion = checked

    def _on_gesture_toggled(self, checked):
        """手势识别切换"""
        self.main_window.use_gesture = checked

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

    def _on_bottom_info_collapse(self):
        """当底部信息区域收起时，调整分割器高度为标签栏高度并隐藏分割线"""
        bottom_info_area = self.main_window.bottom_info_area
        current_sizes = self.main_window.main_splitter.sizes()
        top_height = current_sizes[0]
        self.main_window.main_splitter.setSizes([top_height, self.main_window.tab_bar_height])
        # 收起时设置分割线宽度为0，隐藏分割线，用户无法拖动
        self.main_window.main_splitter.setHandleWidth(0)

    def _on_bottom_info_expand(self):
        """当底部信息区域展开时，调整分割器高度为展开高度并显示分割线"""
        bottom_info_area = self.main_window.bottom_info_area
        # 恢复分割线宽度，允许用户拖动
        self.main_window.main_splitter.setHandleWidth(self.main_window.splitter_handle_width)
        current_sizes = self.main_window.main_splitter.sizes()
        top_height = current_sizes[0]
        expanded_height = bottom_info_area.expanded_height + self.main_window.tab_bar_height
        self.main_window.main_splitter.setSizes([top_height, expanded_height])

    def _on_splitter_moved(self, pos, index):
        """当分割器移动时，更新底部信息栏的展开高度"""
        # 参数 pos 和 index 未使用，但需要保留以匹配信号签名
        bottom_info_area = self.main_window.bottom_info_area
        if bottom_info_area.is_expanded:
            current_sizes = self.main_window.main_splitter.sizes()
            bottom_height = current_sizes[1]
            # 更新展开高度（减去标签栏高度）
            bottom_info_area.expanded_height = bottom_height - self.main_window.tab_bar_height

    def _connect_bottom_info_signals(self):
        """连接底部信息栏相关信号"""
        # 获取底部信息栏和分割器
        bottom_info_area = self.main_window.bottom_info_area
        main_splitter = self.main_window.main_splitter

        # 连接分割器移动信号
        main_splitter.splitterMoved.connect(self._on_splitter_moved)

        # 连接底部信息栏的展开/收起信号
        bottom_info_area.on_collapse = self._on_bottom_info_collapse
        bottom_info_area.on_expand = self._on_bottom_info_expand
