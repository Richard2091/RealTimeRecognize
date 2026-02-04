"""
摄像头实现模块
包含具体的摄像头实现类
"""
from .local_camera import LocalCamera
from .rtsp_camera import RTSPCamera

__all__ = ['LocalCamera', 'RTSPCamera']
