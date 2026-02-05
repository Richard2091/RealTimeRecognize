"""
检测信息标签
"""
from .base_tab import BaseTab


class DetectionTab(BaseTab):
    """检测信息标签"""
    
    def __init__(self):
        super().__init__("检测信息", "🎯", "等待检测信息...")
        
    def _format_content(self, content_dict):
        """格式化检测信息内容"""
        content = f"""
        <div class="section">
            <div class="title">模型配置</div>
            <div class="item"><span class="label">当前模型:</span><span class="value">{content_dict.get('model_name', 'N/A')}</span></div>
            <div class="item"><span class="label">检测对象:</span><span class="value">{content_dict.get('detection_objects', 'N/A')}</span></div>
            <div class="item"><span class="label">置信度:</span><span class="value">{content_dict.get('confidence', 'N/A')}</span></div>
            <div class="item"><span class="label">IOU阈值:</span><span class="value">{content_dict.get('iou_threshold', 'N/A')}</span></div>
        </div>
        """
        
        # 添加功能开关状态
        content += f"""
        <div class="section">
            <div class="title">检测功能</div>
            <div class="item"><span class="label">姿态检测:</span><span class="value">{'<span class="success">已启用</span>' if content_dict.get('pose_enabled') == '是' else '<span class="warning">未启用</span>'}</span></div>
            <div class="item"><span class="label">表情检测:</span><span class="value">{'<span class="success">已启用</span>' if content_dict.get('emotion_enabled') == '是' else '<span class="warning">未启用</span>'}</span></div>
            <div class="item"><span class="label">手势检测:</span><span class="value">{'<span class="success">已启用</span>' if content_dict.get('gesture_enabled') == '是' else '<span class="warning">未启用</span>'}</span></div>
        </div>
        """
        
        # 如果有实时检测统计，添加统计部分
        if 'detected_count' in content_dict:
            content += f"""
            <div class="section">
                <div class="title">检测统计</div>
                <div class="item"><span class="label">检测到对象:</span><span class="value">{content_dict.get('detected_count', '0')} 个</span></div>
                <div class="item"><span class="label">检测成功率:</span><span class="value">{content_dict.get('detection_success_rate', 'N/A')}%</span></div>
                <div class="item"><span class="label">误检率:</span><span class="value">{content_dict.get('false_positive_rate', 'N/A')}%</span></div>
            </div>
            """
            
        return self._get_html_template().format(content=content.strip())