"""
资源使用标签
"""
from .base_tab import BaseTab


class ResourceTab(BaseTab):
    """资源使用标签"""
    
    def __init__(self):
        super().__init__("资源使用", "📊", "等待资源数据...")
        
    def _format_content(self, content_dict):
        """格式化资源使用内容"""
        content = f"""
        <div class="section">
            <div class="title">系统资源</div>
            <div class="item"><span class="label">内存使用:</span><span class="value">{content_dict.get('memory_usage', 'N/A')} MB</span></div>
            <div class="item"><span class="label">CPU使用:</span><span class="value">{content_dict.get('cpu_usage', 'N/A')}%</span></div>
            <div class="item"><span class="label">GPU使用:</span><span class="value">{content_dict.get('gpu_usage', 'N/A')}%</span></div>
            <div class="item"><span class="label">GPU内存:</span><span class="value">{content_dict.get('gpu_memory', 'N/A')} MB</span></div>
        </div>
        """
        
        # 如果有系统资源信息，添加系统部分
        if 'system_memory_total' in content_dict:
            memory_total = content_dict.get('system_memory_total', 0)
            memory_used = content_dict.get('system_memory_used', 0)
            memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
            
            content += f"""
            <div class="section">
                <div class="title">系统总览</div>
                <div class="item"><span class="label">总内存:</span><span class="value">{memory_total // 1024} GB</span></div>
                <div class="item"><span class="label">已用内存:</span><span class="value">{memory_used // 1024} GB ({memory_percent:.1f}%)</span></div>
                <div class="item"><span class="label">CPU核心数:</span><span class="value">{content_dict.get('cpu_cores', 'N/A')}</span></div>
                <div class="item"><span class="label">GPU型号:</span><span class="value">{content_dict.get('gpu_name', 'N/A')}</span></div>
            </div>
            """
            
        # 如果有网络资源信息，添加网络部分
        if 'network_upload' in content_dict:
            content += f"""
            <div class="section">
                <div class="title">网络资源</div>
                <div class="item"><span class="label">上传速度:</span><span class="value">{content_dict.get('network_upload', 'N/A')} KB/s</span></div>
                <div class="item"><span class="label">下载速度:</span><span class="value">{content_dict.get('network_download', 'N/A')} KB/s</span></div>
                <div class="item"><span class="label">连接数:</span><span class="value">{content_dict.get('network_connections', 'N/A')}</span></div>
            </div>
            """
            
        return self._get_html_template().format(content=content.strip())