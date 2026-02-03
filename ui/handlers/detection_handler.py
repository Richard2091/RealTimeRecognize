"""
检测处理模块
处理视频帧检测和渲染逻辑
"""
import cv2
from PyQt5.QtCore import Qt
from core.detectors.mediapipe.mediapipe_manager import MediaPipeManager


class DetectionHandler:
    """检测处理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.mediapipe_manager = MediaPipeManager()
        self.detector = None
        self.stats_update_counter = 0
        self.stats_update_interval = 30  # 每30帧更新一次统计信息
        
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
            
            model_name = model_info['name']
            model_path = model_info['file']
            
            # 根据模型类型创建检测器
            if 'yolov8' in model_name:
                from detectors.yolo8_detector import YOLOv8Detector
                print("正在加载YOLOv8检测器...")
                self.detector = YOLOv8Detector(model_path)
            elif 'yolo26' in model_name:
                from detectors.yolo26_detector import YOLO26Detector
                print("正在加载YOLO26检测器...")
                self.detector = YOLO26Detector(model_path)
            elif 'world' in model_name:
                from detectors.yolo_world_detector import YOWorldDetector
                print("正在加载YOLO-World检测器...")
                self.detector = YOWorldDetector(model_path)
            else:
                print(f"❌ 错误: 不支持的模型类型: {model_name}")
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
            
            # 加载MediaPipe检测器
            if self.main_window.use_pose:
                print("\n加载MediaPipe检测器")
                print("-" * 30)
                print("正在加载MediaPipe姿态检测器...")
                self.mediapipe_manager.initialize_detectors(
                    use_pose=self.main_window.use_pose,
                    use_emotion=self.main_window.use_emotion
                )
                print("✓ MediaPipe检测器加载成功")
            
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
            
            # MediaPipe姿态和表情检测
            if self.main_window.use_pose and results:
                self._process_pose_and_emotion(processed_frame, results)
            
            # 镜像处理
            if self.main_window.mirror_mode:
                processed_frame = cv2.flip(processed_frame, 1)
            
            # 更新统计信息
            self._update_statistics()
            
            # 更新显示
            self._update_frame_display(processed_frame)
            
        except Exception as e:
            print(f"帧处理错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _process_pose_and_emotion(self, frame, results):
        """处理姿态和表情检测"""
        self.mediapipe_manager.set_skeleton_visibility(self.main_window.show_skeleton)
        
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
                            # 姿态检测
                            pose_results = self.mediapipe_manager.detect_pose(person_img)
                            
                            # 渲染姿态
                            bbox = (x1_crop, y1_crop, x2_crop, y2_crop)
                            self.mediapipe_manager.render_pose(frame, pose_results, bbox)
    
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
            
            stats = self.main_window.camera_handler.get_statistics()
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
    
    def _process_pose_and_emotion(self, frame, results):
        """处理姿态和表情检测"""
        self.mediapipe_manager.set_skeleton_visibility(self.main_window.show_skeleton)
        
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
                            # 姿态检测
                            pose_results = self.mediapipe_manager.detect_pose(person_img)
                            
                            # 渲染姿态
                            bbox = (x1_crop, y1_crop, x2_crop, y2_crop)
                            self.mediapipe_manager.render_pose(frame, pose_results, bbox)
                            
                            # 表情检测
                            if self.main_window.use_emotion:
                                self._process_emotion_detection(
                                    frame, pose_results, bbox
                                )

    def _process_emotion_detection(self, frame, pose_results, bbox):
        """处理表情检测"""
        # print("执行表情检测...", end='\r')  # 注释掉持续输出

        # 基于鼻子位置检测表情
        if pose_results and pose_results.pose_landmarks:
            landmarks = pose_results.pose_landmarks.landmark
            if len(landmarks) > 0:
                nose = landmarks[0]
                if nose.visibility > 0.5:
                    # 计算在原图中的绝对坐标
                    x1_crop, y1_crop, x2_crop, y2_crop = bbox
                    nose_x = int((nose.x * (x2_crop - x1_crop)) + x1_crop)
                    nose_y = int((nose.y * (y2_crop - y1_crop)) + y1_crop)
                    
                    face_size = 80
                    x1_face = int(max(0, nose_x - face_size))
                    y1_face = int(max(0, nose_y - face_size))
                    x2_face = int(min(frame.shape[1], nose_x + face_size))
                    y2_face = int(min(frame.shape[0], nose_y + face_size * 1.2))
                    
                    emotion = self.mediapipe_manager.detect_emotion(
                        frame, (x1_face, y1_face, x2_face, y2_face)
                    )
                    
                    self.mediapipe_manager.render_emotion(
                        frame, emotion, (x1_face, y1_face, x2_face, y2_face)
                    )