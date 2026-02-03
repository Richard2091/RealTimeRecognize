"""
摄像头工厂类
使用工厂模式创建不同类型的摄像头实例
"""
from typing import Dict, Any, Optional, Union
from .base_camera import BaseCamera
from .local_camera import LocalCamera
from .rtsp_camera import RTSPCamera


class CameraFactory:
    """摄像头工厂类"""
    
    @staticmethod
    def create_camera(config: Dict[str, Any]) -> Optional[BaseCamera]:
        """
        根据配置创建摄像头实例
        
        Args:
            config: 摄像头配置字典
                {
                    'type': 'local' or 'rtsp',
                    'camera_id': int (local摄像头),
                    'rtsp_url': str (RTSP摄像头),
                    'width': int,
                    'height': int,
                    'timeout': int (RTSP)
                }
        
        Returns:
            摄像头实例或None
        """
        try:
            camera_type = config.get('type', 'local')
            
            if camera_type == 'local':
                return CameraFactory._create_local_camera(config)
            elif camera_type == 'rtsp':
                return CameraFactory._create_rtsp_camera(config)
            else:
                print(f"不支持的摄像头类型: {camera_type}")
                return None
                
        except Exception as e:
            print(f"创建摄像头失败: {e}")
            return None
    
    @staticmethod
    def _create_local_camera(config: Dict[str, Any]) -> Optional[LocalCamera]:
        """创建本地摄像头"""
        try:
            camera_id = config.get('camera_id', 0)
            width = config.get('width', 640)
            height = config.get('height', 480)
            
            camera = LocalCamera(
                camera_id=camera_id,
                width=width,
                height=height
            )
            
            if camera.open():
                return camera
            else:
                print(f"无法打开本地摄像头ID: {camera_id}")
                return None
                
        except Exception as e:
            print(f"创建本地摄像头失败: {e}")
            return None
    
    @staticmethod
    def _create_rtsp_camera(config: Dict[str, Any]) -> Optional[RTSPCamera]:
        """创建RTSP摄像头"""
        try:
            rtsp_url = config.get('rtsp_url')
            if not rtsp_url:
                print("RTSP URL不能为空")
                return None
            
            width = config.get('width', 1280)
            height = config.get('height', 720)
            timeout = config.get('timeout', 10)
            
            camera = RTSPCamera(
                rtsp_url=rtsp_url,
                width=width,
                height=height,
                timeout=timeout
            )
            
            if camera.open():
                return camera
            else:
                print(f"无法打开RTSP摄像头: {rtsp_url}")
                return None
                
        except Exception as e:
            print(f"创建RTSP摄像头失败: {e}")
            return None
    
    @staticmethod
    def detect_available_cameras(max_id: int = 3) -> Dict[int, str]:
        """
        检测可用的本地摄像头

        Args:
            max_id: 最大检测ID

        Returns:
            摄像头ID和名称的字典
        """
        cameras = {}
        available_cameras = LocalCamera.detect_cameras(max_id)
        for camera_id in available_cameras:
            cameras[camera_id] = f"摄像头 {camera_id}"
        return cameras
    
    @staticmethod
    def build_config(camera_type: str, **kwargs) -> Dict[str, Any]:
        """
        构建摄像头配置
        
        Args:
            camera_type: 'local' or 'rtsp'
            **kwargs: 其他配置参数
            
        Returns:
            配置字典
        """
        config = {'type': camera_type}
        config.update(kwargs)
        return config
