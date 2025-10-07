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
        
        # Tạo thư mục output
        FileManager.ensure_dir(self.output_path)
        
        # Cấu hình yt-dlp
        self.ydl_opts = self._get_ydl_opts()
    
    def _get_ydl_opts(self) -> Dict[str, Any]:
        """Cấu hình yt-dlp"""
        return {
            'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
            'format': self._get_format_selector(),
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': True,
            'no_warnings': False,
            'extractaudio': False,
            'audioformat': 'mp3',
            'embed_subs': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'postprocessors': [],
            'logger': self._get_logger()
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
    
    def download_video(self, url: str, custom_filename: str = None) -> Optional[str]:
        """Tải video"""
        try:
            if not self.is_supported_url(url):
                Logger.log_error(f"URL không được hỗ trợ: {url}")
                return None
            
            # Cấu hình output template
            opts = self.ydl_opts.copy()
            if custom_filename:
                filename = FileManager.clean_filename(custom_filename)
                opts['outtmpl'] = os.path.join(self.output_path, f"{filename}.%(ext)s")
            
            Logger.log_info(f"Bắt đầu tải video: {url}")
            
            with yt_dlp.YoutubeDL(opts) as ydl:
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
