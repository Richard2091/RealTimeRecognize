"""
性能指标标签
"""
from .base_tab import BaseTab


class PerformanceTab(BaseTab):
    """性能指标标签"""
    
    def __init__(self):
        super().__init__("性能指标", "⚡", "等待性能数据...")
        
    def _format_content(self, content_dict):
        """格式化性能指标内容"""
        content = f"""
        <div class="section">
            <div class="title">帧处理性能</div>
            <div class="item"><span class="label">帧处理延迟:</span><span class="value">{content_dict.get('processing_delay', 'N/A')} ms</span></div>
            <div class="item"><span class="label">检测耗时:</span><span class="value">{content_dict.get('detection_time', 'N/A')} ms</span></div>
            <div class="item"><span class="label">渲染耗时:</span><span class="value">{content_dict.get('render_time', 'N/A')} ms</span></div>
            <div class="item"><span class="label">总处理时间:</span><span class="value">{content_dict.get('total_time', 'N/A')} ms</span></div>
            <div class="item"><span class="label">吞吐量:</span><span class="value">{content_dict.get('throughput', 'N/A')} FPS</span></div>
        </div>
        """
        
        # 如果有性能统计信息，添加统计部分
        if 'fps_avg' in content_dict:
            content += f"""
            <div class="section">
                <div class="title">性能统计</div>
                <div class="item"><span class="label">平均FPS:</span><span class="value">{content_dict.get('fps_avg', 'N/A')}</span></div>
                <div class="item"><span class="label">峰值FPS:</span><span class="value">{content_dict.get('fps_max', 'N/A')}</span></div>
                <div class="item"><span class="label">丢帧率:</span><span class="value">{content_dict.get('drop_rate', '0')}%</span></div>
                <div class="item"><span class="label">CPU负载:</span><span class="value">{content_dict.get('cpu_load', 'N/A')}%</span></div>
            </div>
            """
            
        return self._get_html_template().format(content=content.strip())