"""
摄像头模块 - 统一摄像头管理框架
支持本地摄像头和RTSP网络摄像头
"""
from .camera_manager import CameraManager, CameraState, CameraEvent
from .camera_factory import CameraFactory
from .base_camera import BaseCamera
from .local_camera import LocalCamera
from .rtsp_camera import RTSPCamera

__all__ = [
    'CameraManager',
    'CameraFactory', 
    'BaseCamera',
    'LocalCamera',
    'RTSPCamera',
    'CameraState',
    'CameraEvent'
]
