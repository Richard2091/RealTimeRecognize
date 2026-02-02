"""
配置模块
集中管理所有配置选项
"""


class Config:
    """配置类"""

    # YOLOv8模型配置
    YOLOV8_MODELS = {
        "1": {
            "name": "yolov8n",
            "display": "YOLOv8n (轻量级)",
            "file": "model/yolo8/yolov8n.pt"
        },
        "2": {
            "name": "yolov8s",
            "display": "YOLOv8s (标准版)",
            "file": "model/yolo8/yolov8s.pt"
        }
    }

    # YOLO26模型配置
    YOLO26_MODELS = {
        "3": {
            "name": "yolo26n",
            "display": "YOLO26n (最新边缘优化，CPU快43%)",
            "file": "model/yolo26/yolo26n.pt"
        },
        "4": {
            "name": "yolo26s",
            "display": "YOLO26s (边缘优化标准版)",
            "file": "model/yolo26/yolo26s.pt"
        }
    }

    # YOLO-World配置
    YOLO_WORLD_MODELS = {
        "5": {
            "name": "yolov8s-worldv2",
            "display": "YOLO-World (开放词汇，自定义类别)",
            "file": "model/yoloworld/yolov8s-worldv2.pt"
        }
    }

    # 所有模型映射
    ALL_MODELS = {**YOLOV8_MODELS, **YOLO26_MODELS, **YOLO_WORLD_MODELS}

    # 检测器类型
    DETECTOR_TYPES = {
        "yolov8n": "YOLOv8",
        "yolov8s": "YOLOv8",
        "yolo26n": "YOLO26",
        "yolo26s": "YOLO26",
        "yolov8s-worldv2": "YOLO-World"
    }

    # 摄像头配置
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    CAMERA_FPS = 30

    # 检测类别（YOLO-World默认）
    DEFAULT_CLASSES = [
        'person', 'car', 'dog', 'cat', 'bicycle',
        'cell phone', 'laptop', 'cup'
    ]

    @staticmethod
    def get_detector_type(model_name):
        """获取检测器类型"""
        for name, detector_type in Config.DETECTOR_TYPES.items():
            if name in model_name:
                return detector_type
        return "Unknown"

    @staticmethod
    def is_yolo26(model_name):
        """判断是否为YOLO26模型"""
        return Config.get_detector_type(model_name) == "YOLO26"

    @staticmethod
    def is_yolo_world(model_name):
        """判断是否为YOLO-World模型"""
        return Config.get_detector_type(model_name) == "YOLO-World"

    @staticmethod
    def is_yolo8(model_name):
        """判断是否为YOLOv8模型"""
        return Config.get_detector_type(model_name) == "YOLOv8"
