"""
检测器基类
定义所有检测器的通用接口
"""
from abc import ABC, abstractmethod


class BaseDetector(ABC):
    """检测器基类"""
    
    def __init__(self, model_path):
        """
        初始化检测器
        
        Args:
            model_path: 模型文件路径
        """
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    @abstractmethod
    def load_model(self):
        """加载模型"""
        pass
    
    @abstractmethod
    def detect(self, frame, verbose=True):
        """
        检测对象
        
        Args:
            frame: 输入图像
            verbose: 是否显示详细信息
            
        Returns:
            检测结果
        """
        pass
    
    @abstractmethod
    def get_classes(self):
        """获取支持的类别"""
        pass
    
    def preprocess(self, frame):
        """
        预处理图像
        
        Args:
            frame: 输入图像
            
        Returns:
            预处理后的图像
        """
        return frame
    
    def postprocess(self, results):
        """
        后处理检测结果
        
        Args:
            results: 原始检测结果
            
        Returns:
            处理后的结果
        """
        return results