"""
显示区域组件
包含右侧视频显示区域和统计信息显示
"""
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QTextEdit, QSizeGrip
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
        video_label.setMinimumSize(800, 600)
        layout.addWidget(video_label)
        
        # 状态标签
        status_label = QLabel("状态: 就绪")
        layout.addWidget(status_label)
        
        # 统计信息显示容器
        stats_container = QFrame()
        stats_container.setFrameShape(QFrame.Box)
        stats_layout = QVBoxLayout(stats_container)
        
        # 统计信息标题
        stats_title = QLabel("视频统计信息")
        stats_title.setStyleSheet("font-weight: bold; font-size: 12px;")
        stats_layout.addWidget(stats_title)
        
        # 统计信息显示文本框（可调整大小）
        stats_text = QTextEdit()
        stats_text.setReadOnly(True)
        stats_text.setMinimumHeight(100)
        stats_text.setMaximumHeight(250)
        stats_text.setPlaceholderText("视频统计信息将在此显示...")
        stats_layout.addWidget(stats_text)
        
        # 添加大小调整手柄
        size_grip = QSizeGrip(stats_container)
        stats_layout.addWidget(size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        
        layout.addWidget(stats_container)
        
        frame.setLayout(layout)
        self.frame = frame
        
        # 保存组件引用
        self.components.update({
            'video_label': video_label,
            'status_label': status_label,
            'stats_text': stats_text
        })
        
        return frame
    
    def get_component(self, name):
        """获取指定组件"""
        return self.components.get(name)
    
    def get_all_components(self):
        """获取所有组件"""
        return self.components