"""
摄像头模块 - 统一摄像头管理框架
支持本地摄像头和RTSP网络摄像头
"""
from .camera_controller import CameraController
from .camera_factory import CameraFactory
from .base_camera import BaseCamera
from .enum.camera_status import CameraStatus
from .enum.camera_event import CameraEvent
from .implementations import LocalCamera, RTSPCamera

__all__ = [
    'CameraController',
    'CameraFactory',
    'BaseCamera',
    'LocalCamera',
    'RTSPCamera',
    'CameraStatus',
    'CameraEvent'
]
