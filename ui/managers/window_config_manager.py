"""
窗口配置管理器
负责UI组件与配置的映射（不处理文件IO）
"""
from PyQt5.QtCore import QRect
from ui.managers.config_file_manager import config_manager


class WindowConfigManager:
    """窗口配置管理器 - UI配置适配器"""

    def apply_to_ui(self, control_panel, main_window, config):
        """
        将配置应用到UI组件

        Args:
            control_panel: 控制面板实例
            main_window: 主窗口实例
            config: 配置字典
        """
        try:
            # 应用功能开关
            pose_checkbox = control_panel.get_component('pose_checkbox')
            emotion_checkbox = control_panel.get_component('emotion_checkbox')
            skeleton_checkbox = control_panel.get_component('skeleton_checkbox')
            mirror_checkbox = control_panel.get_component('mirror_checkbox')

            pose_checkbox.setChecked(config_manager.get_config_value(config, 'use_pose', False))
            emotion_checkbox.setChecked(config_manager.get_config_value(config, 'use_emotion', False))
            skeleton_checkbox.setChecked(config_manager.get_config_value(config, 'show_skeleton', False))
            mirror_checkbox.setChecked(config_manager.get_config_value(config, 'mirror_mode', False))

            # 应用窗口几何
            geometry = config_manager.get_config_value(config, 'window_geometry', {})
            if geometry:
                main_window.setGeometry(QRect(
                    geometry.get('x', 100),
                    geometry.get('y', 100),
                    geometry.get('width', 1400),
                    geometry.get('height', 900)
                ))

            # 应用分割器大小
            splitter_sizes = config_manager.get_config_value(config, 'splitter_sizes', [600, 30])
            if hasattr(main_window, 'main_splitter'):
                main_window.main_splitter.setSizes(splitter_sizes)

        except Exception as e:
            print(f"应用配置失败: {e}")

    def save_from_ui(self, control_panel, main_window, config):
        """
        从UI更新配置字典

        Args:
            control_panel: 控制面板实例
            main_window: 主窗口实例
            config: 配置字典（会被修改）
        """
        try:
            # 从UI获取当前状态
            model_combo = control_panel.get_component('model_combo')
            pose_checkbox = control_panel.get_component('pose_checkbox')
            emotion_checkbox = control_panel.get_component('emotion_checkbox')
            skeleton_checkbox = control_panel.get_component('skeleton_checkbox')
            mirror_checkbox = control_panel.get_component('mirror_checkbox')

            # 更新配置字典
            config['selected_model'] = model_combo.currentData() if model_combo.currentData() else None
            config['use_pose'] = pose_checkbox.isChecked()
            config['use_emotion'] = emotion_checkbox.isChecked()
            config['show_skeleton'] = skeleton_checkbox.isChecked()
            config['mirror_mode'] = mirror_checkbox.isChecked()

            # 保存窗口几何信息
            geometry = main_window.geometry()
            config['window_geometry'] = {
                'x': geometry.x(),
                'y': geometry.y(),
                'width': geometry.width(),
                'height': geometry.height()
            }

            # 保存分割器大小
            if hasattr(main_window, 'main_splitter'):
                config['splitter_sizes'] = main_window.main_splitter.sizes()

            # 保存配置文件
            config_manager.save_config(config)

        except Exception as e:
            print(f"保存配置失败: {e}")
