"""
后台日志标签
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit


class LogTab(QWidget):
    """后台日志标签"""
    
    def __init__(self):
        super().__init__()
        self.tab_name = "后台日志"
        self.icon = "📋"
        self.placeholder_text = "后台日志将在此显示..."
        
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)
        
        # 创建日志文本框
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
        
    def get_button_text(self):
        """获取按钮显示的文本"""
        return f"{self.icon} {self.tab_name}"
        
    def append_log(self, message):
        """
        追加日志到日志文本框
        
        Args:
            message: 日志消息
        """
        if self.text_edit:
            # 移动光标到末尾
            cursor = self.text_edit.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.text_edit.setTextCursor(cursor)
            self.text_edit.insertPlainText(message)
            # 自动滚动到底部
            self.text_edit.ensureCursorVisible()
            
    def clear_log(self):
        """清空日志"""
        if self.text_edit:
            self.text_edit.clear()
            self.text_edit.setPlaceholderText(self.placeholder_text)
            
    def get_text_edit(self):
        """获取文本框对象"""
        return self.text_edit