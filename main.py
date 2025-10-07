"""
TikTok Reup Offline - Ứng dụng offline để tải xuống, xử lý và upload video
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from pathlib import Path

# Thêm src vào path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils import ConfigManager, FileManager, Logger
from src.downloader import VideoDownloader
from src.youtube_api import YouTubeAPIService
from src.processor import VideoProcessor
from src.uploader import VideoUploader

class TikTokReupApp:
    """Giao diện chính của ứng dụng"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TikTok Reup Offline")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Khởi tạo các component
        self.config = ConfigManager()
        self.downloader = VideoDownloader(self.config)
        self.youtube_api = YouTubeAPIService(self.config.get('download.youtube_api_key'))
        self.processor = VideoProcessor(self.config)
        self.uploader = VideoUploader(self.config)
        
        # Thiết lập logging
        Logger.setup_logging()
        
        # Tạo giao diện
        self.create_widgets()
        
        # Biến trạng thái
        self.is_processing = False
        self.downloaded_files = []
        self.processed_files = []
    
    def create_widgets(self):
        """Tạo các widget giao diện"""
        # Tạo notebook cho các tab
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab Download
        self.create_download_tab()
        
        # Tab Download List Channel TikTok
        self.create_download_channel_tiktok_tab()
        
        # Tab Download List Channel YouTube
        self.create_download_channel_youtube_tab()
        
        # Tab Process
        self.create_process_tab()
        
        # Tab Upload
        self.create_upload_tab()
        
        # Tab Settings
        self.create_settings_tab()
        
        # Status bar
        self.create_status_bar()
    
    def create_download_tab(self):
        """Tạo tab Download"""
        download_frame = ttk.Frame(self.notebook)
        self.notebook.add(download_frame, text="📥 Download")
        
        # URL input
        url_frame = ttk.LabelFrame(download_frame, text="URL Video", padding=10)
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=80)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.download_btn = ttk.Button(url_frame, text="Download", 
                                     command=self.download_video)
        self.download_btn.pack(side=tk.RIGHT)
        
        # Video info
        info_frame = ttk.LabelFrame(download_frame, text="Thông tin Video", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.info_text = tk.Text(info_frame, height=10, wrap=tk.WORD)
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Downloaded files list
        files_frame = ttk.LabelFrame(download_frame, text="Files đã tải", padding=10)
        files_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.files_listbox = tk.Listbox(files_frame, height=6)
        files_scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = ttk.Frame(files_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Xóa file", command=self.delete_selected_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Mở thư mục", command=self.open_download_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_files_list).pack(side=tk.LEFT)

        # Progress bar
        progress_frame = ttk.Frame(download_frame)
        progress_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
        self.download_progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate', maximum=100)
        self.download_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.download_progress_label = ttk.Label(progress_frame, text="0%")
        self.download_progress_label.pack(side=tk.LEFT, padx=(10,0))

    def create_download_channel_tiktok_tab(self):
        """Tạo tab Download List Channel TikTok"""
        channel_frame = ttk.Frame(self.notebook)
        self.notebook.add(channel_frame, text="📚 Download List Channel TikTok")
        
        # URL kênh
        url_frame = ttk.LabelFrame(channel_frame, text="URL Kênh/Playlist/Profile", padding=10)
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        self.channel_url_var = tk.StringVar()
        ttk.Entry(url_frame, textvariable=self.channel_url_var, width=80).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        ttk.Button(url_frame, text="Lấy danh sách", command=self.fetch_channel_list).pack(side=tk.RIGHT)
        
        # Danh sách video (Treeview 4 cột)
        list_frame = ttk.LabelFrame(channel_frame, text="Danh sách video", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        columns = ("stt", "title", "progress", "selected")
        self.channel_tree = ttk.Treeview(list_frame, columns=columns, show='headings', selectmode='extended', height=14)
        self.channel_tree.heading('stt', text='STT')
        self.channel_tree.heading('title', text='Tiêu đề')
        self.channel_tree.heading('progress', text='Tiến trình')
        self.channel_tree.heading('selected', text='Tải?')
        self.channel_tree.column('stt', width=50, anchor=tk.CENTER, stretch=False)
        self.channel_tree.column('title', width=700, anchor=tk.W)
        self.channel_tree.column('progress', width=100, anchor=tk.CENTER, stretch=False)
        self.channel_tree.column('selected', width=60, anchor=tk.CENTER, stretch=False)
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.channel_tree.yview)
        self.channel_tree.configure(yscrollcommand=list_scrollbar.set)
        self.channel_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Toggle checkbox khi click cột 'selected'
        self.channel_tree.bind('<Button-1>', self.on_channel_tree_click)
        # Menu chuột phải
        self.channel_context_menu = tk.Menu(self.root, tearoff=0)
        self.channel_context_menu.add_command(label="Xóa video đã chọn", command=self.delete_selected_channel_videos)
        self.channel_context_menu.add_command(label="Tải video đã chọn", command=lambda: self.download_channel_videos(selected_only=True))
        self.channel_context_menu.add_separator()
        self.channel_context_menu.add_command(label="Chọn tất cả", command=self.select_all_channel_videos)
        self.channel_context_menu.add_command(label="Bỏ chọn tất cả", command=self.deselect_all_channel_videos)
        self.channel_tree.bind('<Button-3>', self.show_channel_context_menu)
        
        # Buttons
        actions = ttk.Frame(channel_frame)
        actions.pack(fill=tk.X, padx=10, pady=(0,5))
        ttk.Button(actions, text="Tải đã chọn", command=lambda: self.download_channel_videos(selected_only=True)).pack(side=tk.LEFT)
        ttk.Button(actions, text="Tải tất cả", command=lambda: self.download_channel_videos(selected_only=False)).pack(side=tk.LEFT, padx=(10,0))
        ttk.Button(actions, text="Tải lại video lỗi", command=self.retry_failed_videos).pack(side=tk.LEFT, padx=(10,0))
        ttk.Button(actions, text="Xóa video đã chọn", command=self.delete_selected_channel_videos).pack(side=tk.LEFT, padx=(10,0))
        ttk.Button(actions, text="Xóa tất cả", command=self.delete_all_channel_videos).pack(side=tk.LEFT, padx=(10,0))
        
        # Progress tổng
        progress_frame = ttk.Frame(channel_frame)
        progress_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
        self.channel_progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate', maximum=100)
        self.channel_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.channel_progress_label = ttk.Label(progress_frame, text="0%")
        self.channel_progress_label.pack(side=tk.LEFT, padx=(10,0))
        
        # Lưu danh sách videos (mỗi item: title,url,id,duration,selected,progress)
        self.channel_videos = []
    
    def create_download_channel_youtube_tab(self):
        """Tạo tab Download List Channel YouTube"""
        youtube_frame = ttk.Frame(self.notebook)
        self.notebook.add(youtube_frame, text="📺 Download List Channel YouTube")
        
        # API Status
        api_frame = ttk.LabelFrame(youtube_frame, text="Trạng thái API", padding=10)
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.api_status_var = tk.StringVar()
        self.api_status_label = ttk.Label(api_frame, textvariable=self.api_status_var)
        self.api_status_label.pack(side=tk.LEFT)
        
        ttk.Button(api_frame, text="Test API", command=self.test_youtube_api).pack(side=tk.RIGHT)
        
        # URL kênh
        url_frame = ttk.LabelFrame(youtube_frame, text="URL Kênh YouTube", padding=10)
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # URL input
        url_input_frame = ttk.Frame(url_frame)
        url_input_frame.pack(fill=tk.X, pady=(0, 5))
        self.youtube_url_var = tk.StringVar()
        ttk.Entry(url_input_frame, textvariable=self.youtube_url_var, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        
        # Số lượng video
        count_frame = ttk.Frame(url_frame)
        count_frame.pack(fill=tk.X)
        ttk.Label(count_frame, text="Số video:").pack(side=tk.LEFT)
        self.youtube_count_var = tk.StringVar(value="200")
        count_combo = ttk.Combobox(count_frame, textvariable=self.youtube_count_var, 
                                  values=["50", "100", "200", "500"], width=10, state="readonly")
        count_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(url_input_frame, text="Lấy danh sách", command=self.fetch_youtube_channel_list).pack(side=tk.RIGHT)
        
        # Thông tin channel
        info_frame = ttk.LabelFrame(youtube_frame, text="Thông tin Channel", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.youtube_info_text = tk.Text(info_frame, height=4, wrap=tk.WORD)
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.youtube_info_text.yview)
        self.youtube_info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.youtube_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Danh sách video (Treeview 5 cột)
        list_frame = ttk.LabelFrame(youtube_frame, text="Danh sách video", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        columns = ("stt", "title", "duration", "views", "progress", "selected")
        self.youtube_tree = ttk.Treeview(list_frame, columns=columns, show='headings', selectmode='extended', height=12)
        self.youtube_tree.heading('stt', text='STT')
        self.youtube_tree.heading('title', text='Tiêu đề')
        self.youtube_tree.heading('duration', text='Thời lượng')
        self.youtube_tree.heading('views', text='Lượt xem')
        self.youtube_tree.heading('progress', text='Tiến trình')
        self.youtube_tree.heading('selected', text='Tải?')
        self.youtube_tree.column('stt', width=50, anchor=tk.CENTER, stretch=False)
        self.youtube_tree.column('title', width=500, anchor=tk.W)
        self.youtube_tree.column('duration', width=80, anchor=tk.CENTER, stretch=False)
        self.youtube_tree.column('views', width=100, anchor=tk.CENTER, stretch=False)
        self.youtube_tree.column('progress', width=80, anchor=tk.CENTER, stretch=False)
        self.youtube_tree.column('selected', width=60, anchor=tk.CENTER, stretch=False)
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.youtube_tree.yview)
        self.youtube_tree.configure(yscrollcommand=list_scrollbar.set)
        self.youtube_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Toggle checkbox khi click cột 'selected'
        self.youtube_tree.bind('<Button-1>', self.on_youtube_tree_click)
        
        # Menu chuột phải
        self.youtube_context_menu = tk.Menu(self.root, tearoff=0)
        self.youtube_context_menu.add_command(label="Xóa video đã chọn", command=self.delete_selected_youtube_videos)
        self.youtube_context_menu.add_command(label="Tải video đã chọn", command=lambda: self.download_youtube_videos(selected_only=True))
        self.youtube_context_menu.add_separator()
        self.youtube_context_menu.add_command(label="Chọn tất cả", command=self.select_all_youtube_videos)
        self.youtube_context_menu.add_command(label="Bỏ chọn tất cả", command=self.deselect_all_youtube_videos)
        self.youtube_tree.bind('<Button-3>', self.show_youtube_context_menu)
        
        # Buttons
        actions = ttk.Frame(youtube_frame)
        actions.pack(fill=tk.X, padx=10, pady=(0,5))
        ttk.Button(actions, text="Tải đã chọn", command=lambda: self.download_youtube_videos(selected_only=True)).pack(side=tk.LEFT)
        ttk.Button(actions, text="Tải tất cả", command=lambda: self.download_youtube_videos(selected_only=False)).pack(side=tk.LEFT, padx=(10,0))
        ttk.Button(actions, text="Tải lại video lỗi", command=self.retry_failed_youtube_videos).pack(side=tk.LEFT, padx=(10,0))
        ttk.Button(actions, text="Xóa video đã chọn", command=self.delete_selected_youtube_videos).pack(side=tk.LEFT, padx=(10,0))
        ttk.Button(actions, text="Xóa tất cả", command=self.delete_all_youtube_videos).pack(side=tk.LEFT, padx=(10,0))
        
        # Progress tổng
        progress_frame = ttk.Frame(youtube_frame)
        progress_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
        self.youtube_progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate', maximum=100)
        self.youtube_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.youtube_progress_label = ttk.Label(progress_frame, text="0%")
        self.youtube_progress_label.pack(side=tk.LEFT, padx=(10,0))
        
        # Lưu danh sách videos YouTube
        self.youtube_videos = []
        
        # Cập nhật trạng thái API
        self.update_youtube_api_status()
    
    def create_process_tab(self):
        """Tạo tab Process"""
        process_frame = ttk.Frame(self.notebook)
        self.notebook.add(process_frame, text="✂️ Process")
        
        # File selection
        file_frame = ttk.LabelFrame(process_frame, text="Chọn file video", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.process_file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.process_file_var, width=70)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(file_frame, text="Browse", command=self.browse_video_file).pack(side=tk.RIGHT)
        
        # Processing options
        options_frame = ttk.LabelFrame(process_frame, text="Tùy chọn xử lý", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Cut options
        cut_frame = ttk.Frame(options_frame)
        cut_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(cut_frame, text="Cắt video:").pack(side=tk.LEFT)
        self.cut_var = tk.StringVar(value="none")
        cut_combo = ttk.Combobox(cut_frame, textvariable=self.cut_var, 
                               values=["none", "1min", "3min", "5min", "10min", "30min"],
                               state="readonly", width=10)
        cut_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Watermark options
        watermark_frame = ttk.Frame(options_frame)
        watermark_frame.pack(fill=tk.X, pady=5)
        
        self.watermark_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(watermark_frame, text="Thêm watermark", 
                       variable=self.watermark_var).pack(side=tk.LEFT)
        
        self.watermark_text_var = tk.StringVar(value="TikTok Reup Offline")
        ttk.Entry(watermark_frame, textvariable=self.watermark_text_var, width=30).pack(side=tk.LEFT, padx=(10, 0))
        
        # Speed options
        speed_frame = ttk.Frame(options_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="Tốc độ:").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(speed_frame, from_=0.5, to=2.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL, length=200)
        speed_scale.pack(side=tk.LEFT, padx=(10, 0))
        
        self.speed_label = ttk.Label(speed_frame, text="1.0x")
        self.speed_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Other options
        other_frame = ttk.Frame(options_frame)
        other_frame.pack(fill=tk.X, pady=5)
        
        self.flip_var = tk.StringVar(value="none")
        ttk.Label(other_frame, text="Lật:").pack(side=tk.LEFT)
        ttk.Radiobutton(other_frame, text="Không", variable=self.flip_var, value="none").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(other_frame, text="Ngang", variable=self.flip_var, value="horizontal").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(other_frame, text="Dọc", variable=self.flip_var, value="vertical").pack(side=tk.LEFT, padx=(5, 0))
        
        self.convert_916_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(other_frame, text="Chuyển 9:16", 
                       variable=self.convert_916_var).pack(side=tk.LEFT, padx=(20, 0))
        
        self.change_md5_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(other_frame, text="Thay đổi MD5", 
                       variable=self.change_md5_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # Process button
        process_btn_frame = ttk.Frame(process_frame)
        process_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.process_btn = ttk.Button(process_btn_frame, text="Xử lý Video", 
                                    command=self.process_video, style="Accent.TButton")
        self.process_btn.pack(side=tk.LEFT)
        
        # Process log
        log_frame = ttk.LabelFrame(process_frame, text="Log xử lý", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.process_log = tk.Text(log_frame, height=8, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.process_log.yview)
        self.process_log.configure(yscrollcommand=log_scrollbar.set)
        
        self.process_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        speed_scale.configure(command=self.update_speed_label)
    
    def create_upload_tab(self):
        """Tạo tab Upload"""
        upload_frame = ttk.Frame(self.notebook)
        self.notebook.add(upload_frame, text="📤 Upload")
        
        # File selection
        file_frame = ttk.LabelFrame(upload_frame, text="Chọn file video", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.upload_file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.upload_file_var, width=70)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(file_frame, text="Browse", command=self.browse_upload_file).pack(side=tk.RIGHT)
        
        # Platform selection
        platform_frame = ttk.LabelFrame(upload_frame, text="Nền tảng", padding=10)
        platform_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.platform_var = tk.StringVar(value="tiktok")
        ttk.Radiobutton(platform_frame, text="TikTok", variable=self.platform_var, value="tiktok").pack(side=tk.LEFT)
        ttk.Radiobutton(platform_frame, text="YouTube", variable=self.platform_var, value="youtube").pack(side=tk.LEFT, padx=(20, 0))
        ttk.Radiobutton(platform_frame, text="Facebook", variable=self.platform_var, value="facebook").pack(side=tk.LEFT, padx=(20, 0))
        
        # Upload content
        content_frame = ttk.LabelFrame(upload_frame, text="Nội dung", padding=10)
        content_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(content_frame, text="Tiêu đề:").pack(anchor=tk.W)
        self.title_var = tk.StringVar()
        ttk.Entry(content_frame, textvariable=self.title_var, width=80).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(content_frame, text="Mô tả:").pack(anchor=tk.W)
        self.description_var = tk.StringVar()
        ttk.Entry(content_frame, textvariable=self.description_var, width=80).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(content_frame, text="Hashtags:").pack(anchor=tk.W)
        self.hashtags_var = tk.StringVar()
        ttk.Entry(content_frame, textvariable=self.hashtags_var, width=80).pack(fill=tk.X)
        
        # Upload button
        upload_btn_frame = ttk.Frame(upload_frame)
        upload_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.upload_btn = ttk.Button(upload_btn_frame, text="Upload Video", 
                                   command=self.upload_video, style="Accent.TButton")
        self.upload_btn.pack(side=tk.LEFT)
        
        # Upload log
        log_frame = ttk.LabelFrame(upload_frame, text="Log upload", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.upload_log = tk.Text(log_frame, height=8, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.upload_log.yview)
        self.upload_log.configure(yscrollcommand=log_scrollbar.set)
        
        self.upload_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_settings_tab(self):
        """Tạo tab Settings"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Download settings
        download_frame = ttk.LabelFrame(settings_frame, text="Cài đặt Download", padding=10)
        download_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(download_frame, text="Độ phân giải:").pack(anchor=tk.W)
        self.resolution_var = tk.StringVar(value=self.config.get('download.resolution', '1080p'))
        resolution_combo = ttk.Combobox(download_frame, textvariable=self.resolution_var,
                                      values=['360p', '480p', '720p', '1080p'], state="readonly")
        resolution_combo.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))
        
        ttk.Label(download_frame, text="Thư mục lưu:").pack(anchor=tk.W)
        folder_frame = ttk.Frame(download_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.download_folder_var = tk.StringVar(value=self.config.get('download.output_path', 'data/videos'))
        ttk.Entry(folder_frame, textvariable=self.download_folder_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(folder_frame, text="Browse", command=self.browse_download_folder).pack(side=tk.RIGHT)
        
        # Process settings
        process_frame = ttk.LabelFrame(settings_frame, text="Cài đặt xử lý", padding=10)
        process_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(process_frame, text="Thư mục xử lý:").pack(anchor=tk.W)
        process_folder_frame = ttk.Frame(process_frame)
        process_folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.process_folder_var = tk.StringVar(value=self.config.get('processing.output_path', 'data/processed'))
        ttk.Entry(process_folder_frame, textvariable=self.process_folder_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(process_folder_frame, text="Browse", command=self.browse_process_folder).pack(side=tk.RIGHT)
        
        # YouTube API settings
        youtube_frame = ttk.LabelFrame(settings_frame, text="Cài đặt YouTube API", padding=10)
        youtube_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(youtube_frame, text="YouTube API Key:").pack(anchor=tk.W)
        self.youtube_api_key_var = tk.StringVar(value=self.config.get('download.youtube_api_key', ''))
        youtube_key_entry = ttk.Entry(youtube_frame, textvariable=self.youtube_api_key_var, show="*", width=60)
        youtube_key_entry.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(youtube_frame, text="Hướng dẫn:", font=("Arial", 8)).pack(anchor=tk.W)
        ttk.Label(youtube_frame, text="1. Truy cập https://console.developers.google.com/", font=("Arial", 8)).pack(anchor=tk.W)
        ttk.Label(youtube_frame, text="2. Tạo project mới hoặc chọn project hiện có", font=("Arial", 8)).pack(anchor=tk.W)
        ttk.Label(youtube_frame, text="3. Bật YouTube Data API v3", font=("Arial", 8)).pack(anchor=tk.W)
        ttk.Label(youtube_frame, text="4. Tạo API key và dán vào ô trên", font=("Arial", 8)).pack(anchor=tk.W)
        
        # FFmpeg settings
        ffmpeg_frame = ttk.LabelFrame(settings_frame, text="Cài đặt FFmpeg", padding=10)
        ffmpeg_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(ffmpeg_frame, text="Đường dẫn FFmpeg:").pack(anchor=tk.W)
        ffmpeg_path_frame = ttk.Frame(ffmpeg_frame)
        ffmpeg_path_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.ffmpeg_path_var = tk.StringVar(value=self.config.get('ffmpeg.path', 'tools/ffmpeg.exe'))
        ttk.Entry(ffmpeg_path_frame, textvariable=self.ffmpeg_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(ffmpeg_path_frame, text="Browse", command=self.browse_ffmpeg_path).pack(side=tk.RIGHT)
        
        # Save button
        save_btn_frame = ttk.Frame(settings_frame)
        save_btn_frame.pack(fill=tk.X, padx=10, pady=20)
        
        ttk.Button(save_btn_frame, text="Lưu cài đặt", command=self.save_settings).pack(side=tk.LEFT)
        ttk.Button(save_btn_frame, text="Reset", command=self.reset_settings).pack(side=tk.LEFT, padx=(10, 0))
    
    def create_status_bar(self):
        """Tạo status bar"""
        self.status_var = tk.StringVar(value="Sẵn sàng")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message):
        """Cập nhật status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def update_speed_label(self, value):
        """Cập nhật label tốc độ"""
        self.speed_label.config(text=f"{float(value):.1f}x")
    
    def download_video(self):
        """Tải video"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Lỗi", "Vui lòng nhập URL video")
            return
        
        if not self.downloader.is_supported_url(url):
            messagebox.showerror("Lỗi", "URL không được hỗ trợ")
            return
        
        def download_thread():
            try:
                self.update_status("Đang lấy thông tin video...")
                self.download_btn.config(state="disabled")
                # Đồng bộ cài đặt mới nhất vào downloader
                self.downloader.reload_settings()
                # Reset tiến trình đầu lượt tải
                self.root.after(0, self.update_download_progress, 0.0)
                
                # Lấy thông tin video
                info = self.downloader.get_video_info(url)
                if info:
                    self.root.after(0, self.display_video_info, info)
                
                self.update_status("Đang tải video...")

                def hook(d):
                    try:
                        status = d.get('status')
                        percent = None
                        if status == 'downloading':
                            downloaded = d.get('downloaded_bytes') or 0
                            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                            if total:
                                percent = downloaded * 100.0 / float(total)
                            else:
                                # Fallback theo fragment (HLS/DASH)
                                frag_idx = d.get('fragment_index') or 0
                                frag_cnt = d.get('fragment_count') or 0
                                if frag_cnt:
                                    percent = frag_idx * 100.0 / float(frag_cnt)
                        elif status == 'finished':
                            percent = 100.0
                        if percent is not None:
                            self.root.after(0, self.update_download_progress, percent)
                    except Exception:
                        pass

                file_path = self.downloader.download_video(url, progress_hook=hook)
                
                if file_path:
                    self.root.after(0, self.download_success, file_path)
                else:
                    self.root.after(0, self.download_error)
                    
            except Exception as e:
                self.root.after(0, self.download_error, str(e))
            finally:
                self.root.after(0, self.download_finish)
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def display_video_info(self, info):
        """Hiển thị thông tin video"""
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"Tiêu đề: {info.get('title', 'N/A')}\n")
        self.info_text.insert(tk.END, f"Thời lượng: {info.get('duration', 0)} giây\n")
        self.info_text.insert(tk.END, f"Người đăng: {info.get('uploader', 'N/A')}\n")
        self.info_text.insert(tk.END, f"Lượt xem: {info.get('view_count', 0):,}\n")
        self.info_text.insert(tk.END, f"Lượt thích: {info.get('like_count', 0):,}\n")
        self.info_text.insert(tk.END, f"Nền tảng: {info.get('platform', 'N/A')}\n")
        self.info_text.insert(tk.END, f"URL: {info.get('url', 'N/A')}\n")
    
    def download_success(self, file_path):
        """Xử lý khi tải thành công"""
        self.downloaded_files.append(file_path)
        self.files_listbox.insert(tk.END, os.path.basename(file_path))
        # Cập nhật tiến trình 100%
        self.update_download_progress(100.0)
        messagebox.showinfo("Thành công", f"Tải video thành công:\n{file_path}")
    
    def download_error(self, error_msg=None):
        """Xử lý khi tải lỗi"""
        msg = error_msg or "Lỗi tải video"
        messagebox.showerror("Lỗi", msg)
    
    def download_finish(self):
        """Kết thúc tải"""
        self.download_btn.config(state="normal")
        self.update_status("Sẵn sàng")
        # Giữ nguyên tiến trình để người dùng kịp quan sát
    
    def update_download_progress(self, percent: float):
        """Cập nhật thanh tiến trình tải"""
        try:
            value = max(0, min(100, float(percent)))
        except Exception:
            value = 0.0
        self.download_progress['value'] = value
        self.download_progress_label.config(text=f"{value:.0f}%")
        self.root.update_idletasks()

    def fetch_channel_list(self):
        """Lấy danh sách video public do chủ kênh đăng"""
        url = self.channel_url_var.get().strip()
        if not url:
            messagebox.showerror("Lỗi", "Vui lòng nhập URL kênh hoặc playlist")
            return
        
        def fetch_thread():
            try:
                self.update_status("Đang lấy danh sách video...")
                videos = self.downloader.list_channel_videos(url, max_videos=50)
                # Khởi tạo thêm thuộc tính 'selected' và 'progress' cho mỗi video
                self.channel_videos = [{**v, 'selected': True, 'progress': 0.0} for v in videos]
                def update_ui():
                    self.refresh_channel_list_display()
                    self.update_status(f"Đã lấy {len(videos)} video")
                    self.update_channel_progress(0)
                self.root.after(0, update_ui)
            except Exception as e:
                self.root.after(0, messagebox.showerror, "Lỗi", f"Không lấy được danh sách: {e}")
                self.root.after(0, self.update_status, "Sẵn sàng")
        threading.Thread(target=fetch_thread, daemon=True).start()

    def download_channel_videos(self, selected_only: bool):
        """Tải các video trong danh sách (đã chọn hoặc tất cả)"""
        if not self.channel_videos:
            messagebox.showwarning("Cảnh báo", "Chưa có danh sách video để tải")
            return
        
        if selected_only:
            indices = [i for i, v in enumerate(self.channel_videos) if v.get('selected')]
        else:
            indices = list(range(len(self.channel_videos)))
        if not indices:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn video để tải")
            return
        
        def batch_thread():
            try:
                import time
                total = len(indices)
                successful_downloads = 0
                self.update_status(f"Đang tải danh sách ({total} video)...")
                
                for idx_pos, idx in enumerate(indices, start=1):
                    video = self.channel_videos[idx]
                    url = video.get('url')
                    title = video.get('title') or video.get('id')
                    
                    # Cập nhật tiến trình tổng
                    self.root.after(0, self.update_channel_progress, (idx_pos-1) * 100.0 / total)
                    self.root.after(0, self.update_row_progress, idx, 0.0)
                    
                    # Thử tải với retry
                    success = False
                    for retry in range(3):  # Thử tối đa 3 lần
                        try:
                            def hook(d):
                                try:
                                    status = d.get('status')
                                    file_percent = None
                                    if status == 'downloading':
                                        downloaded = d.get('downloaded_bytes') or 0
                                        t = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                                        if t:
                                            file_percent = downloaded * 100.0 / float(t)
                                        else:
                                            fi = d.get('fragment_index') or 0
                                            fc = d.get('fragment_count') or 0
                                            if fc:
                                                file_percent = fi * 100.0 / float(fc)
                                    elif status == 'finished':
                                        file_percent = 100.0
                                    if file_percent is not None:
                                        overall = (idx_pos-1) * 100.0 / total + (file_percent / total)
                                        self.root.after(0, self.update_channel_progress, overall)
                                        self.root.after(0, self.update_row_progress, idx, file_percent)
                                except Exception:
                                    pass
                            
                            result = self.downloader.download_video(url, custom_filename=None, progress_hook=hook)
                            if result:
                                success = True
                                successful_downloads += 1
                                self.root.after(0, self.update_row_progress, idx, 100.0)
                                break
                            else:
                                if retry < 2:  # Chưa hết lần thử
                                    self.root.after(0, self.update_row_progress, idx, 0.0)
                                    time.sleep(2)  # Delay 2 giây trước khi thử lại
                                    
                        except Exception as e:
                            if retry < 2:
                                time.sleep(2)
                            else:
                                self.root.after(0, self.update_row_progress, idx, 0.0)
                    
                    if not success:
                        self.root.after(0, self.update_row_progress, idx, 0.0)
                    
                    # Delay giữa các video để tránh rate limiting
                    if idx_pos < total:
                        time.sleep(1)
                
                self.root.after(0, self.update_channel_progress, 100.0)
                self.root.after(0, self.update_status, f"Hoàn tất: {successful_downloads}/{total} video thành công")
                
                if successful_downloads < total:
                    self.root.after(0, messagebox.showwarning, "Cảnh báo", 
                                  f"Chỉ tải được {successful_downloads}/{total} video. Có thể do:\n"
                                  "- Firewall/antivirus chặn kết nối\n"
                                  "- TikTok rate limiting\n"
                                  "- Mạng không ổn định")
                
            except Exception as e:
                self.root.after(0, messagebox.showerror, "Lỗi", f"Lỗi tải danh sách: {e}")
                self.root.after(0, self.update_status, "Sẵn sàng")
        threading.Thread(target=batch_thread, daemon=True).start()

    def retry_failed_videos(self):
        """Tải lại những video bị lỗi (tiến trình < 100%)"""
        if not self.channel_videos:
            messagebox.showwarning("Cảnh báo", "Chưa có danh sách video")
            return
        
        # Tìm video có tiến trình < 100%
        failed_indices = []
        for i, video in enumerate(self.channel_videos):
            progress = video.get('progress', 0.0)
            if progress < 100.0:
                failed_indices.append(i)
                video['selected'] = True  # Tự động chọn video lỗi
        
        if not failed_indices:
            messagebox.showinfo("Thông báo", "Không có video nào bị lỗi")
            return
        
        # Cập nhật hiển thị
        for idx in failed_indices:
            self.update_tree_row(idx)
        
        messagebox.showinfo("Thông báo", f"Tìm thấy {len(failed_indices)} video lỗi, bắt đầu tải lại...")
        
        # Tải lại video lỗi
        self.download_channel_videos(selected_only=True)

    def update_channel_progress(self, percent: float):
        """Cập nhật tiến trình cho tab Download List Channel"""
        try:
            value = max(0, min(100, float(percent)))
        except Exception:
            value = 0.0
        self.channel_progress['value'] = value
        self.channel_progress_label.config(text=f"{value:.0f}%")
        self.root.update_idletasks()

    def on_channel_tree_click(self, event):
        """Toggle trạng thái chọn ở cột 'Tải?' khi click"""
        try:
            region = self.channel_tree.identify('region', event.x, event.y)
            if region != 'cell':
                return
            row_id = self.channel_tree.identify_row(event.y)
            col = self.channel_tree.identify_column(event.x)
            if not row_id or col != '#4':
                return
            idx = int(self.channel_tree.index(row_id))
            if 0 <= idx < len(self.channel_videos):
                self.channel_videos[idx]['selected'] = not self.channel_videos[idx].get('selected', True)
                self.update_tree_row(idx)
        except Exception:
            pass
    
    def browse_video_file(self):
        """Chọn file video"""
        file_path = filedialog.askopenfilename(
            title="Chọn file video",
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov *.wmv"), ("All files", "*.*")]
        )
        if file_path:
            self.process_file_var.set(file_path)
    
    def browse_upload_file(self):
        """Chọn file upload"""
        file_path = filedialog.askopenfilename(
            title="Chọn file video",
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov *.wmv"), ("All files", "*.*")]
        )
        if file_path:
            self.upload_file_var.set(file_path)
    
    def process_video(self):
        """Xử lý video"""
        file_path = self.process_file_var.get().strip()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Lỗi", "Vui lòng chọn file video hợp lệ")
            return
        
        def process_thread():
            try:
                self.update_status("Đang xử lý video...")
                self.process_btn.config(state="disabled")
                self.process_log.delete(1.0, tk.END)
                
                current_file = file_path
                operations = []
                
                # Cắt video
                cut_option = self.cut_var.get()
                if cut_option != "none":
                    duration_map = {"1min": 60, "3min": 180, "5min": 300, "10min": 600, "30min": 1800}
                    duration = duration_map.get(cut_option, 60)
                    self.root.after(0, self.log_message, f"Cắt video {cut_option}...")
                    current_file = self.processor.cut_video(current_file, duration)
                    if not current_file:
                        raise Exception("Lỗi cắt video")
                
                # Thêm watermark
                if self.watermark_var.get():
                    self.root.after(0, self.log_message, "Thêm watermark...")
                    current_file = self.processor.add_watermark(current_file, self.watermark_text_var.get())
                    if not current_file:
                        raise Exception("Lỗi thêm watermark")
                
                # Thay đổi tốc độ
                speed = self.speed_var.get()
                if speed != 1.0:
                    self.root.after(0, self.log_message, f"Thay đổi tốc độ {speed}x...")
                    current_file = self.processor.change_speed(current_file, speed)
                    if not current_file:
                        raise Exception("Lỗi thay đổi tốc độ")
                
                # Lật video
                flip_option = self.flip_var.get()
                if flip_option != "none":
                    self.root.after(0, self.log_message, f"Lật video {flip_option}...")
                    current_file = self.processor.flip_video(current_file, flip_option)
                    if not current_file:
                        raise Exception("Lỗi lật video")
                
                # Chuyển 9:16
                if self.convert_916_var.get():
                    self.root.after(0, self.log_message, "Chuyển đổi tỷ lệ 9:16...")
                    current_file = self.processor.convert_to_9_16(current_file)
                    if not current_file:
                        raise Exception("Lỗi chuyển đổi 9:16")
                
                # Thay đổi MD5
                if self.change_md5_var.get():
                    self.root.after(0, self.log_message, "Thay đổi MD5...")
                    current_file = self.processor.change_md5(current_file)
                    if not current_file:
                        raise Exception("Lỗi thay đổi MD5")
                
                self.root.after(0, self.process_success, current_file)
                
            except Exception as e:
                self.root.after(0, self.process_error, str(e))
            finally:
                self.root.after(0, self.process_finish)
        
        threading.Thread(target=process_thread, daemon=True).start()
    
    def log_message(self, message):
        """Thêm message vào log"""
        self.process_log.insert(tk.END, f"{message}\n")
        self.process_log.see(tk.END)
        self.root.update_idletasks()
    
    def process_success(self, file_path):
        """Xử lý thành công"""
        self.processed_files.append(file_path)
        self.log_message(f"Xử lý thành công: {file_path}")
        messagebox.showinfo("Thành công", f"Xử lý video thành công:\n{file_path}")
    
    def process_error(self, error_msg):
        """Xử lý lỗi"""
        self.log_message(f"Lỗi: {error_msg}")
        messagebox.showerror("Lỗi", f"Lỗi xử lý video: {error_msg}")
    
    def process_finish(self):
        """Kết thúc xử lý"""
        self.process_btn.config(state="normal")
        self.update_status("Sẵn sàng")
    
    def upload_video(self):
        """Upload video"""
        file_path = self.upload_file_var.get().strip()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Lỗi", "Vui lòng chọn file video hợp lệ")
            return
        
        platform = self.platform_var.get()
        title = self.title_var.get().strip()
        description = self.description_var.get().strip()
        hashtags = self.hashtags_var.get().strip()
        
        def upload_thread():
            try:
                self.update_status(f"Đang upload lên {platform}...")
                self.upload_btn.config(state="disabled")
                self.upload_log.delete(1.0, tk.END)
                self.upload_log.insert(tk.END, f"Bắt đầu upload lên {platform}...\n")
                
                if platform == "tiktok":
                    success = self.uploader.upload_to_tiktok(file_path, title, hashtags)
                elif platform == "youtube":
                    success = self.uploader.upload_to_youtube(file_path, title, description)
                elif platform == "facebook":
                    success = self.uploader.upload_to_facebook(file_path, title, description)
                else:
                    raise Exception("Nền tảng không được hỗ trợ")
                
                if success:
                    self.root.after(0, self.upload_success)
                else:
                    self.root.after(0, self.upload_error)
                    
            except Exception as e:
                self.root.after(0, self.upload_error, str(e))
            finally:
                self.root.after(0, self.upload_finish)
        
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def upload_success(self):
        """Upload thành công"""
        self.upload_log.insert(tk.END, "Upload thành công!\n")
        messagebox.showinfo("Thành công", "Upload video thành công!")
    
    def upload_error(self, error_msg=None):
        """Upload lỗi"""
        msg = error_msg or "Lỗi upload video"
        self.upload_log.insert(tk.END, f"Lỗi: {msg}\n")
        messagebox.showerror("Lỗi", f"Lỗi upload video: {msg}")
    
    def upload_finish(self):
        """Kết thúc upload"""
        self.upload_btn.config(state="normal")
        self.update_status("Sẵn sàng")
    
    def delete_selected_file(self):
        """Xóa file đã chọn"""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file để xóa")
            return
        
        index = selection[0]
        if index < len(self.downloaded_files):
            file_path = self.downloaded_files[index]
            try:
                os.remove(file_path)
                self.downloaded_files.pop(index)
                self.files_listbox.delete(index)
                messagebox.showinfo("Thành công", "Đã xóa file")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi xóa file: {e}")
    
    def open_download_folder(self):
        """Mở thư mục download"""
        folder_path = self.config.get('download.output_path', 'data/videos')
        if os.path.exists(folder_path):
            os.startfile(folder_path)
        else:
            messagebox.showwarning("Cảnh báo", "Thư mục không tồn tại")
    
    def refresh_files_list(self):
        """Làm mới danh sách file"""
        self.files_listbox.delete(0, tk.END)
        self.downloaded_files.clear()
        
        folder_path = self.config.get('download.output_path', 'data/videos')
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if file.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
                    file_path = os.path.join(folder_path, file)
                    self.downloaded_files.append(file_path)
                    self.files_listbox.insert(tk.END, file)
    
    def browse_download_folder(self):
        """Chọn thư mục download"""
        folder = filedialog.askdirectory(title="Chọn thư mục lưu video")
        if folder:
            self.download_folder_var.set(folder)
    
    def browse_process_folder(self):
        """Chọn thư mục xử lý"""
        folder = filedialog.askdirectory(title="Chọn thư mục xử lý")
        if folder:
            self.process_folder_var.set(folder)
    
    def browse_ffmpeg_path(self):
        """Chọn đường dẫn FFmpeg"""
        file_path = filedialog.askopenfilename(
            title="Chọn file FFmpeg",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if file_path:
            self.ffmpeg_path_var.set(file_path)
    
    def save_settings(self):
        """Lưu cài đặt"""
        try:
            self.config.set('download.resolution', self.resolution_var.get())
            self.config.set('download.output_path', self.download_folder_var.get())
            self.config.set('processing.output_path', self.process_folder_var.get())
            self.config.set('ffmpeg.path', self.ffmpeg_path_var.get())
            self.config.set('download.youtube_api_key', self.youtube_api_key_var.get())
            
            # Cập nhật lại downloader và YouTube API theo cài đặt mới
            self.downloader.reload_settings()
            self.youtube_api = YouTubeAPIService(self.config.get('download.youtube_api_key'))
            self.update_youtube_api_status()
            
            messagebox.showinfo("Thành công", "Đã lưu cài đặt")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi lưu cài đặt: {e}")
    
    def reset_settings(self):
        """Reset cài đặt"""
        self.resolution_var.set('1080p')
        self.download_folder_var.set('data/videos')
        self.process_folder_var.set('data/processed')
        self.ffmpeg_path_var.set('tools/ffmpeg.exe')
        self.youtube_api_key_var.set('')
        messagebox.showinfo("Thông báo", "Đã reset cài đặt về mặc định")
    
    def show_channel_context_menu(self, event):
        """Hiển thị menu chuột phải cho danh sách video"""
        try:
            self.channel_context_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            Logger.log_error(f"Lỗi hiển thị menu: {e}")
    
    def delete_selected_channel_videos(self):
        """Xóa các video đã chọn khỏi danh sách"""
        # Xóa theo các dòng đang được chọn trên Treeview
        selection = [int(self.channel_tree.index(iid)) for iid in self.channel_tree.selection()]
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn video để xóa")
            return
        
        # Xác nhận trước khi xóa
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa {len(selection)} video đã chọn?"):
            try:
                # Xóa theo thứ tự ngược để không ảnh hưởng đến index
                for index in reversed(selection):
                    if 0 <= index < len(self.channel_videos):
                        self.channel_videos.pop(index)
                
                # Cập nhật lại số thứ tự
                self.refresh_channel_list_display()
                messagebox.showinfo("Thành công", f"Đã xóa {len(selection)} video khỏi danh sách")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi xóa video: {e}")
    
    def delete_all_channel_videos(self):
        """Xóa tất cả video khỏi danh sách"""
        if not self.channel_videos:
            messagebox.showwarning("Cảnh báo", "Danh sách video đã trống")
            return
        
        # Xác nhận trước khi xóa
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa tất cả {len(self.channel_videos)} video?"):
            try:
                self.channel_videos.clear()
                self.refresh_channel_list_display()
                messagebox.showinfo("Thành công", "Đã xóa tất cả video khỏi danh sách")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi xóa video: {e}")
    
    def select_all_channel_videos(self):
        """Chọn tất cả video trong danh sách"""
        for i in range(len(self.channel_videos)):
            self.channel_videos[i]['selected'] = True
            self.update_tree_row(i)
    
    def deselect_all_channel_videos(self):
        """Bỏ chọn tất cả video trong danh sách"""
        for i in range(len(self.channel_videos)):
            self.channel_videos[i]['selected'] = False
            self.update_tree_row(i)
    
    def refresh_channel_list_display(self):
        """Làm mới hiển thị Treeview theo dữ liệu hiện tại"""
        for iid in self.channel_tree.get_children():
            self.channel_tree.delete(iid)
        for i, v in enumerate(self.channel_videos, 1):
            title = v.get('title') or v.get('id') or 'Untitled'
            dur = v.get('duration') or 0
            prog = v.get('progress', 0.0)
            selected = '✓' if v.get('selected', True) else ''
            self.channel_tree.insert('', tk.END, values=(f"{i:02d}", f"{title} ({dur}s)", f"{prog:.0f}%", selected))

    def update_row_progress(self, index: int, percent: float):
        """Cập nhật phần trăm cho một dòng"""
        if 0 <= index < len(self.channel_videos):
            try:
                self.channel_videos[index]['progress'] = max(0.0, min(100.0, float(percent)))
                self.update_tree_row(index)
            except Exception:
                pass

    def update_tree_row(self, index: int):
        """Cập nhật lại một dòng trong Treeview theo index"""
        if 0 <= index < len(self.channel_videos):
            # Xóa dòng cũ và chèn lại tại vị trí tương ứng
            children = self.channel_tree.get_children()
            if index < len(children):
                self.channel_tree.delete(children[index])
            v = self.channel_videos[index]
            title = v.get('title') or v.get('id') or 'Untitled'
            dur = v.get('duration') or 0
            prog = v.get('progress', 0.0)
            selected = '✓' if v.get('selected', True) else ''
            self.channel_tree.insert('', index, values=(f"{index+1:02d}", f"{title} ({dur}s)", f"{prog:.0f}%", selected))
    
    # ==================== YOUTUBE TAB METHODS ====================
    
    def update_youtube_api_status(self):
        """Cập nhật trạng thái YouTube API"""
        if self.youtube_api.is_available():
            self.api_status_var.set("✅ YouTube API: Sẵn sàng")
            self.api_status_label.config(foreground="green")
        else:
            self.api_status_var.set("❌ YouTube API: Chưa cấu hình API key")
            self.api_status_label.config(foreground="red")
    
    def test_youtube_api(self):
        """Test kết nối YouTube API"""
        def test_thread():
            try:
                self.update_status("Đang test YouTube API...")
                success = self.youtube_api.test_api_connection()
                
                if success:
                    self.root.after(0, messagebox.showinfo, "Thành công", "YouTube API hoạt động bình thường!")
                    self.root.after(0, self.update_youtube_api_status)
                else:
                    self.root.after(0, messagebox.showerror, "Lỗi", "YouTube API không hoạt động. Kiểm tra API key trong Settings.")
                
            except Exception as e:
                self.root.after(0, messagebox.showerror, "Lỗi", f"Lỗi test API: {e}")
            finally:
                self.root.after(0, self.update_status, "Sẵn sàng")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def fetch_youtube_channel_list(self):
        """Lấy danh sách video YouTube channel"""
        url = self.youtube_url_var.get().strip()
        if not url:
            messagebox.showerror("Lỗi", "Vui lòng nhập URL kênh YouTube")
            return
        
        if not self.youtube_api.is_available():
            messagebox.showerror("Lỗi", "YouTube API chưa được cấu hình. Vui lòng thêm API key trong Settings.")
            return
        
        def fetch_thread():
            try:
                self.update_status("Đang lấy thông tin channel...")
                
                # Lấy thông tin channel
                channel_info = self.youtube_api.get_channel_info(url)
                if channel_info:
                    def update_channel_info():
                        self.youtube_info_text.delete(1.0, tk.END)
                        self.youtube_info_text.insert(tk.END, f"Tên: {channel_info['title']}\n")
                        self.youtube_info_text.insert(tk.END, f"Subscribers: {channel_info['subscriber_count']:,}\n")
                        self.youtube_info_text.insert(tk.END, f"Videos: {channel_info['video_count']:,}\n")
                        self.youtube_info_text.insert(tk.END, f"Views: {channel_info['view_count']:,}\n")
                    self.root.after(0, update_channel_info)
                
                self.update_status("Đang lấy danh sách video...")
                max_videos = int(self.youtube_count_var.get())
                
                # Thử YouTube API trước
                videos = self.youtube_api.get_channel_videos(url, max_results=max_videos)
                
                # Nếu YouTube API trả về ít video hơn mong muốn, thử yt-dlp
                if len(videos) < max_videos * 0.8:  # Nếu ít hơn 80% số video mong muốn
                    Logger.log_info("YouTube API trả về ít video, thử yt-dlp...")
                    try:
                        yt_dlp_videos = self.downloader.list_channel_videos(url)
                        if yt_dlp_videos and len(yt_dlp_videos) > len(videos):
                            Logger.log_info(f"yt-dlp tìm thấy {len(yt_dlp_videos)} video, sử dụng kết quả này")
                            # Chuyển đổi format từ yt-dlp sang YouTube API format
                            videos = []
                            for i, video in enumerate(yt_dlp_videos[:max_videos]):
                                videos.append({
                                    'id': video.get('id', f'video_{i}'),
                                    'title': video.get('title', 'Unknown'),
                                    'description': video.get('description', ''),
                                    'url': video.get('url', ''),
                                    'thumbnail': video.get('thumbnail', ''),
                                    'published_at': video.get('upload_date', ''),
                                    'duration': video.get('duration', 0),
                                    'view_count': video.get('view_count', 0),
                                    'like_count': 0,
                                    'comment_count': 0
                                })
                    except Exception as e:
                        Logger.log_warning(f"yt-dlp fallback thất bại: {e}")
                
                # Khởi tạo thêm thuộc tính 'selected' và 'progress' cho mỗi video
                self.youtube_videos = [{**v, 'selected': True, 'progress': 0.0} for v in videos]
                
                def update_ui():
                    self.refresh_youtube_list_display()
                    self.update_status(f"Đã lấy {len(videos)} video")
                    self.update_youtube_progress(0)
                self.root.after(0, update_ui)
                
            except Exception as e:
                self.root.after(0, messagebox.showerror, "Lỗi", f"Không lấy được danh sách: {e}")
                self.root.after(0, self.update_status, "Sẵn sàng")
        
        threading.Thread(target=fetch_thread, daemon=True).start()
    
    def download_youtube_videos(self, selected_only: bool):
        """Tải các video YouTube đã chọn"""
        if not self.youtube_videos:
            messagebox.showwarning("Cảnh báo", "Chưa có danh sách video để tải")
            return
        
        if selected_only:
            indices = [i for i, v in enumerate(self.youtube_videos) if v.get('selected')]
        else:
            indices = list(range(len(self.youtube_videos)))
        
        if not indices:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn video để tải")
            return
        
        def batch_thread():
            try:
                import time
                total = len(indices)
                successful_downloads = 0
                self.update_status(f"Đang tải danh sách YouTube ({total} video)...")
                
                for idx_pos, idx in enumerate(indices, start=1):
                    video = self.youtube_videos[idx]
                    url = video.get('url')
                    title = video.get('title') or video.get('id')
                    
                    # Cập nhật tiến trình tổng
                    self.root.after(0, self.update_youtube_progress, (idx_pos-1) * 100.0 / total)
                    self.root.after(0, self.update_youtube_row_progress, idx, 0.0)
                    
                    # Thử tải với retry
                    success = False
                    for retry in range(3):
                        try:
                            def hook(d):
                                try:
                                    status = d.get('status')
                                    file_percent = None
                                    if status == 'downloading':
                                        downloaded = d.get('downloaded_bytes') or 0
                                        t = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                                        if t:
                                            file_percent = downloaded * 100.0 / float(t)
                                        else:
                                            fi = d.get('fragment_index') or 0
                                            fc = d.get('fragment_count') or 0
                                            if fc:
                                                file_percent = fi * 100.0 / float(fc)
                                    elif status == 'finished':
                                        file_percent = 100.0
                                    if file_percent is not None:
                                        overall = (idx_pos-1) * 100.0 / total + (file_percent / total)
                                        self.root.after(0, self.update_youtube_progress, overall)
                                        self.root.after(0, self.update_youtube_row_progress, idx, file_percent)
                                except Exception:
                                    pass
                            
                            result = self.downloader.download_video(url, custom_filename=None, progress_hook=hook)
                            if result:
                                success = True
                                successful_downloads += 1
                                self.root.after(0, self.update_youtube_row_progress, idx, 100.0)
                                break
                            else:
                                if retry < 2:
                                    self.root.after(0, self.update_youtube_row_progress, idx, 0.0)
                                    time.sleep(2)
                                    
                        except Exception as e:
                            if retry < 2:
                                time.sleep(2)
                            else:
                                self.root.after(0, self.update_youtube_row_progress, idx, 0.0)
                    
                    if not success:
                        self.root.after(0, self.update_youtube_row_progress, idx, 0.0)
                    
                    # Delay giữa các video
                    if idx_pos < total:
                        time.sleep(1)
                
                self.root.after(0, self.update_youtube_progress, 100.0)
                self.root.after(0, self.update_status, f"Hoàn tất: {successful_downloads}/{total} video thành công")
                
            except Exception as e:
                self.root.after(0, messagebox.showerror, "Lỗi", f"Lỗi tải danh sách: {e}")
                self.root.after(0, self.update_status, "Sẵn sàng")
        
        threading.Thread(target=batch_thread, daemon=True).start()
    
    def retry_failed_youtube_videos(self):
        """Tải lại video YouTube bị lỗi"""
        if not self.youtube_videos:
            messagebox.showwarning("Cảnh báo", "Chưa có danh sách video")
            return
        
        failed_indices = []
        for i, video in enumerate(self.youtube_videos):
            progress = video.get('progress', 0.0)
            if progress < 100.0:
                failed_indices.append(i)
                video['selected'] = True
        
        if not failed_indices:
            messagebox.showinfo("Thông báo", "Không có video nào bị lỗi")
            return
        
        for idx in failed_indices:
            self.update_youtube_tree_row(idx)
        
        messagebox.showinfo("Thông báo", f"Tìm thấy {len(failed_indices)} video lỗi, bắt đầu tải lại...")
        self.download_youtube_videos(selected_only=True)
    
    def on_youtube_tree_click(self, event):
        """Toggle trạng thái chọn ở cột 'Tải?' khi click"""
        try:
            region = self.youtube_tree.identify('region', event.x, event.y)
            if region != 'cell':
                return
            row_id = self.youtube_tree.identify_row(event.y)
            col = self.youtube_tree.identify_column(event.x)
            if not row_id or col != '#6':  # Cột 'selected' là cột thứ 6
                return
            idx = int(self.youtube_tree.index(row_id))
            if 0 <= idx < len(self.youtube_videos):
                self.youtube_videos[idx]['selected'] = not self.youtube_videos[idx].get('selected', True)
                self.update_youtube_tree_row(idx)
        except Exception:
            pass
    
    def show_youtube_context_menu(self, event):
        """Hiển thị menu chuột phải cho danh sách video YouTube"""
        try:
            self.youtube_context_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            Logger.log_error(f"Lỗi hiển thị menu: {e}")
    
    def delete_selected_youtube_videos(self):
        """Xóa các video YouTube đã chọn khỏi danh sách"""
        selection = [int(self.youtube_tree.index(iid)) for iid in self.youtube_tree.selection()]
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn video để xóa")
            return
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa {len(selection)} video đã chọn?"):
            try:
                for index in reversed(selection):
                    if 0 <= index < len(self.youtube_videos):
                        self.youtube_videos.pop(index)
                
                self.refresh_youtube_list_display()
                messagebox.showinfo("Thành công", f"Đã xóa {len(selection)} video khỏi danh sách")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi xóa video: {e}")
    
    def delete_all_youtube_videos(self):
        """Xóa tất cả video YouTube khỏi danh sách"""
        if not self.youtube_videos:
            messagebox.showwarning("Cảnh báo", "Danh sách video đã trống")
            return
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa tất cả {len(self.youtube_videos)} video?"):
            try:
                self.youtube_videos.clear()
                self.refresh_youtube_list_display()
                messagebox.showinfo("Thành công", "Đã xóa tất cả video khỏi danh sách")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi xóa video: {e}")
    
    def select_all_youtube_videos(self):
        """Chọn tất cả video YouTube trong danh sách"""
        for i in range(len(self.youtube_videos)):
            self.youtube_videos[i]['selected'] = True
            self.update_youtube_tree_row(i)
    
    def deselect_all_youtube_videos(self):
        """Bỏ chọn tất cả video YouTube trong danh sách"""
        for i in range(len(self.youtube_videos)):
            self.youtube_videos[i]['selected'] = False
            self.update_youtube_tree_row(i)
    
    def refresh_youtube_list_display(self):
        """Làm mới hiển thị Treeview YouTube theo dữ liệu hiện tại"""
        for iid in self.youtube_tree.get_children():
            self.youtube_tree.delete(iid)
        for i, v in enumerate(self.youtube_videos, 1):
            title = v.get('title') or v.get('id') or 'Untitled'
            duration = v.get('duration') or 0
            views = v.get('view_count') or 0
            prog = v.get('progress', 0.0)
            selected = '✓' if v.get('selected', True) else ''
            
            # Format duration
            dur_str = f"{duration//60}:{duration%60:02d}" if duration > 0 else "0:00"
            # Format views
            views_str = f"{views:,}" if views > 0 else "0"
            
            self.youtube_tree.insert('', tk.END, values=(
                f"{i:02d}", 
                title[:60] + "..." if len(title) > 60 else title,
                dur_str,
                views_str,
                f"{prog:.0f}%", 
                selected
            ))
    
    def update_youtube_row_progress(self, index: int, percent: float):
        """Cập nhật phần trăm cho một dòng YouTube"""
        if 0 <= index < len(self.youtube_videos):
            try:
                self.youtube_videos[index]['progress'] = max(0.0, min(100.0, float(percent)))
                self.update_youtube_tree_row(index)
            except Exception:
                pass
    
    def update_youtube_tree_row(self, index: int):
        """Cập nhật lại một dòng trong Treeview YouTube theo index"""
        if 0 <= index < len(self.youtube_videos):
            children = self.youtube_tree.get_children()
            if index < len(children):
                self.youtube_tree.delete(children[index])
            v = self.youtube_videos[index]
            title = v.get('title') or v.get('id') or 'Untitled'
            duration = v.get('duration') or 0
            views = v.get('view_count') or 0
            prog = v.get('progress', 0.0)
            selected = '✓' if v.get('selected', True) else ''
            
            dur_str = f"{duration//60}:{duration%60:02d}" if duration > 0 else "0:00"
            views_str = f"{views:,}" if views > 0 else "0"
            
            self.youtube_tree.insert('', index, values=(
                f"{index+1:02d}", 
                title[:60] + "..." if len(title) > 60 else title,
                dur_str,
                views_str,
                f"{prog:.0f}%", 
                selected
            ))
    
    def update_youtube_progress(self, percent: float):
        """Cập nhật tiến trình cho tab YouTube"""
        try:
            value = max(0, min(100, float(percent)))
        except Exception:
            value = 0.0
        self.youtube_progress['value'] = value
        self.youtube_progress_label.config(text=f"{value:.0f}%")
        self.root.update_idletasks()
    
    def run(self):
        """Chạy ứng dụng"""
        # Tạo thư mục cần thiết
        FileManager.ensure_dir('data/videos')
        FileManager.ensure_dir('data/processed')
        FileManager.ensure_dir('data/music')
        FileManager.ensure_dir('data/fonts')
        FileManager.ensure_dir('logs')
        
        # Làm mới danh sách file
        self.refresh_files_list()
        
        # Chạy ứng dụng
        self.root.mainloop()

if __name__ == "__main__":
    app = TikTokReupApp()
    app.run()
