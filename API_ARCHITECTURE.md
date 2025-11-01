# API 架构说明图

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                         客户端层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Web浏览器│  │ Python   │  │ curl命令 │  │ 其他应用 │   │
│  │ (Swagger)│  │ requests │  │   行      │  │          │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │
                    HTTP 请求 (JSON)
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI 服务器                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   api.py                              │  │
│  │                                                        │  │
│  │  ┌──────────────┐  ┌──────────────┐                 │  │
│  │  │ 路由系统     │  │ 数据验证     │                 │  │
│  │  │ (Endpoints)  │  │ (Pydantic)   │                 │  │
│  │  └──────┬───────┘  └──────┬───────┘                 │  │
│  │         │                  │                          │  │
│  │         └──────────┬───────┘                          │  │
│  │                    │                                   │  │
│  │         ┌──────────▼───────────┐                      │  │
│  │         │   业务逻辑层          │                      │  │
│  │         │  - 创建草稿          │                      │  │
│  │         │  - 添加片段          │                      │  │
│  │         │  - 保存草稿          │                      │  │
│  │         └──────────┬───────────┘                      │  │
│  │                    │                                   │  │
│  │         ┌──────────▼───────────┐                      │  │
│  │         │   存储管理层          │                      │  │
│  │         │  active_drafts: {}   │ (线程安全)          │  │
│  │         │  draft_folders: {}   │                      │  │
│  │         └──────────┬───────────┘                      │  │
│  └────────────────────┼────────────────────────────────┘  │
└───────────────────────┼───────────────────────────────────┘
                        │
                        │ 调用
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 pyJianYingDraft 核心库                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  DraftFolder  →  ScriptFile  →  Segments            │   │
│  │  创建草稿         添加轨道        音频/视频/文本      │   │
│  └─────────────────────┬───────────────────────────────┘   │
└────────────────────────┼─────────────────────────────────────┘
                         │
                         │ 生成
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    文件系统                                  │
│  JianyingPro Drafts/                                        │
│    └── 草稿名称/                                             │
│         ├── draft_content.json  (草稿数据)                  │
│         └── draft_meta_info.json (元信息)                   │
└─────────────────────────────────────────────────────────────┘
```

## 请求处理流程

### 示例：创建视频片段

```
步骤 1: 客户端发送请求
┌─────────────────────────────────────┐
│ POST /draft/test/segment/video      │
│ {                                    │
│   "material_path": "video.mp4",     │
│   "start_time": "0s",               │
│   "duration": "5s",                 │
│   "animation_type": "斜切"          │
│ }                                    │
└──────────────┬──────────────────────┘
               │
               ▼
步骤 2: FastAPI 接收并验证
┌─────────────────────────────────────┐
│ Pydantic 自动验证:                   │
│  ✓ material_path 是字符串            │
│  ✓ start_time 是字符串               │
│  ✓ duration 是字符串                 │
│  ✓ animation_type 是可选字符串       │
└──────────────┬──────────────────────┘
               │
               ▼
步骤 3: 路径安全检查
┌─────────────────────────────────────┐
│ _validate_path("video.mp4")         │
│  ✓ 转换为绝对路径                    │
│  ✓ 检查路径遍历攻击                  │
│  ✓ 验证文件存在                      │
└──────────────┬──────────────────────┘
               │
               ▼
步骤 4: 获取草稿对象
┌─────────────────────────────────────┐
│ _get_draft_from_storage("test")     │
│  使用线程锁                          │
│  从 active_drafts 获取               │
└──────────────┬──────────────────────┘
               │
               ▼
步骤 5: 调用 pyJianYingDraft
┌─────────────────────────────────────┐
│ video_segment = VideoSegment(...)   │
│ animation = IntroType.from_name()   │
│ video_segment.add_animation()       │
│ script.add_segment(video_segment)   │
└──────────────┬──────────────────────┘
               │
               ▼
步骤 6: 返回响应
┌─────────────────────────────────────┐
│ {                                    │
│   "success": true,                  │
│   "message": "视频片段添加成功",     │
│   "draft_name": "test"              │
│ }                                    │
└─────────────────────────────────────┘
```

## 数据模型层次

```
请求模型 (Pydantic)
    │
    ├── DraftFolderCreate
    │   ├── folder_id: str
    │   └── folder_path: str
    │
    ├── DraftCreate
    │   ├── folder_id: str
    │   ├── draft_name: str
    │   ├── width: int (默认1920)
    │   └── height: int (默认1080)
    │
    ├── TrackAdd
    │   ├── track_type: str
    │   ├── track_name: Optional[str]
    │   └── relative_index: Optional[int]
    │
    ├── AudioSegmentAdd
    │   ├── material_path: str
    │   ├── start_time: str
    │   ├── duration: str
    │   ├── volume: Optional[float]
    │   ├── fade_in: Optional[str]
    │   └── fade_out: Optional[str]
    │
    ├── VideoSegmentAdd
    │   ├── material_path: str
    │   ├── start_time: str
    │   ├── duration: str
    │   ├── animation_type: Optional[str]
    │   ├── transition_type: Optional[str]
    │   ├── alpha: Optional[float]
    │   └── scale: Optional[float]
    │
    ├── StickerSegmentAdd
    │   ├── material_path: str
    │   ├── start_time: str
    │   ├── duration: Optional[str]
    │   └── background_blur: Optional[float]
    │
    └── TextSegmentAdd
        ├── text: str
        ├── start_time: str
        ├── duration: str
        ├── font: Optional[str]
        ├── size: Optional[float]
        ├── color: Optional[List[float]]
        ├── transform_y: Optional[float]
        └── animation_type: Optional[str]

响应模型
    │
    └── DraftResponse
        ├── success: bool
        ├── message: str
        ├── draft_name: Optional[str]
        └── data: Optional[Dict]
```

## API 端点分类

```
草稿文件夹管理
├── POST   /folder/register          注册文件夹
└── GET    /folder/{id}/drafts       列出草稿

草稿生命周期
├── POST   /draft/create             创建草稿
├── POST   /draft/{name}/save        保存草稿
└── DELETE /draft/{name}             关闭草稿

轨道管理
└── POST   /draft/{name}/track/add   添加轨道

片段操作
├── POST   /draft/{name}/segment/audio    添加音频
├── POST   /draft/{name}/segment/video    添加视频
├── POST   /draft/{name}/segment/sticker  添加贴纸
└── POST   /draft/{name}/segment/text     添加文本

元数据查询
├── GET    /metadata/fonts                 字体列表
├── GET    /metadata/animations/intro      入场动画
├── GET    /metadata/animations/outro      出场动画
├── GET    /metadata/animations/text-intro 文本入场
├── GET    /metadata/animations/text-outro 文本出场
├── GET    /metadata/transitions           转场效果
└── GET    /metadata/filters               滤镜效果
```

## 线程安全机制

```
多个客户端同时访问
    │
    ├─→ 客户端 A: POST /draft/test1/save
    ├─→ 客户端 B: POST /draft/test2/save
    └─→ 客户端 C: GET  /folder/my/drafts
         │
         ▼
    所有请求进入 FastAPI
         │
         ▼
    需要访问共享资源 (active_drafts)
         │
         ▼
    ┌─────────────────┐
    │  RLock 互斥锁   │
    │  等待队列        │
    └────────┬────────┘
             │
    依次获取锁并执行
             │
    ├─→ A 获取锁 → 执行 → 释放锁
    ├─→ B 获取锁 → 执行 → 释放锁
    └─→ C 获取锁 → 执行 → 释放锁
             │
             ▼
        避免数据竞争
```

## 安全防护层

```
用户输入
    │
    ▼
┌─────────────────────┐
│  路径验证层          │
│                     │
│  检查项:            │
│  • 路径遍历 (..)    │
│  • 绝对路径验证      │
│  • 文件存在性        │
│  • 规范化处理        │
└──────┬──────────────┘
       │ (验证通过)
       ▼
┌─────────────────────┐
│  Pydantic 验证层    │
│                     │
│  检查项:            │
│  • 数据类型         │
│  • 必填字段         │
│  • 数值范围         │
│  • 格式正确性       │
└──────┬──────────────┘
       │ (验证通过)
       ▼
┌─────────────────────┐
│  业务逻辑层         │
│                     │
│  执行:              │
│  • 调用核心库       │
│  • 处理业务逻辑     │
│  • 返回结果         │
└─────────────────────┘
```

## 错误处理流程

```
请求处理
    │
    ├─→ 正常流程
    │       │
    │       ▼
    │   返回 200 OK
    │   {"success": true, ...}
    │
    └─→ 异常情况
            │
            ├─→ 路径不存在
            │       │
            │       ▼
            │   返回 404 Not Found
            │   {"detail": "文件不存在"}
            │
            ├─→ 参数错误
            │       │
            │       ▼
            │   返回 400 Bad Request
            │   {"detail": "无效的动画类型"}
            │
            └─→ 服务器错误
                    │
                    ▼
                返回 500 Internal Error
                {"detail": "内部错误信息"}
```

## 部署架构（生产环境建议）

```
                    ┌────────────┐
                    │   Nginx    │ (反向代理)
                    │  :80/:443  │
                    └─────┬──────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼─────┐   ┌────▼─────┐   ┌────▼─────┐
    │  Uvicorn  │   │ Uvicorn  │   │ Uvicorn  │ (多进程)
    │  Worker 1 │   │ Worker 2 │   │ Worker 3 │
    └─────┬─────┘   └────┬─────┘   └────┬─────┘
          │              │              │
          └──────────────┼──────────────┘
                         │
                    ┌────▼─────┐
                    │  Redis   │ (会话存储)
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │  数据库   │ (持久化)
                    └──────────┘
```

## 开发 vs 生产

```
开发环境:
┌────────────────────────────────┐
│ python api.py                  │
│  单进程                         │
│  内存存储                       │
│  自动重载                       │
│  详细错误信息                   │
└────────────────────────────────┘

生产环境:
┌────────────────────────────────┐
│ uvicorn api:app                │
│  --workers 4                   │ (多进程)
│  --host 0.0.0.0                │ (外部访问)
│  --port 8000                   │
│  使用数据库                     │ (持久化)
│  错误日志记录                   │
│  反向代理 (Nginx)              │
│  HTTPS/SSL                     │
└────────────────────────────────┘
```
