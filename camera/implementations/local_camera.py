"""
本地摄像头实现类
支持笔记本内置摄像头
"""
import cv2
import time
import numpy as np
from typing import Tuple, Optional, Dict, Any
from ..base_camera import BaseCamera


class LocalCamera(BaseCamera):
    """本地摄像头类"""

    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        """
        初始化本地摄像头

        Args:
            camera_id: 摄像头ID（默认0）
            width: 期望宽度（默认640）
            height: 期望高度（默认480）
        """
        super().__init__()
        self._camera_id = camera_id
        self._desired_width = width
        self._desired_height = height
        self._cap = None
        self._fps = 0
        self._fps_buffer = []
        self._fps_buffer_size = 30

    def open(self) -> bool:
        """打开摄像头"""
        try:
            # 使用DirectShow后端（Windows）
            self._cap = cv2.VideoCapture(self._camera_id, cv2.CAP_DSHOW)

            if not self._cap.isOpened():
                return False

            # 设置分辨率（最佳实践：先设置再验证）
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._desired_width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._desired_height)

            # 等待设置生效
            time.sleep(0.1)

            # 验证分辨率
            actual_width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # 如果设置失败，获取实际分辨率
            if actual_width == 0 or actual_height == 0:
                # 尝试读取一帧来确定实际分辨率
                ret, frame = self._cap.read()
                if ret and frame is not None:
                    actual_height, actual_width = frame.shape[:2]
                else:
                    # 使用默认值
                    actual_width, actual_height = 640, 480

            self._width = actual_width
            self._height = actual_height
            self._is_opened = True
            self._start_time = time.time()
            self._last_frame_time = self._start_time

            return True

        except Exception as e:
            print(f"打开摄像头失败: {e}")
            self.release()
            return False

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """读取一帧"""
        if not self._is_opened or self._cap is None:
            return False, None

        try:
            ret, frame = self._cap.read()

            if not ret or frame is None:
                self._error_count += 1
                return False, None

            # 更新统计信息
            current_time = time.time()
            self._frame_count += 1

            # 计算FPS
            if len(self._fps_buffer) > 0:
                fps = 1.0 / (current_time - self._fps_buffer[-1])
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
            print(f"读取帧失败: {e}")
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

        return {
            'camera_id': self._camera_id,
            'resolution': self.get_resolution(),
            'frame_count': self._frame_count,
            'error_count': self._error_count,
            'error_rate': round(error_rate, 2),
            'avg_fps': round(avg_fps, 1),
            'real_time_fps': round(real_time_fps, 1),
            'running_time': round(running_time, 1),
            'is_opened': self._is_opened
        }

    @staticmethod
    def detect_cameras(max_id: int = 3) -> list:
        """
        检测可用的本地摄像头

        Args:
            max_id: 最大检测ID（默认3）

        Returns:
            可用摄像头ID列表
        """
        available_cameras = []

        for camera_id in range(max_id):
            try:
                # 尝试不同的后端
                cap = None
                for backend in [cv2.CAP_DSHOW, cv2.CAP_ANY]:
                    try:
                        cap = cv2.VideoCapture(camera_id, backend)
                        if cap and cap.isOpened():
                            break
                    except:
                        continue

                if cap is None or not cap.isOpened():
                    print(f"  ✗ 摄像头 {camera_id}: 无法打开")
                    continue

                # 测试读取一帧
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"  ✓ 发现摄像头 {camera_id}: {width}x{height}")
                    available_cameras.append(camera_id)
                else:
                    print(f"  ✗ 摄像头 {camera_id}: 无法读取帧")

                cap.release()
                cap = None

            except Exception as e:
                print(f"  ✗ 摄像头 {camera_id}: 检测失败 - {e}")
                if cap is not None:
                    try:
                        cap.release()
                    except:
                        pass
                cap = None

        return available_cameras
