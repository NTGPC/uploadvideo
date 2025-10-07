#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.downloader import VideoDownloader
from src.utils import ConfigManager, Logger

# Setup logging
Logger.setup_logging()

# Test TikTok channel
config = ConfigManager()
downloader = VideoDownloader(config)

# Test URL
test_url = "https://www.tiktok.com/@giangpc99"
print(f"Testing TikTok channel: {test_url}")

try:
    videos = downloader.list_channel_videos(test_url, max_videos=10)
    print(f"Found {len(videos)} videos")
    for i, video in enumerate(videos[:5]):  # Show first 5
        print(f"{i+1}. {video.get('title', 'No title')} - {video.get('url', 'No URL')}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
