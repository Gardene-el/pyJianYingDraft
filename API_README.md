# pyJianYingDraft FastAPI Documentation

This document describes the FastAPI endpoints added to pyJianYingDraft for programmatic creation and manipulation of JianYing video drafts.

## Installation

Install the required dependencies:

```bash
pip install fastapi uvicorn pydantic
```

Or install all requirements from the updated requirements.txt:

```bash
pip install -r requirements.txt
```

## Starting the API Server

Run the API server using uvicorn:

```bash
# From the project root directory
python api.py

# Or using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

Interactive API documentation (Swagger UI) will be available at `http://localhost:8000/docs`

Alternative API documentation (ReDoc) will be available at `http://localhost:8000/redoc`

## API Endpoints

### Root Endpoint

#### GET `/`
Returns basic API information.

**Response:**
```json
{
  "name": "pyJianYingDraft API",
  "version": "1.0.0",
  "description": "REST API for creating and manipulating JianYing video drafts"
}
```

---

### Draft Folder Management

#### POST `/folder/register`
Register a JianYing draft folder for use with the API.

**Request Body:**
```json
{
  "folder_id": "my_folder",
  "folder_path": "C:/Users/YourName/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Draft folder registered successfully",
  "data": {
    "folder_id": "my_folder",
    "path": "C:/Users/YourName/..."
  }
}
```

#### GET `/folder/{folder_id}/drafts`
List all drafts in a registered folder.

**Response:**
```json
{
  "success": true,
  "message": "Found 5 drafts",
  "data": {
    "drafts": ["draft1", "draft2", "draft3", "draft4", "draft5"]
  }
}
```

---

### Draft Operations

#### POST `/draft/create`
Create a new draft.

**Request Body:**
```json
{
  "folder_id": "my_folder",
  "draft_name": "my_video_project",
  "width": 1920,
  "height": 1080,
  "allow_replace": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Draft 'my_video_project' created successfully",
  "draft_name": "my_video_project",
  "data": {
    "width": 1920,
    "height": 1080
  }
}
```

#### POST `/draft/{draft_name}/track/add`
Add a track to an existing draft.

**Request Body:**
```json
{
  "track_type": "video",
  "track_name": "main_video",
  "relative_index": 1
}
```

Valid track types: `audio`, `video`, `text`, `effect`, `filter`

**Response:**
```json
{
  "success": true,
  "message": "Track 'video' added successfully",
  "draft_name": "my_video_project"
}
```

---

### Segment Operations

#### POST `/draft/{draft_name}/segment/audio`
Add an audio segment to the draft.

**Request Body:**
```json
{
  "material_path": "/path/to/audio.mp3",
  "start_time": "0s",
  "duration": "5s",
  "track_name": null,
  "volume": 0.6,
  "fade_in": "1s",
  "fade_out": "0s"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Audio segment added successfully",
  "draft_name": "my_video_project"
}
```

#### POST `/draft/{draft_name}/segment/video`
Add a video segment to the draft.

**Request Body:**
```json
{
  "material_path": "/path/to/video.mp4",
  "start_time": "0s",
  "duration": "4.2s",
  "track_name": null,
  "animation_type": "斜切",
  "transition_type": "信号故障",
  "alpha": 1.0,
  "scale": 1.0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Video segment added successfully",
  "draft_name": "my_video_project"
}
```

#### POST `/draft/{draft_name}/segment/sticker`
Add a sticker/GIF segment to the draft.

**Request Body:**
```json
{
  "material_path": "/path/to/sticker.gif",
  "start_time": "4.2s",
  "duration": null,
  "track_name": null,
  "background_blur": 0.0625
}
```

**Response:**
```json
{
  "success": true,
  "message": "Sticker segment added successfully",
  "draft_name": "my_video_project"
}
```

#### POST `/draft/{draft_name}/segment/text`
Add a text segment to the draft.

**Request Body:**
```json
{
  "text": "据说pyJianYingDraft效果还不错?",
  "start_time": "0s",
  "duration": "4.2s",
  "track_name": null,
  "font": "文轩体",
  "size": 5.0,
  "color": [1.0, 1.0, 0.0],
  "transform_y": -0.8,
  "animation_type": "故障闪动",
  "bubble_category_id": "361595",
  "bubble_resource_id": "6742029398926430728",
  "effect_resource_id": "7296357486490144036"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Text segment added successfully",
  "draft_name": "my_video_project"
}
```

---

### Draft Finalization

#### POST `/draft/{draft_name}/save`
Save all changes to the draft.

**Response:**
```json
{
  "success": true,
  "message": "Draft 'my_video_project' saved successfully",
  "draft_name": "my_video_project"
}
```

#### DELETE `/draft/{draft_name}`
Close and remove a draft from active drafts (does not delete the file).

**Response:**
```json
{
  "success": true,
  "message": "Draft 'my_video_project' closed successfully",
  "draft_name": "my_video_project"
}
```

---

### Metadata Endpoints

These endpoints provide lists of available options for various effects and styles.

#### GET `/metadata/fonts`
List all available font types.

**Response:**
```json
{
  "success": true,
  "count": 50,
  "fonts": ["文轩体", "思源黑体", "华文楷体", ...]
}
```

#### GET `/metadata/animations/intro`
List all available intro animation types.

#### GET `/metadata/animations/outro`
List all available outro animation types.

#### GET `/metadata/animations/text-intro`
List all available text intro animation types.

#### GET `/metadata/animations/text-outro`
List all available text outro animation types.

#### GET `/metadata/transitions`
List all available transition types.

#### GET `/metadata/filters`
List all available filter types.

---

## Complete Example: Recreating demo.py via API

Here's how to recreate the demo.py example using the API endpoints:

```bash
# 1. Register draft folder
curl -X POST "http://localhost:8000/folder/register" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_id": "my_folder",
    "folder_path": "C:/path/to/JianyingPro Drafts"
  }'

# 2. Create draft
curl -X POST "http://localhost:8000/draft/create" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_id": "my_folder",
    "draft_name": "api_demo",
    "width": 1920,
    "height": 1080,
    "allow_replace": true
  }'

# 3. Add tracks
curl -X POST "http://localhost:8000/draft/api_demo/track/add" \
  -H "Content-Type: application/json" \
  -d '{"track_type": "audio"}'

curl -X POST "http://localhost:8000/draft/api_demo/track/add" \
  -H "Content-Type: application/json" \
  -d '{"track_type": "video"}'

curl -X POST "http://localhost:8000/draft/api_demo/track/add" \
  -H "Content-Type: application/json" \
  -d '{"track_type": "text"}'

# 4. Add audio segment with fade
curl -X POST "http://localhost:8000/draft/api_demo/segment/audio" \
  -H "Content-Type: application/json" \
  -d '{
    "material_path": "/path/to/audio.mp3",
    "start_time": "0s",
    "duration": "5s",
    "volume": 0.6,
    "fade_in": "1s",
    "fade_out": "0s"
  }'

# 5. Add video segment with animation
curl -X POST "http://localhost:8000/draft/api_demo/segment/video" \
  -H "Content-Type: application/json" \
  -d '{
    "material_path": "/path/to/video.mp4",
    "start_time": "0s",
    "duration": "4.2s",
    "animation_type": "斜切",
    "transition_type": "信号故障"
  }'

# 6. Add GIF segment with background blur
curl -X POST "http://localhost:8000/draft/api_demo/segment/sticker" \
  -H "Content-Type: application/json" \
  -d '{
    "material_path": "/path/to/sticker.gif",
    "start_time": "4.2s",
    "background_blur": 0.0625
  }'

# 7. Add text segment with effects
curl -X POST "http://localhost:8000/draft/api_demo/segment/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "据说pyJianYingDraft效果还不错?",
    "start_time": "0s",
    "duration": "4.2s",
    "font": "文轩体",
    "color": [1.0, 1.0, 0.0],
    "transform_y": -0.8,
    "animation_type": "故障闪动",
    "bubble_category_id": "361595",
    "bubble_resource_id": "6742029398926430728",
    "effect_resource_id": "7296357486490144036"
  }'

# 8. Save draft
curl -X POST "http://localhost:8000/draft/api_demo/save"
```

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Register folder
response = requests.post(f"{BASE_URL}/folder/register", json={
    "folder_id": "my_folder",
    "folder_path": "C:/path/to/JianyingPro Drafts"
})
print(response.json())

# Create draft
response = requests.post(f"{BASE_URL}/draft/create", json={
    "folder_id": "my_folder",
    "draft_name": "api_demo",
    "width": 1920,
    "height": 1080,
    "allow_replace": True
})
print(response.json())

# Add video track
response = requests.post(f"{BASE_URL}/draft/api_demo/track/add", json={
    "track_type": "video"
})
print(response.json())

# Add video segment
response = requests.post(f"{BASE_URL}/draft/api_demo/segment/video", json={
    "material_path": "/path/to/video.mp4",
    "start_time": "0s",
    "duration": "5s",
    "animation_type": "斜切"
})
print(response.json())

# Save draft
response = requests.post(f"{BASE_URL}/draft/api_demo/save")
print(response.json())
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `404`: Resource not found (draft, folder, or file)
- `400`: Bad request (invalid parameters)
- `500`: Internal server error

Error responses include a detail message:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Notes

- Time values can be specified in various formats: `"1s"`, `"1.5s"`, `"1m30s"`, `"1h3m12s"`
- Colors are specified as RGB arrays with values from 0.0 to 1.0: `[1.0, 0.0, 0.0]` for red
- File paths should be absolute paths to ensure the API can find the resources
- The API stores active drafts in memory, so restarting the server will clear all active drafts
- For production use, consider implementing persistent storage for draft state
