#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import re

def debug_tiktok_data(username):
    """Debug TikTok JSON data"""
    try:
        url = f"https://www.tiktok.com/@{username}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            
            # Tìm JSON data
            patterns = [
                r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
                r'<script id="SIGI_STATE" type="application/json">(.*?)</script>'
            ]
            
            for i, pattern in enumerate(patterns):
                matches = re.findall(pattern, html)
                if matches:
                    print(f"Found JSON data with pattern {i+1}")
                    try:
                        data = json.loads(matches[0])
                        print(f"JSON type: {type(data)}")
                        
                        # Tìm video data
                        def find_video_keys(obj, path=""):
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    if 'video' in key.lower() or 'item' in key.lower():
                                        print(f"Found potential video key: {path}.{key}")
                                        if isinstance(value, list) and len(value) > 0:
                                            print(f"  List with {len(value)} items")
                                            if isinstance(value[0], dict):
                                                print(f"  First item keys: {list(value[0].keys())}")
                                    elif isinstance(value, (dict, list)):
                                        find_video_keys(value, f"{path}.{key}")
                            elif isinstance(obj, list) and len(obj) > 0:
                                if isinstance(obj[0], dict):
                                    print(f"List with {len(obj)} items, first item keys: {list(obj[0].keys())}")
                        
                        find_video_keys(data)
                        
                        # Tìm tất cả keys có chứa 'video' hoặc 'item'
                        def find_all_keys(obj, path=""):
                            keys = []
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    current_path = f"{path}.{key}" if path else key
                                    if 'video' in key.lower() or 'item' in key.lower():
                                        keys.append(current_path)
                                    if isinstance(value, (dict, list)):
                                        keys.extend(find_all_keys(value, current_path))
                            elif isinstance(obj, list) and len(obj) > 0:
                                if isinstance(obj[0], dict):
                                    keys.extend(find_all_keys(obj[0], f"{path}[0]"))
                            return keys
                        
                        video_keys = find_all_keys(data)
                        print(f"All video/item keys: {video_keys[:10]}")  # Show first 10
                        
                        return data
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        continue
            
            print("No JSON data found")
            return None
        else:
            print(f"HTTP error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test
username = "giangpc99"
print(f"Debugging TikTok username: {username}")
data = debug_tiktok_data(username)
