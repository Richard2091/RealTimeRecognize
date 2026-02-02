"""
摄像头控制器模块
支持硬件和软件缩放功能
"""
import cv2
import numpy as np


class CameraController:
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

    def open(self):
        """打开摄像头"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"无法打开摄像头 {self.camera_id}")

        # 设置分辨率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.initial_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.initial_height)

        # 尝试启用硬件缩放
        self._try_enable_hardware_zoom()

        print(f"✓ 摄像头已打开 (分辨率: {self.get_actual_resolution()})")
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
        读取帧（带缩放）

        Returns:
            ret: 是否成功读取
            frame: 帧（已应用缩放）
        """
        if self.cap is None:
            return False, None

        ret, frame = self.cap.read()
        if not ret:
            return ret, frame

        self.frame_count += 1

        # 应用缩放
        if self.zoom_level != 1.0:
            if self.use_hardware_zoom:
                self.set_hardware_zoom(self.zoom_level)
            else:
                frame = self.software_zoom(frame, self.zoom_level)

        return ret, frame

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
