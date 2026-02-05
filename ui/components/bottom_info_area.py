"""
底部信息显示区域组件
类似IDEA侧栏，按钮在底部，默认只显示按钮高度
"""
from PyQt5.QtWidgets import (QFrame, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QStackedWidget)
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QTextCursor


class BottomInfoArea(QObject):
    """底部信息显示区域组件（IDEA侧栏样式）"""

    def __init__(self):
        super().__init__()
        self.stacked_widget = None
        self.components = {}
        self.current_button = None  # 当前选中的按钮
        self.active_panel = None  # 当前展开的面板
        self.is_expanded = False  # 是否已展开
        self.expanded_height = 200  # 展开时的默认高度
        self.loading_config = False  # 是否正在加载配置（用于避免触发回调）

    def create_bottom_info_area(self):
        """创建底部信息显示区域"""
        # 创建外层Frame，添加黑色边框
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)

        # 创建主垂直布局
        main_layout = QVBoxLayout(frame)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建顶部标签栏（水平排列）
        tab_bar = QWidget()
        tab_bar.setFixedHeight(30)
        tab_layout = QHBoxLayout(tab_bar)
        tab_layout.setContentsMargins(5, 0, 0, 0)
        tab_layout.setSpacing(2)

        # 创建"视频信息"标签按钮
        video_btn = self._create_tab_button("📊 视频信息")
        video_btn.clicked.connect(lambda: self._on_button_clicked(video_btn, 0))
        self.video_btn = video_btn

        # 创建"后台日志"标签按钮
        log_btn = self._create_tab_button("📋 后台日志")
        log_btn.clicked.connect(lambda: self._on_button_clicked(log_btn, 1))
        self.log_btn = log_btn

        tab_layout.addWidget(video_btn)
        tab_layout.addWidget(log_btn)
        tab_layout.addStretch()

        # 创建内容区域（使用StackedWidget，动态高度）
        stacked_widget = QStackedWidget()
        self.stacked_widget = stacked_widget

        # 创建视频信息面板
        info_panel = QWidget()
        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(5, 5, 5, 5)

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setPlaceholderText("视频信息将在此显示...")
        # 设置无边框样式
        info_text.setStyleSheet("QTextEdit { border: none; background-color: #ffffff; }")
        # 移除最大高度限制，允许自适应扩展
        info_text.setMinimumHeight(100)
        info_layout.addWidget(info_text)

        # 创建后台日志面板
        log_panel = QWidget()
        log_layout = QVBoxLayout(log_panel)
        log_layout.setContentsMargins(5, 5, 5, 5)

        log_text = QTextEdit()
        log_text.setReadOnly(True)
        log_text.setPlaceholderText("后台日志将在此显示...")
        # 设置日志样式：等宽字体，无边框
        log_text.setStyleSheet("QTextEdit { border: none; background-color: #ffffff; font-family: Consolas, Monaco, monospace; font-size: 10pt; }")
        # 移除最大高度限制，允许自适应扩展
        log_text.setMinimumHeight(100)
        log_layout.addWidget(log_text)

        # 添加面板到StackedWidget
        stacked_widget.addWidget(info_panel)  # index 0
        stacked_widget.addWidget(log_panel)   # index 1

        # 将内容区域和标签栏添加到主布局（标签栏在底部）
        main_layout.addWidget(stacked_widget)
        main_layout.addWidget(tab_bar)

        # 保存组件引用
        self.components.update({
            'frame': frame,
            'stacked_widget': stacked_widget,
            'info_text': info_text,
            'log_text': log_text,
            'video_btn': video_btn,
            'log_btn': log_btn
        })

        # 默认隐藏内容区域，只显示标签栏
        stacked_widget.hide()

        return frame

    def _create_tab_button(self, text):
        """创建标签页按钮（横向样式）"""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setSizePolicy(btn.sizePolicy().Preferred, btn.sizePolicy().Fixed)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333333;
                border: none;
                border-top: 2px solid transparent;
                padding: 5px 15px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:checked {
                background-color: #ffffff;
                color: #2196F3;
                font-weight: bold;
                border-top: 2px solid #2196F3;
            }
            QPushButton:!checked {
                background-color: #e8e8e8;
            }
        """)
        return btn

    def _on_button_clicked(self, clicked_btn, index):
        """按钮点击事件处理"""
        # 如果点击的是当前已选中的按钮，则收起
        if clicked_btn == self.current_button:
            self.collapse_panel()
            clicked_btn.setChecked(False)
            self.current_button = None
            self.active_panel = None
            self.is_expanded = False
        else:
            # 切换到新面板
            if self.current_button:
                self.current_button.setChecked(False)

            clicked_btn.setChecked(True)
            self.current_button = clicked_btn
            self.active_panel = index
            self.stacked_widget.setCurrentIndex(index)
            self.stacked_widget.show()
            self.is_expanded = True
            # 如果不是在加载配置，则通知主窗口更新分割器高度
            if not self.loading_config and hasattr(self, 'on_expand'):
                self.on_expand()

    def collapse_panel(self):
        """收起当前展开的面板"""
        self.stacked_widget.hide()
        self.is_expanded = False
        # 如果不是在加载配置，则通知主窗口更新分割器高度
        if not self.loading_config and hasattr(self, 'on_collapse'):
            self.on_collapse()

    def get_splitter_height(self, tab_bar_height, expanded=False):
        """
        获取分割器高度

        Args:
            tab_bar_height: 标签栏高度
            expanded: 是否展开状态

        Returns:
            int: 分割器高度
        """
        if expanded:
            return self.expanded_height + tab_bar_height
        else:
            return tab_bar_height

    def update_expanded_height(self, current_height, tab_bar_height):
        """
        更新展开高度

        Args:
            current_height: 当前分割器高度
            tab_bar_height: 标签栏高度
        """
        if self.is_expanded:
            self.expanded_height = current_height - tab_bar_height

    def apply_config_to_splitter(self, splitter, tab_bar_height):
        """
        应用配置到分割器

        Args:
            splitter: 分割器对象
            tab_bar_height: 标签栏高度
        """
        # 设置加载配置标志，避免触发回调
        self.loading_config = True

        # 根据展开状态调整分割器
        if self.is_expanded:
            # 展开状态：确保分割器高度足够显示内容，并显示分割线
            splitter.setHandleWidth(6)
            current_sizes = splitter.sizes()
            top_height = current_sizes[0]
            total_height = top_height + current_sizes[1]
            # 如果底部高度小于标签栏+展开高度，则调整
            if current_sizes[1] < self.expanded_height + tab_bar_height:
                expanded_height = self.expanded_height + tab_bar_height
                splitter.setSizes([top_height, expanded_height])
        else:
            # 收起状态：确保底部高度只有标签栏高度，并隐藏分割线
            current_sizes = splitter.sizes()
            top_height = current_sizes[0]
            splitter.setSizes([top_height, tab_bar_height])
            splitter.setHandleWidth(0)

        # 恢复加载配置标志
        self.loading_config = False

    def switch_panel(self, panel_index):
        """
        切换到底部信息栏的指定面板

        Args:
            panel_index: 面板索引（0=视频信息，1=后台日志）
        """
        if panel_index == 0:
            self._on_button_clicked(self.video_btn, 0)
        elif panel_index == 1:
            self._on_button_clicked(self.log_btn, 1)

    def get_component(self, name):
        """获取指定组件"""
        return self.components.get(name)

    def get_all_components(self):
        """获取所有组件"""
        return self.components

    def append_log(self, message):
        """追加日志到日志文本框"""
        log_text = self.get_component('log_text')
        if log_text:
            # 移动光标到末尾
            cursor = log_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            log_text.setTextCursor(cursor)
            log_text.insertPlainText(message)
            # 自动滚动到底部
            log_text.ensureCursorVisible()
