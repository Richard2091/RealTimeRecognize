"""
YOLO26检测器
支持目标检测
优化边缘设备，CPU推理速度提升43%
"""
from ultralytics import YOLO
from ..base import BaseDetector


class YOLO26Detector(BaseDetector):
    """YOLO26检测器"""

    def __init__(self, model_path="model/yolo26/yolo26n.pt"):
        """
        初始化YOLO26检测器

        Args:
            model_path: 模型文件路径
        """
        super().__init__(model_path)
    
    def load_model(self):
        """加载模型"""
        try:
            self.model = YOLO(self.model_path)
            print(f"✓ 加载YOLO26目标检测模型: {self.model_path}")
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
            'version': 'YOLO26',
            'model': self.model_path,
            'classes': self.get_classes(),
            'features': ['端到端无NMS', 'CPU推理快43%', '边缘设备优化']
        }