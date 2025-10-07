#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import re

def get_tiktok_videos_api(username):
    """Lấy video TikTok sử dụng API chính thức"""
    try:
        # Sử dụng TikTok API endpoint
        api_url = f"https://www.tiktok.com/api/user/detail/?uniqueId={username}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': f'https://www.tiktok.com/@{username}',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        response = requests.get(api_url, headers=headers, timeout=30)
        print(f"API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
            
            # Tìm video trong response
            videos = []
            if 'userInfo' in data and 'user' in data['userInfo']:
                user_data = data['userInfo']['user']
                print(f"User data keys: {list(user_data.keys())}")
                
                # Tìm video count
                video_count = user_data.get('videoCount', 0)
                print(f"Video count: {video_count}")
                
                # Thử lấy video list
                video_list_url = f"https://www.tiktok.com/api/post/item_list/?secUid={user_data.get('secUid', '')}&count=20&maxCursor=0&minCursor=0"
                
                video_response = requests.get(video_list_url, headers=headers, timeout=30)
                print(f"Video list status: {video_response.status_code}")
                
                if video_response.status_code == 200:
                    video_data = video_response.json()
                    print(f"Video data keys: {list(video_data.keys()) if isinstance(video_data, dict) else 'Not dict'}")
                    
                    if 'itemList' in video_data:
                        for item in video_data['itemList']:
                            if 'video' in item:
                                video_info = item['video']
                                videos.append({
                                    'id': video_info.get('id', ''),
                                    'title': video_info.get('desc', 'No title'),
                                    'url': f"https://www.tiktok.com/@{username}/video/{video_info.get('id', '')}",
                                    'duration': video_info.get('duration', 0)
                                })
                
                return videos
            else:
                print("No userInfo found in response")
                return []
        else:
            print(f"API Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        return []

# Test
username = "giangpc99"
print(f"Testing TikTok API for @{username}")
videos = get_tiktok_videos_api(username)
print(f"Found {len(videos)} videos")
for i, video in enumerate(videos[:5]):
    print(f"{i+1}. {video['title']} - {video['url']}")
