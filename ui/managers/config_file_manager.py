"""
配置文件管理器
负责config.json文件的读写操作
"""
import json
import os
from pathlib import Path


class ConfigFileManager:
    """配置文件管理器类 - 专注于配置文件的IO操作"""

    def __init__(self):
        # 配置文件路径
        self.config_file = Path("config.json")

    def load_config(self):
        """
        加载配置文件

        Returns:
            dict: 配置字典
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print("✓ 配置文件加载成功")
                return config
            else:
                print("⚠ 配置文件不存在，创建默认配置")
                # 创建默认配置
                default_config = self._create_default_config()
                self.save_config(default_config)
                return default_config
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}")
            return self._create_default_config()

    def _create_default_config(self):
        """创建默认配置"""
        return {
            "models": {
                "yolov8n": {
                    "display": "YOLOv8n (轻量级)",
                    "file": "model/yolo8/yolov8n.pt",
                    "type": "YOLOv8"
                },
                "yolov8s": {
                    "display": "YOLOv8s (标准版)",
                    "file": "model/yolo8/yolov8s.pt",
                    "type": "YOLOv8"
                },
                "yolo26n": {
                    "display": "YOLO26n (最新边缘优化，CPU快43%)",
                    "file": "model/yolo26/yolo26n.pt",
                    "type": "YOLO26"
                },
                "yolo26s": {
                    "display": "YOLO26s (边缘优化标准版)",
                    "file": "model/yolo26/yolo26s.pt",
                    "type": "YOLO26"
                },
                "yolov8s-worldv2": {
                    "display": "YOLO-World (开放词汇，自定义类别)",
                    "file": "model/yoloworld/yolov8s-worldv2.pt",
                    "type": "YOLO-World"
                }
            },
            "rtsp_url": "",
            "camera_source": "local",
            "use_pose": False,
            "use_emotion": False,
            "show_skeleton": False,
            "mirror_mode": False,
            "selected_model": "yolov8n",
            "window_geometry": {
                "x": 100,
                "y": 100,
                "width": 1400,
                "height": 900
            },
            "camera_settings": {
                "width": 1280,
                "height": 720
            },
            "show_statistics": True,
            "splitter_sizes": [600, 30],
            "selected_camera_id": 0
        }

    def save_config(self, config):
        """
        保存配置文件

        Args:
            config (dict): 配置字典
        """
        try:
            # 创建备份
            if self.config_file.exists():
                backup_file = self.config_file.with_suffix('.json.bak')
                self.config_file.rename(backup_file)

            # 保存新配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            # 删除备份
            backup_file = self.config_file.with_suffix('.json.bak')
            if backup_file.exists():
                backup_file.unlink()

            print("✓ 配置文件保存成功")
            return True
        except Exception as e:
            print(f"❌ 配置文件保存失败: {e}")
            # 恢复备份
            backup_file = self.config_file.with_suffix('.json.bak')
            if backup_file.exists():
                backup_file.rename(self.config_file)
            return False

    def get_config_value(self, config, key, default=None):
        """
        获取配置值（支持嵌套键）

        Args:
            config (dict): 配置字典
            key (str): 键名，支持点号分隔的嵌套键（如"window_geometry.x"）
            default: 默认值

        Returns:
            配置值
        """
        try:
            if '.' in key:
                keys = key.split('.')
                value = config
                for k in keys:
                    value = value[k]
                return value
            else:
                return config.get(key, default)
        except (KeyError, TypeError):
            return default

    def set_config_value(self, config, key, value):
        """
        设置配置值（支持嵌套键）

        Args:
            config (dict): 配置字典
            key (str): 键名，支持点号分隔的嵌套键
            value: 值
        """
        try:
            if '.' in key:
                keys = key.split('.')
                target = config
                for k in keys[:-1]:
                    if k not in target:
                        target[k] = {}
                    target = target[k]
                target[keys[-1]] = value
            else:
                config[key] = value
        except Exception as e:
            print(f"❌ 设置配置值失败: {e}")


# 全局配置文件管理器实例
config_manager = ConfigFileManager()
