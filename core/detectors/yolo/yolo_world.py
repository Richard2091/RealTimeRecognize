"""
YOLO-World检测器
开放词汇目标检测，支持自定义类别
"""
from ultralytics import YOLOWorld


class YOWorldDetector:
    """YOLO-World检测器"""

    # 默认检测类别
    DEFAULT_CLASSES = [
        'person', 'car', 'dog', 'cat', 'bicycle',
        'cell phone', 'laptop', 'cup'
    ]

    def __init__(self, model_name="model/yoloworld/yolov8s-worldv2.pt", custom_classes=None):
        """
        初始化YOLO-World检测器

        Args:
            model_name: 模型文件路径
            custom_classes: 自定义类别列表
        """
        self.model_name = model_name
        self.classes = custom_classes or self.DEFAULT_CLASSES
        self.model = None
        self.load_model()

    def load_model(self):
        """加载模型"""
        try:
            self.model = YOLOWorld(self.model_name)
            self.model.set_classes(self.classes)
            print(f"✓ 加载YOLO-World模型: {self.model_name}")
            print(f"✓ 检测类别: {', '.join(self.classes)}")
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
        # 重新设置为只检测人
        original_classes = self.classes.copy()
        self.model.set_classes(['person'])
        results = self.model(frame, verbose=verbose)
        self.model.set_classes(original_classes)
        return results

    def set_classes(self, classes):
        """
        设置自定义类别

        Args:
            classes: 类别列表
        """
        self.classes = classes
        self.model.set_classes(classes)
        print(f"✓ 更新检测类别: {', '.join(classes)}")

    def get_classes(self):
        """获取支持的类别"""
        return self.classes

    def get_info(self):
        """获取检测器信息"""
        return {
            'version': 'YOLO-World',
            'model': self.model_name,
            'classes': self.classes,
            'features': ['开放词汇', '自定义类别', '零样本检测']
        }
