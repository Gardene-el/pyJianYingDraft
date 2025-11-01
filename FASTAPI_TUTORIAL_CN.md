# FastAPI 完整教程 - pyJianYingDraft API 实现详解

## 目录
1. [什么是 FastAPI](#什么是-fastapi)
2. [为什么选择 FastAPI](#为什么选择-fastapi)
3. [我的工作详解](#我的工作详解)
4. [实现步骤说明](#实现步骤说明)
5. [如何使用](#如何使用)
6. [实战示例](#实战示例)

---

## 什么是 FastAPI

FastAPI 是一个现代、快速的 Python Web 框架，用于构建 API（应用程序接口）。

### 核心概念

**1. API (应用程序接口)**
- API 就像是一个"服务窗口"
- 客户端（比如网页、手机应用）通过 HTTP 请求向服务器发送指令
- 服务器执行操作后返回结果
- 例如：你在网页上点击"创建草稿"，网页会向 API 发送 POST 请求

**2. REST API**
- REST 是一种设计 API 的规范
- 使用不同的 HTTP 方法表示不同的操作：
  - `GET`: 获取数据（查询）
  - `POST`: 创建数据
  - `PUT/PATCH`: 更新数据
  - `DELETE`: 删除数据

**3. FastAPI 的特点**
- 自动生成交互式文档（访问 `/docs` 即可看到）
- 数据验证（使用 Pydantic 模型）
- 高性能（基于 Starlette 和 Pydantic）
- 类型提示支持

---

## 为什么选择 FastAPI

在您的项目中添加 FastAPI 有以下好处：

1. **远程访问**: 可以通过网络调用，不需要在同一台机器上
2. **跨语言**: 任何能发送 HTTP 请求的语言都可以使用（JavaScript、Java、Go 等）
3. **Web 集成**: 可以轻松创建网页界面来控制视频生成
4. **微服务架构**: 可以作为独立服务部署
5. **自动化流程**: 可以集成到 CI/CD 流程中

---

## 我的工作详解

我为 pyJianYingDraft 项目添加了完整的 REST API 功能。以下是详细说明：

### 第一步：项目规划（Commit 1ae5714）

我首先分析了 `demo.py` 文件，了解了项目的核心功能：
- 创建草稿
- 添加轨道（音频、视频、文本）
- 添加片段（音频、视频、贴纸、文本）
- 添加效果（动画、转场、淡入淡出等）
- 保存草稿

然后规划了需要实现的 API 端点。

### 第二步：创建 API 核心（Commit 6eef1e6）

创建了 `api.py` 文件，包含：

#### 1. 导入必要的库
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pyJianYingDraft as draft
```

#### 2. 创建 FastAPI 应用
```python
app = FastAPI(
    title="pyJianYingDraft API",
    description="REST API for creating and manipulating JianYing video drafts",
    version="1.0.0"
)
```

#### 3. 定义数据模型（Pydantic Models）
这些模型用于验证输入数据：

```python
class DraftCreate(BaseModel):
    """创建草稿的请求模型"""
    folder_id: str = Field(..., description="草稿文件夹ID")
    draft_name: str = Field(..., description="草稿名称")
    width: int = Field(1920, description="视频宽度")
    height: int = Field(1080, description="视频高度")
```

#### 4. 实现 API 端点

**示例 1: 注册草稿文件夹**
```python
@app.post("/folder/register", response_model=DraftResponse)
async def register_draft_folder(folder_data: DraftFolderCreate):
    """
    注册一个剪映草稿文件夹
    """
    try:
        folder = draft.DraftFolder(folder_data.folder_path)
        draft_folders[folder_data.folder_id] = folder
        return DraftResponse(
            success=True,
            message="文件夹注册成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**示例 2: 创建草稿**
```python
@app.post("/draft/create", response_model=DraftResponse)
async def create_draft(draft_data: DraftCreate):
    """
    创建一个新草稿
    """
    folder = draft_folders[draft_data.folder_id]
    script = folder.create_draft(
        draft_data.draft_name,
        draft_data.width,
        draft_data.height
    )
    active_drafts[draft_data.draft_name] = script
    return DraftResponse(success=True, message="草稿创建成功")
```

**示例 3: 添加视频片段**
```python
@app.post("/draft/{draft_name}/segment/video")
async def add_video_segment(draft_name: str, segment_data: VideoSegmentAdd):
    """
    向草稿添加视频片段
    """
    script = active_drafts[draft_name]
    
    # 创建视频片段
    video_segment = draft.VideoSegment(
        segment_data.material_path,
        draft.trange(segment_data.start_time, segment_data.duration)
    )
    
    # 添加动画（如果指定）
    if segment_data.animation_type:
        animation = draft.IntroType.from_name(segment_data.animation_type)
        video_segment.add_animation(animation)
    
    # 添加到脚本
    script.add_segment(video_segment)
    return DraftResponse(success=True, message="视频片段添加成功")
```

#### 5. 元数据端点

提供查询功能，让用户知道有哪些选项可用：

```python
@app.get("/metadata/fonts")
async def list_fonts():
    """列出所有可用字体"""
    fonts = [f.name for f in draft.FontType]
    return {"success": True, "count": len(fonts), "fonts": fonts}
```

### 第三步：代码质量改进（Commit ced9038）

修复了代码风格问题：
- 移除未使用的导入
- 修复空白行问题
- 修复字符串格式问题

### 第四步：代码审查反馈（Commit 535f035）

根据代码审查建议进行了改进：

#### 1. 添加线程安全
使用 `threading.RLock()` 保护共享数据：

```python
_storage_lock = threading.RLock()
active_drafts: Dict[str, draft.ScriptFile] = {}

# 使用锁保护访问
with _storage_lock:
    draft_folders[folder_data.folder_id] = folder
```

**为什么需要线程安全？**
- FastAPI 可能同时处理多个请求
- 如果多个请求同时修改 `active_drafts`，可能导致数据错误
- 使用锁确保一次只有一个请求能修改数据

#### 2. 改进异常处理
捕获更准确的异常类型：

```python
# 之前只捕获 AttributeError
except AttributeError:
    raise HTTPException(status_code=400, detail="无效的动画类型")

# 现在捕获两种异常
except (AttributeError, ValueError):
    raise HTTPException(status_code=400, detail="无效的动画类型")
```

#### 3. 改进淡入淡出逻辑
只在用户真正提供参数时才添加效果：

```python
# 之前：即使两个都是 None 也会添加
if segment_data.fade_in or segment_data.fade_out:
    audio_segment.add_fade(...)

# 现在：只有在真正提供时才添加
if segment_data.fade_in is not None or segment_data.fade_out is not None:
    audio_segment.add_fade(...)
```

### 第五步：安全加固（Commit f48d326）

添加路径验证功能，防止安全漏洞：

```python
def _validate_path(path: str, path_type: str = "file") -> str:
    """
    验证和清理文件/文件夹路径，防止路径遍历攻击
    """
    # 转换为绝对路径并规范化
    abs_path = os.path.abspath(os.path.normpath(path))
    
    # 检查路径遍历尝试
    if '..' in path:
        raise HTTPException(status_code=400, detail="检测到路径遍历")
    
    # 验证路径存在
    if path_type == "file" and not os.path.isfile(abs_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return abs_path
```

**为什么需要路径验证？**
- 用户可能输入恶意路径，如 `../../etc/passwd`
- 这可能让攻击者访问系统中的任意文件
- 路径验证确保只能访问合法的文件

### 第六步：文档和示例（Commit 18f1e65）

创建了：
1. **API_README.md** - 完整的 API 文档
2. **api_demo_example.py** - 可运行的示例代码
3. 更新了主 README 介绍新功能

---

## 实现步骤说明

### 总体架构

```
客户端（浏览器/Python脚本）
    ↓ HTTP 请求
FastAPI 服务器（api.py）
    ↓ 调用
pyJianYingDraft 库
    ↓ 生成
草稿文件（draft_content.json）
```

### 数据流程

1. **客户端发送请求**
   ```
   POST /draft/create
   Body: {"folder_id": "my_folder", "draft_name": "test", ...}
   ```

2. **FastAPI 接收并验证**
   - Pydantic 自动验证数据格式
   - 检查必填字段是否存在
   - 验证数据类型是否正确

3. **执行业务逻辑**
   - 调用 pyJianYingDraft 库创建草稿
   - 将草稿对象保存到内存

4. **返回响应**
   ```json
   {
     "success": true,
     "message": "草稿创建成功",
     "draft_name": "test"
   }
   ```

### 核心组件说明

#### 1. 全局存储
```python
active_drafts: Dict[str, draft.ScriptFile] = {}
draft_folders: Dict[str, draft.DraftFolder] = {}
```
- 使用字典在内存中保存活动的草稿和文件夹
- 生产环境应该使用数据库

#### 2. 请求模型
```python
class AudioSegmentAdd(BaseModel):
    material_path: str = Field(..., description="音频文件路径")
    start_time: str = Field(..., description="开始时间")
    duration: str = Field(..., description="持续时间")
    volume: Optional[float] = Field(None, description="音量")
```
- 定义请求数据的结构
- 自动验证和文档生成

#### 3. 响应模型
```python
class DraftResponse(BaseModel):
    success: bool
    message: str
    draft_name: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
```
- 统一的响应格式
- 便于客户端处理

---

## 如何使用

### 1. 安装依赖

```bash
cd /path/to/pyJianYingDraft
pip install -r requirements.txt
```

这会安装：
- `fastapi>=0.115.5` - Web 框架
- `uvicorn>=0.34.0` - ASGI 服务器（运行 FastAPI）
- `pydantic>=2.10.4` - 数据验证

### 2. 启动服务器

**方法 1: 直接运行**
```bash
python api.py
```

**方法 2: 使用 uvicorn（推荐开发时使用）**
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

参数说明：
- `api:app` - 模块名:应用对象
- `--reload` - 代码修改后自动重启
- `--host 0.0.0.0` - 允许外部访问
- `--port 8000` - 端口号

### 3. 访问文档

启动后，打开浏览器访问：

**Swagger UI (推荐)**
```
http://localhost:8000/docs
```
- 交互式文档
- 可以直接在页面上测试 API

**ReDoc**
```
http://localhost:8000/redoc
```
- 更专业的文档展示

### 4. 测试 API

**使用浏览器（Swagger UI）**
1. 访问 `http://localhost:8000/docs`
2. 找到要测试的端点，点击展开
3. 点击 "Try it out"
4. 填写参数
5. 点击 "Execute"
6. 查看响应

**使用 curl（命令行）**
```bash
# 注册文件夹
curl -X POST "http://localhost:8000/folder/register" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_id": "my_folder",
    "folder_path": "/path/to/JianyingPro Drafts"
  }'

# 创建草稿
curl -X POST "http://localhost:8000/draft/create" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_id": "my_folder",
    "draft_name": "test_draft",
    "width": 1920,
    "height": 1080
  }'
```

**使用 Python requests**
```python
import requests

# 注册文件夹
response = requests.post(
    "http://localhost:8000/folder/register",
    json={
        "folder_id": "my_folder",
        "folder_path": "/path/to/JianyingPro Drafts"
    }
)
print(response.json())
```

---

## 实战示例

### 完整流程：创建一个简单的视频草稿

```python
import requests

BASE_URL = "http://localhost:8000"

# 步骤 1: 注册草稿文件夹
print("1. 注册草稿文件夹...")
response = requests.post(f"{BASE_URL}/folder/register", json={
    "folder_id": "my_drafts",
    "folder_path": "C:/Users/YourName/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft"
})
print(f"结果: {response.json()['message']}")

# 步骤 2: 创建草稿
print("\n2. 创建草稿...")
response = requests.post(f"{BASE_URL}/draft/create", json={
    "folder_id": "my_drafts",
    "draft_name": "我的第一个API草稿",
    "width": 1920,
    "height": 1080,
    "allow_replace": True
})
print(f"结果: {response.json()['message']}")

# 步骤 3: 添加视频轨道
print("\n3. 添加视频轨道...")
response = requests.post(f"{BASE_URL}/draft/我的第一个API草稿/track/add", json={
    "track_type": "video"
})
print(f"结果: {response.json()['message']}")

# 步骤 4: 添加音频轨道
print("\n4. 添加音频轨道...")
response = requests.post(f"{BASE_URL}/draft/我的第一个API草稿/track/add", json={
    "track_type": "audio"
})
print(f"结果: {response.json()['message']}")

# 步骤 5: 添加视频片段
print("\n5. 添加视频片段...")
response = requests.post(f"{BASE_URL}/draft/我的第一个API草稿/segment/video", json={
    "material_path": "D:/Videos/my_video.mp4",
    "start_time": "0s",
    "duration": "10s",
    "animation_type": "斜切",  # 添加入场动画
    "transition_type": "信号故障"  # 添加转场
})
print(f"结果: {response.json()['message']}")

# 步骤 6: 添加音频片段
print("\n6. 添加音频片段...")
response = requests.post(f"{BASE_URL}/draft/我的第一个API草稿/segment/audio", json={
    "material_path": "D:/Audio/background.mp3",
    "start_time": "0s",
    "duration": "10s",
    "volume": 0.5,  # 音量 50%
    "fade_in": "1s",  # 1秒淡入
    "fade_out": "1s"  # 1秒淡出
})
print(f"结果: {response.json()['message']}")

# 步骤 7: 保存草稿
print("\n7. 保存草稿...")
response = requests.post(f"{BASE_URL}/draft/我的第一个API草稿/save")
print(f"结果: {response.json()['message']}")

print("\n✅ 完成！现在可以在剪映中打开'我的第一个API草稿'查看效果。")
```

### 查询可用的效果

```python
import requests

BASE_URL = "http://localhost:8000"

# 查询所有可用字体
response = requests.get(f"{BASE_URL}/metadata/fonts")
data = response.json()
print(f"可用字体数量: {data['count']}")
print(f"前10个字体: {data['fonts'][:10]}")

# 查询所有入场动画
response = requests.get(f"{BASE_URL}/metadata/animations/intro")
data = response.json()
print(f"\n可用入场动画数量: {data['count']}")
print(f"前10个动画: {data['animations'][:10]}")

# 查询所有转场效果
response = requests.get(f"{BASE_URL}/metadata/transitions")
data = response.json()
print(f"\n可用转场效果数量: {data['count']}")
print(f"前10个转场: {data['transitions'][:10]}")
```

### 批量处理：自动生成多个草稿

```python
import requests

BASE_URL = "http://localhost:8000"

# 配置
videos = [
    {"name": "视频1", "path": "D:/Videos/video1.mp4", "duration": "5s"},
    {"name": "视频2", "path": "D:/Videos/video2.mp4", "duration": "8s"},
    {"name": "视频3", "path": "D:/Videos/video3.mp4", "duration": "6s"},
]

# 注册文件夹
requests.post(f"{BASE_URL}/folder/register", json={
    "folder_id": "batch_folder",
    "folder_path": "C:/path/to/drafts"
})

# 为每个视频创建草稿
for video in videos:
    draft_name = f"自动草稿_{video['name']}"
    
    # 创建草稿
    requests.post(f"{BASE_URL}/draft/create", json={
        "folder_id": "batch_folder",
        "draft_name": draft_name,
        "width": 1920,
        "height": 1080
    })
    
    # 添加轨道
    requests.post(f"{BASE_URL}/draft/{draft_name}/track/add", json={
        "track_type": "video"
    })
    
    # 添加视频片段
    requests.post(f"{BASE_URL}/draft/{draft_name}/segment/video", json={
        "material_path": video["path"],
        "start_time": "0s",
        "duration": video["duration"],
        "animation_type": "动感放大"
    })
    
    # 保存
    requests.post(f"{BASE_URL}/draft/{draft_name}/save")
    
    print(f"✅ 已创建: {draft_name}")

print("\n批量处理完成！")
```

---

## 常见问题

### Q1: 为什么需要先注册文件夹？
A: API 需要知道剪映草稿存储在哪里。注册后，API 会记住这个位置，后续操作都会在这个文件夹中进行。

### Q2: 草稿数据存储在哪里？
A: API 在内存中临时保存草稿对象。最终调用 `save()` 时，会保存到剪映的草稿文件夹中。

### Q3: 如何找到我的剪映草稿文件夹？
A: 打开剪映 → 设置 → 草稿位置。通常路径类似：
- Windows: `C:/Users/用户名/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft`

### Q4: API 服务器可以远程访问吗？
A: 可以。启动时使用 `--host 0.0.0.0`，然后通过 IP 地址访问。但注意安全性，建议添加认证。

### Q5: 为什么时间格式是字符串（如 "5s"）？
A: 这是为了方便输入。API 会自动转换为内部使用的微秒格式。支持的格式：
- `"5s"` - 5秒
- `"1m30s"` - 1分30秒
- `"1h2m3s"` - 1小时2分3秒

### Q6: 如何添加多个轨道？
A: 多次调用 `/track/add` 端点，可以指定不同的 `track_name` 和 `relative_index`。

### Q7: 为什么有些参数是 Optional？
A: Optional 参数是可选的，不提供时使用默认值。例如，`volume` 不提供时使用原始音量。

---

## 进阶主题

### 错误处理

API 使用标准 HTTP 状态码：
- `200` - 成功
- `400` - 请求参数错误
- `404` - 资源不存在（文件、草稿等）
- `500` - 服务器内部错误

示例：
```python
response = requests.post(url, json=data)
if response.status_code == 200:
    print("成功:", response.json())
elif response.status_code == 404:
    print("错误: 文件不存在")
    print("详情:", response.json()["detail"])
else:
    print("其他错误:", response.status_code)
```

### 性能优化

1. **复用连接**
```python
session = requests.Session()
session.post(...)  # 使用 session 而不是 requests
```

2. **批量操作**
- 尽量减少 API 调用次数
- 在本地准备好所有数据再发送

3. **异步处理**
- 对于大量草稿，可以使用异步库（如 `aiohttp`）并发处理

### 扩展 API

如果需要添加新功能：

1. 定义请求模型
```python
class MyNewRequest(BaseModel):
    param1: str
    param2: int
```

2. 实现端点
```python
@app.post("/my/new/endpoint")
async def my_new_function(data: MyNewRequest):
    # 实现逻辑
    return {"success": True}
```

3. 重启服务器，文档会自动更新

---

## 总结

我的工作实现了：

✅ **完整的 REST API** - 覆盖 demo.py 的所有功能
✅ **类型安全** - 使用 Pydantic 进行数据验证
✅ **自动文档** - Swagger UI 和 ReDoc
✅ **安全性** - 路径验证和线程安全
✅ **易用性** - 清晰的错误信息和一致的响应格式
✅ **示例代码** - api_demo_example.py 提供可运行的示例

现在您可以：
- 通过 HTTP 请求控制剪映草稿生成
- 集成到 Web 应用中
- 实现自动化视频生产流程
- 远程管理草稿

如有任何问题，欢迎随时询问！
