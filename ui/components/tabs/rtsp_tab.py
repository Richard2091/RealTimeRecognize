"""
RTSP信息标签
"""
from .base_tab import BaseTab


class RTSPTab(BaseTab):
    """RTSP信息标签"""
    
    def __init__(self):
        super().__init__("RTSP信息", "🌐", "等待RTSP信息...")
        
    def _format_content(self, content_dict):
        """格式化RTSP信息内容"""
        content = f"""
        <div class="section">
            <div class="title">连接信息</div>
            <div class="item"><span class="label">RTSP地址:</span><span class="value">{content_dict.get('rtsp_url', 'N/A')}</span></div>
            <div class="item"><span class="label">连接状态:</span><span class="value">{self._get_connection_status(content_dict.get('connection_status', 'unknown'))}</span></div>
            <div class="item"><span class="label">连接稳定性:</span><span class="value">{content_dict.get('connection_stability', 'N/A')}%</span></div>
            <div class="item"><span class="label">数据速率:</span><span class="value">{content_dict.get('data_rate_mbps', 'N/A')} Mbps</span></div>
        </div>
        """
        
        # 添加流信息
        content += f"""
        <div class="section">
            <div class="title">流信息</div>
            <div class="item"><span class="label">编码格式:</span><span class="value">{content_dict.get('codec', 'N/A')}</span></div>
            <div class="item"><span class="label">码率:</span><span class="value">{content_dict.get('bitrate', 'N/A')} kbps</span></div>
            <div class="item"><span class="label">GOP大小:</span><span class="value">{content_dict.get('gop_size', 'N/A')}</span></div>
            <div class="item"><span class="label">帧类型:</span><span class="value">{content_dict.get('frame_type', 'N/A')}</span></div>
        </div>
        """
        
        # 添加统计信息
        content += f"""
        <div class="section">
            <div class="title">统计信息</div>
            <div class="item"><span class="label">重连次数:</span><span class="value">{content_dict.get('reconnection_count', 'N/A')}</span></div>
            <div class="item"><span class="label">丢包率:</span><span class="value">{content_dict.get('packet_loss_rate', 'N/A')}%</span></div>
            <div class="item"><span class="label">延迟抖动:</span><span class="value">{content_dict.get('jitter_ms', 'N/A')} ms</span></div>
            <div class="item"><span class="label">缓冲区大小:</span><span class="value">{content_dict.get('buffer_size', 'N/A')} KB</span></div>
        </div>
        """
        
        return self._get_html_template().format(content=content.strip())
    
    def _get_connection_status(self, status):
        """获取连接状态显示"""
        status_map = {
            'connected': '<span class="success">已连接</span>',
            'connecting': '<span class="warning">连接中</span>',
            'disconnected': '<span class="highlight">已断开</span>',
            'error': '<span class="highlight">连接错误</span>',
            'unknown': '<span class="warning">未知</span>'
        }
        return status_map.get(status, '<span class="warning">未知</span>')