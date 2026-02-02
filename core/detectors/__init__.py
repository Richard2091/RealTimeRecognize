"""
检测器模块
包含所有检测器的基类和实现
"""
from .base import BaseDetector
from .yolo import *
from .pose import PoseDetector
from .emotion import EmotionDetector