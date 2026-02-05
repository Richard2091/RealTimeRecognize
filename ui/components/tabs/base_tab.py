"""
标签基类
提供统一的样式和接口
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit


class BaseTab(QWidget):
    """标签基类"""
    
    def __init__(self, tab_name, icon, placeholder_text=""):
        super().__init__()
        self.tab_name = tab_name
        self.icon = icon
        self.placeholder_text = placeholder_text
        
        # 创建布局和内容区域
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)
        
        # 创建内容文本框
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlaceholderText(self.placeholder_text)
        self.text_edit.setStyleSheet(self._get_text_style())
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        layout.addWidget(self.text_edit)
        
    def _get_text_style(self):
        """获取文本框样式"""
        return """
            QTextEdit {
                border: none;
                background-color: #ffffff;
                font-size: 12px;
                padding: 10px;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border: none;
                outline: none;
            }
        """
        
    def _get_html_template(self):
        """获取HTML模板"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-size: 12px;
                    line-height: 1.4;
                    color: #333333;
                    margin: 0;
                    padding: 0;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                    font-smooth: always;
                    text-rendering: optimizeLegibility;
                }}
                .section {{
                    margin-bottom: 15px;
                    border-left: 3px solid #2196F3;
                    padding-left: 10px;
                }}
                .title {{
                    color: #1976D2;
                    font-size: 13px;
                    margin-bottom: 8px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    text-shadow: 0.5px 0.5px 1px rgba(0,0,0,0.1);
                }}
                .item {{
                    margin: 5px 0;
                    display: flex;
                    align-items: center;
                    min-height: 18px;
                }}
                .label {{
                    color: #555555;
                    min-width: 120px;
                    font-size: 12px;
                    text-shadow: 0.5px 0.5px 1px rgba(0,0,0,0.05);
                }}
                .value {{
                    color: #222222;
                    flex: 1;
                    font-size: 12px;
                    text-shadow: 0.5px 0.5px 1px rgba(0,0,0,0.05);
                }}
                .highlight {{
                    color: #D32F2F;
                    font-weight: 600;
                    text-shadow: 0.5px 0.5px 1px rgba(211,47,47,0.2);
                }}
                .warning {{
                    color: #F57C00;
                    font-weight: 600;
                    text-shadow: 0.5px 0.5px 1px rgba(245,124,0,0.2);
                }}
                .success {{
                    color: #388E3C;
                    font-weight: 600;
                    text-shadow: 0.5px 0.5px 1px rgba(56,142,60,0.2);
                }}
                .info {{
                    color: #1976D2;
                    font-weight: 500;
                    text-shadow: 0.5px 0.5px 1px rgba(25,118,210,0.2);
                }}
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
        
    def get_button_text(self):
        """获取按钮显示的文本"""
        return f"{self.icon} {self.tab_name}"
        
    def update_content(self, content_dict):
        """
        更新标签内容
        
        Args:
            content_dict: 包含标签内容的字典
        """
        html_content = self._format_content(content_dict)
        self.text_edit.setText(html_content)
        
    def _format_content(self, content_dict):
        """
        格式化内容为HTML
        
        Args:
            content_dict: 内容字典
            
        Returns:
            str: HTML格式的内容
        """
        # 子类需要实现这个方法
        raise NotImplementedError("子类必须实现 _format_content 方法")
        
    def clear_content(self):
        """清空内容"""
        self.text_edit.setText("")
        self.text_edit.setPlaceholderText(self.placeholder_text)