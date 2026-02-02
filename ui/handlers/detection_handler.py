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
        self.stats_update_counter = 0
        self.stats_update_interval = 30  # 每30帧更新一次统计信息
        
    def process_frame(self):
        """处理视频帧"""
        try:
            # 注意：这个方法只在摄像头成功连接后才会被调用
            camera_handler = self.main_window.camera_handler
            
            # 安全检查：确保摄像头对象存在
            if camera_handler.camera is None:
                return
            
            # 读取帧
            ret, frame = camera_handler.camera.read()
            if not ret:
                print("无法读取视频帧")
                self.main_window.display_area.get_component('status_label').setText("状态: 视频读取错误")
                self.main_window.camera_handler.stop_detection()
                camera_handler.update_ui_state()
                return
            
            # YOLO目标检测（带错误处理）
            try:
                print("执行YOLO检测...", end='\r')
                results = camera_handler.detector.detect(frame, verbose=False)
                
                # 绘制YOLO检测结果
                for result in results:
                    if result.boxes is not None:
                        annotated_frame = result.plot()
                        frame = annotated_frame
            except Exception as e:
                print(f"❌ YOLO检测失败: {e}")
                # 在图像上显示错误信息
                cv2.putText(frame, "YOLO检测失败", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                results = []
            
            # 姿态和表情检测
            if (self.main_window.use_pose and 
                self.mediapipe_manager.pose_detector and 
                self.mediapipe_manager.emotion_detector and results):
                self._process_pose_and_emotion(frame, results)
            
            # 镜像处理
            if self.main_window.mirror_mode:
                frame = cv2.flip(frame, 1)
            
            # 显示帧
            self._update_frame_display(frame)
            
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
                            
                            # 表情检测
                            if self.main_window.use_emotion:
                                self._process_emotion_detection(
                                    frame, pose_results, bbox
                                )

    def _process_emotion_detection(self, frame, pose_results, bbox):
        """处理表情检测"""
        print("执行表情检测...", end='\r')
        
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
        
        # 更新统计信息
        self.stats_update_counter += 1
        if self.stats_update_counter >= self.stats_update_interval:
            self.stats_update_counter = 0
            self._update_statistics()
    
    def _update_statistics(self):
        """更新统计信息显示"""
        camera_handler = self.main_window.camera_handler
        if not camera_handler.camera:
            return
        
        # 获取统计信息
        stats = camera_handler.camera.get_statistics()
        if not stats:
            return
        
        # 格式化统计信息文本
        stats_text = f"""=== 视频流统计信息 ===
分辨率: {stats['resolution'][0]}x{stats['resolution'][1]}
总帧数: {stats['frame_count']}
平均FPS: {stats['avg_fps']}
实时FPS: {stats['real_time_fps']}
延迟: {stats['latency_ms']}ms
运行时间: {stats['running_time_seconds']}秒
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
        stats_text_edit = self.main_window.display_area.get_component('stats_text')
        if stats_text_edit:
            stats_text_edit.setText(stats_text)