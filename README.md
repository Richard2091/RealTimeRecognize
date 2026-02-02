# YOLO实时检测系统

基于YOLO和MediaPipe的实时目标检测系统，支持目标检测、姿态识别和表情分析。

## ✨ 主要特性

- 🎯 **多模型支持**: YOLOv8、YOLO26、YOLO-World
- 🤸 **姿态检测**: 基于MediaPipe的人体姿态识别
- 😊 **表情分析**: 基于MediaPipe的面部表情检测
- 🖼️ **实时显示**: 高性能的视频流处理
- 🎨 **图形化界面**: PyQt5实现，完美支持中文

## 🚀 快速开始

### 环境要求

- Python 3.10+
- OpenCV 4.8+
- PyQt5 5.15+
- MediaPipe 0.10+
- Ultralytics 8.0+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
# 运行QT版本（推荐，支持中文）
python main_qt.py

# 运行OpenCV版本
python main.py
```

## 📁 项目结构

```
opencv&yolo/
├── core/                      # 核心功能模块
│   ├── detectors/             # 所有检测器
│   │   ├── base.py          # 基础检测器抽象类
│   │   ├── yolo/           # YOLO系列检测器
│   │   ├── pose/           # 姿态检测
│   │   └── emotion/       # 表情检测
│   ├── display/              # 显示渲染
│   │   └── renderers/     # 渲染器
│   └── pipeline/           # 检测流水线
│
├── ui/                       # QT用户界面
│   └── qt_main.py           # PyQt5主窗口
│
├── camera/                  # 摄像头控制
│   └── camera_controller.py
│
├── utils/                   # 工具模块
│   └── config.py          # 配置管理
│
├── main.py                 # OpenCV版本主入口
├── main_qt.py            # QT版本主入口（推荐）
└── model/                 # 模型文件
    ├── yolo8/
    ├── yolo26/
    └── yoloworld/
```

## 💡 使用示例

### 编程使用

```python
import cv2
from core.detectors import YOLOv8Detector, PoseDetector
from core.pipeline import DetectionPipeline

# 创建检测器
yolo = YOLOv8Detector("model/yolo8/yolov8n.pt")
pose = PoseDetector()

# 创建流水线
pipeline = DetectionPipeline(
    yolo_detector=yolo,
    pose_detector=pose
)

# 处理视频帧
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 执行检测
    results = pipeline.process(frame, use_pose=True)
    
    # 显示结果
    cv2.imshow("Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## 🔧 开发指南

### 添加新的检测器

1. 继承`BaseDetector`类
2. 实现`detect()`和`get_classes()`方法
3. 在`core/detectors/`中创建新模块

```python
from core.detectors.base import BaseDetector

class MyDetector(BaseDetector):
    def load_model(self):
        # 加载模型
        pass
    
    def detect(self, frame, verbose=True):
        # 检测逻辑
        pass
    
    def get_classes(self):
        # 返回支持的类别
        pass
```

## 📚 架构说明

### 核心模块整合

- **检测器统一管理**: `core/detectors/` 包含所有检测器，采用统一基类接口
- **UI和Display分离**: `ui/` 专注于用户界面，`core/display/` 专注于渲染逻辑
- **检测流水线**: `core/pipeline/` 提供统一的检测流程

### 设计模式

- **策略模式**: `BaseDetector`提供不同检测策略
- **工厂模式**: `DetectionPipeline`作为检测器工厂

## 🐛 故障排除

### 中文乱码
- **问题**: OpenCV GUI显示中文乱码
- **解决**: 使用QT版本 `python main_qt.py`

### 模型加载失败
- **问题**: 模型文件不存在或损坏
- **解决**: 检查`model/`目录下的模型文件

### MediaPipe导入失败
- **问题**: MediaPipe版本不兼容
- **解决**: 重新安装 `pip install mediapipe==0.10.9`

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

本项目仅供学习和研究使用。

## 🎉 致谢

感谢以下开源项目：
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- [MediaPipe](https://github.com/google/mediapipe)
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)

---

**推荐使用 `main_qt.py` 启动QT版本以获得最佳中文支持体验。**