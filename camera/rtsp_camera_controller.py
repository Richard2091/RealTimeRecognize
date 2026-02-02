"""
RTSP摄像头控制器模块
支持通过RTSP协议连接网络摄像头
"""
import cv2
import subprocess
import re
import os
import sys
from .camera_controller import CameraController


class RTSPCameraController(CameraController):
    """RTSP摄像头控制器"""

    def __init__(self, rtsp_url, width=1280, height=720):
        """
        初始化RTSP摄像头控制器

        Args:
            rtsp_url: RTSP流地址 (例如: rtsp://192.168.1.100:554/stream)
            width: 初始宽度
            height: 初始高度
        """
        # 初始化基类
        super().__init__(camera_id=rtsp_url, width=width, height=height)

        self.rtsp_url = rtsp_url
        self.use_rtsp = True
        
        # RTSP特有统计信息
        self.connection_attempts = 0
        self.reconnection_count = 0
        self.last_connection_time = None

        # 初始化时尝试打开RTSP流
        if not self.rtsp_url:
            raise RuntimeError("RTSP地址未设置")

        print(f"正在连接RTSP流: {self.rtsp_url}")

        # 尝试打开RTSP流
        self.cap = cv2.VideoCapture(self.rtsp_url)

        # 设置RTSP连接参数以加快连接
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # 检查是否成功打开
        if not self.cap.isOpened():
            raise RuntimeError(f"无法连接到RTSP流: {self.rtsp_url}")

        # 尝试读取第一帧以验证连接
        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.cap.release()
            raise RuntimeError(f"RTSP流可用但无法读取数据: {self.rtsp_url}")

        print(f"✓ RTSP摄像头已初始化")
        print(f"   RTSP地址: {rtsp_url}")
        print(f"   分辨率: {frame.shape[1]}x{frame.shape[0]}")
        
        # 设置初始分辨率
        self.initial_width = frame.shape[1]
        self.initial_height = frame.shape[0]

    def get_rtsp_info(self):
        """
        获取RTSP信息

        Returns:
            dict: RTSP相关信息
        """
        return {
            'rtsp_url': self.rtsp_url,
            'is_available': self.cap is not None and self.cap.isOpened()
        }

    def read(self):
        """
        从RTSP摄像头读取帧（带错误处理和统计）

        Returns:
            ret: 是否成功读取
            frame: 帧
        """
        import time
        
        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.frame_read_errors += 1
                return False, None
            
            # 检查帧是否有效
            if frame.size == 0:
                self.frame_read_errors += 1
                return False, None

            # 初始化开始时间
            if self.start_time is None:
                self.start_time = time.time()
                self.last_frame_time = self.start_time
                self.last_connection_time = self.start_time
            
            current_time = time.time()
            
            # 记录帧时间
            self.frame_times.append(current_time)
            self.fps_buffer.append(current_time)
            
            # 保持缓冲区大小
            if len(self.frame_times) > self.buffer_size:
                self.frame_times.pop(0)
            if len(self.fps_buffer) > self.buffer_size:
                self.fps_buffer.pop(0)
            
            self.frame_count += 1
            self.last_frame_time = current_time

            # 应用缩放
            if self.zoom_level != 1.0:
                frame = self.software_zoom(frame, self.zoom_level)

            return True, frame

        except Exception as e:
            # 捕获解码错误，返回读取失败
            self.frame_read_errors += 1
            print(f"RTSP读取错误: {e}")
            return False, None

    def release(self):
        """释放RTSP摄像头"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        print("✓ RTSP摄像头已释放")

    def get_resolution(self):
        """
        获取RTSP流的实际分辨率

        Returns:
            tuple: (width, height) 或 (0, 0)
        """
        if self.cap is None or not self.cap.isOpened():
            return (0, 0)

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)

    def get_statistics(self):
        """
        获取RTSP视频统计信息（包含RTSP特有信息）

        Returns:
            dict: 统计信息
        """
        import time
        
        if self.start_time is None:
            return {}
            
        current_time = time.time()
        running_time = current_time - self.start_time
        
        # 计算平均FPS
        avg_fps = self.frame_count / running_time if running_time > 0 else 0
        
        # 计算实时FPS（最近30帧）
        if len(self.fps_buffer) >= 2:
            real_time_fps = len(self.fps_buffer) / (self.fps_buffer[-1] - self.fps_buffer[0])
        else:
            real_time_fps = avg_fps
            
        # 计算错误率
        total_attempts = self.frame_count + self.frame_read_errors
        error_rate = (self.frame_read_errors / total_attempts * 100) if total_attempts > 0 else 0
        
        # 计算延迟（帧处理间隔）
        latency = 0
        if len(self.frame_times) >= 2:
            intervals = [self.frame_times[i+1] - self.frame_times[i] for i in range(len(self.frame_times)-1)]
            if intervals:
                latency = sum(intervals) / len(intervals) * 1000  # 转换为毫秒
        
        # 计算连接稳定性
        connection_stability = 100 - error_rate
        
        # 计算数据速率（估算）
        data_rate = 0
        if running_time > 0:
            resolution = self.get_resolution()
            pixels_per_frame = resolution[0] * resolution[1] if resolution != (0, 0) else 0
            total_pixels = self.frame_count * pixels_per_frame
            # 假设每像素3字节（RGB），转换为Mbps
            data_rate = (total_pixels * 3 * 8) / (running_time * 1000000) if total_pixels > 0 else 0
        
        return {
            'frame_count': self.frame_count,
            'frame_read_errors': self.frame_read_errors,
            'error_rate': round(error_rate, 2),
            'avg_fps': round(avg_fps, 1),
            'real_time_fps': round(real_time_fps, 1),
            'latency_ms': round(latency, 1),
            'running_time_seconds': round(running_time, 1),
            'resolution': self.get_resolution(),
            'rtsp_url': self.rtsp_url,
            'connection_stability': round(connection_stability, 1),
            'data_rate_mbps': round(data_rate, 2),
            'connection_attempts': self.connection_attempts,
            'reconnection_count': self.reconnection_count
        }
