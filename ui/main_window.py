"""
重构后的主窗口类
使用模块化架构，代码更清晰易维护
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QSplitter, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from ui.components.control_panel import ControlPanel
from ui.components.display_area import DisplayArea
from ui.components.bottom_info_area import BottomInfoArea
from ui.managers.camera_manager import CameraController, CameraManager
from ui.managers.detection_manager import DetectionManager
from ui.managers.signal_manager import SignalManager
from ui.managers.config_file_manager import config_manager


class MainWindow(QMainWindow):
    """重构后的主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO实时检测识别系统")

        # 配置参数
        self.selected_model = None
        self.use_pose = False
        self.use_emotion = False
        self.use_gesture = False
        self.mirror_mode = False
        self.tab_bar_height = 30  # 标签栏高度
        self.splitter_handle_width = 6  # 分割器句柄的原始宽度

        # 模块化组件
        self.control_panel = ControlPanel()
        self.display_area = DisplayArea()
        self.bottom_info_area = BottomInfoArea()
        self.camera_manager = CameraManager(self)
        self.detection_manager = DetectionManager(self)
        self.signal_manager = SignalManager(self)

        # 加载配置
        self._load_configuration()

        # 初始化UI
        self._init_ui()

        # 连接信号
        self.signal_manager.connect_all_signals()

        # 应用配置到UI
        self._apply_configuration()

        # 重定向标准输出到日志
        self._setup_log_redirect()
    
    def _apply_configuration(self):
        """将配置应用到UI组件"""
        try:
            # 使用 WindowConfigManager 应用配置
            from ui.managers.window_config_manager import WindowConfigManager
            window_config_manager = WindowConfigManager()

            # 设置加载配置标志，避免触发回调
            self.bottom_info_area.loading_config = True

            window_config_manager.apply_to_ui(self.control_panel, self, self.current_config)

            # 恢复加载配置标志
            self.bottom_info_area.loading_config = False

            # 根据底部信息栏的展开状态调整分割器
            if self.bottom_info_area.is_expanded:
                # 展开状态：确保分割器高度足够显示内容，并显示分割线
                self.main_splitter.setHandleWidth(self.splitter_handle_width)
                current_sizes = self.main_splitter.sizes()
                top_height = current_sizes[0]
                # 如果底部高度小于标签栏+展开高度，则调整
                if current_sizes[1] < self.bottom_info_area.expanded_height + self.tab_bar_height:
                    expanded_height = self.bottom_info_area.expanded_height + self.tab_bar_height
                    self.main_splitter.setSizes([top_height, expanded_height])
            else:
                # 收起状态：确保底部高度只有标签栏高度，并隐藏分割线
                current_sizes = self.main_splitter.sizes()
                top_height = current_sizes[0]
                self.main_splitter.setSizes([top_height, self.tab_bar_height])
                self.main_splitter.setHandleWidth(0)

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
        self.use_gesture = config_manager.get_config_value(config, 'use_gesture', False)
        self.mirror_mode = config_manager.get_config_value(config, 'mirror_mode', False)

        # 保存配置引用
        self.current_config = config
    
    def _save_configuration(self):
        """保存当前配置"""
        try:
            # 使用 WindowConfigManager 保存配置
            from ui.managers.window_config_manager import WindowConfigManager
            window_config_manager = WindowConfigManager()
            window_config_manager.save_from_ui(self.control_panel, self, self.current_config)

        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def _on_bottom_info_collapse(self):
        """当底部信息区域收起时，调整分割器高度为标签栏高度并隐藏分割线"""
        current_sizes = self.main_splitter.sizes()
        top_height = current_sizes[0]
        self.main_splitter.setSizes([top_height, self.tab_bar_height])
        # 收起时设置分割线宽度为0，隐藏分割线，用户无法拖动
        self.main_splitter.setHandleWidth(0)

    def _on_bottom_info_expand(self):
        """当底部信息区域展开时，调整分割器高度为展开高度并显示分割线"""
        # 恢复分割线宽度，允许用户拖动
        self.main_splitter.setHandleWidth(self.splitter_handle_width)
        current_sizes = self.main_splitter.sizes()
        top_height = current_sizes[0]
        expanded_height = self.bottom_info_area.expanded_height + self.tab_bar_height
        self.main_splitter.setSizes([top_height, expanded_height])

    def _on_splitter_moved(self, pos, index):
        """当分割器移动时，更新底部信息栏的展开高度"""
        # 参数 pos 和 index 未使用，但需要保留以匹配信号签名
        if self.bottom_info_area.is_expanded:
            current_sizes = self.main_splitter.sizes()
            bottom_height = current_sizes[1]
            # 更新展开高度（减去标签栏高度）
            self.bottom_info_area.expanded_height = bottom_height - self.tab_bar_height

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

        # 连接底部信息区域的展开/收起信号
        self.bottom_info_area.on_collapse = self._on_bottom_info_collapse
        self.bottom_info_area.on_expand = self._on_bottom_info_expand

        # 创建垂直分割器
        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.setChildrenCollapsible(False)
        vertical_splitter.setHandleWidth(self.splitter_handle_width)

        # 添加上部和下部到分割器
        vertical_splitter.addWidget(top_widget)
        vertical_splitter.addWidget(bottom_info_area)

        # 初始状态为收起，隐藏分割线，设置宽度为0
        vertical_splitter.setHandleWidth(0)

        # 连接分割器移动信号，用于更新底部信息栏的展开高度
        vertical_splitter.splitterMoved.connect(self._on_splitter_moved)

        # 设置分割器的初始比例
        vertical_splitter.setStretchFactor(0, 1)
        vertical_splitter.setStretchFactor(1, 0)
        # 初始状态：收起，只显示标签栏高度
        vertical_splitter.setSizes([600, self.tab_bar_height])

        # 显示分割线
        vertical_splitter.setStyleSheet("QSplitter::handle { background-color: #E0E0E0; }")

        # 将垂直分割器添加到边框容器
        border_layout.addWidget(vertical_splitter)

        # 将边框容器添加到主布局
        main_layout.addWidget(border_container, 1)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 保存组件引用
        self.main_splitter = vertical_splitter

    def _detect_and_populate_cameras(self):
        """检测并填充可用摄像头列表"""
        try:
            print("\n检测可用摄像头...")
            print("-" * 30)

            local_camera_combo = self.control_panel.get_component('local_camera_combo')

            # 清空现有选项
            local_camera_combo.clear()

            # 使用CameraUIHandler检测摄像头
            cameras = self.camera_manager.detect_cameras(max_id=3)

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

    def update_detection_ui(self, detecting: bool):
        """更新检测相关UI"""
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

    def toggle_camera_ui(self, camera_type: str):
        """切换摄像头UI显示"""
        control_panel = self.control_panel

        if camera_type == 'local':
            # 显示本地摄像头选择，隐藏RTSP输入
            control_panel.get_component('local_camera_label').setVisible(True)
            control_panel.get_component('local_camera_combo').setVisible(True)
            control_panel.get_component('rtsp_label').setVisible(False)
            control_panel.get_component('rtsp_url_input').setVisible(False)
            control_panel.get_component('rtsp_hint_label').setVisible(False)
            print(f"✓ 切换到本地摄像头")
        elif camera_type == 'rtsp':
            # 显示RTSP输入，隐藏本地摄像头选择
            control_panel.get_component('local_camera_label').setVisible(False)
            control_panel.get_component('local_camera_combo').setVisible(False)
            control_panel.get_component('rtsp_label').setVisible(True)
            control_panel.get_component('rtsp_url_input').setVisible(True)
            control_panel.get_component('rtsp_hint_label').setVisible(True)
            print(f"✓ 切换到RTSP摄像头")

    def closeEvent(self, event):
        """关闭事件"""
        self.detection_manager.stop_detection()
        self._save_configuration()

        # 恢复标准输出
        if hasattr(sys.stdout, 'terminal'):
            sys.stdout = sys.stdout.terminal
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    # 设置应用图标
    app.setWindowIcon(QIcon('ui/logo.svg'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
