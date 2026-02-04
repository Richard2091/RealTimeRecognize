"""
RTSP摄像头实现类
支持RTSP网络摄像头
"""
import cv2
import time
import numpy as np
from typing import Tuple, Optional, Dict, Any
from ..base_camera import BaseCamera


class RTSPCamera(BaseCamera):
    """RTSP摄像头类"""

    def __init__(self, rtsp_url: str, width: int = 1280, height: int = 720, timeout: int = 10):
        """
        初始化RTSP摄像头

        Args:
            rtsp_url: RTSP流地址（如：rtsp://192.168.1.100:554/stream）
            width: 期望宽度（默认1280）
            height: 期望高度（默认720）
            timeout: 连接超时时间（秒，默认10秒）
        """
        super().__init__()
        self._rtsp_url = rtsp_url
        self._desired_width = width
        self._desired_height = height
        self._timeout = timeout
        self._cap = None
        self._fps = 0
        self._fps_buffer = []
        self._fps_buffer_size = 30
        self._connection_attempts = 0
        self._reconnection_count = 0

    def open(self) -> bool:
        """打开RTSP摄像头"""
        try:
            print(f"正在连接RTSP摄像头: {self._rtsp_url}")
            self._connection_attempts += 1

            # 创建VideoCapture
            self._cap = cv2.VideoCapture(self._rtsp_url, cv2.CAP_FFMPEG)

            if not self._cap.isOpened():
                print(f"无法打开RTSP流: {self._rtsp_url}")
                return False

            # 设置低延迟模式
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            # 尝试读取第一帧（验证连接）
            start_time = time.time()
            while time.time() - start_time < self._timeout:
                ret, frame = self._cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    self._width = width
                    self._height = height
                    self._is_opened = True
                    self._start_time = time.time()
                    self._last_frame_time = self._start_time
                    print(f"✓ RTSP摄像头连接成功: {self._rtsp_url}")
                    print(f"  分辨率: {self._width}x{self._height}")
                    return True
                time.sleep(0.1)

            # 超时
            print(f"RTSP连接超时 ({self._timeout}秒)")
            self.release()
            return False

        except Exception as e:
            print(f"打开RTSP摄像头失败: {e}")
            self.release()
            return False

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """读取一帧"""
        if not self._is_opened or self._cap is None:
            return False, None

        try:
            ret, frame = self._cap.read()

            if not ret or frame is None:
                # 尝试重新连接
                self._error_count += 1
                self._reconnection_count += 1
                print(f"RTSP流读取失败，尝试重新连接 ({self._reconnection_count})")
                self.release()
                time.sleep(1)
                if self.open():
                    return self.read()
                else:
                    return False, None

            # 更新统计信息
            current_time = time.time()
            self._frame_count += 1

            # 计算FPS
            if len(self._fps_buffer) > 0:
                self._fps_buffer.append(current_time)
                if len(self._fps_buffer) > self._fps_buffer_size:
                    self._fps_buffer.pop(0)
                self._fps = len(self._fps_buffer) / (self._fps_buffer[-1] - self._fps_buffer[0]) if len(self._fps_buffer) > 1 else 0
            else:
                self._fps_buffer.append(current_time)
                self._fps = 0

            self._last_frame_time = current_time

            # 验证帧的有效性
            if frame.size == 0:
                self._error_count += 1
                return False, None

            return True, frame

        except Exception as e:
            print(f"读取RTSP帧失败: {e}")
            self._error_count += 1
            return False, None

    def release(self) -> None:
        """释放摄像头"""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        self._is_opened = False

    def is_opened(self) -> bool:
        """检查摄像头是否已打开"""
        return self._is_opened and self._cap is not None and self._cap.isOpened()

    def get_resolution(self) -> Tuple[int, int]:
        """获取摄像头分辨率"""
        if self._cap is not None and self._cap.isOpened():
            width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if width > 0 and height > 0:
                self._width = width
                self._height = height
        return self._width, self._height

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self._is_opened or self._start_time == 0:
            return {}

        current_time = time.time()
        running_time = current_time - self._start_time

        # 计算平均FPS
        avg_fps = self._frame_count / running_time if running_time > 0 else 0

        # 计算实时FPS
        real_time_fps = self._fps if self._fps > 0 else avg_fps

        # 计算错误率
        total_attempts = self._frame_count + self._error_count
        error_rate = (self._error_count / total_attempts * 100) if total_attempts > 0 else 0

        # 计算连接稳定性
        connection_stability = max(0, 100 - error_rate)

        # 估算数据速率（Mbps）
        data_rate = 0
        if self._frame_count > 0:
            # 假设每帧大小 = width * height * 3 bytes * 0.5 (压缩率)
            frame_size_mb = (self._width * self._height * 3 * 0.5) / (1024 * 1024)
            total_data_mb = frame_size_mb * self._frame_count
            data_rate = (total_data_mb * 8) / running_time if running_time > 0 else 0

        return {
            'rtsp_url': self._rtsp_url,
            'resolution': self.get_resolution(),
            'frame_count': self._frame_count,
            'error_count': self._error_count,
            'error_rate': round(error_rate, 2),
            'avg_fps': round(avg_fps, 1),
            'real_time_fps': round(real_time_fps, 1),
            'running_time': round(running_time, 1),
            'connection_stability': round(connection_stability, 1),
            'data_rate_mbps': round(data_rate, 2),
            'connection_attempts': self._connection_attempts,
            'reconnection_count': self._reconnection_count,
            'is_opened': self._is_opened
        }

    @property
    def rtsp_url(self) -> str:
        """获取RTSP地址"""
        return self._rtsp_url

    @staticmethod
    def build_rtsp_url(ip: str, port: int = 554, path: str = "") -> str:
        """
        构建RTSP URL

        Args:
            ip: IP地址
            port: 端口号（默认554）
            path: 路径

        Returns:
            RTSP URL
        """
        return f"rtsp://{ip}:{port}/{path.lstrip('/')}"

    @staticmethod
    def parse_rtsp_url(url: str) -> Tuple[str, int, str]:
        """
        解析RTSP URL

        Args:
            url: RTSP URL

        Returns:
            (ip, port, path)
        """
        try:
            # 移除rtsp://前缀
            url = url.replace("rtsp://", "")
            # 分割地址和路径
            if "/" in url:
                addr, path = url.split("/", 1)
            else:
                addr = url
                path = ""

            # 分割IP和端口
            if ":" in addr:
                ip, port = addr.rsplit(":", 1)
                port = int(port)
            else:
                ip = addr
                port = 554

            return ip, port, path
        except Exception as e:
            print(f"解析RTSP URL失败: {e}")
            return "", 554, ""
