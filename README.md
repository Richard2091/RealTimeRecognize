# YOLO实时检测系统

基于YOLO和MediaPipe的实时目标检测系统，支持目标检测、姿态识别和表情分析。

## ✨ 主要特性

- 🎯 **多模型支持**: YOLOv8、YOLO26、YOLO-World
- 🤸 **姿态检测**: 基于MediaPipe的人体姿态识别
- 😊 **表情分析**: 基于MediaPipe的面部表情检测
- 📹 **RTSP摄像头**: 支持通过RTSP协议连接网络摄像头
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
# 运行QT版本
python main.py
```

## 📁 项目结构

```
RealTimeRecognize/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖包列表
├── README.md              # 项目说明文档
│
├── camera/                # 摄像头控制模块
│   ├── __init__.py
│   ├── camera_controller.py      # 本地摄像头控制器
│   └── rtsp_camera_controller.py # RTSP网络摄像头控制器
│
├── core/                  # 核心功能模块
│   ├── __init__.py
│   ├── detectors/         # 检测器模块
│   │   ├── __init__.py
│   │   ├── base.py        # 基础检测器抽象类
│   │   ├── mediapipe/     # MediaPipe相关检测器（预留）
│   │   └── yolo/          # YOLO相关检测器（预留）
│   ├── display/           # 显示渲染模块
│   │   ├── __init__.py
│   │   └── renderers/     # 渲染器（预留）
│   └── pipeline/          # 检测流水线
│       ├── __init__.py
│       └── detection_pipeline.py # 检测流水线实现
│
├── detectors/             # 实际的检测器实现
│   ├── __init__.py
│   ├── yolo8_detector.py      # YOLOv8检测器
│   ├── yolo26_detector.py     # YOLO26检测器
│   └── yolo_world_detector.py # YOLO-World检测器
│
├── model/                 # 模型文件
│   ├── yolo8/            # YOLOv8模型
│   │   ├── yolov8n.pt
│   │   ├── yolov8n-pose.pt
│   │   └── yolov8s.pt
│   ├── yolo26/           # YOLO26模型
│   │   ├── yolo26n.pt
│   │   ├── yolo26n-pose.pt
│   │   └── yolo26s.pt
│   └── yoloworld/        # YOLO-World模型
│       └── yolov8s-worldv2.pt
│
├── ui/                   # PyQt5用户界面
│   ├── __init__.py
│   ├── main_window.py            # 主窗口
│   ├── components/               # UI组件
│   │   ├── __init__.py
│   │   ├── control_panel.py      # 控制面板
│   │   └── display_area.py       # 显示区域
│   ├── handlers/                 # 功能处理器
│   │   ├── __init__.py
│   │   ├── camera_handler.py     # 摄像头处理器
│   │   └── detection_handler.py  # 检测处理器
│   └── threads/                  # 线程模块
│       ├── __init__.py
│       └── rtsp_thread.py        # RTSP线程
│
└── utils/                # 工具模块
    ├── __init__.py
    └── config.py         # 配置管理
```

## 💡 使用示例

### 使用RTSP网络摄像头

**通过GUI使用**:
1. 启动程序: `python main_qt.py`
2. 在左侧"摄像头设置"中选择"RTSP网络摄像头"
3. 输入IP地址（例如: 192.168.1.100 或 192.168.1.100:554）
   - 只需输入IP，无需输入"rtsp://"前缀
   - 默认端口为8554，如需其他端口可在IP后添加（如: 192.168.1.100:554）
4. 点击"启动检测"

**编程使用**:

```python
from camera.rtsp_camera_controller import RTSPCameraController

# 连接RTSP摄像头
camera = RTSPCameraController(
  rtsp_url='rtsp://192.168.1.100:8554/',
  width=1280,
  height=720
)

ret, frame = camera.read()
camera.release()
```

**常见RTSP地址格式**:
- 默认格式（本程序）: `rtsp://ip:8554/`
- 海康威视: `rtsp://username:password@ip:554/Streaming/Channels/101`
- 大华: `rtsp://username:password@ip:554/cam/realmonitor?channel=1&subtype=0`
- 其他通用格式: `rtsp://ip:port/stream`

**注意事项**:
- 确保设备和电脑在同一网络
- 检查防火墙设置
- 验证RTSP端口是否开放（常见端口: 554, 8554）

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

### RTSP无法连接
- **问题**: 无法连接到RTSP流
- **解决**:
  1. 检查RTSP地址是否正确
  2. 确保设备和电脑在同一网络
  3. 检查防火墙设置
  4. 验证RTSP端口是否开放（常见端口: 554, 8554）
  5. 使用FFmpeg测试: `ffplay rtsp://ip:port/stream`

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