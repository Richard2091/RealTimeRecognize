"""
YOLO实时检测系统 - QT版本
使用重构后的架构和PyQt5实现
"""
import sys
import cv2
from pathlib import Path

# 导入核心模块
from core.detectors import YOLOv8Detector, YOLO26Detector, YOWorldDetector
from core.detectors import PoseDetector, EmotionDetector
from core.pipeline import DetectionPipeline
from core.display import PoseRenderer, EmotionRenderer, YOLORenderer

# 导入QT界面
from ui.qt_main import MainWindow, main as qt_main
from utils.config import Config

# 导入旧模块（用于兼容）
from camera.camera_controller import CameraController


def check_mediapipe():
    """检查MediaPipe是否可用"""
    try:
        import mediapipe as mp
        print("✓ MediaPipe已安装")
        return True
    except ImportError:
        print("✗ MediaPipe未安装")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("YOLO实时检测系统 - QT版本")
    print("=" * 50)
    
    # 检查MediaPipe
    MEDIAPIPE_AVAILABLE = check_mediapipe()
    
    # 启动QT界面
    print("启动图形化界面...")
    qt_main()


if __name__ == "__main__":
    main()