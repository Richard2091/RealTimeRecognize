"""
摄像头管理器
处理摄像头相关的事件和与UI框架的交互
"""
from PyQt5.QtCore import QObject, QTimer
from camera import CameraController, CameraFactory, LocalCamera


class CameraManager(QObject):
    """摄像头管理器 - 负责UI层与CameraManager的交互"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.camera_manager = CameraController()
        self.frame_timer = None

        # 绑定信号
        self._connect_signals()

    def _connect_signals(self):
        """连接摄像头管理器的信号"""
        self.camera_manager.state_changed.connect(self._on_state_changed)
        self.camera_manager.frame_ready.connect(self._on_frame_ready)
        self.camera_manager.error_occurred.connect(self._on_error_occurred)
        self.camera_manager.camera_opened.connect(self._on_camera_opened)
        self.camera_manager.camera_closed.connect(self._on_camera_closed)

    def initialize_camera(self, config: dict) -> bool:
        """
        初始化摄像头

        Args:
            config: 摄像头配置

        Returns:
            是否成功
        """
        print("=" * 50)
        print("初始化摄像头")
        print("=" * 50)

        # 关闭已打开的摄像头
        if self.camera_manager.is_opened():
            self.camera_manager.close_camera()

        # 初始化
        success = self.camera_manager.initialize(config)

        if success:
            print(f"✓ 摄像头初始化成功: {config['type']}")
        else:
            print(f"❌ 摄像头初始化失败")

        return success

    def start_camera(self) -> bool:
        """打开并开始读取摄像头"""
        if not self.camera_manager.config:
            self._on_error_occurred("摄像头未初始化")
            return False

        print("-" * 30)
        print("打开摄像头")
        print("-" * 30)

        # 打开摄像头
        if not self.camera_manager.open_camera():
            return False

        # 开始读取
        if not self.camera_manager.start_reading():
            return False

        # 启动帧读取定时器
        self._start_frame_timer()

        return True

    def stop_camera(self) -> bool:
        """停止并关闭摄像头"""
        print("-" * 30)
        print("停止摄像头")
        print("-" * 30)

        # 停止定时器
        if self.frame_timer:
            self.frame_timer.stop()
            self.frame_timer = None

        # 停止读取并关闭摄像头
        self.camera_manager.stop_reading()
        self.camera_manager.close_camera()

        return True

    def get_frame(self) -> tuple:
        """
        获取当前帧

        Returns:
            (ret, frame): 是否成功和帧数据
        """
        return self.camera_manager.read_frame()

    def update_config(self, config: dict) -> bool:
        """更新摄像头配置"""
        return self.camera_manager.update_config(config)

    def get_statistics(self) -> dict:
        """获取摄像头统计信息"""
        return self.camera_manager.get_statistics()

    def get_camera_manager(self):
        """获取摄像头管理器"""
        return self.camera_manager

    @staticmethod
    def detect_cameras(max_id: int = 3) -> dict:
        """
        检测可用的本地摄像头

        Args:
            max_id: 最大检测ID

        Returns:
            可用摄像头ID和名称的字典
        """
        print(f"  正在检测 {max_id} 个摄像头...")
        cameras = {}

        # 使用LocalCamera的静态方法检测摄像头
        available_cameras = LocalCamera.detect_cameras(max_id)

        for camera_id in available_cameras:
            try:
                test_config = {
                    'type': 'local',
                    'camera_id': camera_id,
                    'width': 640,
                    'height': 480
                }

                camera = CameraFactory.create_camera(test_config)
                if camera is not None:
                    stats = camera.get_statistics()
                    resolution = stats.get('resolution', (640, 480))
                    cameras[camera_id] = f"摄像头 {camera_id} ({resolution[0]}x{resolution[1]})"
                    camera.release()
                    print(f"  ✓ 已添加摄像头 {camera_id} 到列表")
                else:
                    print(f"  ✗ 无法创建摄像头 {camera_id} 实例")

            except Exception as e:
                print(f"  ✗ 摄像头 {camera_id} 处理失败: {e}")

        return cameras

    def _start_frame_timer(self):
        """启动帧读取定时器"""
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self._on_frame_timer)
        self.frame_timer.start(30)  # 30ms间隔，约33FPS
        print("✓ 帧读取定时器已启动")

    def _on_frame_timer(self):
        """帧定时器回调"""
        if self.camera_manager.is_reading():
            ret, frame = self.camera_manager.read_frame()
            if ret and frame is not None:
                # 委托给检测管理器处理帧
                self.main_window.detection_manager.process_frame(frame)
            else:
                print(f"⚠ 读取帧失败: ret={ret}, frame is None={frame is None}")

    def _on_state_changed(self, old_state: str, new_state: str):
        """状态变化回调"""
        print(f"摄像头状态变化: {old_state} -> {new_state}")

        # 更新UI状态
        status_label = self.main_window.display_area.get_component('status_label')
        if status_label:
            status_label.setText(f"状态: {new_state}")

    def _on_frame_ready(self, frame):
        """帧准备好回调"""
        # 此回调在get_frame中已处理
        pass

    def _on_error_occurred(self, error_message: str):
        """错误发生回调"""
        print(f"❌ 摄像头错误: {error_message}")

        # 更新UI状态
        if hasattr(self.main_window, 'display_area'):
            status_label = self.main_window.display_area.get_component('status_label')
            if status_label:
                status_label.setText(f"状态: {error_message}")

    def _on_camera_opened(self):
        """摄像头已打开回调"""
        # 更新UI状态
        if hasattr(self.main_window, 'display_area'):
            status_label = self.main_window.display_area.get_component('status_label')
            if status_label:
                status_label.setText("状态: 摄像头已打开")

    def _on_camera_closed(self):
        """摄像头已关闭回调"""
        # 更新UI状态
        if hasattr(self.main_window, 'display_area'):
            status_label = self.main_window.display_area.get_component('status_label')
            if status_label:
                status_label.setText("状态: 摄像头已关闭")

    def is_camera_opened(self) -> bool:
        """检查摄像头是否已打开"""
        return self.camera_manager.is_opened()

    def is_camera_reading(self) -> bool:
        """检查是否正在读取"""
        return self.camera_manager.is_reading()
