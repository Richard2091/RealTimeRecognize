"""
YOLO实时检测系统 - QT版本
使用重构后的架构和PyQt5实现
"""

# 导入QT界面
from ui.main_window import main as ui_main

def main():
    """主函数"""
    print("=" * 50)
    print("YOLO实时检测识别系统")
    print("=" * 50)
    
    # 启动QT界面
    print("启动图形化界面")
    ui_main()


if __name__ == "__main__":
    main()