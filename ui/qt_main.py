"""
QT主窗口
使用PyQt5实现图形化用户界面
"""
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QCheckBox, QGroupBox, QFrame, QSlider)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from utils.config import Config


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO实时检测系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 检测器实例
        self.detector = None
        self.pose_detector = None
        self.emotion_detector = None
        
        # 配置
        self.selected_model = None
        self.use_pose = False
        self.use_emotion = False
        self.mirror_mode = True
        
        # 摄像头
        self.camera = None
        self.timer = None
        
        # 初始化UI
        self._init_ui()
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建主部件和布局
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # 左侧控制面板
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel, 1)
        
        # 右侧显示区域
        display_area = self._create_display_area()
        main_layout.addWidget(display_area, 3)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def _create_control_panel(self):
        """创建控制面板"""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout()
        
        # 模型选择
        model_group = self._create_model_selector()
        layout.addWidget(model_group)
        
        # 功能选择
        feature_group = self._create_feature_selector()
        layout.addWidget(feature_group)
        
        # 显示设置
        display_group = self._create_display_settings()
        layout.addWidget(display_group)
        
        # 控制按钮
        control_group = self._create_control_buttons()
        layout.addWidget(control_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
    
    def _create_model_selector(self):
        """创建模型选择器"""
        group = QGroupBox("模型选择")
        layout = QVBoxLayout()
        
        # 模型下拉框
        self.model_combo = QComboBox()
        for key, model_info in Config.ALL_MODELS.items():
            self.model_combo.addItem(model_info['display'], key)
        layout.addWidget(self.model_combo)
        
        group.setLayout(layout)
        return group
    
    def _create_feature_selector(self):
        """创建功能选择器"""
        group = QGroupBox("检测功能")
        layout = QVBoxLayout()
        
        # 姿态检测
        self.pose_checkbox = QCheckBox("姿态检测")
        self.pose_checkbox.toggled.connect(self._on_pose_toggled)
        layout.addWidget(self.pose_checkbox)
        
        # 表情检测
        self.emotion_checkbox = QCheckBox("表情检测")
        self.emotion_checkbox.setEnabled(False)
        self.emotion_checkbox.toggled.connect(self._on_emotion_toggled)
        layout.addWidget(self.emotion_checkbox)
        
        group.setLayout(layout)
        return group
    
    def _create_display_settings(self):
        """创建显示设置"""
        group = QGroupBox("显示设置")
        layout = QVBoxLayout()
        
        # 镜像模式
        self.mirror_checkbox = QCheckBox("镜像模式")
        self.mirror_checkbox.setChecked(True)
        self.mirror_checkbox.toggled.connect(self._on_mirror_toggled)
        layout.addWidget(self.mirror_checkbox)
        
        # 骨骼显示
        self.skeleton_checkbox = QCheckBox("显示骨骼连接")
        self.skeleton_checkbox.setChecked(True)
        self.skeleton_checkbox.setEnabled(False)
        layout.addWidget(self.skeleton_checkbox)
        
        group.setLayout(layout)
        return group
    
    def _create_control_buttons(self):
        """创建控制按钮"""
        group = QGroupBox("控制")
        layout = QVBoxLayout()
        
        # 启动按钮
        self.start_button = QPushButton("启动检测")
        self.start_button.clicked.connect(self._start_detection)
        layout.addWidget(self.start_button)
        
        # 停止按钮
        self.stop_button = QPushButton("停止检测")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._stop_detection)
        layout.addWidget(self.stop_button)
        
        # 退出按钮
        exit_button = QPushButton("退出")
        exit_button.clicked.connect(self.close)
        layout.addWidget(exit_button)
        
        group.setLayout(layout)
        return group
    
    def _create_display_area(self):
        """创建显示区域"""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout()
        
        # 视频显示标签
        self.video_label = QLabel("等待启动...")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(800, 600)
        layout.addWidget(self.video_label)
        
        # 状态标签
        self.status_label = QLabel("状态: 就绪")
        layout.addWidget(self.status_label)
        
        frame.setLayout(layout)
        return frame
    
    def _on_pose_toggled(self, checked):
        """姿态检测切换"""
        self.skeleton_checkbox.setEnabled(checked)
        self.emotion_checkbox.setEnabled(checked)
    
    def _on_emotion_toggled(self, checked):
        """表情检测切换"""
        pass
    
    def _on_mirror_toggled(self, checked):
        """镜像模式切换"""
        self.mirror_mode = checked
    
    def _start_detection(self):
        """启动检测"""
        print("=" * 50)
        print("【步骤1】获取配置信息")
        print("=" * 50)
        
        # 获取选择的模型
        model_key = self.model_combo.currentData()
        if not model_key:
            print("❌ 错误: 未选择模型")
            self.status_label.setText("状态: 请选择模型")
            return
        
        print(f"✓ 选择的模型: {model_key}")
        
        # 获取模型信息
        from utils.config import Config
        model_info = Config.ALL_MODELS.get(model_key)
        if not model_info:
            print(f"❌ 错误: 模型信息不存在: {model_key}")
            self.status_label.setText("状态: 模型加载失败")
            return
        
        model_path = model_info['file']
        print(f"✓ 模型路径: {model_path}")
        print(f"✓ 模型描述: {model_info['display']}")
        
        # 获取功能选择
        self.use_pose = self.pose_checkbox.isChecked()
        self.use_emotion = self.emotion_checkbox.isChecked()
        print(f"✓ 姿态检测: {'是' if self.use_pose else '否'}")
        print(f"✓ 表情检测: {'是' if self.use_emotion else '否'}")
        print(f"✓ 镜像模式: {'是' if self.mirror_mode else '否'}")
        
        # 检查MediaPipe
        print("\n【步骤2】检查依赖")
        print("-" * 30)
        if self.use_pose or self.use_emotion:
            try:
                import mediapipe as mp
                print("✓ MediaPipe已安装")
            except ImportError:
                print("❌ MediaPipe未安装，无法使用姿态和表情检测")
                self.status_label.setText("状态: 缺少MediaPipe依赖")
                return
        
        # 加载YOLO模型
        print("\n【步骤3】加载检测模型")
        print("-" * 30)
        try:
            from core.detectors import YOLOv8Detector, YOLO26Detector, YOWorldDetector

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
                self.status_label.setText("状态: 不支持的模型")
                return
            
            print("✓ 模型加载成功")
            
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            self.status_label.setText(f"状态: 模型加载失败")
            import traceback
            traceback.print_exc()
            return
        
        # 加载姿态检测器
        if self.use_pose:
            print("\n【步骤4】加载姿态检测器")
            print("-" * 30)
            try:
                from core.detectors import PoseDetector
                print("正在加载MediaPipe姿态检测器...")
                self.pose_detector = PoseDetector()
                print("✓ 姿态检测器加载成功")
            except Exception as e:
                print(f"❌ 姿态检测器加载失败: {e}")
                self.status_label.setText("状态: 姿态检测器加载失败")
                import traceback
                traceback.print_exc()
                return
        
        # 加载表情检测器
        if self.use_emotion:
            print("\n【步骤5】加载表情检测器")
            print("-" * 30)
            try:
                from core.detectors import EmotionDetector
                print("正在加载MediaPipe表情检测器...")
                self.emotion_detector = EmotionDetector()
                print("✓ 表情检测器加载成功")
            except Exception as e:
                print(f"❌ 表情检测器加载失败: {e}")
                self.status_label.setText("状态: 表情检测器加载失败")
                import traceback
                traceback.print_exc()
                return
        
        # 打开摄像头
        print("\n【步骤6】打开摄像头")
        print("-" * 30)
        try:
            from camera.camera_controller import CameraController
            print("正在初始化摄像头...")
            self.camera = CameraController(camera_id=0)
            
            # 检查摄像头是否成功打开
            ret, frame = self.camera.read()
            if not ret:
                print("❌ 错误: 无法从摄像头读取帧")
                self.status_label.setText("状态: 摄像头错误")
                return
            
            height, width = frame.shape[:2]
            print(f"✓ 摄像头已打开 (分辨率: {width}x{height})")
            
        except Exception as e:
            print(f"❌ 摄像头打开失败: {e}")
            self.status_label.setText("状态: 摄像头打开失败")
            import traceback
            traceback.print_exc()
            return
        
        # 更新UI状态
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("状态: 检测中...")
        
        # 创建定时器处理视频帧
        print("\n【步骤7】启动检测")
        print("=" * 50)
        print("✓ 系统启动成功，开始实时检测")
        print("=" * 50)
        print()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._process_frame)
        self.timer.start(30)  # 30ms间隔，约33FPS
    
    def _process_frame(self):
        """处理视频帧"""
        try:
            # 读取帧
            ret, frame = self.camera.read()
            if not ret:
                print("❌ 无法读取视频帧")
                self.status_label.setText("状态: 视频读取错误")
                self._stop_detection()
                return
            
            # YOLO目标检测
            print("🔍 执行YOLO检测...", end='\r')
            results = self.detector.detect(frame, verbose=False)
            
            # 绘制YOLO检测结果
            for result in results:
                if result.boxes is not None:
                    annotated_frame = result.plot()
                    frame = annotated_frame
            
            # 姿态和表情检测
            if self.use_pose and self.pose_detector and results:
                print("🤸 执行姿态检测...", end='\r')
                
                from core.display import PoseRenderer
                pose_renderer = PoseRenderer(show_skeleton=self.skeleton_checkbox.isChecked())
                
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
                                    pose_results = self.pose_detector.detect(person_img)
                                    
                                    # 渲染姿态
                                    bbox = (x1_crop, y1_crop, x2_crop, y2_crop)
                                    pose_renderer.render_pose(frame, pose_results, bbox)
                                    
                                    # 表情检测
                                    if self.use_emotion and self.emotion_detector:
                                        print("😊 执行表情检测...", end='\r')
                                        
                                        from core.display import EmotionRenderer
                                        emotion_renderer = EmotionRenderer()
                                        
                                        # 基于鼻子位置检测表情
                                        if pose_results.pose_landmarks:
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
                                                    
                                                    emotion = self.emotion_detector.detect_emotion(
                                                        frame, (x1_face, y1_face, x2_face, y2_face)
                                                    )
                                                    
                                                    emotion_renderer.render_emotion(
                                                        frame, emotion, (x1_face, y1_face, x2_face, y2_face)
                                                    )
            
            # 镜像处理
            if self.mirror_mode:
                frame = cv2.flip(frame, 1)
            
            # 显示帧
            self.update_frame(frame)
            
            # 输出处理信息（避免频繁输出）
            # print("✓ 帧处理完成", end='\r')
            
        except Exception as e:
            print(f"❌ 帧处理错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _stop_detection(self):
        """停止检测"""
        print("\n" + "=" * 50)
        print("【停止检测】")
        print("=" * 50)
        
        # 停止定时器
        if self.timer:
            self.timer.stop()
            print("✓ 定时器已停止")
        
        # 释放摄像头
        if self.camera:
            self.camera.release()
            print("✓ 摄像头已释放")
        
        # 清空显示
        self.video_label.setText("已停止")
        self.video_label.clear()
        
        # 更新UI状态
        self.status_label.setText("状态: 已停止")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # 清空检测器引用
        self.detector = None
        self.pose_detector = None
        self.emotion_detector = None
        self.camera = None
        self.timer = None
        
        print("✓ 检测已停止")
        print("=" * 50)
    
    def update_frame(self, frame):
        """更新显示帧"""
        # 转换BGR到RGB
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        # 缩放以适应标签
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        self.video_label.setPixmap(scaled_pixmap)
    
    def closeEvent(self, event):
        """关闭事件"""
        self._stop_detection()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()