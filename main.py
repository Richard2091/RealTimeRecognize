"""
YOLO统一启动脚本
整合所有功能，运行时交互式选择配置
架构：
- YOLO: 目标检测（找到人）
- MediaPipe Pose: 姿态检测（人体骨骼）
- MediaPipe FaceMesh: 表情检测（面部表情）
"""
import cv2
import sys
from pathlib import Path

# 导入各个模块
from detectors.yolo8_detector import YOLOv8Detector
from detectors.yolo26_detector import YOLO26Detector
from detectors.yolo_world_detector import YOWorldDetector
from emotion.emotion_detector import FaceEmotionDetector
from pose.pose_detector import PoseDetector
from display.opencv_display import OpenCVDisplay
from camera.camera_controller import CameraController
from utils.config import Config
from ui.config_window import ConfigWindow


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_menu(options, title="请选择"):
    """打印菜单并获取用户选择"""
    print(f"\n{title}:")
    for key, value in options.items():
        print(f"  {key}. {value}")
    print()
    choice = input("请输入选项: ").strip()
    return choice


def check_dependencies():
    """检查依赖"""
    print("检查依赖...")

    # 检查ultralytics
    try:
        from ultralytics import YOLO
        print("✓ ultralytics")
    except ImportError:
        print("✗ ultralytics未安装")
        print("  安装命令: pip install ultralytics")
        return False

    # 检查MediaPipe（可选，但姿态检测需要）
    try:
        import mediapipe
        print("✓ mediapipe")
        MEDIAPIPE_AVAILABLE = True
    except ImportError:
        print("⚠ mediapipe未安装 (姿态检测和表情检测功能不可用)")
        print("  安装命令: pip install mediapipe")
        MEDIAPIPE_AVAILABLE = False

    return True, MEDIAPIPE_AVAILABLE


def create_detector(model_name):
    """
    根据模型名称创建对应的检测器

    Args:
        model_name: 模型文件路径

    Returns:
        detector: 检测器实例
    """
    detector_type = Config.get_detector_type(model_name)

    if detector_type == "YOLOv8":
        return YOLOv8Detector(model_name)
    elif detector_type == "YOLO26":
        return YOLO26Detector(model_name)
    elif detector_type == "YOLO-World":
        return YOWorldDetector(model_name)
    else:
        raise ValueError(f"不支持的模型: {model_name}")


def main():
    """主函数"""
    print_header("YOLO实时检测系统")

    # 检查依赖
    dep_result = check_dependencies()
    if isinstance(dep_result, bool):
        if not dep_result:
            return
        MEDIAPIPE_AVAILABLE = False
    else:
        ok, MEDIAPIPE_AVAILABLE = dep_result
        if not ok:
            return

    # 显示配置窗口
    print_header("配置向导")
    config_window = ConfigWindow()
    config_complete, model_path, use_opencv, use_pose, use_emotion = config_window.show(
        mediapipe_available=MEDIAPIPE_AVAILABLE
    )
    
    if not config_complete:
        print("配置未完成，程序退出")
        return
    
    # 获取模型信息
    model_info = None
    for key, info in Config.ALL_MODELS.items():
        if info["file"] == model_path:
            model_info = info
            break
    
    if not model_info:
        print(f"无效的模型路径: {model_path}")
        return
    
    # 加载模型
    print_header("正在加载模型")
    print(f"YOLO模型: {model_path}")
    print(f"显示方式: {'OpenCV' if use_opencv else 'YOLO内置'}")
    print(f"姿态检测: {'是' if use_pose else '否'}")
    print(f"表情检测: {'是' if use_emotion else '否'}")

    # 初始化YOLO检测器
    try:
        detector = create_detector(model_path)
    except Exception as e:
        print(f"✗ 模型加载失败: {e}")
        return

    print("✓ YOLO模型加载成功")

    # 初始化MediaPipe姿态检测器
    pose_detector = None
    if use_pose and MEDIAPIPE_AVAILABLE:
        try:
            pose_detector = PoseDetector()
            print("✓ MediaPipe姿态检测器初始化成功")
        except Exception as e:
            print(f"✗ 姿态检测器初始化失败: {e}")
            use_pose = False
            use_emotion = False

    # 初始化表情检测器
    emotion_detector = None
    if use_emotion and MEDIAPIPE_AVAILABLE:
        try:
            emotion_detector = FaceEmotionDetector()
            print("✓ MediaPipe表情检测器初始化成功")
        except Exception as e:
            print(f"✗ 表情检测器初始化失败: {e}")
            use_emotion = False

    print()

    # YOLO内置显示模式
    if not use_opencv:
        print_header("正在打开摄像头...")
        print("\n开始检测...")
        print("按 'q' 键退出")
        print("注意: YOLO内置显示模式下缩放功能不可用")
        print("-" * 60)

        try:
            detector.model(source=0, show=True, verbose=False)
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        finally:
            if pose_detector:
                pose_detector.close()
            return

    # OpenCV显示模式（支持姿态和表情检测）
    # 打开摄像头
    print_header("正在打开摄像头...")
    try:
        camera = CameraController(
            camera_id=0,
            width=Config.CAMERA_WIDTH,
            height=Config.CAMERA_HEIGHT
        )
        camera.open()
    except Exception as e:
        print(f"✗ 摄像头初始化失败: {e}")
        return

    display = OpenCVDisplay(show_skeleton=True)
    display.start()

    # 鼠标回调函数
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # 检查按钮点击
            button_id, should_exit, update_buttons = display.button_manager.check_button_click(x, y, camera)
            
            if button_id:
                # 处理表情检测按钮
                if button_id == 'emotion':
                    nonlocal use_emotion
                    use_emotion = not use_emotion
                    print(f"表情检测: {'开' if use_emotion else '关'}")
                
                return
            
            # 如果没有点击按钮，设置缩放中心点
            camera.set_zoom_center(x, y)
            print(f"缩放中心点已设置为 ({x}, {y})")

    cv2.setMouseCallback(display.window_name, mouse_callback)

    print("\n开始检测...")
    print("按 'q' 键退出")
    print("按 'm' 键切换镜像")
    print("按 '+' 键放大")
    print("按 '-' 键缩小")
    print("按 'r' 键重置缩放")
    print("按 'c' 键重置缩放中心点")
    print("鼠标左键点击: 设置缩放中心点")
    if use_pose:
        print("按 's' 键切换骨骼显示")
    if use_emotion:
        print("按 'e' 键切换表情显示")
    print("-" * 60)

    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                print("无法读取帧")
                break

            # 处理帧
            processed_frame = display.process_frame(
                frame,
                detector,
                pose_detector=pose_detector,
                emotion_detector=emotion_detector,
                use_pose=use_pose,
                use_emotion=use_emotion,
                zoom_level=camera.zoom_level
            )

            # 显示
            display.show_frame(processed_frame)

            # 检查窗口是否被关闭
            try:
                if cv2.getWindowProperty(display.window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            except:
                break

            # 键盘控制
            key = cv2.waitKey(1) & 0xFF
            should_exit, show_skeleton, _ = display.handle_key(
                key, use_pose, use_emotion
            )

            # 缩放控制
            if key == ord('+') or key == ord('='):
                camera.zoom_in()
            elif key == ord('-') or key == ord('_'):
                camera.zoom_out()
            elif key == ord('r'):
                camera.reset_zoom()
            elif key == ord('c'):
                camera.reset_zoom_center()
                print("缩放中心点已重置为图像中心")

            # 切换表情检测
            if key == ord('e') and use_emotion:
                use_emotion = not use_emotion
                status = "开" if use_emotion else "关"
                print(f"表情检测: {status}")

            display.show_skeleton = show_skeleton
            if should_exit:
                break

    except KeyboardInterrupt:
        print("\n程序被用户中断")

    finally:
        # 统计信息
        stats = display.get_stats()

        if pose_detector:
            pose_detector.close()
        camera.release()
        display.close()

        if stats:
            print_header("统计信息")
            print(f"总运行时间: {stats['elapsed_time']:.1f}秒")
            print(f"总处理帧数: {stats['frame_count']}")
            print(f"平均FPS: {stats['avg_fps']:.1f}")
            print("=" * 60)
            print("程序结束")


if __name__ == "__main__":
    main()
