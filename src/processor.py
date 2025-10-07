"""
Module xử lý video (cắt, thêm nhạc, watermark, etc.)
"""
import os
import json
import random
import string
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
from .utils import ConfigManager, FileManager, FFmpegManager, Logger

class VideoProcessor:
    """Xử lý video"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.output_path = self.config.get('processing.output_path', 'data/processed')
        self.ffmpeg = FFmpegManager(self.config.get('ffmpeg.path', 'tools/ffmpeg.exe'))
        
        # Tạo thư mục output
        FileManager.ensure_dir(self.output_path)
        
        # Load templates
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        """Tải templates xử lý"""
        try:
            with open('config/templates.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            Logger.log_error(f"Lỗi tải templates: {e}")
            return {}
    
    def cut_video(self, input_path: str, duration: int, start_time: int = 0) -> Optional[str]:
        """Cắt video theo thời gian"""
        try:
            if not os.path.exists(input_path):
                Logger.log_error(f"File không tồn tại: {input_path}")
                return None
            
            # Tạo tên file output
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{base_name}_cut_{duration}s.mp4"
            output_path = os.path.join(self.output_path, output_filename)
            
            # Lệnh FFmpeg
            command = f'ffmpeg -i "{input_path}" -ss {start_time} -t {duration} -c copy "{output_path}"'
            
            if self.ffmpeg.run_command(command):
                Logger.log_info(f"Cắt video thành công: {output_path}")
                return output_path
            else:
                Logger.log_error("Lỗi cắt video")
                return None
                
        except Exception as e:
            Logger.log_error(f"Lỗi cắt video: {e}")
            return None
    
    def add_watermark(self, input_path: str, text: str = None, 
                     position: str = "bottom-right") -> Optional[str]:
        """Thêm watermark text"""
        try:
            if not os.path.exists(input_path):
                Logger.log_error(f"File không tồn tại: {input_path}")
                return None
            
            # Lấy cấu hình watermark
            watermark_config = self.config.get('processing.watermark', {})
            if not watermark_config.get('enabled', True):
                return input_path
            
            text = text or watermark_config.get('text', 'TikTok Reup Offline')
            font_size = watermark_config.get('size', 24)
            color = watermark_config.get('color', '#FFFFFF')
            
            # Tạo tên file output
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{base_name}_watermark.mp4"
            output_path = os.path.join(self.output_path, output_filename)
            
            # Tạo font path
            font_path = self._get_font_path()
            
            # Lệnh FFmpeg với watermark
            command = f'''ffmpeg -i "{input_path}" -vf "drawtext=text='{text}':fontfile='{font_path}':fontsize={font_size}:fontcolor={color}:x=w-tw-10:y=h-th-10" -c:a copy "{output_path}"'''
            
            if self.ffmpeg.run_command(command):
                Logger.log_info(f"Thêm watermark thành công: {output_path}")
                return output_path
            else:
                Logger.log_error("Lỗi thêm watermark")
                return None
                
        except Exception as e:
            Logger.log_error(f"Lỗi thêm watermark: {e}")
            return None
    
    def add_music(self, input_path: str, music_path: str, 
                 volume: float = 0.5) -> Optional[str]:
        """Thêm nhạc nền"""
        try:
            if not os.path.exists(input_path):
                Logger.log_error(f"File video không tồn tại: {input_path}")
                return None
            
            if not os.path.exists(music_path):
                Logger.log_error(f"File nhạc không tồn tại: {music_path}")
                return None
            
            # Tạo tên file output
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{base_name}_with_music.mp4"
            output_path = os.path.join(self.output_path, output_filename)
            
            # Lệnh FFmpeg để mix audio
            command = f'''ffmpeg -i "{input_path}" -i "{music_path}" -filter_complex "[0:a]volume=1.0[a0];[1:a]volume={volume}[a1];[a0][a1]amix=inputs=2:duration=first[aout]" -map 0:v -map "[aout]" -c:v copy -c:a aac "{output_path}"'''
            
            if self.ffmpeg.run_command(command):
                Logger.log_info(f"Thêm nhạc thành công: {output_path}")
                return output_path
            else:
                Logger.log_error("Lỗi thêm nhạc")
                return None
                
        except Exception as e:
            Logger.log_error(f"Lỗi thêm nhạc: {e}")
            return None
    
    def change_speed(self, input_path: str, speed: float) -> Optional[str]:
        """Thay đổi tốc độ video"""
        try:
            if not os.path.exists(input_path):
                Logger.log_error(f"File không tồn tại: {input_path}")
                return None
            
            # Tạo tên file output
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{base_name}_speed_{speed}x.mp4"
            output_path = os.path.join(self.output_path, output_filename)
            
            # Lệnh FFmpeg
            command = f'ffmpeg -i "{input_path}" -filter:v "setpts={1/speed}*PTS" -filter:a "atempo={speed}" "{output_path}"'
            
            if self.ffmpeg.run_command(command):
                Logger.log_info(f"Thay đổi tốc độ thành công: {output_path}")
                return output_path
            else:
                Logger.log_error("Lỗi thay đổi tốc độ")
                return None
                
        except Exception as e:
            Logger.log_error(f"Lỗi thay đổi tốc độ: {e}")
            return None
    
    def flip_video(self, input_path: str, direction: str = "horizontal") -> Optional[str]:
        """Lật video"""
        try:
            if not os.path.exists(input_path):
                Logger.log_error(f"File không tồn tại: {input_path}")
                return None
            
            # Tạo tên file output
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{base_name}_flip_{direction}.mp4"
            output_path = os.path.join(self.output_path, output_filename)
            
            # Lệnh FFmpeg
            filter_name = "hflip" if direction == "horizontal" else "vflip"
            command = f'ffmpeg -i "{input_path}" -vf "{filter_name}" "{output_path}"'
            
            if self.ffmpeg.run_command(command):
                Logger.log_info(f"Lật video thành công: {output_path}")
                return output_path
            else:
                Logger.log_error("Lỗi lật video")
                return None
                
        except Exception as e:
            Logger.log_error(f"Lỗi lật video: {e}")
            return None
    
    def convert_to_9_16(self, input_path: str) -> Optional[str]:
        """Chuyển đổi tỷ lệ 9:16"""
        try:
            if not os.path.exists(input_path):
                Logger.log_error(f"File không tồn tại: {input_path}")
                return None
            
            # Tạo tên file output
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{base_name}_9_16.mp4"
            output_path = os.path.join(self.output_path, output_filename)
            
            # Lệnh FFmpeg
            command = f'ffmpeg -i "{input_path}" -vf "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2:black" "{output_path}"'
            
            if self.ffmpeg.run_command(command):
                Logger.log_info(f"Chuyển đổi 9:16 thành công: {output_path}")
                return output_path
            else:
                Logger.log_error("Lỗi chuyển đổi 9:16")
                return None
                
        except Exception as e:
            Logger.log_error(f"Lỗi chuyển đổi 9:16: {e}")
            return None
    
    def change_md5(self, input_path: str) -> Optional[str]:
        """Thay đổi MD5 để tránh duplicate detection"""
        try:
            if not os.path.exists(input_path):
                Logger.log_error(f"File không tồn tại: {input_path}")
                return None
            
            # Tạo tên file output
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{base_name}_md5_changed.mp4"
            output_path = os.path.join(self.output_path, output_filename)
            
            # Tạo metadata ngẫu nhiên
            random_title = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            random_artist = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Lệnh FFmpeg
            command = f'''ffmpeg -i "{input_path}" -c copy -metadata title="{random_title}" -metadata artist="{random_artist}" -metadata comment="Processed by TikTok Reup Offline" "{output_path}"'''
            
            if self.ffmpeg.run_command(command):
                Logger.log_info(f"Thay đổi MD5 thành công: {output_path}")
                return output_path
            else:
                Logger.log_error("Lỗi thay đổi MD5")
                return None
                
        except Exception as e:
            Logger.log_error(f"Lỗi thay đổi MD5: {e}")
            return None
    
    def apply_template(self, input_path: str, template_name: str) -> Optional[str]:
        """Áp dụng template xử lý"""
        try:
            if template_name not in self.templates.get('video_templates', {}):
                Logger.log_error(f"Template không tồn tại: {template_name}")
                return None
            
            template = self.templates['video_templates'][template_name]
            command = template['ffmpeg_command']
            
            # Thay thế placeholders
            command = command.replace('{input}', input_path)
            
            # Tạo tên file output
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{base_name}_{template_name}.mp4"
            output_path = os.path.join(self.output_path, output_filename)
            command = command.replace('{output}', output_path)
            
            if self.ffmpeg.run_command(command):
                Logger.log_info(f"Áp dụng template thành công: {output_path}")
                return output_path
            else:
                Logger.log_error("Lỗi áp dụng template")
                return None
                
        except Exception as e:
            Logger.log_error(f"Lỗi áp dụng template: {e}")
            return None
    
    def batch_process(self, input_files: List[str], operations: List[Dict[str, Any]]) -> List[str]:
        """Xử lý hàng loạt"""
        try:
            results = []
            
            for input_file in input_files:
                current_file = input_file
                
                for operation in operations:
                    op_type = operation.get('type')
                    op_params = operation.get('params', {})
                    
                    if op_type == 'cut':
                        current_file = self.cut_video(current_file, **op_params)
                    elif op_type == 'watermark':
                        current_file = self.add_watermark(current_file, **op_params)
                    elif op_type == 'music':
                        current_file = self.add_music(current_file, **op_params)
                    elif op_type == 'speed':
                        current_file = self.change_speed(current_file, **op_params)
                    elif op_type == 'flip':
                        current_file = self.flip_video(current_file, **op_params)
                    elif op_type == '9_16':
                        current_file = self.convert_to_9_16(current_file)
                    elif op_type == 'md5':
                        current_file = self.change_md5(current_file)
                    
                    if not current_file:
                        Logger.log_error(f"Lỗi xử lý file: {input_file}")
                        break
                
                if current_file:
                    results.append(current_file)
            
            Logger.log_info(f"Xử lý hàng loạt hoàn thành: {len(results)}/{len(input_files)} file")
            return results
            
        except Exception as e:
            Logger.log_error(f"Lỗi xử lý hàng loạt: {e}")
            return []
    
    def _get_font_path(self) -> str:
        """Lấy đường dẫn font"""
        font_paths = [
            'data/fonts/arial.ttf',
            'data/fonts/segoeui.ttf',
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/segoeui.ttf'
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path
        
        return 'arial'  # Fallback to system font
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Lấy thông tin video"""
        return self.ffmpeg.get_video_info(video_path)
    
    def create_thumbnail(self, video_path: str, time_offset: int = 5) -> Optional[str]:
        """Tạo thumbnail"""
        try:
            if not os.path.exists(video_path):
                return None
            
            # Tạo tên file thumbnail
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            thumbnail_path = os.path.join(self.output_path, f"{base_name}_thumb.jpg")
            
            # Lệnh FFmpeg
            command = f'ffmpeg -i "{video_path}" -ss {time_offset} -vframes 1 "{thumbnail_path}"'
            
            if self.ffmpeg.run_command(command):
                return thumbnail_path
            else:
                return None
                
        except Exception as e:
            Logger.log_error(f"Lỗi tạo thumbnail: {e}")
            return None
