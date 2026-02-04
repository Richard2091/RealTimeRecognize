"""
YOLO检测器系列
"""
from .yolo8 import YOLOv8Detector
from .yolo26 import YOLO26Detector
from .yolo_world import YOWorldDetector

__all__ = ['YOLOv8Detector', 'YOLO26Detector', 'YOWorldDetector']
