"""
摄像头控制器模块
支持硬件和软件缩放功能
"""
import cv2
import numpy as np


class BaseCameraController:
    """摄像头控制器基类"""

    def __init__(self, width=1280, height=720):
        """
        初始化摄像头控制器

        Args:
            width: 初始宽度
            height: 初始高度
        """
        self.cap = None
        self.initial_width = width
        self.initial_height = height

        # 缩放参数
        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        self.zoom_step = 0.1
        self.use_hardware_zoom = False

        # 缩放中心点（图像中心）
        self.zoom_center = None

        # 统计信息
        self.frame_count = 0
        self.frame_read_errors = 0
        self.start_time = None
        self.last_frame_time = None
        self.frame_times = []
        self.fps_buffer = []
        self.buffer_size = 30  # 统计最近30帧的数据

    def open(self):
        """打开摄像头（子类实现）"""
        raise NotImplementedError

    def read(self):
        """读取帧（子类实现）"""
        raise NotImplementedError

    def release(self):
        """释放摄像头（子类实现）"""
        raise NotImplementedError

    def software_zoom(self, frame, zoom_level):
        """
        软件缩放（通过裁剪和缩放图像）

        Args:
            frame: 输入帧
            zoom_level: 缩放级别 (1.0 = 无缩放, >1.0 放大)

        Returns:
            zoomed_frame: 缩放后的帧
        """
        if zoom_level <= 1.0:
            return frame

        height, width = frame.shape[:2]

        # 计算裁剪区域
        crop_width = int(width / zoom_level)
        crop_height = int(height / zoom_level)

        # 如果缩放中心点未设置，使用图像中心
        if self.zoom_center is None:
            center_x = width // 2
            center_y = height // 2
        else:
            center_x, center_y = self.zoom_center

        # 计算裁剪区域的左上角
        x1 = max(0, center_x - crop_width // 2)
        y1 = max(0, center_y - crop_height // 2)
        x2 = min(width, x1 + crop_width)
        y2 = min(height, y1 + crop_height)

        # 裁剪并缩放回原始尺寸
        cropped = frame[y1:y2, x1:x2]
        zoomed = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LINEAR)

        return zoomed

    def set_zoom(self, zoom_level):
        """
        设置缩放级别

        Args:
            zoom_level: 缩放级别 (1.0 = 无缩放, >1.0 放大, <1.0 缩小)
        """
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, zoom_level))

    def zoom_in(self):
        """放大"""
        if self.zoom_level < self.max_zoom:
            self.zoom_level += self.zoom_step
            print(f"缩放: {self.zoom_level:.1f}x")
        else:
            print(f"已达到最大缩放: {self.max_zoom:.1f}x")

    def zoom_out(self):
        """缩小"""
        if self.zoom_level > self.min_zoom:
            self.zoom_level -= self.zoom_step
            print(f"缩放: {self.zoom_level:.1f}x")
        else:
            print(f"已达到最小缩放: {self.min_zoom:.1f}x")

    def reset_zoom(self):
        """重置缩放"""
        self.zoom_level = 1.0
        if self.use_hardware_zoom:
            self.set_hardware_zoom(1.0)
        print(f"缩放已重置: {self.zoom_level:.1f}x")

    def set_zoom_center(self, x, y):
        """
        设置缩放中心点

        Args:
            x: x坐标
            y: y坐标
        """
        self.zoom_center = (x, y)

    def reset_zoom_center(self):
        """重置缩放中心点为图像中心"""
        self.zoom_center = None

    def get_actual_resolution(self):
        """
        获取实际分辨率

        Returns:
            (width, height): 宽度和高度
        """
        if self.cap is None:
            return (0, 0)

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)

    def get_zoom_info(self):
        """
        获取缩放信息

        Returns:
            dict: 缩放相关信息
        """
        return {
            'zoom_level': self.zoom_level,
            'min_zoom': self.min_zoom,
            'max_zoom': self.max_zoom,
            'use_hardware_zoom': self.use_hardware_zoom
        }

    def get_statistics(self):
        """
        获取视频统计信息

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
        
        return {
            'frame_count': self.frame_count,
            'frame_read_errors': self.frame_read_errors,
            'error_rate': round(error_rate, 2),
            'avg_fps': round(avg_fps, 1),
            'real_time_fps': round(real_time_fps, 1),
            'latency_ms': round(latency, 1),
            'running_time_seconds': round(running_time, 1),
            'resolution': self.get_actual_resolution()
        }

    def is_opened(self):
        """摄像头是否已打开"""
        return self.cap is not None and self.cap.isOpened()

    def __enter__(self):
        """上下文管理器入口"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.release()


class CameraController(BaseCameraController):
    """摄像头控制器"""

    def __init__(self, camera_id=0, width=1280, height=720):
        """
        初始化摄像头控制器

        Args:
            camera_id: 摄像头ID
            width: 初始宽度
            height: 初始高度
        """
        self.camera_id = camera_id
        self.cap = None
        self.initial_width = width
        self.initial_height = height

        # 缩放参数
        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        self.zoom_step = 0.1
        self.use_hardware_zoom = False

        # 缩放中心点（图像中心）
        self.zoom_center = None

        # 统计信息
        self.frame_count = 0
        self.frame_read_errors = 0
        self.start_time = None
        self.last_frame_time = None
        self.frame_times = []
        self.fps_buffer = []
        self.buffer_size = 30  # 统计最近30帧的数据

    def open(self):
        """打开摄像头"""
        import time
        
        print(f"  尝试打开摄像头ID: {self.camera_id}...")
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            # 尝试其他摄像头ID和模式
            print(f"  ⚠ 无法使用摄像头ID {self.camera_id}，尝试其他ID...")
            for cam_id in [0, 1, 2]:
                print(f"  尝试摄像头ID: {cam_id}...")
                self.cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
                if self.cap.isOpened():
                    self.camera_id = cam_id
                    print(f"  ✓ 成功打开摄像头ID: {cam_id}")
                    break
            else:
                raise RuntimeError(f"无法打开摄像头，请检查摄像头是否被占用或需要权限")
        else:
            print(f"  ✓ cv2.VideoCapture打开成功")

        # 设置分辨率（但不强制，让摄像头使用默认分辨率）
        # 某些摄像头不支持设置分辨率，设置后可能导致无法读取
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.initial_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.initial_height)
        
        # 等待一下让设置生效
        time.sleep(0.1)

        # 尝试启用硬件缩放
        self._try_enable_hardware_zoom()
        
        # 初始化统计信息
        self.start_time = time.time()
        self.frame_count = 0
        self.frame_read_errors = 0
        self.frame_times = []
        self.fps_buffer = []

        print(f"✓ 摄像头已打开 (实际分辨率: {self.get_actual_resolution()})")
        if self.use_hardware_zoom:
            print(f"  硬件缩放: 支持")
        else:
            print(f"  硬件缩放: 不支持 (使用软件缩放)")

    def _try_enable_hardware_zoom(self):
        """尝试启用硬件缩放"""
        try:
            # 尝试设置缩放属性（部分摄像头支持）
            self.cap.set(cv2.CAP_PROP_ZOOM, 0)
            zoom = self.cap.get(cv2.CAP_PROP_ZOOM)
            if zoom is not None and zoom != 0:
                self.use_hardware_zoom = True
        except:
            self.use_hardware_zoom = False

    def set_hardware_zoom(self, zoom_level):
        """
        设置硬件缩放级别

        Args:
            zoom_level: 缩放级别 (1.0 = 无缩放)

        Returns:
            bool: 是否成功设置
        """
        if not self.use_hardware_zoom:
            return False

        try:
            # 将缩放级别映射到摄像头的缩放范围（通常是0-100或0-65535）
            hardware_zoom = int((zoom_level - 1.0) * 100)
            hardware_zoom = max(0, min(65535, hardware_zoom))
            self.cap.set(cv2.CAP_PROP_ZOOM, hardware_zoom)
            return True
        except:
            return False

    def software_zoom(self, frame, zoom_level):
        """
        软件缩放（通过裁剪和缩放图像）

        Args:
            frame: 输入帧
            zoom_level: 缩放级别 (1.0 = 无缩放, >1.0 放大)

        Returns:
            zoomed_frame: 缩放后的帧
        """
        if zoom_level <= 1.0:
            return frame

        height, width = frame.shape[:2]

        # 计算裁剪区域
        crop_width = int(width / zoom_level)
        crop_height = int(height / zoom_level)

        # 如果缩放中心点未设置，使用图像中心
        if self.zoom_center is None:
            center_x = width // 2
            center_y = height // 2
        else:
            center_x, center_y = self.zoom_center

        # 计算裁剪区域的左上角
        x1 = max(0, center_x - crop_width // 2)
        y1 = max(0, center_y - crop_height // 2)
        x2 = min(width, x1 + crop_width)
        y2 = min(height, y1 + crop_height)

        # 裁剪并缩放回原始尺寸
        cropped = frame[y1:y2, x1:x2]
        zoomed = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LINEAR)

        return zoomed

    def read(self):
        """
        读取帧（带缩放和错误处理）

        Returns:
            ret: 是否成功读取
            frame: 帧（已应用缩放）
        """
        import time
        
        if self.cap is None:
            return False, None

        try:
            ret, frame = self.cap.read()
            if not ret:
                self.frame_read_errors += 1
                return ret, frame
            
            # 检查帧是否有效
            if frame is None or frame.size == 0:
                self.frame_read_errors += 1
                return False, None

            # 初始化开始时间
            if self.start_time is None:
                self.start_time = time.time()
                self.last_frame_time = self.start_time
            
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
                if self.use_hardware_zoom:
                    self.set_hardware_zoom(self.zoom_level)
                else:
                    frame = self.software_zoom(frame, self.zoom_level)

            return ret, frame
            
        except Exception as e:
            # 捕获解码错误，返回读取失败
            self.frame_read_errors += 1
            print(f"摄像头读取错误: {e}")
            return False, None

    def set_zoom(self, zoom_level):
        """
        设置缩放级别

        Args:
            zoom_level: 缩放级别 (1.0 = 无缩放, >1.0 放大, <1.0 缩小)
        """
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, zoom_level))

    def zoom_in(self):
        """放大"""
        if self.zoom_level < self.max_zoom:
            self.zoom_level += self.zoom_step
            print(f"缩放: {self.zoom_level:.1f}x")
        else:
            print(f"已达到最大缩放: {self.max_zoom:.1f}x")

    def zoom_out(self):
        """缩小"""
        if self.zoom_level > self.min_zoom:
            self.zoom_level -= self.zoom_step
            print(f"缩放: {self.zoom_level:.1f}x")
        else:
            print(f"已达到最小缩放: {self.min_zoom:.1f}x")

    def reset_zoom(self):
        """重置缩放"""
        self.zoom_level = 1.0
        if self.use_hardware_zoom:
            self.set_hardware_zoom(1.0)
        print(f"缩放已重置: {self.zoom_level:.1f}x")

    def set_zoom_center(self, x, y):
        """
        设置缩放中心点

        Args:
            x: x坐标
            y: y坐标
        """
        self.zoom_center = (x, y)

    def reset_zoom_center(self):
        """重置缩放中心点为图像中心"""
        self.zoom_center = None

    def get_actual_resolution(self):
        """
        获取实际分辨率

        Returns:
            (width, height): 宽度和高度
        """
        if self.cap is None:
            return (0, 0)

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)

    def get_zoom_info(self):
        """
        获取缩放信息

        Returns:
            dict: 缩放相关信息
        """
        return {
            'zoom_level': self.zoom_level,
            'min_zoom': self.min_zoom,
            'max_zoom': self.max_zoom,
            'use_hardware_zoom': self.use_hardware_zoom
        }

    def get_statistics(self):
        """
        获取视频统计信息

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
        
        return {
            'frame_count': self.frame_count,
            'frame_read_errors': self.frame_read_errors,
            'error_rate': round(error_rate, 2),
            'avg_fps': round(avg_fps, 1),
            'real_time_fps': round(real_time_fps, 1),
            'latency_ms': round(latency, 1),
            'running_time_seconds': round(running_time, 1),
            'resolution': self.get_actual_resolution()
        }

    def is_opened(self):
        """摄像头是否已打开"""
        return self.cap is not None and self.cap.isOpened()

    def release(self):
        """释放摄像头"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("✓ 摄像头已释放")

    def __enter__(self):
        """上下文管理器入口"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.release()
