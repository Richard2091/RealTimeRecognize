"""
摄像头管理器类
统一管理摄像头实例，提供状态管理和事件通知
"""
import time
from typing import Optional, Dict, Any, Callable, List
from PyQt5.QtCore import QObject, pyqtSignal
from .base_camera import BaseCamera
from .camera_factory import CameraFactory


class CameraState:
    """摄像头状态枚举"""
    CLOSED = "closed"              # 已关闭
    OPENING = "opening"            # 正在打开
    OPENED = "opened"              # 已打开
    READING = "reading"            # 正在读取
    ERROR = "error"                # 错误状态
    RECONNECTING = "reconnecting"  # 正在重连


class CameraEvent:
    """摄像头事件枚举"""
    STATE_CHANGED = "state_changed"
    FRAME_READ = "frame_read"
    ERROR_OCCURRED = "error_occurred"
    CONFIG_CHANGED = "config_changed"


class CameraManager(QObject):
    """摄像头管理器，提供统一的摄像头管理接口"""
    
    # 信号定义
    state_changed = pyqtSignal(str, str)  # (old_state, new_state)
    frame_ready = pyqtSignal(object)      # (frame)
    error_occurred = pyqtSignal(str)      # (error_message)
    camera_opened = pyqtSignal()          # 摄像头已打开
    camera_closed = pyqtSignal()          # 摄像头已关闭
    
    def __init__(self):
        super().__init__()
        self._camera: Optional[BaseCamera] = None
        self._config: Dict[str, Any] = {}
        self._state = CameraState.CLOSED
        self._is_reading = False
        self._read_thread = None
        self._event_listeners: Dict[str, List[Callable]] = {
            CameraEvent.STATE_CHANGED: [],
            CameraEvent.FRAME_READ: [],
            CameraEvent.ERROR_OCCURRED: [],
            CameraEvent.CONFIG_CHANGED: []
        }
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化摄像头管理器
        
        Args:
            config: 摄像头配置
            
        Returns:
            是否成功
        """
        try:
            self._config = config.copy()
            print(f"摄像头管理器初始化: {config}")
            return True
        except Exception as e:
            self._notify_error(f"初始化失败: {e}")
            return False
    
    def open_camera(self) -> bool:
        """打开摄像头"""
        if self._state != CameraState.CLOSED:
            self._notify_error(f"无法打开摄像头，当前状态: {self._state}")
            return False
        
        try:
            # 状态转换：closed -> opening
            self._change_state(CameraState.OPENING)
            
            # 创建摄像头实例
            self._camera = CameraFactory.create_camera(self._config)
            
            if self._camera is None:
                self._notify_error("创建摄像头实例失败")
                self._change_state(CameraState.CLOSED)
                return False
            
            # 状态转换：opening -> opened
            self._change_state(CameraState.OPENED)
            self.camera_opened.emit()
            print("✓ 摄像头已打开")
            
            return True
            
        except Exception as e:
            self._notify_error(f"打开摄像头失败: {e}")
            self._change_state(CameraState.ERROR)
            return False
    
    def close_camera(self) -> bool:
        """关闭摄像头"""
        if self._camera is None:
            return True
        
        try:
            # 停止读取
            if self._is_reading:
                self.stop_reading()
            
            # 释放摄像头
            self._camera.release()
            self._camera = None
            
            # 状态转换
            self._change_state(CameraState.CLOSED)
            self.camera_closed.emit()
            print("✓ 摄像头已关闭")
            
            return True
            
        except Exception as e:
            self._notify_error(f"关闭摄像头失败: {e}")
            return False
    
    def start_reading(self) -> bool:
        """开始读取帧"""
        if self._state != CameraState.OPENED:
            self._notify_error(f"无法开始读取，当前状态: {self._state}")
            return False
        
        if self._is_reading:
            return True
        
        try:
            self._is_reading = True
            # 状态转换：opened -> reading
            self._change_state(CameraState.READING)
            print("✓ 开始读取帧")
            
            return True
            
        except Exception as e:
            self._notify_error(f"开始读取失败: {e}")
            return False
    
    def stop_reading(self) -> bool:
        """停止读取帧"""
        if not self._is_reading:
            return True
        
        try:
            self._is_reading = False
            
            # 状态转换：reading -> opened
            if self._state == CameraState.READING:
                self._change_state(CameraState.OPENED)
            
            print("✓ 停止读取帧")
            return True
            
        except Exception as e:
            self._notify_error(f"停止读取失败: {e}")
            return False
    
    def read_frame(self) -> tuple:
        """
        读取一帧
        
        Returns:
            (ret, frame): ret为是否成功，frame为图像数据或None
        """
        if self._camera is None:
            return False, None
        
        if self._state not in [CameraState.OPENED, CameraState.READING]:
            return False, None
        
        try:
            ret, frame = self._camera.read()
            
            if ret and frame is not None:
                # 通知监听器
                self._notify_listeners(CameraEvent.FRAME_READ, frame)
                self.frame_ready.emit(frame)
            elif not ret:
                # 读取失败，尝试错误处理
                self._handle_read_error()
            
            return ret, frame
            
        except Exception as e:
            self._notify_error(f"读取帧失败: {e}")
            return False, None
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """
        更新配置
        
        Args:
            config: 新配置
            
        Returns:
            是否成功
        """
        try:
            # 如果摄像头已打开，需要先关闭
            if self._state != CameraState.CLOSED:
                self.close_camera()
            
            self._config = config.copy()
            self._notify_listeners(CameraEvent.CONFIG_CHANGED, config)
            return True
            
        except Exception as e:
            self._notify_error(f"更新配置失败: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取摄像头统计信息"""
        if self._camera is None:
            return {}
        
        try:
            return self._camera.get_statistics()
        except Exception as e:
            self._notify_error(f"获取统计信息失败: {e}")
            return {}
    
    def get_state(self) -> str:
        """获取当前状态"""
        return self._state
    
    def is_opened(self) -> bool:
        """检查摄像头是否已打开"""
        return self._state in [CameraState.OPENED, CameraState.READING]
    
    def is_reading(self) -> bool:
        """检查是否正在读取"""
        return self._is_reading
    
    def add_event_listener(self, event: str, callback: Callable):
        """
        添加事件监听器
        
        Args:
            event: 事件类型
            callback: 回调函数
        """
        if event in self._event_listeners:
            self._event_listeners[event].append(callback)
    
    def remove_event_listener(self, event: str, callback: Callable):
        """
        移除事件监听器
        
        Args:
            event: 事件类型
            callback: 回调函数
        """
        if event in self._event_listeners and callback in self._event_listeners[event]:
            self._event_listeners[event].remove(callback)
    
    def _change_state(self, new_state: str):
        """状态转换"""
        old_state = self._state
        self._state = new_state
        
        # 通知状态变化
        self._notify_listeners(CameraEvent.STATE_CHANGED, {
            'old_state': old_state,
            'new_state': new_state
        })
        self.state_changed.emit(old_state, new_state)
    
    def _notify_listeners(self, event: str, data: Any):
        """通知事件监听器"""
        if event in self._event_listeners:
            for callback in self._event_listeners[event]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"事件监听器回调失败: {e}")
    
    def _notify_error(self, message: str):
        """通知错误"""
        self._notify_listeners(CameraEvent.ERROR_OCCURRED, message)
        self.error_occurred.emit(message)
    
    def _handle_read_error(self):
        """处理读取错误"""
        # 可以在这里实现重连逻辑
        self._error_count += 1 if hasattr(self, '_error_count') else 0
    
    @property
    def camera(self) -> Optional[BaseCamera]:
        """获取当前摄像头实例"""
        return self._camera
    
    @property
    def config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self._config.copy()
