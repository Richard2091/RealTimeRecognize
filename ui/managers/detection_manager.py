"""
检测管理器
整合检测流程编排、帧处理、渲染等逻辑
"""
import cv2
import time
import psutil
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
        
        # 7. 立即更新标签页信息
        self._update_statistics()
        
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

            # 记录开始时间
            frame_start_time = time.time()

            # 创建可修改的副本
            processed_frame = frame.copy()
            results = []

            # 镜像处理
            if self.main_window.mirror_mode:
                processed_frame = cv2.flip(processed_frame, 1)

            # YOLO目标检测
            detection_time = 0
            if self.detector:
                try:
                    detection_start = time.time()
                    results = self.detector.detect(processed_frame, verbose=False)
                    detection_time = (time.time() - detection_start) * 1000  # 转换为毫秒

                    # 绘制YOLO检测结果
                    for result in results:
                        if result.boxes is not None:
                            annotated_frame = result.plot()
                            processed_frame = annotated_frame
                except Exception as e:
                    print(f"YOLO检测失败: {e}")

            # MediaPipe姿态检测
            pose_time = 0
            if self.main_window.use_pose and results:
                pose_start = time.time()
                self._process_pose_detection(processed_frame, results)
                pose_time = (time.time() - pose_start) * 1000

            # MediaPipe表情检测
            emotion_time = 0
            if self.main_window.use_emotion and results:
                emotion_start = time.time()
                self._process_emotion_detection(processed_frame, results)
                emotion_time = (time.time() - emotion_start) * 1000

            # MediaPipe手势识别（包含手部检测和渲染）
            gesture_time = 0
            if hasattr(self.main_window, 'use_gesture') and self.main_window.use_gesture:
                gesture_start = time.time()
                self._process_gesture_recognition(processed_frame)
                gesture_time = (time.time() - gesture_start) * 1000

            # 记录总处理时间
            total_processing_time = (time.time() - frame_start_time) * 1000

            # 更新统计信息（包含性能数据）
            self._update_statistics({
                'detection_time': round(detection_time, 2),
                'pose_time': round(pose_time, 2),
                'emotion_time': round(emotion_time, 2),
                'gesture_time': round(gesture_time, 2),
                'total_processing_time': round(total_processing_time, 2)
            })

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
        from PyQt5.QtCore import QSize
        scaled_pixmap = pixmap.scaled(
            QSize(video_label.size()),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        video_label.setPixmap(scaled_pixmap)

    def _update_statistics(self, performance_data=None):
        """更新统计信息"""
        # 获取摄像头统计信息
        stats = self.main_window.camera_manager.get_statistics()
        
        # 立即更新初始信息，然后按间隔更新
        if self.stats_update_counter == 0:
            # 首次更新：立即显示基本信息
            self._update_info_dict(stats, performance_data, is_initial=True)
        
        self.stats_update_counter += 1
        if self.stats_update_counter >= self.stats_update_interval:
            self.stats_update_counter = 0
            # 使用最新的摄像头统计信息更新
            self._update_info_dict(stats, performance_data)

    def _update_info_dict(self, stats, performance_data=None, is_initial=False):
        """构建并更新信息字典"""
        if not stats:
            # 即使没有摄像头统计信息，也更新基本信息
            stats = {}

        # 构建视频信息字典
        info_dict = {
            # 视频流信息（使用 get 方法提供默认值）
            'resolution': f"{stats.get('resolution', ['N/A', 'N/A'])[0]}x{stats.get('resolution', ['N/A', 'N/A'])[1]}" if stats.get('resolution') else 'N/A',
            'fps': f"{stats.get('real_time_fps', 0):.1f} / {stats.get('avg_fps', 0):.1f}" if stats.get('real_time_fps') else 'N/A',
            'frame_count': f"{stats.get('frame_count', 0):,}" if stats.get('frame_count') else '0',
            'running_time': f"{stats.get('running_time', 0):.1f} 秒" if stats.get('running_time') else 'N/A',
            'error_rate': f"{stats.get('error_rate', 0):.2f}" if stats.get('error_rate') else '0.00',

            # 性能数据（如果有）
            'processing_delay': f"{performance_data.get('total_processing_time', 0):.1f}" if performance_data else "N/A",
            'detection_time': f"{performance_data.get('detection_time', 0):.1f}" if performance_data else "N/A",
            'render_time': "N/A",  # 渲染时间可以后续添加
            'total_time': f"{performance_data.get('total_processing_time', 0):.1f}" if performance_data else "N/A",
            'throughput': f"{1000/max(performance_data.get('total_processing_time', 1), 1):.1f}" if performance_data else "N/A",

            # 检测信息
            'model_name': self.main_window.selected_model or 'N/A',
            'detection_objects': 'N/A',  # 可以在检测时统计
            'confidence': 'N/A',  # 可以在检测时计算平均置信度
            'pose_enabled': '是' if self.main_window.use_pose else '否',
            'emotion_enabled': '是' if self.main_window.use_emotion else '否',
            'gesture_enabled': '是' if getattr(self.main_window, 'use_gesture', False) else '否',

            # 资源使用
            'memory_usage': f"{psutil.Process().memory_info().rss / 1024 / 1024:.1f}",
            'cpu_usage': f"{psutil.cpu_percent(interval=0.1):.1f}",
            'gpu_usage': 'N/A',  # 需要额外的库来获取GPU使用率
        }

        # 如果是首次更新，添加初始化状态信息
        if is_initial:
            info_dict['status'] = '检测已启动'
            info_dict['initial_info'] = '系统正在初始化，请稍候...'

        # 添加检测器性能细分（如果有）
        if performance_data:
            detection_breakdown = []
            if performance_data.get('detection_time', 0) > 0:
                detection_breakdown.append(f"目标检测: {performance_data['detection_time']:.1f}ms")
            if performance_data.get('pose_time', 0) > 0:
                detection_breakdown.append(f"姿态检测: {performance_data['pose_time']:.1f}ms")
            if performance_data.get('emotion_time', 0) > 0:
                detection_breakdown.append(f"表情检测: {performance_data['emotion_time']:.1f}ms")
            if performance_data.get('gesture_time', 0) > 0:
                detection_breakdown.append(f"手势检测: {performance_data['gesture_time']:.1f}ms")

            if detection_breakdown:
                info_dict['detection_breakdown'] = ' | '.join(detection_breakdown)

        # 添加RTSP特有信息
        if 'rtsp_url' in stats:
            info_dict.update({
                'rtsp_url': stats['rtsp_url'],
                'connection_stability': f"{stats['connection_stability']}%",
                'data_rate_mbps': f"{stats['data_rate_mbps']}",
                'reconnection_count': f"{stats['reconnection_count']}"
            })
            # 显示RTSP标签
            self.main_window.bottom_info_area.set_rtsp_visible(True)
        else:
            # 隐藏RTSP标签
            self.main_window.bottom_info_area.set_rtsp_visible(False)

        # 更新UI显示
        self.main_window.bottom_info_area.update_video_info(info_dict)

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
