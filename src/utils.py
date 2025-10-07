"""
Utilities cho TikTok Reup Offline
"""
import os
import json
import hashlib
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Quản lý cấu hình ứng dụng"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Tải cấu hình từ file JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
        except json.JSONDecodeError:
            logging.error(f"Lỗi đọc file cấu hình: {self.config_path}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Cấu hình mặc định"""
        return {
            "download": {
                "resolution": "1080p",
                "output_path": "data/videos",
                "max_downloads": 10
            },
            "processing": {
                "output_path": "data/processed",
                "watermark": {
                    "enabled": True,
                    "text": "TikTok Reup Offline"
                }
            }
        }
    
    def get(self, key: str, default=None):
        """Lấy giá trị cấu hình"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Đặt giá trị cấu hình"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def save_config(self):
        """Lưu cấu hình vào file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Lỗi lưu cấu hình: {e}")

class FileManager:
    """Quản lý file và thư mục"""
    
    @staticmethod
    def ensure_dir(path: str):
        """Tạo thư mục nếu chưa tồn tại"""
        Path(path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """Tính hash MD5 của file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logging.error(f"Lỗi tính hash file {file_path}: {e}")
            return ""
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Lấy kích thước file"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """Làm sạch tên file"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()

class FFmpegManager:
    """Quản lý FFmpeg"""
    
    def __init__(self, ffmpeg_path: str = "tools/ffmpeg.exe"):
        self.ffmpeg_path = ffmpeg_path
    
    def is_available(self) -> bool:
        """Kiểm tra FFmpeg có sẵn không"""
        try:
            result = subprocess.run([self.ffmpeg_path, '-version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False
    
    def run_command(self, command: str, timeout: int = 300) -> bool:
        """Chạy lệnh FFmpeg"""
        try:
            # Thay thế ffmpeg path trong command
            if command.startswith('ffmpeg '):
                command = command.replace('ffmpeg ', f'"{self.ffmpeg_path}" ', 1)
            
            logging.info(f"Chạy lệnh FFmpeg: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  text=True, timeout=timeout)
            
            if result.returncode == 0:
                logging.info("FFmpeg chạy thành công")
                return True
            else:
                logging.error(f"FFmpeg lỗi: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logging.error("FFmpeg timeout")
            return False
        except Exception as e:
            logging.error(f"Lỗi chạy FFmpeg: {e}")
            return False
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Lấy thông tin video"""
        try:
            cmd = f'"{self.ffmpeg_path}" -i "{video_path}" -f null -'
            result = subprocess.run(cmd, shell=True, capture_output=True, 
                                  text=True, timeout=30)
            
            # Parse thông tin từ stderr
            info = {
                'duration': 0,
                'width': 0,
                'height': 0,
                'fps': 0
            }
            
            stderr = result.stderr
            if 'Duration:' in stderr:
                # Parse duration
                duration_line = [line for line in stderr.split('\n') if 'Duration:' in line][0]
                duration_str = duration_line.split('Duration:')[1].split(',')[0].strip()
                info['duration'] = self._parse_duration(duration_str)
            
            if 'Video:' in stderr:
                # Parse video info
                video_line = [line for line in stderr.split('\n') if 'Video:' in line][0]
                parts = video_line.split()
                for i, part in enumerate(parts):
                    if 'x' in part and part.replace('x', '').replace('.', '').isdigit():
                        try:
                            width, height = part.split('x')
                            info['width'] = int(width)
                            info['height'] = int(height)
                        except:
                            pass
                    elif 'fps' in part:
                        try:
                            info['fps'] = float(part.replace('fps', ''))
                        except:
                            pass
            
            return info
            
        except Exception as e:
            logging.error(f"Lỗi lấy thông tin video: {e}")
            return {}
    
    def _parse_duration(self, duration_str: str) -> float:
        """Parse duration string thành seconds"""
        try:
            # Format: HH:MM:SS.mmm
            parts = duration_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        except:
            return 0

class Logger:
    """Quản lý logging"""
    
    @staticmethod
    def setup_logging(log_file: str = "logs/app.log"):
        """Thiết lập logging"""
        FileManager.ensure_dir(os.path.dirname(log_file))
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    @staticmethod
    def log_info(message: str):
        """Log thông tin"""
        logging.info(message)
    
    @staticmethod
    def log_error(message: str):
        """Log lỗi"""
        logging.error(message)
    
    @staticmethod
    def log_warning(message: str):
        """Log cảnh báo"""
        logging.warning(message)
