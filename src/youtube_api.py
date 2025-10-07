"""
YouTube Data API v3 Service
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .utils import Logger

class YouTubeAPIService:
    """Service để tương tác với YouTube Data API v3"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Khởi tạo YouTube API service"""
        try:
            if not self.api_key:
                Logger.log_error("YouTube API key không được cung cấp")
                return
            
            self.service = build('youtube', 'v3', developerKey=self.api_key)
            Logger.log_info("YouTube API service đã được khởi tạo")
            
        except Exception as e:
            Logger.log_error(f"Lỗi khởi tạo YouTube API service: {e}")
            self.service = None
    
    def is_available(self) -> bool:
        """Kiểm tra API có sẵn không"""
        return self.service is not None
    
    def get_channel_info(self, channel_url: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin channel từ URL"""
        try:
            if not self.is_available():
                Logger.log_error("YouTube API service không khả dụng")
                return None
            
            # Trích xuất channel ID từ URL
            channel_id = self._extract_channel_id(channel_url)
            if not channel_id:
                Logger.log_error("Không thể trích xuất channel ID từ URL")
                return None
            
            # Lấy thông tin channel
            request = self.service.channels().list(
                part='snippet,statistics',
                id=channel_id
            )
            response = request.execute()
            
            if not response['items']:
                Logger.log_error("Channel không tồn tại")
                return None
            
            channel = response['items'][0]
            snippet = channel['snippet']
            statistics = channel['statistics']
            
            return {
                'id': channel['id'],
                'title': snippet['title'],
                'description': snippet['description'],
                'custom_url': snippet.get('customUrl'),
                'subscriber_count': int(statistics.get('subscriberCount', 0)),
                'video_count': int(statistics.get('videoCount', 0)),
                'view_count': int(statistics.get('viewCount', 0)),
                'thumbnail': snippet['thumbnails']['high']['url'],
                'country': snippet.get('country'),
                'published_at': snippet['publishedAt']
            }
            
        except HttpError as e:
            if e.resp.status == 403:
                Logger.log_error("YouTube API quota đã hết hoặc bị từ chối")
            elif e.resp.status == 404:
                Logger.log_error("Channel không tồn tại")
            else:
                Logger.log_error(f"Lỗi HTTP YouTube API: {e}")
            return None
        except Exception as e:
            Logger.log_error(f"Lỗi lấy thông tin channel: {e}")
            return None
    
    def get_channel_videos(self, channel_url: str, max_results: int = 200) -> List[Dict[str, Any]]:
        """Lấy danh sách video của channel"""
        try:
            if not self.is_available():
                Logger.log_error("YouTube API service không khả dụng")
                return []
            
            # Lấy channel ID
            channel_id = self._extract_channel_id(channel_url)
            if not channel_id:
                Logger.log_error("Không thể trích xuất channel ID từ URL")
                return []
            
            # Thử phương pháp 1: Sử dụng uploads playlist (hiệu quả hơn)
            videos = self._get_videos_from_uploads_playlist(channel_id, max_results)
            
            # Nếu không đủ video, thử phương pháp 2: Search API
            if len(videos) < max_results * 0.5:  # Nếu ít hơn 50% số video mong muốn
                Logger.log_info("Uploads playlist không đủ video, thử Search API...")
                search_videos = self._get_videos_from_search(channel_id, max_results)
                if len(search_videos) > len(videos):
                    videos = search_videos
            
            Logger.log_info(f"Hoàn thành: Đã lấy {len(videos)} video từ channel")
            return videos
            
        except Exception as e:
            Logger.log_error(f"Lỗi tổng quát: {e}")
            return []
    
    def _get_videos_from_uploads_playlist(self, channel_id: str, max_results: int) -> List[Dict[str, Any]]:
        """Lấy video từ uploads playlist (hiệu quả hơn)"""
        try:
            # Lấy thông tin channel để lấy uploads playlist ID
            channel_request = self.service.channels().list(
                part='contentDetails',
                id=channel_id
            )
            channel_response = channel_request.execute()
            
            if not channel_response['items']:
                Logger.log_warning("Không tìm thấy channel")
                return []
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            Logger.log_info(f"Uploads playlist ID: {uploads_playlist_id}")
            
            videos = []
            next_page_token = None
            page_count = 0
            
            while len(videos) < max_results:
                try:
                    # Lấy video từ uploads playlist
                    playlist_request = self.service.playlistItems().list(
                        part='snippet,contentDetails',
                        playlistId=uploads_playlist_id,
                        maxResults=min(50, max_results - len(videos)),
                        pageToken=next_page_token
                    )
                    playlist_response = playlist_request.execute()
                    
                    if 'items' not in playlist_response or not playlist_response['items']:
                        Logger.log_info("Không còn video trong playlist")
                        break
                    
                    # Lấy video IDs để lấy thông tin chi tiết
                    video_ids = [item['contentDetails']['videoId'] for item in playlist_response['items']]
                    
                    # Lấy thông tin chi tiết của tất cả video trong batch
                    videos_request = self.service.videos().list(
                        part='snippet,contentDetails,statistics',
                        id=','.join(video_ids)
                    )
                    videos_response = videos_request.execute()
                    
                    # Xử lý từng video
                    for item in videos_response['items']:
                        if len(videos) >= max_results:
                            break
                            
                        snippet = item['snippet']
                        content_details = item['contentDetails']
                        statistics = item['statistics']
                        
                        # Parse duration
                        duration_iso = content_details.get('duration', 'PT0S')
                        duration_seconds = self._parse_iso8601_duration(duration_iso)
                        
                        videos.append({
                            'id': item['id'],
                            'title': snippet['title'],
                            'description': snippet['description'],
                            'url': f"https://www.youtube.com/watch?v={item['id']}",
                            'thumbnail': snippet['thumbnails']['high']['url'],
                            'published_at': snippet['publishedAt'],
                            'duration': duration_seconds,
                            'view_count': int(statistics.get('viewCount', 0)),
                            'like_count': int(statistics.get('likeCount', 0)),
                            'comment_count': int(statistics.get('commentCount', 0))
                        })
                    
                    next_page_token = playlist_response.get('nextPageToken')
                    if not next_page_token:
                        break
                        
                    page_count += 1
                    Logger.log_info(f"Đã lấy trang {page_count}, tổng cộng {len(videos)} video...")
                    
                    # Delay để tránh rate limit
                    import time
                    time.sleep(0.3)
                    
                except HttpError as e:
                    if e.resp.status == 403:
                        Logger.log_error("YouTube API quota đã hết")
                        break
                    else:
                        Logger.log_error(f"Lỗi HTTP {e.resp.status}: {e}")
                        break
                except Exception as e:
                    Logger.log_error(f"Lỗi xử lý playlist: {e}")
                    break
            
            return videos
            
        except Exception as e:
            Logger.log_error(f"Lỗi lấy uploads playlist: {e}")
            return []
    
    def _get_videos_from_search(self, channel_id: str, max_results: int) -> List[Dict[str, Any]]:
        """Lấy video từ Search API (fallback)"""
        try:
            videos = []
            next_page_token = None
            page_count = 0
            max_pages = (max_results + 49) // 50
            
            Logger.log_info(f"Bắt đầu lấy video từ Search API, tối đa {max_results} video...")
            
            while len(videos) < max_results and page_count < max_pages:
                try:
                    # Lấy danh sách video (50 video/lần)
                    request = self.service.search().list(
                        part='snippet',
                        channelId=channel_id,
                        type='video',
                        order='date',
                        maxResults=min(50, max_results - len(videos)),
                        pageToken=next_page_token
                    )
                    response = request.execute()
                    
                    # Kiểm tra có video không
                    if 'items' not in response or not response['items']:
                        Logger.log_warning(f"Trang {page_count + 1} không có video")
                        break
                    
                    # Xử lý từng video trong trang hiện tại
                    for item in response['items']:
                        if len(videos) >= max_results:
                            break
                            
                        video_id = item['id']['videoId']
                        snippet = item['snippet']
                        
                        # Lấy thông tin chi tiết video (bỏ qua nếu lỗi)
                        try:
                            video_details = self._get_video_details(video_id)
                            if video_details:
                                videos.append({
                                    'id': video_id,
                                    'title': snippet['title'],
                                    'description': snippet['description'],
                                    'url': f"https://www.youtube.com/watch?v={video_id}",
                                    'thumbnail': snippet['thumbnails']['high']['url'],
                                    'published_at': snippet['publishedAt'],
                                    'duration': video_details.get('duration', 0),
                                    'view_count': video_details.get('view_count', 0),
                                    'like_count': video_details.get('like_count', 0),
                                    'comment_count': video_details.get('comment_count', 0)
                                })
                        except Exception as e:
                            Logger.log_warning(f"Bỏ qua video {video_id}: {e}")
                            continue
                    
                    # Kiểm tra có trang tiếp theo không
                    next_page_token = response.get('nextPageToken')
                    if not next_page_token:
                        Logger.log_info("Không còn trang tiếp theo")
                        break
                        
                    page_count += 1
                    Logger.log_info(f"Đã lấy trang {page_count}, tổng cộng {len(videos)} video...")
                    
                    # Thêm delay để tránh rate limit
                    import time
                    time.sleep(0.5)
                    
                except HttpError as e:
                    if e.resp.status == 403:
                        Logger.log_error("YouTube API quota đã hết hoặc bị từ chối")
                        break
                    elif e.resp.status == 404:
                        Logger.log_error("Channel không tồn tại")
                        break
                    else:
                        Logger.log_error(f"Lỗi HTTP {e.resp.status}: {e}")
                        break
                except Exception as e:
                    Logger.log_error(f"Lỗi không xác định: {e}")
                    break
            
            return videos
            
        except Exception as e:
            Logger.log_error(f"Lỗi Search API: {e}")
            return []
    
    def _parse_iso8601_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration string to seconds"""
        import re
        # Example: PT1H2M3S
        total_seconds = 0
        if 'H' in duration_str:
            hours = int(re.search(r'(\d+)H', duration_str).group(1))
            total_seconds += hours * 3600
        if 'M' in duration_str:
            minutes = int(re.search(r'(\d+)M', duration_str).group(1))
            total_seconds += minutes * 60
        if 'S' in duration_str:
            seconds = int(re.search(r'(\d+)S', duration_str).group(1))
            total_seconds += seconds
        return total_seconds
    
    def _get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin chi tiết video"""
        try:
            request = self.service.videos().list(
                part='contentDetails,statistics',
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                return None
            
            video = response['items'][0]
            content_details = video['contentDetails']
            statistics = video['statistics']
            
            # Chuyển đổi duration từ ISO 8601 sang giây
            duration = self._parse_duration(content_details['duration'])
            
            return {
                'duration': duration,
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0))
            }
            
        except Exception as e:
            Logger.log_error(f"Lỗi lấy thông tin video {video_id}: {e}")
            return None
    
    def _extract_channel_id(self, channel_url: str) -> Optional[str]:
        """Trích xuất channel ID từ URL"""
        try:
            # Xử lý các format URL khác nhau
            if '/channel/' in channel_url:
                return channel_url.split('/channel/')[-1].split('/')[0].split('?')[0]
            elif '/c/' in channel_url:
                # Lấy custom URL và tìm channel ID
                custom_url = channel_url.split('/c/')[-1].split('/')[0].split('?')[0]
                return self._get_channel_id_by_custom_url(custom_url)
            elif '/@' in channel_url:
                # Lấy handle và tìm channel ID
                handle = channel_url.split('/@')[-1].split('/')[0].split('?')[0]
                return self._get_channel_id_by_handle(handle)
            else:
                Logger.log_error(f"URL format không được hỗ trợ: {channel_url}")
                return None
                
        except Exception as e:
            Logger.log_error(f"Lỗi trích xuất channel ID: {e}")
            return None
    
    def _get_channel_id_by_custom_url(self, custom_url: str) -> Optional[str]:
        """Lấy channel ID từ custom URL"""
        try:
            request = self.service.channels().list(
                part='id',
                forUsername=custom_url
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]['id']
            return None
            
        except Exception as e:
            Logger.log_error(f"Lỗi lấy channel ID từ custom URL {custom_url}: {e}")
            return None
    
    def _get_channel_id_by_handle(self, handle: str) -> Optional[str]:
        """Lấy channel ID từ handle (@username)"""
        try:
            # Thử tìm kiếm channel theo handle
            request = self.service.search().list(
                part='snippet',
                q=handle,
                type='channel',
                maxResults=1
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]['id']['channelId']
            return None
            
        except Exception as e:
            Logger.log_error(f"Lỗi lấy channel ID từ handle {handle}: {e}")
            return None
    
    def _parse_duration(self, duration: str) -> int:
        """Chuyển đổi duration từ ISO 8601 sang giây"""
        try:
            # Loại bỏ 'PT' prefix
            duration = duration[2:]
            total_seconds = 0
            
            # Xử lý hours
            if 'H' in duration:
                hours = int(duration.split('H')[0].split('T')[-1])
                total_seconds += hours * 3600
                duration = duration.split('H')[1]
            
            # Xử lý minutes
            if 'M' in duration:
                minutes = int(duration.split('M')[0])
                total_seconds += minutes * 60
                duration = duration.split('M')[1]
            
            # Xử lý seconds
            if 'S' in duration:
                seconds = int(duration.split('S')[0])
                total_seconds += seconds
            
            return total_seconds
            
        except Exception as e:
            Logger.log_error(f"Lỗi parse duration {duration}: {e}")
            return 0
    
    def test_api_connection(self) -> bool:
        """Test kết nối API"""
        try:
            if not self.is_available():
                return False
            
            # Test với một request đơn giản
            request = self.service.channels().list(
                part='snippet',
                forUsername='youtube'  # Channel YouTube chính thức
            )
            response = request.execute()
            
            return len(response['items']) > 0
            
        except Exception as e:
            Logger.log_error(f"Lỗi test API connection: {e}")
            return False
