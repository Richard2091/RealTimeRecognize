"""
基础摄像头抽象类
定义所有摄像头类型的统一接口
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any
import numpy as np


class BaseCamera(ABC):
    """摄像头抽象基类，定义统一接口"""
    
    def __init__(self):
        self._is_opened = False
        self._frame_count = 0
        self._error_count = 0
        self._last_frame_time = 0
        self._start_time = 0
        self._width = 0
        self._height = 0
        
    @abstractmethod
    def open(self) -> bool:
        """打开摄像头，返回是否成功"""
        pass
    
    @abstractmethod
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        读取一帧
        Returns:
            (ret, frame): ret为是否成功，frame为图像数据或None
        """
        pass
    
    @abstractmethod
    def release(self) -> None:
        """释放摄像头资源"""
        pass
    
    @abstractmethod
    def is_opened(self) -> bool:
        """检查摄像头是否已打开"""
        return self._is_opened
    
    @abstractmethod
    def get_resolution(self) -> Tuple[int, int]:
        """获取摄像头分辨率 (width, height)"""
        return self._width, self._height
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取摄像头统计信息
        Returns:
            包含fps、错误率、分辨率等信息的字典
        """
        pass
    
    @property
    def frame_count(self) -> int:
        """获取已读取的帧数"""
        return self._frame_count
    
    @property
    def error_count(self) -> int:
        """获取读取错误数"""
        return self._error_count
