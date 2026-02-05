"""
MediaPipe日志抑制工具
用于抑制MediaPipe C++警告信息
"""
import os
import sys
from contextlib import contextmanager


class FilteredStderr:
    """过滤 stderr 输出，屏蔽特定的 MediaPipe 警告"""

    def __init__(self):
        self.original_stderr = sys.stderr

    def write(self, text):
        """过滤特定的警告信息"""
        # 过滤掉 MediaPipe C++ 警告
        if any(keyword in text for keyword in [
            'WARNING: Logging before InitGoogleLogging',
            'GLOG_v',
            'TF_CPP_MIN_LOG_LEVEL',
            'libprotobuf',
        ]):
            return
        self.original_stderr.write(text)

    def flush(self):
        """刷新输出"""
        self.original_stderr.flush()


@contextmanager
def suppress_stderr_context():
    """
    上下文管理器，用于临时抑制 stderr 输出

    使用示例:
        with suppress_stderr_context():
            # 这里运行会产生警告的代码
            pass
    """
    # 设置环境变量抑制日志
    original_glog_level = os.environ.get('GLOG_minloglevel', '0')
    original_tf_level = os.environ.get('TF_CPP_MIN_LOG_LEVEL', '0')

    os.environ['GLOG_minloglevel'] = '3'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    # 替换 stderr
    original_stderr = sys.stderr
    sys.stderr = FilteredStderr()

    try:
        yield
    finally:
        # 恢复原始 stderr 和环境变量
        sys.stderr = original_stderr
        os.environ['GLOG_minloglevel'] = original_glog_level
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = original_tf_level


def suppress_mediapipe_warnings():
    """
    永久抑制 MediaPipe 警告
    建议在程序启动时调用
    """
    os.environ['GLOG_minloglevel'] = '3'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
