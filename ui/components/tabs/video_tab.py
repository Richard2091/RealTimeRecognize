"""
视频信息标签
"""
from .base_tab import BaseTab


class VideoTab(BaseTab):
    """视频信息标签"""
    
    def __init__(self):
        super().__init__("视频信息", "📹", "等待视频信息...")
        
    def _format_content(self, content_dict):
        """格式化视频信息内容"""
        content = f"""
        <div class="section">
            <div class="title">视频流信息</div>
            <div class="item"><span class="label">分辨率:</span><span class="value">{content_dict.get('resolution', 'N/A')}</span></div>
            <div class="item"><span class="label">帧率:</span><span class="value">{content_dict.get('fps', 'N/A')}</span></div>
            <div class="item"><span class="label">总帧数:</span><span class="value">{content_dict.get('frame_count', 'N/A')}</span></div>
            <div class="item"><span class="label">运行时间:</span><span class="value">{content_dict.get('running_time', 'N/A')}</span></div>
            <div class="item"><span class="label">错误率:</span><span class="value highlight">{content_dict.get('error_rate', '0')}%</span></div>
        </div>
        """
        
        # 如果有延迟信息，添加延迟统计
        if 'avg_delay' in content_dict:
            content += f"""
            <div class="section">
                <div class="title">延迟统计</div>
                <div class="item"><span class="label">平均延迟:</span><span class="value">{content_dict.get('avg_delay', 'N/A')} ms</span></div>
                <div class="item"><span class="label">最大延迟:</span><span class="value">{content_dict.get('max_delay', 'N/A')} ms</span></div>
                <div class="item"><span class="label">最小延迟:</span><span class="value">{content_dict.get('min_delay', 'N/A')} ms</span></div>
                <div class="item"><span class="label">抖动:</span><span class="value">{content_dict.get('jitter', 'N/A')} ms</span></div>
            </div>
            """
            
        return self._get_html_template().format(content=content.strip())