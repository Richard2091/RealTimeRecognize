"""
YOLO渲染器
负责YOLO检测结果的绘制
"""
import cv2


class YOLORenderer:
    """YOLO检测渲染器"""
    
    def __init__(self, show_confidence=True, show_class=True):
        self.show_confidence = show_confidence
        self.show_class = show_class
    
    def render_results(self, frame, results):
        """
        渲染YOLO检测结果
        
        Args:
            frame: 输入帧
            results: YOLO检测结果
        """
        # 使用YOLO内置的绘制功能
        for result in results:
            if result.boxes is not None:
                annotated_frame = result.plot()
                return annotated_frame
        
        return frame
    
    def render_persons_only(self, frame, results):
        """
        只渲染人员检测结果
        
        Args:
            frame: 输入帧
            results: YOLO检测结果
        """
        for result in results:
            if result.boxes is not None:
                boxes = result.boxes
                for box in boxes:
                    # 只渲染人员（class_id=0）
                    if int(box.cls[0]) == 0:
                        self._draw_box(frame, box)
        
        return frame
    
    def _draw_box(self, frame, box):
        """
        绘制单个检测框
        
        Args:
            frame: 输入帧
            box: 检测框
        """
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
        
        # 绘制矩形框
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # 绘制置信度和类别
        if self.show_confidence or self.show_class:
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            
            label_parts = []
            if self.show_class:
                label_parts.append(f"Person")
            if self.show_confidence:
                label_parts.append(f"{conf:.2f}")
            
            if label_parts:
                label = " ".join(label_parts)
                text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                cv2.rectangle(frame, (x1, y1 - text_size[1] - 10),
                            (x1 + text_size[0], y1), (0, 255, 0), -1)
                cv2.putText(frame, label, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)