"""
YOLOv8检测器
支持目标检测
姿态检测现在由MediaPipe Pose统一处理
"""
from ultralytics import YOLO


class YOLOv8Detector:
    """YOLOv8检测器"""

    def __init__(self, model_name="model/yolo8/yolov8n.pt"):
        """
        初始化YOLOv8检测器

        Args:
            model_name: 模型文件路径
        """
        self.model_name = model_name
        self.model = None
        self.load_model()

    def load_model(self):
        """加载模型"""
        try:
            self.model = YOLO(self.model_name)
            print(f"✓ 加载YOLOv8目标检测模型: {self.model_name}")
        except Exception as e:
            print(f"✗ 模型加载失败: {e}")
            raise

    def detect(self, frame, verbose=False):
        """
        执行检测

        Args:
            frame: 输入图像
            verbose: 是否显示详细信息

        Returns:
            检测结果
        """
        return self.model(frame, verbose=verbose)

    def detect_persons(self, frame, verbose=False):
        """
        只检测人员

        Args:
            frame: 输入图像
            verbose: 是否显示详细信息

        Returns:
            人员检测结果
        """
        results = self.model(frame, verbose=verbose, classes=[0])
        return results
    
    def get_classes(self):
        """获取支持的类别"""
        return self.model.names if hasattr(self.model, 'names') else {}

    def get_info(self):
        """获取检测器信息"""
        return {
            'version': 'YOLOv8',
            'model': self.model_name
        }
