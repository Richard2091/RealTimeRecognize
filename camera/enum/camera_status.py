"""
摄像头状态定义
"""
class CameraStatus:
    CLOSED = "closed"              # 已关闭
    OPENING = "opening"            # 正在打开
    OPENED = "opened"              # 已打开
    READING = "reading"            # 正在读取
    ERROR = "error"                # 错误状态
    RECONNECTING = "reconnecting"  # 正在重连