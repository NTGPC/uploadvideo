"""
Module tải video từ các nền tảng
"""
import os
import subprocess
import json
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import yt_dlp
from .utils import ConfigManager, FileManager, Logger

class VideoDownloader:
    """Tải video từ các nền tảng"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.supported_platforms = self.config.get('download.supported_platforms', [])
        self.output_path = self.config.get('download.output_path', 'data/videos')
        self.resolution = self.config.get('download.resolution', '1080p')
        
        # Cấu hình proxy và cookies
        self.proxy = self.config.get('download.proxy', None)
        self.cookies_file = self.config.get('download.cookies_file', None)
        
        # Tạo thư mục output
        FileManager.ensure_dir(self.output_path)
        
        # Cấu hình yt-dlp
        self.ydl_opts = self._get_ydl_opts()

    def reload_settings(self):
        """Đồng bộ lại cấu hình từ ConfigManager.

        Gọi hàm này sau khi người dùng thay đổi cài đặt để đảm bảo
        `output_path`, `resolution` và tùy chọn yt-dlp được cập nhật.
        """
        self.supported_platforms = self.config.get('download.supported_platforms', [])
        self.output_path = self.config.get('download.output_path', 'data/videos')
        self.resolution = self.config.get('download.resolution', '1080p')
        
        # Cập nhật proxy và cookies
        self.proxy = self.config.get('download.proxy', None)
        self.cookies_file = self.config.get('download.cookies_file', None)
        
        # Đảm bảo thư mục tồn tại khi người dùng đổi đường dẫn
        FileManager.ensure_dir(self.output_path)
        # Cập nhật cấu hình yt-dlp với đường dẫn mới
        self.ydl_opts = self._get_ydl_opts()
    
    def _get_ydl_opts(self) -> Dict[str, Any]:
        """Cấu hình yt-dlp"""
        return {
            'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
            # Ưu tiên video + audio, fallback mp4 tốt nhất
            'format': f"bv*+ba/best[ext=mp4]/{self._get_format_selector()}",
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': True,
            'no_warnings': False,
            'extractaudio': False,
            'audioformat': 'mp3',
            'embed_subs': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'postprocessors': [
                { 'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4' }
            ],
            'logger': self._get_logger(),
            # Cải thiện xử lý lỗi kết nối và socket
            'socket_timeout': 60,
            'retries': 5,
            'fragment_retries': 5,
            'retry_sleep_functions': {'http': lambda n: min(2 ** n, 30)},
            'http_chunk_size': 1048576,  # 1MB chunks
            'concurrent_fragment_downloads': 1,  # Giảm số kết nối đồng thời
            # Thêm cấu hình để fix lỗi socket
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            # Cấu hình cho TikTok
            'extractor_args': {
                'tiktok': {
                    'webpage_url_basename': 'tiktok',
                    'api_hostname': 'api.tiktokv.com',
                    'api_url': 'https://api.tiktokv.com/aweme/v1/',
                }
            },
            # Thêm cấu hình proxy và cookies
            'proxy': self.proxy,  # Cấu hình proxy nếu có
            'cookies': self.cookies_file,  # Cấu hình cookies nếu có
            # Cải thiện xử lý lỗi
            'ignoreerrors': True,
            'no_warnings': False,
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'writedescription': False,
            'writeannotations': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'writedescription': False,
            'writeannotations': False,
        }
    
    def _get_format_selector(self) -> str:
        """Chọn format video dựa trên resolution"""
        format_map = {
            '1080p': 'best[height<=1080]/best',
            '720p': 'best[height<=720]/best',
            '480p': 'best[height<=480]/best',
            '360p': 'best[height<=360]/best'
        }
        return format_map.get(self.resolution, 'best')
    
    def _get_logger(self):
        """Logger cho yt-dlp"""
        class YDLLogger:
            def debug(self, msg):
                Logger.log_info(f"yt-dlp DEBUG: {msg}")
            
            def warning(self, msg):
                Logger.log_warning(f"yt-dlp WARNING: {msg}")
            
            def error(self, msg):
                Logger.log_error(f"yt-dlp ERROR: {msg}")
        
        return YDLLogger()
    
    def _get_fallback_opts(self, base_opts: Dict[str, Any]) -> Dict[str, Any]:
        """Cấu hình fallback khi gặp lỗi socket"""
        fallback_opts = base_opts.copy()
        
        # Giảm timeout và retry
        fallback_opts.update({
            'socket_timeout': 30,
            'retries': 2,
            'fragment_retries': 2,
            'http_chunk_size': 512 * 1024,  # 512KB chunks
            'concurrent_fragment_downloads': 1,
            # Thêm cấu hình cho TikTok
            'extractor_args': {
                'tiktok': {
                    'webpage_url_basename': 'tiktok',
                    'api_hostname': 'api.tiktokv.com',
                    'api_url': 'https://api.tiktokv.com/aweme/v1/',
                    'skip_download': False,
                }
            },
            # Cấu hình HTTP khác
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
            }
        })
        
        return fallback_opts
    
    def _get_alternative_headers_opts(self, base_opts: Dict[str, Any]) -> Dict[str, Any]:
        """Cấu hình với User-Agent khác khi gặp lỗi HTTP"""
        alt_opts = base_opts.copy()
        
        # User-Agent khác nhau
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/109.0 Firefox/109.0'
        ]
        
        import random
        selected_ua = random.choice(user_agents)
        
        alt_opts['http_headers'] = {
            'User-Agent': selected_ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        return alt_opts
    
    def _check_channel_exists(self, url: str) -> bool:
        """Kiểm tra channel có tồn tại không"""
        try:
            # Thử lấy thông tin cơ bản trước
            opts = {
                'quiet': True,
                'extract_flat': True,
                'playlistend': 1,  # Chỉ lấy 1 video để test
                'logger': self._get_logger(),
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info is not None and 'entries' in info
                
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "Not Found" in error_msg:
                return False
            return True  # Nếu lỗi khác, giả sử channel tồn tại
    
    def _handle_socket_error(self, error_msg: str) -> bool:
        """Xử lý lỗi socket và trả về True nếu có thể retry"""
        if "WinError 10013" in error_msg:
            Logger.log_warning("Phát hiện lỗi WinError 10013 - Socket access permissions")
            Logger.log_info("Thử các giải pháp sau:")
            Logger.log_info("1. Chạy ứng dụng với quyền Administrator")
            Logger.log_info("2. Kiểm tra firewall và antivirus")
            Logger.log_info("3. Thử sử dụng proxy")
            return True
        elif "socket" in error_msg.lower():
            Logger.log_warning("Phát hiện lỗi socket chung")
            return True
        return False
    
    def _handle_http_error(self, error_msg: str) -> bool:
        """Xử lý lỗi HTTP và trả về True nếu có thể retry"""
        if "HTTP Error 403" in error_msg:
            Logger.log_warning("Phát hiện lỗi HTTP 403 - Forbidden")
            Logger.log_info("Thử thay đổi User-Agent hoặc sử dụng cookies")
            return True
        elif "HTTP Error 429" in error_msg:
            Logger.log_warning("Phát hiện lỗi HTTP 429 - Too Many Requests")
            Logger.log_info("Thử giảm tốc độ tải hoặc sử dụng proxy")
            return True
        elif "HTTP Error 404" in error_msg:
            Logger.log_warning("Phát hiện lỗi HTTP 404 - Not Found")
            Logger.log_info("Channel hoặc video không tồn tại, thử các URL format khác")
            return True
        return False
    
    def is_supported_url(self, url: str) -> bool:
        """Kiểm tra URL có được hỗ trợ không"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Kiểm tra các domain được hỗ trợ
            supported_domains = {
                'tiktok.com': 'tiktok',
                'youtube.com': 'youtube',
                'youtu.be': 'youtube',
                'facebook.com': 'facebook',
                'instagram.com': 'instagram',
                'twitter.com': 'twitter',
                'x.com': 'twitter'
            }
            
            for supported_domain, platform in supported_domains.items():
                if supported_domain in domain and platform in self.supported_platforms:
                    return True
            
            return False
            
        except Exception as e:
            Logger.log_error(f"Lỗi kiểm tra URL: {e}")
            return False
    
    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin video"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'url': url,
                    'platform': self._detect_platform(url)
                }
                
        except Exception as e:
            Logger.log_error(f"Lỗi lấy thông tin video: {e}")
            return None
    
    def _detect_platform(self, url: str) -> str:
        """Phát hiện nền tảng từ URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if 'tiktok.com' in domain:
                return 'tiktok'
            elif 'youtube.com' in domain or 'youtu.be' in domain:
                return 'youtube'
            elif 'facebook.com' in domain:
                return 'facebook'
            elif 'instagram.com' in domain:
                return 'instagram'
            elif 'twitter.com' in domain or 'x.com' in domain:
                return 'twitter'
            else:
                return 'unknown'
        except:
            return 'unknown'
    
    def download_video(self, url: str, custom_filename: str = None, progress_hook=None) -> Optional[str]:
        """Tải video"""
        try:
            # Đảm bảo cấu hình mới nhất trước khi tải
            self.reload_settings()
            if not self.is_supported_url(url):
                Logger.log_error(f"URL không được hỗ trợ: {url}")
                return None
            
            # Cấu hình output template
            opts = self.ydl_opts.copy()
            if custom_filename:
                filename = FileManager.clean_filename(custom_filename)
                opts['outtmpl'] = os.path.join(self.output_path, f"{filename}.%(ext)s")
            # Thêm progress hook nếu có
            if progress_hook is not None:
                opts['progress_hooks'] = [progress_hook]
            
            Logger.log_info(f"Bắt đầu tải video: {url}")
            
            # Thử tải với retry mechanism
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        # Kiểm tra trước xem có phải nội dung video không
                        pre_info = ydl.extract_info(url, download=False)
                        if pre_info is None:
                            Logger.log_error("Không lấy được thông tin video")
                            if attempt < max_attempts - 1:
                                Logger.log_info(f"Thử lại lần {attempt + 2}...")
                                continue
                            return None
                        
                        # Phát hiện nội dung không phải video (ảnh/slideshow)
                        ext = (pre_info.get('ext') or '').lower()
                        vcodec = (pre_info.get('vcodec') or '').lower()
                        duration = pre_info.get('duration') or 0
                        if ext in ('jpg', 'jpeg', 'png', 'webp') or vcodec == 'none' or duration == 0:
                            Logger.log_error("Nội dung không phải video (có thể là bài ảnh của TikTok)")
                            return None
                        
                        # Tiến hành tải
                        info = ydl.extract_info(url, download=True)
                        
                        if info:
                            # Tìm file đã tải
                            filename = ydl.prepare_filename(info)
                            if os.path.exists(filename):
                                Logger.log_info(f"Tải video thành công: {filename}")
                                return filename
                            else:
                                # Tìm file với extension thực tế
                                base_name = os.path.splitext(filename)[0]
                                for ext in ['.mp4', '.webm', '.mkv', '.avi']:
                                    test_file = base_name + ext
                                    if os.path.exists(test_file):
                                        Logger.log_info(f"Tải video thành công: {test_file}")
                                        return test_file
                        
                        Logger.log_error("Không tìm thấy file video đã tải")
                        if attempt < max_attempts - 1:
                            Logger.log_info(f"Thử lại lần {attempt + 2}...")
                            continue
                        return None
                        
                except Exception as e:
                    error_msg = str(e)
                    Logger.log_error(f"Lỗi tải video (lần {attempt + 1}): {error_msg}")
                    
                    # Xử lý các lỗi cụ thể
                    if self._handle_socket_error(error_msg):
                        Logger.log_warning("Phát hiện lỗi socket, thử cấu hình khác...")
                        # Thử với cấu hình khác
                        opts = self._get_fallback_opts(opts)
                        if attempt < max_attempts - 1:
                            Logger.log_info(f"Thử lại với cấu hình fallback lần {attempt + 2}...")
                            continue
                    elif self._handle_http_error(error_msg):
                        Logger.log_warning("Phát hiện lỗi HTTP, thử với User-Agent khác...")
                        # Thử với User-Agent khác
                        opts = self._get_alternative_headers_opts(opts)
                        if attempt < max_attempts - 1:
                            Logger.log_info(f"Thử lại với User-Agent khác lần {attempt + 2}...")
                            continue
                    
                    if attempt < max_attempts - 1:
                        Logger.log_info(f"Thử lại lần {attempt + 2}...")
                        continue
                    return None
                
        except Exception as e:
            Logger.log_error(f"Lỗi tải video: {e}")
            return None
    
    def download_playlist(self, url: str, max_videos: int = 10) -> List[str]:
        """Tải playlist"""
        try:
            Logger.log_info(f"Bắt đầu tải playlist: {url}")
            
            downloaded_files = []
            opts = self.ydl_opts.copy()
            opts['playlistend'] = max_videos
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry:
                            filename = ydl.prepare_filename(entry)
                            if os.path.exists(filename):
                                downloaded_files.append(filename)
                            else:
                                # Tìm file với extension thực tế
                                base_name = os.path.splitext(filename)[0]
                                for ext in ['.mp4', '.webm', '.mkv', '.avi']:
                                    test_file = base_name + ext
                                    if os.path.exists(test_file):
                                        downloaded_files.append(test_file)
                                        break
            
            Logger.log_info(f"Tải playlist hoàn thành: {len(downloaded_files)} video")
            return downloaded_files
            
        except Exception as e:
            Logger.log_error(f"Lỗi tải playlist: {e}")
            return []
    
    def get_available_formats(self, url: str) -> List[Dict[str, Any]]:
        """Lấy danh sách format có sẵn"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                formats = []
                if 'formats' in info:
                    for fmt in info['formats']:
                        if fmt.get('vcodec') != 'none':  # Chỉ video formats
                            formats.append({
                                'format_id': fmt.get('format_id'),
                                'ext': fmt.get('ext'),
                                'resolution': fmt.get('resolution'),
                                'fps': fmt.get('fps'),
                                'filesize': fmt.get('filesize'),
                                'quality': fmt.get('quality')
                            })
                
                return formats
                
        except Exception as e:
            Logger.log_error(f"Lỗi lấy format: {e}")
            return []
    
    def download_with_format(self, url: str, format_id: str) -> Optional[str]:
        """Tải video với format cụ thể"""
        try:
            opts = self.ydl_opts.copy()
            opts['format'] = format_id
            
            Logger.log_info(f"Tải video với format {format_id}: {url}")
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if info:
                    filename = ydl.prepare_filename(info)
                    if os.path.exists(filename):
                        return filename
                    else:
                        # Tìm file với extension thực tế
                        base_name = os.path.splitext(filename)[0]
                        for ext in ['.mp4', '.webm', '.mkv', '.avi']:
                            test_file = base_name + ext
                            if os.path.exists(test_file):
                                return test_file
                
                return None
                
        except Exception as e:
            Logger.log_error(f"Lỗi tải video với format: {e}")
            return None

    def list_channel_videos(self, url: str, max_videos: int = 50) -> List[Dict[str, Any]]:
        """Lấy danh sách video public do chủ kênh đăng (không lấy liked/favorites).

        Trả về danh sách dict: { 'title', 'url', 'id', 'duration' }.
        """
        try:
            # Chuẩn hóa URL trước khi xử lý
            url = self._normalize_url(url)
            if not url:
                Logger.log_error("URL không hợp lệ")
                return []
            
            # Xử lý TikTok đặc biệt
            if 'tiktok.com' in url and '@' in url:
                return self._get_tiktok_videos_direct(url, max_videos)
            
            # Kiểm tra channel có tồn tại không
            Logger.log_info(f"Kiểm tra channel: {url}")
            if not self._check_channel_exists(url):
                Logger.log_warning("Channel không tồn tại hoặc không thể truy cập")
                Logger.log_info("Thử các URL format khác...")
                return self._try_fallback_urls(url, max_videos)
            
            # extract_flat để không tải dữ liệu, chỉ lấy danh sách entries
            opts = {
                'quiet': True,
                'extract_flat': True,
                'playlistend': max_videos,
                'logger': self._get_logger(),
                # Giới hạn ngay từ phía yt-dlp, tránh phân trang vô hạn
                'playlist_items': f'1:{max_videos}',
                # Cải thiện xử lý YouTube
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash', 'hls'],
                        'player_skip': ['configs'],
                        'comment_sort': ['top'],
                        'max_comments': [0]
                    }
                }
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                entries = []
                if info is None:
                    return entries
                
                # Xử lý các loại info khác nhau
                if 'entries' in info and isinstance(info['entries'], list):
                    iterable = info['entries']
                elif isinstance(info, dict) and 'entries' in info:
                    iterable = info['entries'] if isinstance(info['entries'], list) else []
                else:
                    iterable = []
                
                for entry in iterable:
                    if not entry:
                        continue
                    
                    video_url = entry.get('url') or entry.get('webpage_url')
                    title = entry.get('title') or ''
                    duration = entry.get('duration') or 0
                    video_id = entry.get('id') or ''
                    
                    # Lọc video hợp lệ
                    is_valid_video = False
                    if video_url and duration > 0:
                        # TikTok: có '/video/' trong URL
                        if '/video/' in video_url:
                            is_valid_video = True
                        # YouTube: có 'watch?v=' hoặc 'shorts/'
                        elif 'watch?v=' in video_url or '/shorts/' in video_url:
                            is_valid_video = True
                        # Facebook: có '/videos/' hoặc '/watch/'
                        elif '/videos/' in video_url or '/watch/' in video_url:
                            is_valid_video = True
                        # Instagram: có '/reel/' hoặc '/p/'
                        elif '/reel/' in video_url or '/p/' in video_url:
                            is_valid_video = True
                        # Kiểm tra extractor key
                        elif 'video' in (entry.get('ie_key') or '').lower():
                            is_valid_video = True
                    
                    if is_valid_video:
                        entries.append({
                            'title': title,
                            'url': video_url,
                            'id': video_id,
                            'duration': duration
                        })
                
                Logger.log_info(f"Đã lấy {len(entries)} video từ {url}")
                return entries
        except Exception as e:
            Logger.log_error(f"Lỗi lấy danh sách video kênh: {e}")
            # Thử fallback URLs nếu URL gốc lỗi
            return self._try_fallback_urls(url, max_videos)
    
    def _get_tiktok_videos_direct(self, url: str, max_videos: int) -> List[Dict[str, Any]]:
        """Lấy video TikTok sử dụng phương pháp tìm kiếm"""
        try:
            # Trích xuất username từ URL
            username = url.split('@')[-1].split('/')[0]
            Logger.log_info(f"Lấy video TikTok cho @{username}")
            
            # Thử nhiều phương pháp khác nhau
            methods = [
                self._try_tiktok_search_method,
                self._try_tiktok_hashtag_method,
                self._try_tiktok_user_method
            ]
            
            for method in methods:
                try:
                    videos = method(username, max_videos)
                    if videos:
                        Logger.log_info(f"Thành công với phương pháp {method.__name__}: {len(videos)} video")
                        return videos
                except Exception as e:
                    Logger.log_warning(f"Phương pháp {method.__name__} thất bại: {e}")
                    continue
            
            Logger.log_warning("Tất cả phương pháp đều thất bại")
            return []
                
        except Exception as e:
            Logger.log_error(f"Lỗi lấy video TikTok: {e}")
            return []
    
    def _try_tiktok_search_method(self, username: str, max_videos: int) -> List[Dict[str, Any]]:
        """Thử tìm video bằng tìm kiếm"""
        try:
            import requests
            import json
            import re
            
            # Tìm kiếm video của user
            search_url = f"https://www.tiktok.com/search?q=@{username}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(search_url, headers=headers, timeout=30)
            if response.status_code != 200:
                return []
            
            html = response.text
            
            # Tìm video URLs trong HTML
            video_pattern = r'https://www\.tiktok\.com/@[^/]+/video/\d+'
            video_urls = re.findall(video_pattern, html)
            
            # Lấy thông tin video
            videos = []
            for video_url in video_urls[:max_videos]:
                try:
                    info = self.get_video_info(video_url)
                    if info:
                        videos.append({
                            'title': info.get('title', 'No title'),
                            'url': video_url,
                            'id': video_url.split('/')[-1],
                            'duration': info.get('duration', 0)
                        })
                except:
                    continue
            
            return videos
            
        except Exception as e:
            Logger.log_error(f"Lỗi tìm kiếm TikTok: {e}")
            return []
    
    def _try_tiktok_hashtag_method(self, username: str, max_videos: int) -> List[Dict[str, Any]]:
        """Thử tìm video bằng hashtag"""
        try:
            # Tạo hashtag từ username
            hashtag = f"@{username}"
            
            # Sử dụng yt-dlp để tìm kiếm hashtag
            search_url = f"https://www.tiktok.com/tag/{hashtag}"
            
            opts = {
                'quiet': True,
                'extract_flat': True,
                'playlistend': max_videos,
                'logger': self._get_logger(),
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(search_url, download=False)
                
                if not info or 'entries' not in info:
                    return []
                
                videos = []
                for entry in info['entries'][:max_videos]:
                    if not entry:
                        continue
                    
                    video_url = entry.get('url') or entry.get('webpage_url')
                    if video_url and '/video/' in video_url:
                        videos.append({
                            'title': entry.get('title', 'No title'),
                            'url': video_url,
                            'id': entry.get('id', ''),
                            'duration': entry.get('duration', 0)
                        })
                
                return videos
                
        except Exception as e:
            Logger.log_error(f"Lỗi hashtag method: {e}")
            return []
    
    def _try_tiktok_user_method(self, username: str, max_videos: int) -> List[Dict[str, Any]]:
        """Thử lấy video trực tiếp từ user profile"""
        try:
            # Thử với URL profile khác nhau
            profile_urls = [
                f"https://www.tiktok.com/@{username}",
                f"https://www.tiktok.com/@{username}/video",
                f"https://www.tiktok.com/@{username}/videos"
            ]
            
            for profile_url in profile_urls:
                try:
                    opts = {
                        'quiet': True,
                        'extract_flat': True,
                        'playlistend': max_videos,
                        'logger': self._get_logger(),
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
                        }
                    }
                    
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(profile_url, download=False)
                        
                        if info and 'entries' in info and info['entries']:
                            videos = []
                            for entry in info['entries'][:max_videos]:
                                if not entry:
                                    continue
                                
                                video_url = entry.get('url') or entry.get('webpage_url')
                                if video_url and '/video/' in video_url:
                                    videos.append({
                                        'title': entry.get('title', 'No title'),
                                        'url': video_url,
                                        'id': entry.get('id', ''),
                                        'duration': entry.get('duration', 0)
                                    })
                            
                            if videos:
                                return videos
                                
                except Exception as e:
                    Logger.log_warning(f"URL {profile_url} thất bại: {e}")
                    continue
            
            return []
            
        except Exception as e:
            Logger.log_error(f"Lỗi user method: {e}")
            return []
    
    def _normalize_url(self, url: str) -> str:
        """Chuẩn hóa URL để tương thích với yt-dlp"""
        try:
            if not url:
                return ""
            
            url = url.strip()
            
            # Xử lý YouTube URLs
            if 'youtube.com' in url or 'youtu.be' in url:
                # Xử lý @username - thử nhiều format khác nhau
                if '/@' in url and '/videos' not in url and '/playlists' not in url and '/shorts' not in url:
                    username = url.split('/@')[-1].split('/')[0].split('?')[0]
                    # Thử các format khác nhau của YouTube
                    possible_urls = [
                        f"https://www.youtube.com/@{username}/videos",
                        f"https://www.youtube.com/c/{username}/videos", 
                        f"https://www.youtube.com/user/{username}/videos",
                        f"https://www.youtube.com/channel/{username}/videos"
                    ]
                    # Trả về URL đầu tiên, sẽ thử fallback sau
                    return possible_urls[0]
                # Chuyển youtu.be thành youtube.com
                elif 'youtu.be' in url:
                    video_id = url.split('/')[-1].split('?')[0]
                    url = f"https://www.youtube.com/watch?v={video_id}"
                return url
            
            # Xử lý TikTok URLs
            elif 'tiktok.com' in url:
                if '/@' in url and '/video' not in url:
                    # Chuyển profile thành videos tab
                    if not url.endswith('/video'):
                        url = url.rstrip('/') + '/video'
                return url
            
            # Xử lý Facebook URLs
            elif 'facebook.com' in url:
                if '/videos' not in url and '/watch' not in url:
                    if '/profile.php' in url:
                        url = url + '/videos'
                    elif '/pages/' in url:
                        url = url.rstrip('/') + '/videos'
                return url
            
            # Xử lý Instagram URLs
            elif 'instagram.com' in url:
                if '/reel' not in url and '/p/' not in url and '/tv/' not in url:
                    if '/reels/' not in url:
                        url = url.rstrip('/') + '/reels/'
                return url
            
            return url
            
        except Exception as e:
            Logger.log_error(f"Lỗi chuẩn hóa URL: {e}")
            return url
    
    def _try_fallback_urls(self, original_url: str, max_videos: int) -> List[Dict[str, Any]]:
        """Thử các URL fallback khác nhau nếu URL gốc lỗi"""
        try:
            fallback_urls = []
            
            # Tạo các URL fallback dựa trên URL gốc
            if 'youtube.com' in original_url or 'youtu.be' in original_url:
                # Thử các format khác nhau của YouTube
                if '/@' in original_url:
                    username = original_url.split('/@')[-1].split('/')[0].split('?')[0]
                    # Thử nhiều format khác nhau
                    fallback_urls = [
                        f"https://www.youtube.com/@{username}/videos",
                        f"https://www.youtube.com/@{username}/shorts", 
                        f"https://www.youtube.com/c/{username}/videos",
                        f"https://www.youtube.com/user/{username}/videos",
                        f"https://www.youtube.com/channel/{username}/videos",
                        # Thử tìm kiếm channel
                        f"https://www.youtube.com/results?search_query={username}&sp=EgIQAg%253D%253D"
                    ]
                elif '/channel/' in original_url:
                    channel_id = original_url.split('/channel/')[-1].split('/')[0]
                    fallback_urls = [
                        f"https://www.youtube.com/channel/{channel_id}/videos",
                        f"https://www.youtube.com/channel/{channel_id}/shorts"
                    ]
                elif '/c/' in original_url:
                    channel_name = original_url.split('/c/')[-1].split('/')[0]
                    fallback_urls = [
                        f"https://www.youtube.com/c/{channel_name}/videos",
                        f"https://www.youtube.com/@{channel_name}/videos",
                        f"https://www.youtube.com/user/{channel_name}/videos"
                    ]
            
            elif 'tiktok.com' in original_url:
                if '/@' in original_url:
                    username = original_url.split('/@')[-1].split('/')[0]
                    fallback_urls = [
                        f"https://www.tiktok.com/@{username}",
                        f"https://www.tiktok.com/@{username}/video"
                    ]
            
            # Thử từng fallback URL
            for i, fallback_url in enumerate(fallback_urls, 1):
                try:
                    Logger.log_info(f"Thử fallback URL {i}/{len(fallback_urls)}: {fallback_url}")
                    # Gọi trực tiếp logic xử lý để tránh vòng lặp
                    result = self._extract_videos_from_url(fallback_url, max_videos)
                    if result:
                        Logger.log_info(f"✅ Thành công với fallback URL: {fallback_url}")
                        return result
                    else:
                        Logger.log_warning(f"❌ Fallback URL không trả về video: {fallback_url}")
                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg or "Not Found" in error_msg:
                        Logger.log_warning(f"❌ Channel không tồn tại: {fallback_url}")
                    else:
                        Logger.log_warning(f"❌ Fallback URL thất bại {fallback_url}: {e}")
                    continue
            
            Logger.log_error("❌ Tất cả fallback URLs đều thất bại")
            Logger.log_error("💡 Có thể channel không tồn tại hoặc đã bị xóa")
            Logger.log_error("💡 Thử kiểm tra URL trên trình duyệt trước")
            return []
            
        except Exception as e:
            Logger.log_error(f"Lỗi thử fallback URLs: {e}")
            return []
    
    def _extract_videos_from_url(self, url: str, max_videos: int) -> List[Dict[str, Any]]:
        """Trích xuất video từ URL mà không gọi lại list_channel_videos"""
        try:
            url = self._normalize_url(url)
            if not url:
                return []
            
            opts = {
                'quiet': True,
                'extract_flat': True,
                'playlistend': max_videos,
                'logger': self._get_logger(),
                'playlist_items': f'1:{max_videos}',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash', 'hls'],
                        'player_skip': ['configs'],
                        'comment_sort': ['top'],
                        'max_comments': [0]
                    },
                    'tiktok': {
                        'api_hostname': 'api.tiktokv.com'
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                entries = []
                if info is None:
                    return entries
                
                if 'entries' in info and isinstance(info['entries'], list):
                    iterable = info['entries']
                elif isinstance(info, dict) and 'entries' in info:
                    iterable = info['entries'] if isinstance(info['entries'], list) else []
                else:
                    iterable = []
                
                for entry in iterable:
                    if not entry:
                        continue
                    
                    video_url = entry.get('url') or entry.get('webpage_url')
                    title = entry.get('title') or ''
                    duration = entry.get('duration') or 0
                    video_id = entry.get('id') or ''
                    
                    is_valid_video = False
                    if video_url and duration > 0:
                        if '/video/' in video_url or 'watch?v=' in video_url or '/shorts/' in video_url or '/videos/' in video_url or '/watch/' in video_url or '/reel/' in video_url or '/p/' in video_url or 'video' in (entry.get('ie_key') or '').lower():
                            is_valid_video = True
                    
                    if is_valid_video:
                        entries.append({
                            'title': title,
                            'url': video_url,
                            'id': video_id,
                            'duration': duration
                        })
                
                return entries
                
        except Exception as e:
            Logger.log_error(f"Lỗi trích xuất video từ URL: {e}")
            return []
    
    def test_download_capabilities(self, test_url: str = None) -> Dict[str, Any]:
        """Test khả năng tải video và trả về báo cáo chi tiết"""
        test_results = {
            'success': False,
            'error_type': None,
            'error_message': None,
            'suggestions': [],
            'config_used': None
        }
        
        try:
            # Sử dụng URL test mặc định nếu không có
            if not test_url:
                test_url = "https://www.tiktok.com/@test/video/1234567890"
            
            Logger.log_info(f"Bắt đầu test khả năng tải video với URL: {test_url}")
            
            # Test 1: Kiểm tra URL có được hỗ trợ không
            if not self.is_supported_url(test_url):
                test_results['error_type'] = 'unsupported_url'
                test_results['error_message'] = 'URL không được hỗ trợ'
                test_results['suggestions'].append('Kiểm tra URL có đúng format không')
                return test_results
            
            # Test 2: Thử lấy thông tin video
            try:
                info = self.get_video_info(test_url)
                if info:
                    test_results['success'] = True
                    test_results['config_used'] = 'standard'
                    Logger.log_info("Test thành công - có thể lấy thông tin video")
                else:
                    test_results['error_type'] = 'info_extraction_failed'
                    test_results['error_message'] = 'Không thể lấy thông tin video'
                    test_results['suggestions'].extend([
                        'Kiểm tra kết nối internet',
                        'Thử sử dụng proxy',
                        'Kiểm tra URL có còn hoạt động không'
                    ])
            except Exception as e:
                error_msg = str(e)
                test_results['error_message'] = error_msg
                
                if "WinError 10013" in error_msg:
                    test_results['error_type'] = 'socket_permission_error'
                    test_results['suggestions'].extend([
                        'Chạy ứng dụng với quyền Administrator',
                        'Kiểm tra firewall và antivirus',
                        'Thử sử dụng proxy',
                        'Khởi động lại ứng dụng'
                    ])
                elif "HTTP Error 403" in error_msg:
                    test_results['error_type'] = 'http_forbidden'
                    test_results['suggestions'].extend([
                        'Thử sử dụng cookies',
                        'Thay đổi User-Agent',
                        'Sử dụng proxy'
                    ])
                elif "HTTP Error 429" in error_msg:
                    test_results['error_type'] = 'rate_limited'
                    test_results['suggestions'].extend([
                        'Chờ một lúc rồi thử lại',
                        'Sử dụng proxy',
                        'Giảm tốc độ tải'
                    ])
                else:
                    test_results['error_type'] = 'unknown_error'
                    test_results['suggestions'].append('Kiểm tra log để biết thêm chi tiết')
            
            return test_results
            
        except Exception as e:
            Logger.log_error(f"Lỗi trong test: {e}")
            test_results['error_type'] = 'test_failed'
            test_results['error_message'] = str(e)
            test_results['suggestions'].append('Kiểm tra cấu hình hệ thống')
            return test_results
