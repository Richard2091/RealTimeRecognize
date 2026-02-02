"""
YOLO实时检测系统 - QT版本
使用重构后的架构和PyQt5实现
"""

import os
# 设置OpenCV日志级别，抑制不必要的警告
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
os.environ['OPENCV_FFMPEG_LOG_LEVEL'] = 'ERROR'

# 导入QT界面
from ui.main_window import main as ui_main


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
    ui_main()


if __name__ == "__main__":
    main()