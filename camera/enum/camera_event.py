"""
摄像头事件定义
"""
class CameraEvent:
    STATE_CHANGED = "state_changed"
    FRAME_READ = "frame_read"
    ERROR_OCCURRED = "error_occurred"
    CONFIG_CHANGED = "config_changed"