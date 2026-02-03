"""
显示区域组件
只包含视频显示区域和状态标签
"""
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class DisplayArea:
    """显示区域组件管理器"""

    def __init__(self):
        self.frame = None
        self.components = {}

    def create_display_area(self):
        """创建显示区域"""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout()

        # 视频显示标签
        video_label = QLabel("等待启动...")
        video_label.setAlignment(Qt.AlignCenter)
        # 移除最小高度限制，允许底部信息区域展开到任意高度
        # 只设置最小宽度，不设置最小高度
        video_label.setMinimumWidth(800)
        layout.addWidget(video_label, 1)  # 使用stretch=1让视频区域占据主要空间

        # 状态标签
        status_label = QLabel("状态: 就绪")
        layout.addWidget(status_label)

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