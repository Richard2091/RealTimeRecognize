"""
显示区域组件
只包含视频显示区域和状态标签
"""
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt


class DisplayArea:
    """显示区域组件管理器"""

    def __init__(self):
        self.frame = None
        self.components = {}

    def create_display_area(self):
        """创建显示区域"""
        frame = QFrame()
        frame.setFrameShape(QFrame.NoFrame)  # 无边框
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 移除边距

        # 状态标签
        status_label = QLabel("状态: 就绪")
        status_label.setAlignment(Qt.AlignCenter)
        status_size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        status_label.setSizePolicy(status_size_policy)
        layout.addWidget(status_label)

        # 视频显示标签
        video_label = QLabel("等待启动...")
        video_label.setAlignment(Qt.AlignCenter)
        # 设置尺寸策略：可扩展且可以缩小
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        video_label.setSizePolicy(size_policy)
        # 设置最小尺寸，允许在需要时缩小
        video_label.setMinimumSize(400, 300)
        layout.addWidget(video_label, 1)  # 使用stretch=1让视频区域占据主要空间

        frame.setLayout(layout)
        self.frame = frame

        # 保存组件引用
        self.components.update({
            'video_label': video_label,
            'status_label': status_label
        })

        return frame

    def get_component(self, name):
        """获取指定组件"""
        return self.components.get(name)

    def get_all_components(self):
        """获取所有组件"""
        return self.components