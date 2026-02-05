"""
检测管理器
整合检测流程编排、帧处理、渲染等逻辑
"""
import cv2
from PyQt5.QtCore import Qt, QObject
from ui.managers.config_file_manager import config_manager
from core.detectors.mediapipe.detector import MediaPipeDetector
from core.detectors.mediapipe.renderer import MediaPipeRenderer
from utils.logger_suppressor import suppress_stderr_context


class DetectionManager(QObject):
    """检测管理器 - 整合检测流程、帧处理和渲染"""

    def __init__(self, main_window):
        """
        初始化检测管理器

        Args:
            main_window: 主窗口实例
        """
        super().__init__()
        self.main_window = main_window

        # 检测器
        self.detector = None
        self.mediapipe_pose_detector = None
        self.mediapipe_emotion_detector = None
        self.mediapipe_gesture_detector = None
        self.mediapipe_renderer = MediaPipeRenderer()

        # 统计信息
        self.stats_update_counter = 0
        self.stats_update_interval = 30  # 每30帧更新一次统计信息

    def start_detection(self):
        """启动检测流程"""
        print("=" * 50)
        print("启动检测")
        print("=" * 50)

        # 1. 获取模型配置
        model_combo = self.main_window.control_panel.get_component('model_combo')
        model_key = model_combo.currentData()

        if not model_key:
            print("❌ 错误: 未选择模型")
            status_label = self.main_window.display_area.get_component('status_label')
            status_label.setText("状态: 请选择模型")
            return

        print(f"✓ 选择的模型: {model_key}")

        # 2. 获取模型信息
        config = config_manager.load_config()
        models = config.get('models', {})
        model_info = models.get(model_key)
        if not model_info:
            print(f"❌ 错误: 模型信息不存在: {model_key}")
            status_label = self.main_window.display_area.get_component('status_label')
            status_label.setText("状态: 模型加载失败")
            return

        print(f"✓ 模型路径: {model_info['file']}")
        print(f"✓ 模型描述: {model_info['display']}")

        # 3. 加载检测器
        if not self.load_detector(model_info):
            return

        # 4. 初始化摄像头
        camera_config = self.get_camera_config()
        if not self.main_window.camera_manager.initialize_camera(camera_config):
            status_label = self.main_window.display_area.get_component('status_label')
            status_label.setText("状态: 摄像头初始化失败")
            return

        # 5. 打开摄像头
        if not self.main_window.camera_manager.start_camera():
            status_label = self.main_window.display_area.get_component('status_label')
            status_label.setText("状态: 摄像头打开失败")
            return

        # 6. 更新UI状态
        self.main_window.update_detection_ui(True)
        print("=" * 50)
        print("✓ 检测已启动")
        print("=" * 50)

    def stop_detection(self):
        """停止检测流程"""
        print("\n" + "=" * 50)
        print("【停止检测】")
        print("=" * 50)

        # 停止摄像头
        self.main_window.camera_manager.stop_camera()

        # 更新UI状态
        self.main_window.update_detection_ui(False)

        # 清空显示
        video_label = self.main_window.display_area.get_component('video_label')
        video_label.setText("等待启动...")
        video_label.clear()

        print("✓ 检测已停止")
        print("=" * 50)

    def load_detector(self, model_info: dict) -> bool:
        """
        加载检测器

        Args:
            model_info: 模型信息

        Returns:
            是否成功
        """
        try:
            print("\n加载检测模型")
            print("-" * 30)

            model_type = model_info['type']
            model_path = model_info['file']

            # 根据模型类型创建检测器
            if 'YOLOv8' in model_type:
                from core.detectors.yolo.yolo8 import YOLOv8Detector
                print("正在加载YOLOv8检测器...")
                self.detector = YOLOv8Detector(model_path)
            elif 'YOLO26' in model_type:
                from core.detectors.yolo.yolo26 import YOLO26Detector
                print("正在加载YOLO26检测器...")
                self.detector = YOLO26Detector(model_path)
            elif 'YOLO-World' in model_type:
                from core.detectors.yolo.yolo_world import YOWorldDetector
                print("正在加载YOLO-World检测器...")
                self.detector = YOWorldDetector(model_path)
            else:
                print(f"❌ 错误: 不支持的模型类型: {model_type}")
                return False

            print("✓ 模型加载成功")

            # 检查MediaPipe依赖
            if self.main_window.use_pose or self.main_window.use_emotion:
                print("\n检查依赖")
                print("-" * 30)
                try:
                    import mediapipe as mp
                    print("✓ MediaPipe已安装")
                except ImportError:
                    print("❌ MediaPipe未安装，无法使用姿态和表情检测")
                    return False

            # 加载MediaPipe检测器（抑制 C++ 日志输出）
            if self.main_window.use_pose:
                print("\n加载MediaPipe检测器")
                print("-" * 30)
                print("正在加载MediaPipe姿态检测器...")
                with suppress_stderr_context():
                    self.mediapipe_pose_detector = MediaPipeDetector(detection_type="pose")
                print("✓ MediaPipe姿态检测器加载成功")

            if self.main_window.use_emotion:
                print("正在加载MediaPipe表情检测器...")
                with suppress_stderr_context():
                    self.mediapipe_emotion_detector = MediaPipeDetector(detection_type="face")
                print("✓ MediaPipe表情检测器加载成功")

            if hasattr(self.main_window, 'use_gesture') and self.main_window.use_gesture:
                print("正在加载MediaPipe手势识别器...")
                with suppress_stderr_context():
                    self.mediapipe_gesture_detector = MediaPipeDetector(detection_type="gesture")
                print("✓ MediaPipe手势识别器加载成功（包含手部检测功能）")

            return True

        except Exception as e:
            print(f"❌ 检测器加载失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_frame(self, frame):
        """处理视频帧"""
        try:
            if frame is None:
                return

            # 创建可修改的副本
            processed_frame = frame.copy()
            results = []

            # 镜像处理
            if self.main_window.mirror_mode:
                processed_frame = cv2.flip(processed_frame, 1)

            # YOLO目标检测
            if self.detector:
                try:
                    results = self.detector.detect(processed_frame, verbose=False)

                    # 绘制YOLO检测结果
                    for result in results:
                        if result.boxes is not None:
                            annotated_frame = result.plot()
                            processed_frame = annotated_frame
                except Exception as e:
                    print(f"YOLO检测失败: {e}")

            # MediaPipe姿态检测
            if self.main_window.use_pose and results:
                self._process_pose_detection(processed_frame, results)

            # MediaPipe表情检测
            if self.main_window.use_emotion and results:
                self._process_emotion_detection(processed_frame, results)

            # MediaPipe手势识别（包含手部检测和渲染）
            if hasattr(self.main_window, 'use_gesture') and self.main_window.use_gesture:
                self._process_gesture_recognition(processed_frame)

            # 更新统计信息
            self._update_statistics()

            # 更新显示
            self._update_frame_display(processed_frame)

        except Exception as e:
            print(f"帧处理错误: {e}")
            import traceback
            traceback.print_exc()

    def _update_frame_display(self, frame):
        """更新显示帧"""
        # 转换BGR到RGB
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w

        from PyQt5.QtGui import QImage, QPixmap
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        # 缩放以适应标签
        video_label = self.main_window.display_area.get_component('video_label')
        scaled_pixmap = pixmap.scaled(
            video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        video_label.setPixmap(scaled_pixmap)

    def _update_statistics(self):
        """更新统计信息"""
        self.stats_update_counter += 1
        if self.stats_update_counter >= self.stats_update_interval:
            self.stats_update_counter = 0

            stats = self.main_window.camera_manager.get_statistics()
            if not stats:
                return

            # 格式化统计信息文本
            stats_text = f"""=== 视频流统计信息 ===
分辨率: {stats['resolution'][0]}x{stats['resolution'][1]}
总帧数: {stats['frame_count']}
平均FPS: {stats['avg_fps']}
实时FPS: {stats['real_time_fps']}
运行时间: {stats['running_time']}秒
错误率: {stats['error_rate']}%
"""

            # 添加RTSP特有信息
            if 'rtsp_url' in stats:
                stats_text += f"""
=== RTSP连接信息 ===
RTSP地址: {stats['rtsp_url']}
连接稳定性: {stats['connection_stability']}%
数据速率: {stats['data_rate_mbps']} Mbps
重连次数: {stats['reconnection_count']}
"""

            # 更新UI显示
            info_text = self.main_window.bottom_info_area.get_component('info_text')
            if info_text:
                info_text.setText(stats_text)

    def _process_pose_detection(self, frame, results):
        """处理姿态检测"""
        for result in results:
            if result.boxes is not None:
                boxes = result.boxes
                for idx, box in enumerate(boxes):
                    # 只对类别为"人"（class_id=0）的目标进行姿态检测
                    if int(box.cls[0]) == 0:
                        # 获取检测框
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

                        # 裁剪人体区域
                        margin = 50
                        x1_crop = max(0, x1 - margin)
                        y1_crop = max(0, y1 - margin)
                        x2_crop = min(frame.shape[1], x2 + margin)
                        y2_crop = min(frame.shape[0], y2 + margin)

                        person_img = frame[y1_crop:y2_crop, x1_crop:x2_crop]

                        if person_img.size > 0:
                            bbox = (x1_crop, y1_crop, x2_crop, y2_crop)

                            # 姿态检测
                            if self.mediapipe_pose_detector:
                                pose_results = self.mediapipe_pose_detector.detect_pose(person_img)

                                # 渲染姿态
                                self.mediapipe_renderer.render_pose(frame, pose_results, bbox)

    def _process_emotion_detection(self, frame, results):
        """处理表情检测"""
        for result in results:
            if result.boxes is not None:
                boxes = result.boxes
                for idx, box in enumerate(boxes):
                    # 只对类别为"人"（class_id=0）的目标进行表情检测
                    if int(box.cls[0]) == 0:
                        # 获取检测框
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

                        # 裁剪人体区域
                        margin = 50
                        x1_crop = max(0, x1 - margin)
                        y1_crop = max(0, y1 - margin)
                        x2_crop = min(frame.shape[1], x2 + margin)
                        y2_crop = min(frame.shape[0], y2 + margin)

                        person_img = frame[y1_crop:y2_crop, x1_crop:x2_crop]

                        if person_img.size > 0:
                            bbox = (x1_crop, y1_crop, x2_crop, y2_crop)

                            # 表情检测（使用独立的表情检测器）
                            if self.mediapipe_emotion_detector:
                                emotion_results = self.mediapipe_emotion_detector.detect(person_img)

                                # 渲染表情
                                if emotion_results.face_landmarks:
                                    # 计算面部边界框
                                    landmarks = emotion_results.face_landmarks[0]
                                    xs = [lm.x * (x2_crop - x1_crop) + x1_crop for lm in landmarks]
                                    ys = [lm.y * (y2_crop - y1_crop) + y1_crop for lm in landmarks]
                                    face_bbox = (int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys)))

                                    # 分析表情
                                    emotion = self.mediapipe_emotion_detector._analyze_emotion(landmarks)

                                    # 渲染表情
                                    self.mediapipe_renderer.render_emotion(frame, emotion, face_bbox)

    def _process_gesture_recognition(self, frame):
        """
        处理手势识别
        根据官方文档，GestureRecognizer 返回包含 hand_landmarks 和 gestures 的完整结果
        参考: https://github.com/google-ai-edge/mediapipe-samples/blob/main/examples/gesture_recognizer/python/gesture_recognizer.ipynb
        """
        if self.mediapipe_gesture_detector:
            try:
                # 使用 recognize_gesture 方法，返回完整的结果对象（包含手势、手部关键点、手部类型）
                gesture_results = self.mediapipe_gesture_detector.recognize_gesture(frame)

                # 渲染手势识别结果（包括手部关键点和连接线）
                if gesture_results and gesture_results.hand_landmarks:
                    self.mediapipe_renderer.render_gesture(frame, gesture_results)
            except Exception as e:
                print(f"手势识别失败: {e}")

    def get_camera_config(self) -> dict:
        """获取摄像头配置"""
        control_panel = self.main_window.control_panel
        camera_source_combo = control_panel.get_component('camera_source_combo')
        local_camera_combo = control_panel.get_component('local_camera_combo')
        rtsp_url_input = control_panel.get_component('rtsp_url_input')

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
