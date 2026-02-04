"""
摄像头模块 - 基础组件
包含基类、状态定义等
"""
from .camera_status import CameraStatus
from .camera_event import CameraEvent

__all__ = ['CameraStatus', 'CameraEvent']
