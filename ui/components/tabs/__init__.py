"""
底部信息区域标签组件模块
"""

from .video_tab import VideoTab
from .performance_tab import PerformanceTab
from .detection_tab import DetectionTab
from .resource_tab import ResourceTab
from .rtsp_tab import RTSPTab
from .log_tab import LogTab

__all__ = [
    'VideoTab',
    'PerformanceTab', 
    'DetectionTab',
    'ResourceTab',
    'RTSPTab',
    'LogTab'
]