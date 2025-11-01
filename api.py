"""
FastAPI application for pyJianYingDraft
Provides REST API endpoints for creating and manipulating JianYing video drafts
"""

import os
import threading
from typing import Optional, List, Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pyJianYingDraft as draft


# Initialize FastAPI app
app = FastAPI(
    title="pyJianYingDraft API",
    description="REST API for creating and manipulating JianYing video drafts",
    version="1.0.0"
)


# Global storage for draft folders and active scripts
# In production, this should be replaced with a proper database
# Using a lock to ensure thread-safe access
_storage_lock = threading.RLock()
active_drafts: Dict[str, draft.ScriptFile] = {}
draft_folders: Dict[str, draft.DraftFolder] = {}


# Helper functions

def _validate_path(path: str, path_type: str = "file") -> str:
    """
    Validate and sanitize file/folder paths to prevent path traversal attacks.

    Args:
        path: The path to validate
        path_type: Either 'file' or 'folder'

    Returns:
        Normalized absolute path

    Raises:
        HTTPException: If path is invalid or contains suspicious patterns
    """
    try:
        # Resolve to absolute path and normalize
        abs_path = os.path.abspath(os.path.normpath(path))

        # Check for path traversal attempts
        if '..' in path or path.startswith('/') and not os.path.isabs(path):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid path: Path traversal detected in {path}"
            )

        # Verify path exists
        if path_type == "file" and not os.path.isfile(abs_path):
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {path}"
            )
        elif path_type == "folder" and not os.path.isdir(abs_path):
            raise HTTPException(
                status_code=404,
                detail=f"Folder not found: {path}"
            )

        return abs_path
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid path: {str(e)}"
        )


def _get_draft_from_storage(draft_name: str) -> draft.ScriptFile:
    """Helper function to safely retrieve a draft from storage"""
    with _storage_lock:
        if draft_name not in active_drafts:
            raise HTTPException(status_code=404, detail=f"Draft '{draft_name}' not found")
        return active_drafts[draft_name]


# Pydantic models for request/response validation
class DraftFolderCreate(BaseModel):
    """Model for registering a draft folder"""
    folder_id: str = Field(..., description="Unique identifier for the draft folder")
    folder_path: str = Field(..., description="Path to the JianYing drafts folder")


class DraftCreate(BaseModel):
    """Model for creating a new draft"""
    folder_id: str = Field(..., description="ID of the draft folder to use")
    draft_name: str = Field(..., description="Name for the new draft")
    width: int = Field(1920, description="Video width in pixels")
    height: int = Field(1080, description="Video height in pixels")
    allow_replace: bool = Field(False, description="Whether to replace existing draft with same name")


class TrackAdd(BaseModel):
    """Model for adding a track to a draft"""
    track_type: str = Field(..., description="Type of track: 'audio', 'video', 'text', 'effect', 'filter'")
    track_name: Optional[str] = Field(None, description="Optional name for the track")
    relative_index: Optional[int] = Field(None, description="Relative position of the track")


class AudioSegmentAdd(BaseModel):
    """Model for adding an audio segment"""
    material_path: str = Field(..., description="Path to audio file")
    start_time: str = Field(..., description="Start time on timeline (e.g., '0s', '1m30s')")
    duration: str = Field(..., description="Duration of the segment (e.g., '5s', '10.5s')")
    track_name: Optional[str] = Field(None, description="Target track name")
    volume: Optional[float] = Field(None, description="Volume level (0.0 to 1.0)")
    fade_in: Optional[str] = Field(None, description="Fade in duration (e.g., '1s')")
    fade_out: Optional[str] = Field(None, description="Fade out duration (e.g., '1s')")


class VideoSegmentAdd(BaseModel):
    """Model for adding a video segment"""
    material_path: str = Field(..., description="Path to video/image file")
    start_time: str = Field(..., description="Start time on timeline")
    duration: str = Field(..., description="Duration of the segment")
    track_name: Optional[str] = Field(None, description="Target track name")
    animation_type: Optional[str] = Field(None, description="Intro animation type")
    transition_type: Optional[str] = Field(None, description="Transition effect type")
    alpha: Optional[float] = Field(None, description="Opacity (0.0 to 1.0)")
    scale: Optional[float] = Field(None, description="Scale factor")


class StickerSegmentAdd(BaseModel):
    """Model for adding a sticker/gif segment"""
    material_path: str = Field(..., description="Path to sticker/gif file")
    start_time: str = Field(..., description="Start time on timeline")
    duration: Optional[str] = Field(None, description="Duration (if None, uses material duration)")
    track_name: Optional[str] = Field(None, description="Target track name")
    background_blur: Optional[float] = Field(None, description="Background blur amount (0.0625 for level 1)")


class TextSegmentAdd(BaseModel):
    """Model for adding a text segment"""
    text: str = Field(..., description="Text content")
    start_time: str = Field(..., description="Start time on timeline")
    duration: str = Field(..., description="Duration of the text")
    track_name: Optional[str] = Field(None, description="Target track name")
    font: Optional[str] = Field(None, description="Font type name")
    size: Optional[float] = Field(None, description="Font size")
    color: Optional[List[float]] = Field(None, description="RGB color as [r, g, b] (0.0 to 1.0)")
    transform_y: Optional[float] = Field(None, description="Vertical position (-1.0 to 1.0)")
    animation_type: Optional[str] = Field(None, description="Animation type")
    bubble_category_id: Optional[str] = Field(None, description="Bubble effect category ID")
    bubble_resource_id: Optional[str] = Field(None, description="Bubble effect resource ID")
    effect_resource_id: Optional[str] = Field(None, description="Flower text effect resource ID")


class DraftResponse(BaseModel):
    """Response model for draft operations"""
    success: bool
    message: str
    draft_name: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


# API Endpoints

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "pyJianYingDraft API",
        "version": "1.0.0",
        "description": "REST API for creating and manipulating JianYing video drafts"
    }


@app.post("/folder/register", response_model=DraftResponse)
async def register_draft_folder(folder_data: DraftFolderCreate):
    """
    Register a JianYing draft folder for use with the API

    This endpoint registers a draft folder path and assigns it a unique ID
    for subsequent operations.
    """
    try:
        # Validate and sanitize the folder path
        validated_path = _validate_path(folder_data.folder_path, path_type="folder")
        folder = draft.DraftFolder(validated_path)
        with _storage_lock:
            draft_folders[folder_data.folder_id] = folder
        return DraftResponse(
            success=True,
            message="Draft folder registered successfully",
            data={"folder_id": folder_data.folder_id, "path": folder_data.folder_path}
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/folder/{folder_id}/drafts")
async def list_drafts(folder_id: str):
    """
    List all drafts in a registered folder
    """
    if folder_id not in draft_folders:
        raise HTTPException(status_code=404, detail=f"Draft folder '{folder_id}' not found")

    try:
        drafts = draft_folders[folder_id].list_drafts()
        return DraftResponse(
            success=True,
            message=f"Found {len(drafts)} drafts",
            data={"drafts": drafts}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/draft/create", response_model=DraftResponse)
async def create_draft(draft_data: DraftCreate):
    """
    Create a new draft

    Creates a new JianYing draft with specified dimensions in the registered folder.
    Note: Draft names should be unique across all folders to avoid conflicts.
    """
    with _storage_lock:
        if draft_data.folder_id not in draft_folders:
            raise HTTPException(status_code=404, detail=f"Draft folder '{draft_data.folder_id}' not found")

    try:
        folder = draft_folders[draft_data.folder_id]
        script = folder.create_draft(
            draft_data.draft_name,
            draft_data.width,
            draft_data.height,
            allow_replace=draft_data.allow_replace
        )

        # Store the draft in active drafts
        # Note: In production, consider using folder_id + draft_name as composite key
        with _storage_lock:
            active_drafts[draft_data.draft_name] = script

        return DraftResponse(
            success=True,
            message=f"Draft '{draft_data.draft_name}' created successfully",
            draft_name=draft_data.draft_name,
            data={
                "width": draft_data.width,
                "height": draft_data.height,
                "folder_id": draft_data.folder_id
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/draft/{draft_name}/track/add", response_model=DraftResponse)
async def add_track(draft_name: str, track_data: TrackAdd):
    """
    Add a track to an existing draft

    Adds a new track (audio, video, text, effect, or filter) to the draft.
    """
    script = _get_draft_from_storage(draft_name)

    try:
        # Map track type string to enum
        track_type_map = {
            'audio': draft.TrackType.audio,
            'video': draft.TrackType.video,
            'text': draft.TrackType.text,
            'effect': draft.TrackType.effect,
            'filter': draft.TrackType.filter
        }

        if track_data.track_type not in track_type_map:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid track type. Must be one of: {list(track_type_map.keys())}"
            )

        track_type = track_type_map[track_data.track_type]

        # Build kwargs, excluding None values for optional parameters
        kwargs = {}
        if track_data.track_name is not None:
            kwargs['track_name'] = track_data.track_name
        if track_data.relative_index is not None:
            kwargs['relative_index'] = track_data.relative_index

        script.add_track(track_type, **kwargs)

        return DraftResponse(
            success=True,
            message=f"Track '{track_data.track_type}' added successfully",
            draft_name=draft_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/draft/{draft_name}/segment/audio", response_model=DraftResponse)
async def add_audio_segment(draft_name: str, segment_data: AudioSegmentAdd):
    """
    Add an audio segment to the draft

    Creates an audio segment with optional volume and fade effects.
    """
    script = _get_draft_from_storage(draft_name)

    try:
        # Validate and sanitize the audio file path
        validated_path = _validate_path(segment_data.material_path, path_type="file")

        # Create audio segment
        audio_segment = draft.AudioSegment(
            validated_path,
            draft.trange(segment_data.start_time, segment_data.duration),
            volume=segment_data.volume
        )

        # Add fade effects if specified
        if segment_data.fade_in is not None or segment_data.fade_out is not None:
            audio_segment.add_fade(
                segment_data.fade_in or "0s",
                segment_data.fade_out or "0s"
            )

        # Add to script
        script.add_segment(audio_segment, segment_data.track_name)

        return DraftResponse(
            success=True,
            message="Audio segment added successfully",
            draft_name=draft_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/draft/{draft_name}/segment/video", response_model=DraftResponse)
async def add_video_segment(draft_name: str, segment_data: VideoSegmentAdd):
    """
    Add a video segment to the draft

    Creates a video segment with optional animation, transition, and visual effects.
    """
    script = _get_draft_from_storage(draft_name)

    try:
        # Validate and sanitize the video file path
        validated_path = _validate_path(segment_data.material_path, path_type="file")

        # Create clip settings if any visual parameters are specified
        clip_settings = None
        if segment_data.alpha is not None or segment_data.scale is not None:
            clip_settings = draft.ClipSettings(
                alpha=segment_data.alpha,
                scale=segment_data.scale
            )

        # Create video segment
        video_segment = draft.VideoSegment(
            validated_path,
            draft.trange(segment_data.start_time, segment_data.duration),
            clip_settings=clip_settings
        )

        # Add animation if specified
        if segment_data.animation_type:
            try:
                animation = draft.IntroType.from_name(segment_data.animation_type)
                video_segment.add_animation(animation)
            except (AttributeError, ValueError):
                raise HTTPException(status_code=400, detail=f"Invalid animation type: {segment_data.animation_type}")

        # Add transition if specified
        if segment_data.transition_type:
            try:
                transition = draft.TransitionType.from_name(segment_data.transition_type)
                video_segment.add_transition(transition)
            except (AttributeError, ValueError):
                raise HTTPException(status_code=400, detail=f"Invalid transition type: {segment_data.transition_type}")

        # Add to script
        script.add_segment(video_segment, segment_data.track_name)

        return DraftResponse(
            success=True,
            message="Video segment added successfully",
            draft_name=draft_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/draft/{draft_name}/segment/sticker", response_model=DraftResponse)
async def add_sticker_segment(draft_name: str, segment_data: StickerSegmentAdd):
    """
    Add a sticker/GIF segment to the draft

    Creates a sticker or GIF segment with optional background blur effect.
    """
    script = _get_draft_from_storage(draft_name)

    try:
        # Validate and sanitize the sticker file path
        validated_path = _validate_path(segment_data.material_path, path_type="file")

        # Create material to get duration if needed
        gif_material = draft.VideoMaterial(validated_path)

        # Use provided duration or material duration
        duration = segment_data.duration or gif_material.duration

        # Create sticker segment
        gif_segment = draft.VideoSegment(
            gif_material,
            draft.trange(segment_data.start_time, duration)
        )

        # Add background blur if specified
        if segment_data.background_blur is not None:
            gif_segment.add_background_filling("blur", segment_data.background_blur)

        # Add to script
        script.add_segment(gif_segment, segment_data.track_name)

        return DraftResponse(
            success=True,
            message="Sticker segment added successfully",
            draft_name=draft_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/draft/{draft_name}/segment/text", response_model=DraftResponse)
async def add_text_segment(draft_name: str, segment_data: TextSegmentAdd):
    """
    Add a text segment to the draft

    Creates a text segment with customizable font, style, position, and effects.
    """
    script = _get_draft_from_storage(draft_name)

    try:

        # Build text style
        text_style = None
        if segment_data.size or segment_data.color:
            style_args = {}
            if segment_data.size:
                style_args['size'] = segment_data.size
            if segment_data.color:
                if len(segment_data.color) != 3:
                    raise HTTPException(status_code=400, detail="Color must be [r, g, b] with values 0.0-1.0")
                style_args['color'] = tuple(segment_data.color)
            text_style = draft.TextStyle(**style_args)

        # Build clip settings
        clip_settings = None
        if segment_data.transform_y is not None:
            clip_settings = draft.ClipSettings(transform_y=segment_data.transform_y)

        # Get font if specified
        font = None
        if segment_data.font:
            try:
                font = draft.FontType.from_name(segment_data.font)
            except (AttributeError, ValueError):
                raise HTTPException(status_code=400, detail=f"Invalid font type: {segment_data.font}")

        # Create text segment
        text_segment = draft.TextSegment(
            segment_data.text,
            draft.trange(segment_data.start_time, segment_data.duration),
            font=font,
            style=text_style,
            clip_settings=clip_settings
        )

        # Add animation if specified
        if segment_data.animation_type:
            try:
                # Try text outro first, then intro
                try:
                    animation = draft.TextOutro.from_name(segment_data.animation_type)
                except (AttributeError, ValueError):
                    animation = draft.TextIntro.from_name(segment_data.animation_type)
                text_segment.add_animation(animation)
            except (AttributeError, ValueError):
                raise HTTPException(status_code=400, detail=f"Invalid text animation type: {segment_data.animation_type}")

        # Add bubble effect if specified
        if segment_data.bubble_category_id and segment_data.bubble_resource_id:
            text_segment.add_bubble(segment_data.bubble_category_id, segment_data.bubble_resource_id)

        # Add flower text effect if specified
        if segment_data.effect_resource_id:
            text_segment.add_effect(segment_data.effect_resource_id)

        # Add to script
        script.add_segment(text_segment, segment_data.track_name)

        return DraftResponse(
            success=True,
            message="Text segment added successfully",
            draft_name=draft_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/draft/{draft_name}/save", response_model=DraftResponse)
async def save_draft(draft_name: str):
    """
    Save the draft

    Saves all changes to the draft file.
    """
    script = _get_draft_from_storage(draft_name)

    try:
        script.save()

        return DraftResponse(
            success=True,
            message=f"Draft '{draft_name}' saved successfully",
            draft_name=draft_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/draft/{draft_name}", response_model=DraftResponse)
async def close_draft(draft_name: str):
    """
    Close and remove a draft from active drafts

    This does not delete the draft file, only removes it from the active drafts in memory.
    """
    with _storage_lock:
        if draft_name not in active_drafts:
            raise HTTPException(status_code=404, detail=f"Draft '{draft_name}' not found")

    try:
        with _storage_lock:
            del active_drafts[draft_name]

        return DraftResponse(
            success=True,
            message=f"Draft '{draft_name}' closed successfully",
            draft_name=draft_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metadata/fonts")
async def list_fonts():
    """
    List all available font types
    """
    try:
        fonts = [f.name for f in draft.FontType]
        return {
            "success": True,
            "count": len(fonts),
            "fonts": fonts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metadata/animations/intro")
async def list_intro_animations():
    """
    List all available intro animation types
    """
    try:
        animations = [a.name for a in draft.IntroType]
        return {
            "success": True,
            "count": len(animations),
            "animations": animations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metadata/animations/outro")
async def list_outro_animations():
    """
    List all available outro animation types
    """
    try:
        animations = [a.name for a in draft.OutroType]
        return {
            "success": True,
            "count": len(animations),
            "animations": animations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metadata/animations/text-intro")
async def list_text_intro_animations():
    """
    List all available text intro animation types
    """
    try:
        animations = [a.name for a in draft.TextIntro]
        return {
            "success": True,
            "count": len(animations),
            "animations": animations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metadata/animations/text-outro")
async def list_text_outro_animations():
    """
    List all available text outro animation types
    """
    try:
        animations = [a.name for a in draft.TextOutro]
        return {
            "success": True,
            "count": len(animations),
            "animations": animations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metadata/transitions")
async def list_transitions():
    """
    List all available transition types
    """
    try:
        transitions = [t.name for t in draft.TransitionType]
        return {
            "success": True,
            "count": len(transitions),
            "transitions": transitions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metadata/filters")
async def list_filters():
    """
    List all available filter types
    """
    try:
        filters = [f.name for f in draft.FilterType]
        return {
            "success": True,
            "count": len(filters),
            "filters": filters
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
