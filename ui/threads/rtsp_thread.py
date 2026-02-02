"""
RTSP连接线程
处理RTSP摄像头的后台连接
"""
from PyQt5.QtCore import QThread, pyqtSignal
from camera.rtsp_camera_controller import RTSPCameraController


class RTSPConnectionThread(QThread):
    """RTSP连接线程，避免阻塞UI主线程"""
    connection_finished = pyqtSignal(object, str)  # (camera_object, error_message)

    def __init__(self, rtsp_url, width, height):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.width = width
        self.height = height

    def run(self):
        """在后台线程中执行RTSP连接"""
        try:
            camera = RTSPCameraController(
                rtsp_url=self.rtsp_url,
                width=self.width,
                height=self.height
            )
            self.connection_finished.emit(camera, "")
        except Exception as e:
            self.connection_finished.emit(None, str(e))