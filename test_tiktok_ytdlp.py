#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yt_dlp
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils import Logger

# Setup logging
Logger.setup_logging()

def test_tiktok_ytdlp():
    """Test TikTok với yt-dlp options đặc biệt"""
    try:
        username = "giangpc99"
        url = f"https://www.tiktok.com/@{username}"
        
        # Options đặc biệt cho TikTok
        opts = {
            'quiet': True,
            'extract_flat': True,
            'playlistend': 20,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            'extractor_args': {
                'tiktok': {
                    'api_hostname': 'api.tiktokv.com'
                }
            },
            'ignoreerrors': True,
            'no_warnings': False
        }
        
        print(f"Testing TikTok URL: {url}")
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info is None:
                print("No info extracted")
                return []
            
            print(f"Info type: {type(info)}")
            print(f"Info keys: {list(info.keys()) if isinstance(info, dict) else 'Not dict'}")
            
            entries = []
            if 'entries' in info and isinstance(info['entries'], list):
                entries = info['entries']
                print(f"Found {len(entries)} entries")
                
                for i, entry in enumerate(entries[:5]):
                    print(f"Entry {i+1}: {entry}")
            else:
                print("No entries found")
            
            return entries
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

# Test
videos = test_tiktok_ytdlp()
print(f"Total videos found: {len(videos)}")
