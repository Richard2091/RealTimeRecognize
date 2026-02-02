"""
摄像头事件处理器
处理摄像头相关的事件和操作
"""
import cv2
from PyQt5.QtCore import QTimer
from camera.camera_controller import CameraController
from camera.rtsp_camera_controller import RTSPCameraController
from detectors.yolo8_detector import YOLOv8Detector
from detectors.yolo26_detector import YOLO26Detector
from detectors.yolo_world_detector import YOWorldDetector
from core.detectors.mediapipe.mediapipe_manager import MediaPipeManager


class CameraHandler:
    """摄像头事件处理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.detector = None
        self.mediapipe_manager = MediaPipeManager()
        self.camera = None
        self.timer = None
        
    def handle_camera_selection(self, camera_source):
        """处理摄像头源选择"""
        is_rtsp = (camera_source == 'rtsp')
        
        # 显示/隐藏RTSP相关控件
        rtsp_label = self.main_window.control_panel.get_component('rtsp_label')
        rtsp_url_input = self.main_window.control_panel.get_component('rtsp_url_input')
        rtsp_hint_label = self.main_window.control_panel.get_component('rtsp_hint_label')
        
        rtsp_label.setVisible(is_rtsp)
        rtsp_url_input.setVisible(is_rtsp)
        rtsp_hint_label.setVisible(is_rtsp)

        if is_rtsp:
            if not self.main_window.rtsp_url:
                self.main_window.display_area.get_component('status_label').setText("状态: 请输入RTSP地址")
                return
            self._test_rtsp_connection()

    def handle_rtsp_url_change(self, text):
        """处理RTSP地址变化"""
        ip_text = text.strip()

        if not ip_text:
            self.main_window.rtsp_url = ''
            return

        # 构建完整的RTSP URL
        if ':' in ip_text:
            # 用户指定了端口
            self.main_window.rtsp_url = f"rtsp://{ip_text}/"
        else:
            # 使用默认端口8554
            self.main_window.rtsp_url = f"rtsp://{ip_text}:8554/"

    def _test_rtsp_connection(self):
        """测试RTSP连接"""
        if not self.main_window.rtsp_url:
            self.main_window.display_area.get_component('status_label').setText("状态: 请输入RTSP地址")
            return

        self.main_window.display_area.get_component('status_label').setText("状态: 正在测试RTSP连接...")
        print(f"正在测试RTSP连接: {self.main_window.rtsp_url}")

        # 使用RTSP连接线程进行测试
        from ui.threads.rtsp_thread import RTSPConnectionThread
        self.rtsp_test_thread = RTSPConnectionThread(self.main_window.rtsp_url, 1280, 720)
        self.rtsp_test_thread.connection_finished.connect(self._on_rtsp_test_finished)
        self.rtsp_test_thread.start()

    def _on_rtsp_test_finished(self, camera, error_message):
        """RTSP连接测试完成回调"""
        if camera is None:
            self.main_window.display_area.get_component('status_label').setText(f"状态: 无法连接到RTSP流")
            print(f"⚠ RTSP连接失败: {error_message}")
        else:
            camera.release()  # 释放测试连接
            self.main_window.display_area.get_component('status_label').setText("状态: RTSP连接正常")
            print(f"✓ RTSP连接成功: {self.main_window.rtsp_url}")

    def start_detection(self):
        """启动检测流程"""
        print("=" * 50)
        print("获取配置信息")
        print("=" * 50)
        
        # 获取选择的模型
        model_combo = self.main_window.control_panel.get_component('model_combo')
        model_key = model_combo.currentData()
        if not model_key:
            print("❌ 错误: 未选择模型")
            self.main_window.display_area.get_component('status_label').setText("状态: 请选择模型")
            return False
        
        print(f"✓ 选择的模型: {model_key}")
        
        # 获取模型信息
        from utils.config import Config
        model_info = Config.ALL_MODELS.get(model_key)
        if not model_info:
            print(f"❌ 错误: 模型信息不存在: {model_key}")
            self.main_window.display_area.get_component('status_label').setText("状态: 模型加载失败")
            return False
        
        model_path = model_info['file']
        print(f"✓ 模型路径: {model_path}")
        print(f"✓ 模型描述: {model_info['display']}")
        
        # 获取功能选择
        pose_checkbox = self.main_window.control_panel.get_component('pose_checkbox')
        emotion_checkbox = self.main_window.control_panel.get_component('emotion_checkbox')
        
        self.main_window.use_pose = pose_checkbox.isChecked()
        self.main_window.use_emotion = emotion_checkbox.isChecked()
        print(f"✓ 姿态检测: {'是' if self.main_window.use_pose else '否'}")
        print(f"✓ 表情检测: {'是' if self.main_window.use_emotion else '否'}")
        
        # 检查MediaPipe
        print("\n检查依赖")
        print("-" * 30)
        if self.main_window.use_pose or self.main_window.use_emotion:
            try:
                import mediapipe as mp
                print("✓ MediaPipe已安装")
            except ImportError:
                print("❌ MediaPipe未安装，无法使用姿态和表情检测")
                self.main_window.display_area.get_component('status_label').setText("状态: 缺少MediaPipe依赖")
                return False
        
        # 加载检测器
        if not self._load_detectors(model_info, model_path):
            return False
        
        # 打开摄像头
        return self._open_camera()

    def _load_detectors(self, model_info, model_path):
        """加载检测器"""
        try:
            print("\n加载检测模型")
            print("-" * 30)
            
            model_name = model_info['name']
            
            # 根据模型类型创建检测器
            if 'yolov8' in model_name:
                print("正在加载YOLOv8检测器...")
                self.detector = YOLOv8Detector(model_path)
            elif 'yolo26' in model_name:
                print("正在加载YOLO26检测器...")
                self.detector = YOLO26Detector(model_path)
            elif 'world' in model_name:
                print("正在加载YOLO-World检测器...")
                self.detector = YOWorldDetector(model_path)
            else:
                print(f"❌ 错误: 不支持的模型类型: {model_name}")
                self.main_window.display_area.get_component('status_label').setText("状态: 不支持的模型")
                return False
            
            print("✓ 模型加载成功")
            
            # 加载MediaPipe检测器
            if self.main_window.use_pose or self.main_window.use_emotion:
                print("\n加载MediaPipe检测器")
                print("-" * 30)
                print("正在加载MediaPipe检测器...")
                self.mediapipe_manager.initialize_detectors(
                    use_pose=self.main_window.use_pose,
                    use_emotion=self.main_window.use_emotion
                )
                print("[OK] MediaPipe检测器加载成功")
            
            return True
            
        except Exception as e:
            print(f"❌ 检测器加载失败: {e}")
            self.main_window.display_area.get_component('status_label').setText(f"状态: 检测器加载失败")
            import traceback
            traceback.print_exc()
            return False

    def _open_camera(self):
        """打开摄像头"""
        print("\n打开摄像头")
        print("-" * 30)

        if self.main_window.camera_source == 'rtsp':
            # 使用RTSP摄像头
            if not self.main_window.rtsp_url:
                print("❌ 错误: 请输入RTSP地址")
                self.main_window.display_area.get_component('status_label').setText("状态: 请输入RTSP地址")
                return False

            self.main_window.display_area.get_component('status_label').setText("状态: 正在连接RTSP摄像头...")
            print(f"正在初始化RTSP摄像头...")

            # 创建并启动连接线程
            from ui.threads.rtsp_thread import RTSPConnectionThread
            self.rtsp_connect_thread = RTSPConnectionThread(
                self.main_window.rtsp_url,
                self.main_window.camera_width,
                self.main_window.camera_height
            )
            self.rtsp_connect_thread.connection_finished.connect(self._on_camera_connected)
            self.rtsp_connect_thread.start()
            
            # 启动一个定时器来监控连接状态，如果连接超时就停止
            self._start_connection_timeout_monitor()
            
            # 对于RTSP摄像头，返回True表示已启动连接过程
            # 真正的连接结果会在_on_camera_connected回调中处理
            return True
        else:
            # 使用本地摄像头
            try:
                print("正在初始化摄像头...")
                self.camera = CameraController(
                    camera_id=0,
                    width=self.main_window.camera_width,
                    height=self.main_window.camera_height
                )

                # 获取分辨率信息
                resolution = self.camera.get_resolution()
                print(f"✓ 摄像头已打开 (分辨率: {resolution[0]}x{resolution[1]})")

                # 启动检测流程
                self._start_detection_process()
                return True

            except Exception as e:
                print(f"❌ 摄像头打开失败: {e}")
                self.main_window.display_area.get_component('status_label').setText("状态: 摄像头打开失败")
                import traceback
                traceback.print_exc()
                return False

    def _on_camera_connected(self, camera, error_message):
        """RTSP摄像头连接完成回调"""
        # 停止连接超时监控
        if hasattr(self, 'connection_timer'):
            self.connection_timer.stop()
            
        if camera is None:
            print(f"❌ RTSP摄像头连接失败: {error_message}")
            self.main_window.display_area.get_component('status_label').setText("状态: RTSP连接失败")
            # 恢复启动按钮
            start_button = self.main_window.control_panel.get_component('start_button')
            start_button.setEnabled(True)
            return
            
        # 验证摄像头连接状态
        try:
            # 测试读取一帧以验证连接是否真正可用
            ret, frame = camera.read()
            if not ret or frame is None:
                print("❌ RTSP摄像头连接但无法读取数据")
                self.main_window.display_area.get_component('status_label').setText("状态: RTSP流不可用")
                camera.release()
                start_button = self.main_window.control_panel.get_component('start_button')
                start_button.setEnabled(True)
                return
        except Exception as e:
            print(f"❌ RTSP摄像头连接测试失败: {e}")
            self.main_window.display_area.get_component('status_label').setText("状态: RTSP连接异常")
            start_button = self.main_window.control_panel.get_component('start_button')
            start_button.setEnabled(True)
            return
            
        # 连接成功
        self.camera = camera
        resolution = self.camera.get_resolution()
        print(f"✓ RTSP摄像头已打开 (分辨率: {resolution[0]}x{resolution[1]})")
        
        # 启动检测流程
        self._start_detection_process()

    def _start_detection_process(self):
        """启动检测流程（摄像头已连接）"""
        # 确保摄像头已正确连接
        if self.camera is None or not self.camera.is_opened():
            print("❌ 错误: 摄像头未正确连接")
            self.main_window.display_area.get_component('status_label').setText("状态: 摄像头连接失败")
            self.stop_detection()
            return
            
        # 更新UI状态
        start_button = self.main_window.control_panel.get_component('start_button')
        stop_button = self.main_window.control_panel.get_component('stop_button')
        status_label = self.main_window.display_area.get_component('status_label')
        
        start_button.setEnabled(False)
        stop_button.setEnabled(True)
        status_label.setText("状态: 检测中...")
        
        # 创建定时器处理视频帧
        print("\n启动检测")
        print("=" * 50)
        print("✓ 系统启动成功，开始实时检测")
        print("=" * 50)
        print()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._process_frame)
        self.timer.start(30)  # 30ms间隔，约33FPS

    def stop_detection(self):
        """停止检测"""
        print("\n" + "=" * 50)
        print("【停止检测】")
        print("=" * 50)
        
        # 先停止定时器，防止再次调用_process_frame
        if self.timer:
            self.timer.stop()
            self.timer = None
            print("✓ 定时器已停止")
        
        # 释放摄像头
        if self.camera:
            self.camera.release()
            self.camera = None
            print("✓ 摄像头已释放")
        
        # 清空检测器引用
        self.detector = None
        if self.mediapipe_manager:
            self.mediapipe_manager.close()
        
        # 清空统计信息
        stats_text = self.main_window.display_area.get_component('stats_text')
        if stats_text:
            stats_text.setText("")
        
        print("✓ 检测已停止")
        print("=" * 50)

    def update_ui_state(self):
        """更新UI状态"""
        # 更新按钮状态
        start_button = self.main_window.control_panel.get_component('start_button')
        stop_button = self.main_window.control_panel.get_component('stop_button')
        
        start_button.setEnabled(True)
        stop_button.setEnabled(False)
        
        # 更新状态标签
        status_label = self.main_window.display_area.get_component('status_label')
        status_label.setText("状态: 已停止")
        
        # 清空显示
        video_label = self.main_window.display_area.get_component('video_label')
        video_label.setText("已停止")
        video_label.clear()

    def _start_connection_timeout_monitor(self):
        """启动连接超时监控"""
        # 设置连接超时时间为10秒
        self.connection_timeout_count = 0
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self._check_connection_timeout)
        self.connection_timer.start(1000)  # 每秒检查一次

    def _check_connection_timeout(self):
        """检查连接超时"""
        self.connection_timeout_count += 1
        
        # 如果超过10秒还没连接成功，认为连接超时
        if self.connection_timeout_count >= 10:
            print("❌ RTSP连接超时")
            self.connection_timer.stop()
            self.main_window.display_area.get_component('status_label').setText("状态: RTSP连接超时")
            
            # 恢复启动按钮
            start_button = self.main_window.control_panel.get_component('start_button')
            start_button.setEnabled(True)
            
            # 如果已经创建了定时器，停止它
            if hasattr(self, 'timer') and self.timer:
                self.timer.stop()
                
    def _process_frame(self):
        """处理视频帧（由定时器触发）"""
        try:
            # 注意：这个方法只在摄像头成功连接后才会被定时器调用
            # 调用检测处理器
            self.main_window.detection_handler.process_frame()
            
        except Exception as e:
            print(f"帧处理错误: {e}")
            import traceback
            traceback.print_exc()