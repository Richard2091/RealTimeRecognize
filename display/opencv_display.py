"""
OpenCV显示模块
提供实时显示和交互功能
集成MediaPipe姿态检测
"""
import cv2
import time
import numpy as np
from .button_manager import ButtonManager
from .pose_renderer import PoseRenderer


class OpenCVDisplay:
    """OpenCV显示控制器"""

    def __init__(self, window_name='YOLO Detection', show_skeleton=True):
        """
        初始化显示控制器

        Args:
            window_name: 窗口名称
            show_skeleton: 是否显示骨骼连接线
        """
        self.window_name = window_name
        self.show_skeleton = show_skeleton
        self.mirror_mode = True

        # 按钮配置（保留兼容性）
        self.button_height = 40
        self.button_width = 120
        self.button_margin = 10
        self.button_font = cv2.FONT_HERSHEY_SIMPLEX
        self.button_font_scale = 0.7
        self.button_font_thickness = 2
        
        # 按钮状态颜色（保留兼容性）
        self.button_color_active = (70, 130, 180)  # 钢蓝色
        self.button_color_inactive = (100, 100, 100)  # 灰色
        self.button_text_color = (255, 255, 255)  # 白色
        
        # 统计信息
        self.frame_count = 0
        self.start_time = None
        self.window_created = False
        
        # 按钮管理器
        self.button_manager = ButtonManager(self)
        self.buttons = self.button_manager.buttons
        
        # 姿态渲染器
        self.pose_renderer = PoseRenderer(show_skeleton)

    def start(self):
        """开始统计并创建窗口"""
        self.start_time = time.time()
        self.frame_count = 0
        if not self.window_created:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            self.window_created = True







    def process_frame(self, frame, detector, pose_detector=None, emotion_detector=None,
                      use_pose=False, use_emotion=False, verbose=True, zoom_level=1.0):
        """
        处理并显示帧

        Args:
            frame: 输入帧
            detector: YOLO检测器实例
            pose_detector: MediaPipe姿态检测器实例
            emotion_detector: 表情检测器实例
            use_pose: 是否使用姿态检测
            use_emotion: 是否显示表情
            verbose: 是否显示FPS等信息
            zoom_level: 缩放级别 (1.0 = 无缩放)

        Returns:
            frame: 处理后的帧
        """
        self.frame_count += 1
        
        # 初始化按钮（如果尚未初始化）
        if not self.buttons:
            height, width = frame.shape[:2]
            self.button_manager.setup_buttons(width, height, use_pose, use_emotion)
        
        # 更新按钮状态
        self.button_manager.update_button_states(use_pose, use_emotion)

        # 镜像处理
        if self.mirror_mode:
            frame = cv2.flip(frame, 1)

        # YOLO目标检测
        t0_detect = time.time()
        results = detector.detect(frame, verbose=False)
        t1_detect = time.time()

        fps = 1.0 / (t1_detect - t0_detect) if t1_detect > t0_detect else 0.0

        # 绘制YOLO检测结果（所有目标）
        for result in results:
            if result.boxes is not None:
                annotated_frame = result.plot()
                frame = annotated_frame

        # 对检测到的人进行姿态和表情检测
        if use_pose and pose_detector and results:
            for result in results:
                if result.boxes is not None:
                    boxes = result.boxes
                    for idx, box in enumerate(boxes):
                        # 只对类别为"人"（class_id=0）的目标进行姿态检测
                        if int(box.cls[0]) == 0:  # COCO数据集：0=person
                            # 获取检测框
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                            x1, y1 = max(0, x1), max(0, y1)
                            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

                            # 裁剪人体区域（扩大一点边界以包含完整身体）
                            margin = 50
                            x1_crop = max(0, x1 - margin)
                            y1_crop = max(0, y1 - margin)
                            x2_crop = min(frame.shape[1], x2 + margin)
                            y2_crop = min(frame.shape[0], y2 + margin)

                            person_img = frame[y1_crop:y2_crop, x1_crop:x2_crop]

                            if person_img.size > 0:
                                # 在裁剪区域内检测姿态
                                pose_results = pose_detector.detect(person_img)

                                if pose_results.pose_landmarks:
                                    # 使用姿态渲染器绘制姿态
                                    bbox = (x1_crop, y1_crop, x2_crop, y2_crop)
                                    self.pose_renderer.render_pose(frame, pose_results, bbox)

                                    # 表情检测（基于鼻子位置）
                                    if use_emotion and emotion_detector:
                                        # 鼻子是索引0，使用原图坐标
                                        landmarks = pose_results.pose_landmarks.landmark
                                        if len(landmarks) > 0:
                                            nose = landmarks[0]
                                            if nose.visibility > 0.5:
                                                # 计算在原图中的绝对坐标
                                                nose_x = int((nose.x * (x2_crop - x1_crop)) + x1_crop)
                                                nose_y = int((nose.y * (y2_crop - y1_crop)) + y1_crop)
                                                
                                                face_size = 80
                                                x1_face = int(max(0, nose_x - face_size))
                                                y1_face = int(max(0, nose_y - face_size))
                                                x2_face = int(min(frame.shape[1], nose_x + face_size))
                                                y2_face = int(min(frame.shape[0], nose_y + face_size * 1.2))

                                                emotion = emotion_detector.detect_emotion(frame, (x1_face, y1_face, x2_face, y2_face))

                                                cv2.rectangle(frame, (x1_face, y1_face), (x2_face, y2_face), (255, 0, 0), 2)

                                                label = f"Person: {emotion}"
                                                cv2.putText(frame, label, (x1_face, y1_face - 10),
                                                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # 添加信息
        if verbose:
            height, width = frame.shape[:2]
            
            # 左上角：FPS
            cv2.putText(frame, f"FPS: {fps:.1f}" if fps > 0 else "FPS: --", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # 左上角：其他状态信息
            mirror_status = "开" if self.mirror_mode else "关"
            cv2.putText(frame, f"镜像: {mirror_status}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            y_offset = 90
            if use_pose:
                skeleton_status = "骨骼连接" if self.show_skeleton else "仅关键点"
                cv2.putText(frame, f"骨骼: {skeleton_status}", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                y_offset += 30

            if use_emotion:
                emotion_status = "开" if use_emotion else "关"
                cv2.putText(frame, f"表情: {emotion_status}", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                y_offset += 30

            # 右上角：缩放信息
            zoom_text = f"缩放: {zoom_level:.1f}x"
            text_size = cv2.getTextSize(zoom_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            text_x = width - text_size[0] - 10
            text_y = 30
            
            # 缩放信息背景
            bg_margin = 5
            cv2.rectangle(frame, 
                         (text_x - bg_margin, text_y - text_size[1] - bg_margin),
                         (text_x + text_size[0] + bg_margin, text_y + bg_margin),
                         (0, 0, 0), -1)
            
            cv2.putText(frame, zoom_text, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        # 绘制按钮
        self.button_manager.draw_buttons(frame)

        return frame

    def show_frame(self, frame):
        """显示帧"""
        cv2.imshow(self.window_name, frame)

    def handle_key(self, key_code, use_pose=False, use_emotion=False):
        """
        处理按键

        Args:
            key_code: 按键代码
            use_pose: 是否启用姿态检测（外部传入，内部不修改）
            use_emotion: 是否启用表情检测（外部传入，内部不修改）

        Returns:
            (should_exit, show_skeleton, use_emotion_flag)
        """
        should_exit = False

        if key_code == ord('q'):
            should_exit = True
        elif key_code == ord('m'):
            self.mirror_mode = not self.mirror_mode
            print(f"镜像: {'开' if self.mirror_mode else '关'}")
        elif key_code == ord('s') and use_pose:
            self.show_skeleton = not self.show_skeleton
            mode = "骨骼连接" if self.show_skeleton else "仅关键点"
            print(f"切换到: {mode}模式")
        elif key_code == ord('e') and use_emotion:
            # 注意：这里返回的use_emotion_flag需要由外部处理
            pass

        return should_exit, self.show_skeleton, use_emotion

    def get_stats(self):
        """获取统计信息"""
        if self.start_time is None:
            return None

        elapsed_time = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0

        return {
            'elapsed_time': elapsed_time,
            'frame_count': self.frame_count,
            'avg_fps': avg_fps
        }

    def close(self):
        """关闭显示"""
        cv2.destroyAllWindows()
        self.window_created = False
