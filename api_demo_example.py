#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example script demonstrating how to use the pyJianYingDraft FastAPI

This script recreates the demo.py example using REST API calls instead of
direct library calls, showing how to use the API for automated video draft creation.
"""

import requests
import os
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
DRAFT_FOLDER_PATH = r"<你的草稿文件夹>"  # Replace with your JianYing draft folder path
TUTORIAL_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'readme_assets', 'tutorial')


def create_demo_draft_via_api():
    """
    Create a demo draft using the FastAPI endpoints.
    This recreates the same draft as demo.py but via API calls.
    """

    print("=== Creating Demo Draft via API ===\n")

    # Step 1: Register draft folder
    print("1. Registering draft folder...")
    response = requests.post(f"{API_BASE_URL}/folder/register", json={
        "folder_id": "my_drafts",
        "folder_path": DRAFT_FOLDER_PATH
    })
    if response.status_code != 200:
        print(f"Error: {response.json()}")
        return
    print(f"   ✓ Folder registered: {response.json()['message']}\n")

    # Step 2: Create draft
    print("2. Creating draft...")
    response = requests.post(f"{API_BASE_URL}/draft/create", json={
        "folder_id": "my_drafts",
        "draft_name": "api_demo",
        "width": 1920,
        "height": 1080,
        "allow_replace": True
    })
    if response.status_code != 200:
        print(f"Error: {response.json()}")
        return
    print(f"   ✓ Draft created: {response.json()['message']}\n")

    # Step 3: Add tracks
    print("3. Adding tracks...")
    for track_type in ['audio', 'video', 'text']:
        response = requests.post(f"{API_BASE_URL}/draft/api_demo/track/add", json={
            "track_type": track_type
        })
        if response.status_code != 200:
            print(f"   Error adding {track_type} track: {response.json()}")
            return
        print(f"   ✓ {track_type.capitalize()} track added")
    print()

    # Step 4: Add audio segment with fade
    print("4. Adding audio segment...")
    audio_path = os.path.join(TUTORIAL_ASSET_DIR, 'audio.mp3')
    if os.path.exists(audio_path):
        response = requests.post(f"{API_BASE_URL}/draft/api_demo/segment/audio", json={
            "material_path": audio_path,
            "start_time": "0s",
            "duration": "5s",
            "volume": 0.6,
            "fade_in": "1s",
            "fade_out": "0s"
        })
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
        else:
            print(f"   ✓ Audio segment added with fade\n")
    else:
        print(f"   ⚠ Audio file not found: {audio_path}\n")

    # Step 5: Add video segment with animation
    print("5. Adding video segment...")
    video_path = os.path.join(TUTORIAL_ASSET_DIR, 'video.mp4')
    if os.path.exists(video_path):
        response = requests.post(f"{API_BASE_URL}/draft/api_demo/segment/video", json={
            "material_path": video_path,
            "start_time": "0s",
            "duration": "4.2s",
            "animation_type": "斜切",
            "transition_type": "信号故障"
        })
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
        else:
            print(f"   ✓ Video segment added with animation and transition\n")
    else:
        print(f"   ⚠ Video file not found: {video_path}\n")

    # Step 6: Add GIF/sticker segment with background blur
    print("6. Adding sticker segment...")
    gif_path = os.path.join(TUTORIAL_ASSET_DIR, 'sticker.gif')
    if os.path.exists(gif_path):
        response = requests.post(f"{API_BASE_URL}/draft/api_demo/segment/sticker", json={
            "material_path": gif_path,
            "start_time": "4.2s",
            "duration": None,  # Use material duration
            "background_blur": 0.0625
        })
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
        else:
            print(f"   ✓ Sticker segment added with background blur\n")
    else:
        print(f"   ⚠ Sticker file not found: {gif_path}\n")

    # Step 7: Add text segment with effects
    print("7. Adding text segment...")
    response = requests.post(f"{API_BASE_URL}/draft/api_demo/segment/text", json={
        "text": "据说pyJianYingDraft效果还不错?",
        "start_time": "0s",
        "duration": "4.2s",
        "font": "文轩体",
        "size": None,
        "color": [1.0, 1.0, 0.0],  # Yellow color
        "transform_y": -0.8,  # Position at bottom
        "animation_type": "故障闪动",
        "bubble_category_id": "361595",
        "bubble_resource_id": "6742029398926430728",
        "effect_resource_id": "7296357486490144036"
    })
    if response.status_code != 200:
        print(f"   Error: {response.json()}")
    else:
        print(f"   ✓ Text segment added with bubble and flower effects\n")

    # Step 8: Save draft
    print("8. Saving draft...")
    response = requests.post(f"{API_BASE_URL}/draft/api_demo/save")
    if response.status_code != 200:
        print(f"Error: {response.json()}")
        return
    print(f"   ✓ Draft saved successfully!\n")

    print("=== Demo Completed ===")
    print("You can now open 'api_demo' draft in JianYing to see the result.")


def list_available_metadata():
    """
    List available fonts, animations, transitions, etc.
    """
    print("\n=== Available Metadata ===\n")

    # List fonts
    response = requests.get(f"{API_BASE_URL}/metadata/fonts")
    if response.status_code == 200:
        data = response.json()
        print(f"Available Fonts ({data['count']}): {', '.join(data['fonts'][:10])}...")

    # List intro animations
    response = requests.get(f"{API_BASE_URL}/metadata/animations/intro")
    if response.status_code == 200:
        data = response.json()
        print(f"Intro Animations ({data['count']}): {', '.join(data['animations'][:10])}...")

    # List transitions
    response = requests.get(f"{API_BASE_URL}/metadata/transitions")
    if response.status_code == 200:
        data = response.json()
        print(f"Transitions ({data['count']}): {', '.join(data['transitions'][:10])}...")

    # List filters
    response = requests.get(f"{API_BASE_URL}/metadata/filters")
    if response.status_code == 200:
        data = response.json()
        print(f"Filters ({data['count']}): {', '.join(data['filters'][:10])}...")


if __name__ == "__main__":
    # Check if API server is running
    try:
        response = requests.get(API_BASE_URL, timeout=2)
        if response.status_code != 200:
            print("Error: API server is not responding correctly")
            print("Please start the API server first:")
            print("  python api.py")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to API server")
        print("Please start the API server first:")
        print("  python api.py")
        exit(1)

    # Run the demo
    create_demo_draft_via_api()

    # List metadata
    list_available_metadata()
