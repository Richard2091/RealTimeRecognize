"""
底部信息显示区域组件
类似IDEA侧栏，按钮在底部，默认只显示按钮高度
"""
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import (QFrame, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QStackedWidget)

from .tabs import (VideoTab, PerformanceTab, DetectionTab, 
                   ResourceTab, RTSPTab, LogTab)


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
        self.panel_names = ['video', 'performance', 'detection', 'resource', 'rtsp', 'log']  # 面板名称列表

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

        # 创建标签按钮和对应面板
        self.tab_buttons = {}
        self.panels = {}
        
        # 创建各个标签页实例
        self.tabs = {
            'video': VideoTab(),
            'performance': PerformanceTab(),
            'detection': DetectionTab(),
            'resource': ResourceTab(),
            'rtsp': RTSPTab(),
            'log': LogTab()
        }
        
        # 创建标签按钮和连接信号
        for i, (tab_name, tab_instance) in enumerate(self.tabs.items()):
            # 创建按钮
            btn = self._create_tab_button(tab_instance.get_button_text())
            # 修复闭包问题：使用默认参数捕获当前值
            btn.clicked.connect(lambda checked, btn=btn, idx=i: self._on_button_clicked(btn, idx))
            self.tab_buttons[tab_name] = btn
            self.panels[tab_name] = tab_instance
            
            # 添加到标签栏
            tab_layout.addWidget(btn)
        
        tab_layout.addStretch()
        
        # 隐藏RTSP标签（默认隐藏，只有在RTSP模式下才显示）
        self.tab_buttons['rtsp'].hide()

        # 创建内容区域（使用StackedWidget，动态高度）
        stacked_widget = QStackedWidget()
        self.stacked_widget = stacked_widget

        # 将所有面板添加到StackedWidget
        for tab_instance in self.tabs.values():
            stacked_widget.addWidget(tab_instance)

        # 将内容区域和标签栏添加到主布局（标签栏在底部）
        main_layout.addWidget(stacked_widget)
        main_layout.addWidget(tab_bar)

        # 保存组件引用
        self.components.update({
            'frame': frame,
            'stacked_widget': stacked_widget,
            'log_text': self.tabs['log'].get_text_edit(),
            'rtsp_btn': self.tab_buttons['rtsp'],  # 保存RTSP按钮引用，方便控制显示/隐藏
        })
        
        # 保存所有面板和按钮
        for name, panel in self.panels.items():
            self.components[f'{name}_panel'] = panel
        for name, btn in self.tab_buttons.items():
            self.components[f'{name}_btn'] = btn

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
            panel_index: 面板索引（0=视频信息，1=性能指标，2=检测信息，3=资源使用，4=RTSP信息，5=后台日志）
        """
        # 根据索引获取对应的标签名称
        tab_names = list(self.tabs.keys())
        if 0 <= panel_index < len(tab_names):
            tab_name = tab_names[panel_index]
            btn = self.tab_buttons.get(tab_name)
            if btn:
                self._on_button_clicked(btn, panel_index)
    
    def set_rtsp_visible(self, visible):
        """
        设置RTSP标签是否可见
        
        Args:
            visible: 是否可见
        """
        rtsp_btn = self.tab_buttons.get('rtsp')
        if rtsp_btn:
            rtsp_btn.setVisible(visible)

    def get_component(self, name):
        """获取指定组件"""
        return self.components.get(name)

    def get_all_components(self):
        """获取所有组件"""
        return self.components

    def append_log(self, message):
        """追加日志到日志文本框"""
        log_tab = self.tabs.get('log')
        if log_tab:
            log_tab.append_log(message)

    def update_video_info(self, info_dict):
        """
        更新视频信息面板（分别更新不同的标签）

        Args:
            info_dict: 包含视频信息的字典
        """
        # 1. 更新视频信息标签
        video_tab = self.tabs.get('video')
        if video_tab:
            video_tab.update_content(info_dict)

        # 2. 更新性能指标标签
        performance_tab = self.tabs.get('performance')
        if performance_tab:
            performance_tab.update_content(info_dict)

        # 3. 更新检测信息标签
        detection_tab = self.tabs.get('detection')
        if detection_tab:
            detection_tab.update_content(info_dict)

        # 4. 更新资源使用标签
        resource_tab = self.tabs.get('resource')
        if resource_tab:
            resource_tab.update_content(info_dict)

        # 5. 更新RTSP信息标签（仅RTSP模式下有数据）
        if 'rtsp_url' in info_dict:
            rtsp_tab = self.tabs.get('rtsp')
            if rtsp_tab:
                rtsp_tab.update_content(info_dict)
                
                # 显示RTSP标签
                rtsp_btn = self.tab_buttons.get('rtsp')
                if rtsp_btn:
                    rtsp_btn.show()
