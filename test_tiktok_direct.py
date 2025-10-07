#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import re

def get_tiktok_videos(username):
    """Lấy danh sách video TikTok trực tiếp từ API"""
    try:
        # URL để lấy thông tin user
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
            # Tìm JSON data trong HTML
            html = response.text
            print(f"HTML length: {len(html)}")
            
            # Tìm pattern JSON data
            patterns = [
                r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'<script id="SIGI_STATE" type="application/json">(.*?)</script>'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html)
                if matches:
                    print(f"Found JSON data with pattern: {pattern}")
                    try:
                        data = json.loads(matches[0])
                        print(f"JSON keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        return data
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        continue
            
            print("No JSON data found in HTML")
            return None
        else:
            print(f"HTTP error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test
username = "giangpc99"
print(f"Testing TikTok username: {username}")
data = get_tiktok_videos(username)
if data:
    print("Success! Found data")
    print(json.dumps(data, indent=2)[:500] + "...")
else:
    print("Failed to get data")
