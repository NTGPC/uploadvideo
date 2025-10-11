"""
TikTok Reup Offline - Ứng dụng offline để tải xuống, xử lý và upload video
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from pathlib import Path
from tkinter import font

# Thêm src vào path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils import ConfigManager, FileManager, Logger
from src.downloader import VideoDownloader
from src.youtube_api import YouTubeAPIService
from src.processor import VideoProcessor
from src.uploader import VideoUploader
from src.profile_manager import ProfileManager

class TikTokReupApp:
    """Giao diện chính của ứng dụng"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎬 TikTok Reup Offline")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        # Thiết lập theme và màu sắc
        self.setup_theme()
        
        # Khởi tạo các component
        self.config = ConfigManager()
        self.downloader = VideoDownloader(self.config)
        self.youtube_api = YouTubeAPIService(self.config.get('download.youtube_api_key'))
        self.processor = VideoProcessor(self.config)
        self.uploader = VideoUploader(self.config)
        self.profile_manager = ProfileManager()
        
        # Thiết lập logging
        Logger.setup_logging()
        
        # Tạo giao diện
        self.create_widgets()
        
        # Biến trạng thái
        self.is_processing = False
        self.downloaded_files = []
        self.processed_files = []
    
    def setup_theme(self):
        """Thiết lập theme và màu sắc cho ứng dụng"""
        # Màu sắc chính - Xanh lá cây đẹp mắt
        self.colors = {
            'primary': '#00b894',      # Green primary
            'primary_dark': '#00a085', # Dark green
            'primary_hover': '#00cec9', # Teal hover
            'secondary': '#55efc4',    # Light green
            'secondary_dark': '#00b894', # Green secondary
            'success': '#00b894',      # Green success
            'success_dark': '#00a085', # Dark green success
            'warning': '#fdcb6e',      # Orange warning
            'warning_dark': '#e17055', # Orange warning dark
            'danger': '#e17055',       # Orange danger
            'danger_dark': '#d63031',  # Red danger dark
            'info': '#74b9ff',         # Blue info
            'info_dark': '#0984e3',    # Dark blue info
            'light': '#f8f9fa',        # Very light gray
            'light_hover': '#e8f5e8',  # Light green hover
            'dark': '#00b894',         # Green text
            'gray': '#636e72',         # Medium gray
            'white': '#ffffff',
            'black': '#00b894',         # Green text
            'gradient_start': '#00b894',
            'gradient_end': '#00cec9',
            'text_primary': '#00b894',  # Green text
            'text_secondary': '#00a085' # Dark green text
        }
        
        # Cấu hình style cho ttk
        style = ttk.Style()
        
        # Cấu hình Notebook với tab màu vàng khi active
        style.configure('TNotebook', 
                       background=self.colors['light'],
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', '#ffd700'),  # Màu vàng khi active
                           ('active', '#ffd700')],    # Màu vàng khi hover
                 foreground=[('selected', self.colors['dark']),  # Chữ đen khi active
                           ('active', self.colors['dark'])])    # Chữ đen khi hover
        
        # Cấu hình Frame
        style.configure('Card.TFrame',
                       background=self.colors['white'],
                       relief='flat',
                       borderwidth=1)
        
        # Cấu hình LabelFrame - sử dụng style mặc định để tránh lỗi chồng text
        style.configure('Card.TLabelFrame',
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 11, 'bold'),
                       relief='flat',
                       borderwidth=1)
        style.configure('Card.TLabelFrame.Label',
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 11, 'bold'))
        
        # Cấu hình Button với chữ màu xanh lá cây
        style.configure('Primary.TButton',
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10, 'bold'),
                       relief='flat',
                       borderwidth=2,
                       padding=[15, 10])
        style.map('Primary.TButton',
                 background=[('active', self.colors['light_hover']),
                           ('pressed', self.colors['light_hover']),
                           ('hover', self.colors['light_hover'])],
                 foreground=[('active', self.colors['text_primary']),
                           ('pressed', self.colors['text_primary']),
                           ('hover', self.colors['text_primary'])],
                 bordercolor=[('active', self.colors['text_primary']),
                             ('pressed', self.colors['text_primary']),
                             ('hover', self.colors['text_primary'])])
        
        style.configure('Success.TButton',
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10, 'bold'),
                       relief='flat',
                       borderwidth=2,
                       padding=[15, 10])
        style.map('Success.TButton',
                 background=[('active', self.colors['light_hover']),
                           ('pressed', self.colors['light_hover']),
                           ('hover', self.colors['light_hover'])],
                 foreground=[('active', self.colors['text_primary']),
                           ('pressed', self.colors['text_primary']),
                           ('hover', self.colors['text_primary'])],
                 bordercolor=[('active', self.colors['text_primary']),
                             ('pressed', self.colors['text_primary']),
                             ('hover', self.colors['text_primary'])])
        
        style.configure('Danger.TButton',
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10, 'bold'),
                       relief='flat',
                       borderwidth=2,
                       padding=[15, 10])
        style.map('Danger.TButton',
                 background=[('active', self.colors['light_hover']),
                           ('pressed', self.colors['light_hover']),
                           ('hover', self.colors['light_hover'])],
                 foreground=[('active', self.colors['text_primary']),
                           ('pressed', self.colors['text_primary']),
                           ('hover', self.colors['text_primary'])],
                 bordercolor=[('active', self.colors['text_primary']),
                             ('pressed', self.colors['text_primary']),
                             ('hover', self.colors['text_primary'])])
        
        style.configure('Info.TButton',
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10, 'bold'),
                       relief='flat',
                       borderwidth=2,
                       padding=[15, 10])
        style.map('Info.TButton',
                 background=[('active', self.colors['light_hover']),
                           ('pressed', self.colors['light_hover']),
                           ('hover', self.colors['light_hover'])],
                 foreground=[('active', self.colors['text_primary']),
                           ('pressed', self.colors['text_primary']),
                           ('hover', self.colors['text_primary'])],
                 bordercolor=[('active', self.colors['text_primary']),
                             ('pressed', self.colors['text_primary']),
                             ('hover', self.colors['text_primary'])])
        
        # Cấu hình Entry với chữ màu xanh lá cây
        style.configure('Modern.TEntry',
                       fieldbackground=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10),
                       relief='flat',
                       borderwidth=2,
                       padding=[12, 10])
        style.map('Modern.TEntry',
                 fieldbackground=[('focus', self.colors['light']),
                                ('hover', self.colors['light_hover'])],
                 bordercolor=[('focus', self.colors['text_primary']),
                            ('hover', self.colors['text_primary'])],
                 foreground=[('focus', self.colors['text_primary']),
                           ('hover', self.colors['text_primary'])])
        
        # Cấu hình Progressbar với gradient
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['gradient_start'],
                       troughcolor=self.colors['light'],
                       borderwidth=0,
                       lightcolor=self.colors['gradient_end'],
                       darkcolor=self.colors['gradient_start'])
        
        # Cấu hình Treeview với hover effects
        style.configure('Modern.Treeview',
                       background=self.colors['white'],
                       foreground=self.colors['dark'],
                       font=('Segoe UI', 9),
                       relief='flat',
                       borderwidth=0,
                       rowheight=25)
        style.map('Modern.Treeview',
                 background=[('selected', self.colors['primary']),
                           ('hover', self.colors['light_hover'])],
                 foreground=[('selected', self.colors['white']),
                           ('hover', self.colors['dark'])])
        style.configure('Modern.Treeview.Heading',
                       background=self.colors['gradient_start'],
                       foreground=self.colors['white'],
                       font=('Segoe UI', 9, 'bold'),
                       relief='flat')
        style.map('Modern.Treeview.Heading',
                 background=[('active', self.colors['gradient_end']),
                           ('hover', self.colors['gradient_end'])])
        
        # Cấu hình Scrollbar
        style.configure('Modern.Vertical.TScrollbar',
                       background=self.colors['light'],
                       troughcolor=self.colors['light'],
                       borderwidth=0,
                       arrowcolor=self.colors['gray'],
                       darkcolor=self.colors['light'],
                       lightcolor=self.colors['light'])
        
        # Thiết lập màu nền cho root
        self.root.configure(bg=self.colors['light'])
    
    def create_widgets(self):
        """Tạo các widget giao diện"""
        # Tạo header với logo và title
        self.create_header()
        
        # Tạo notebook cho các tab
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
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
        
        # Tab Login Profile
        self.create_login_profile_tab()
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Tạo header với màu xanh lá cây"""
        header_frame = tk.Frame(self.root, bg=self.colors['white'], height=90)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Container với nền trắng
        gradient_frame = tk.Frame(header_frame, bg=self.colors['white'])
        gradient_frame.pack(expand=True, fill=tk.BOTH)
        
        # Icon và title với màu xanh lá cây
        title_label = tk.Label(gradient_frame, 
                              text="🎬 TikTok Reup Offline", 
                              font=('Segoe UI', 22, 'bold'),
                              fg=self.colors['text_primary'],
                              bg=self.colors['white'])
        title_label.pack(side=tk.LEFT, padx=25, pady=25)
        
        # Subtitle với màu xanh lá cây
        subtitle_label = tk.Label(gradient_frame,
                                 text="✨ Professional Video Processing Tool",
                                 font=('Segoe UI', 13),
                                 fg=self.colors['text_secondary'],
                                 bg=self.colors['white'])
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0), pady=25)
        
        # Version badge với màu xanh lá cây
        version_frame = tk.Frame(gradient_frame, bg=self.colors['white'], relief='raised', bd=2)
        version_frame.pack(side=tk.RIGHT, padx=25, pady=20)
        version_label = tk.Label(version_frame,
                                text="v2.0",
                                font=('Segoe UI', 11, 'bold'),
                                fg=self.colors['text_primary'],
                                bg=self.colors['white'],
                                padx=12,
                                pady=6)
        version_label.pack()
    
    def create_download_tab(self):
        """Tạo tab Download"""
        download_frame = ttk.Frame(self.notebook, style='Card.TFrame')
        self.notebook.add(download_frame, text="📥 Download")
        
        # URL input
        url_frame = ttk.LabelFrame(download_frame, text="🔗 URL Video", padding=15)
        url_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # URL input container
        url_input_frame = tk.Frame(url_frame, bg=self.colors['white'])
        url_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_input_frame, textvariable=self.url_var, 
                            style='Modern.TEntry', width=80)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.download_btn = ttk.Button(url_input_frame, text="⬇️ Download", 
                                     style='Primary.TButton',
                                     command=self.download_video)
        self.download_btn.pack(side=tk.RIGHT)
        
        # Video info
        info_frame = ttk.LabelFrame(download_frame, text="📊 Thông tin Video", padding=15)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Text container
        text_container = tk.Frame(info_frame, bg=self.colors['white'])
        text_container.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(text_container, height=10, wrap=tk.WORD,
                               font=('Consolas', 9),
                               bg=self.colors['light'],
                               fg=self.colors['dark'],
                               relief='flat',
                               borderwidth=0)
        info_scrollbar = ttk.Scrollbar(text_container, orient=tk.VERTICAL, 
                                     command=self.info_text.yview,
                                     style='Modern.Vertical.TScrollbar')
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)
        
        # Downloaded files list
        files_frame = ttk.LabelFrame(download_frame, text="📁 Files đã tải", padding=15)
        files_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Files list container
        files_container = tk.Frame(files_frame, bg=self.colors['white'])
        files_container.pack(fill=tk.X, pady=(5, 0))
        
        self.files_listbox = tk.Listbox(files_container, height=6,
                                      font=('Segoe UI', 9),
                                      bg=self.colors['light'],
                                      fg=self.colors['dark'],
                                      relief='flat',
                                      borderwidth=0,
                                      selectbackground=self.colors['primary'],
                                      selectforeground=self.colors['white'])
        files_scrollbar = ttk.Scrollbar(files_container, orient=tk.VERTICAL, 
                                      command=self.files_listbox.yview,
                                      style='Modern.Vertical.TScrollbar')
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = tk.Frame(files_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="🗑️ Xóa file", style='Danger.TButton',
                  command=self.delete_selected_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="📂 Mở thư mục", style='Info.TButton',
                  command=self.open_download_folder).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="🔄 Refresh", style='Success.TButton',
                  command=self.refresh_files_list).pack(side=tk.LEFT)

        # Progress bar
        progress_frame = ttk.LabelFrame(download_frame, text="📈 Tiến trình", padding=15)
        progress_frame.pack(fill=tk.X, padx=15, pady=10)
        
        progress_container = tk.Frame(progress_frame, bg=self.colors['white'])
        progress_container.pack(fill=tk.X, pady=(5, 0))
        
        self.download_progress = ttk.Progressbar(progress_container, 
                                               orient=tk.HORIZONTAL, 
                                               mode='determinate', 
                                               maximum=100,
                                               style='Modern.Horizontal.TProgressbar')
        self.download_progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.download_progress_label = tk.Label(progress_container, text="0%",
                                              font=('Segoe UI', 10, 'bold'),
                                              fg=self.colors['text_primary'],
                                              bg=self.colors['white'])
        self.download_progress_label.pack(side=tk.LEFT)

    def create_download_channel_tiktok_tab(self):
        """Tạo tab Download List Channel TikTok"""
        channel_frame = ttk.Frame(self.notebook, style='Card.TFrame')
        self.notebook.add(channel_frame, text="📚 TikTok Channel")
        
        # URL kênh
        url_frame = ttk.LabelFrame(channel_frame, text="🔗 URL Kênh/Playlist/Profile", padding=15)
        url_frame.pack(fill=tk.X, padx=15, pady=10)
        
        url_input_frame = tk.Frame(url_frame, bg=self.colors['white'])
        url_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.channel_url_var = tk.StringVar()
        ttk.Entry(url_input_frame, textvariable=self.channel_url_var, 
                 style='Modern.TEntry', width=80).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        ttk.Button(url_input_frame, text="📋 Lấy danh sách", style='Primary.TButton',
                  command=self.fetch_channel_list).pack(side=tk.RIGHT)
        
        # Danh sách video (Treeview 4 cột)
        list_frame = ttk.LabelFrame(channel_frame, text="📋 Danh sách video", padding=15)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
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
        youtube_frame = ttk.Frame(self.notebook, style='Card.TFrame')
        self.notebook.add(youtube_frame, text="📺 YouTube Channel")
        
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
        process_frame = ttk.Frame(self.notebook, style='Card.TFrame')
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
        upload_frame = ttk.Frame(self.notebook, style='Card.TFrame')
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
        settings_frame = ttk.Frame(self.notebook, style='Card.TFrame')
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
        """Tạo status bar với màu xanh lá cây"""
        self.status_var = tk.StringVar(value="✅ Sẵn sàng")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                            font=('Segoe UI', 10, 'bold'),
                            fg=self.colors['text_primary'],
                            bg=self.colors['light_hover'],
                            anchor=tk.W,
                            padx=20,
                            pady=10)
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
    
    def create_login_profile_tab(self):
        """Tạo tab Login Profile"""
        # Tạo frame chính cho tab
        login_frame = ttk.Frame(self.notebook)
        self.notebook.add(login_frame, text="👤 Login Profile")
        
        # Tạo container chính
        main_container = tk.Frame(login_frame, bg=self.colors['light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section
        header_frame = tk.Frame(main_container, bg=self.colors['white'], relief=tk.RAISED, bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(header_frame, 
                              text="🔐 Login Profile Management", 
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text_primary'],
                              bg=self.colors['white'])
        title_label.pack(pady=15)
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Quản lý tài khoản đăng nhập cho các nền tảng",
                                 font=('Segoe UI', 10),
                                 fg=self.colors['gray'],
                                 bg=self.colors['white'])
        subtitle_label.pack(pady=(0, 15))
        
        # Control panel
        control_frame = tk.Frame(main_container, bg=self.colors['white'], relief=tk.RAISED, bd=1)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Add profile button
        add_btn = tk.Button(control_frame,
                           text="➕ Thêm Profile",
                           font=('Segoe UI', 10, 'bold'),
                           bg=self.colors['primary'],
                           fg='white',
                           relief=tk.FLAT,
                           padx=20,
                           pady=10,
                           command=self.add_login_profile)
        add_btn.pack(side=tk.LEFT, padx=15, pady=15)
        
        # Import profiles button
        import_btn = tk.Button(control_frame,
                              text="📥 Import Profiles",
                              font=('Segoe UI', 10, 'bold'),
                              bg=self.colors['info'],
                              fg='white',
                              relief=tk.FLAT,
                              padx=20,
                              pady=10,
                              command=self.import_login_profiles)
        import_btn.pack(side=tk.LEFT, padx=10, pady=15)
        
        # Export profiles button
        export_btn = tk.Button(control_frame,
                              text="📤 Export Profiles",
                              font=('Segoe UI', 10, 'bold'),
                              bg=self.colors['warning'],
                              fg='white',
                              relief=tk.FLAT,
                              padx=20,
                              pady=10,
                              command=self.export_login_profiles)
        export_btn.pack(side=tk.LEFT, padx=10, pady=15)
        
        # Refresh button
        refresh_btn = tk.Button(control_frame,
                               text="🔄 Refresh",
                               font=('Segoe UI', 10, 'bold'),
                               bg=self.colors['secondary'],
                               fg='white',
                               relief=tk.FLAT,
                               padx=20,
                               pady=10,
                               command=self.refresh_login_profiles)
        refresh_btn.pack(side=tk.RIGHT, padx=15, pady=15)
        
        # Profiles table
        table_frame = tk.Frame(main_container, bg=self.colors['white'], relief=tk.RAISED, bd=1)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Table header
        header_table_frame = tk.Frame(table_frame, bg=self.colors['light'])
        header_table_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Column headers
        headers = ["Username", "Platform", "Status", "Last Login", "Notes", "Actions"]
        for i, header in enumerate(headers):
            header_label = tk.Label(header_table_frame,
                                   text=header,
                                   font=('Segoe UI', 10, 'bold'),
                                   fg=self.colors['text_primary'],
                                   bg=self.colors['light'])
            if i == 0:
                header_label.pack(side=tk.LEFT, padx=(0, 20))
            elif i == len(headers) - 1:
                header_label.pack(side=tk.RIGHT, padx=(20, 0))
            else:
                header_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Separator
        separator = tk.Frame(table_frame, height=2, bg=self.colors['primary'])
        separator.pack(fill=tk.X, padx=10)
        
        # Scrollable frame for profiles
        canvas = tk.Canvas(table_frame, bg=self.colors['white'])
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['white'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Load profiles from ProfileManager
        profiles_data = self.profile_manager.get_all_profiles()
        
        # Create profile rows
        for i, profile in enumerate(profiles_data):
            self.create_profile_row(scrollable_frame, profile, i)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Store references
        self.login_canvas = canvas
        self.login_scrollable_frame = scrollable_frame
    
    def create_profile_row(self, parent, profile, row_index):
        """Tạo một hàng profile trong bảng"""
        row_frame = tk.Frame(parent, bg=self.colors['white'], relief=tk.RIDGE, bd=1)
        row_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Username
        username_label = tk.Label(row_frame,
                                 text=profile['username'],
                                 font=('Segoe UI', 9),
                                 fg=self.colors['text_primary'],
                                 bg=self.colors['white'],
                                 anchor='w')
        username_label.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        # Platform
        platform_label = tk.Label(row_frame,
                                  text=profile['platform'],
                                  font=('Segoe UI', 9),
                                  fg=self.colors['info'],
                                  bg=self.colors['white'])
        platform_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Status
        status_color = self.colors['success'] if profile['status'] == 'Active' else \
                      self.colors['warning'] if profile['status'] == 'Pending' else \
                      self.colors['danger']
        
        status_label = tk.Label(row_frame,
                               text=profile['status'],
                               font=('Segoe UI', 9, 'bold'),
                               fg=status_color,
                               bg=self.colors['white'])
        status_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Last Login
        last_login_label = tk.Label(row_frame,
                                   text=profile['last_login'],
                                   font=('Segoe UI', 9),
                                   fg=self.colors['gray'],
                                   bg=self.colors['white'])
        last_login_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Notes
        notes_label = tk.Label(row_frame,
                              text=profile['notes'],
                              font=('Segoe UI', 9),
                              fg=self.colors['gray'],
                              bg=self.colors['white'])
        notes_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Actions
        actions_frame = tk.Frame(row_frame, bg=self.colors['white'])
        actions_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Open Profile button
        open_btn = tk.Button(actions_frame,
                            text="Mở Profile",
                            font=('Segoe UI', 8, 'bold'),
                            bg=self.colors['primary'],
                            fg='white',
                            relief=tk.FLAT,
                            padx=10,
                            pady=5,
                            command=lambda: self.open_chrome_profile(profile))
        open_btn.pack(side=tk.LEFT, padx=2)
        
        # Delete button
        delete_btn = tk.Button(actions_frame,
                              text="Delete",
                              font=('Segoe UI', 8, 'bold'),
                              bg=self.colors['danger'],
                              fg='white',
                              relief=tk.FLAT,
                              padx=10,
                              pady=5,
                              command=lambda: self.delete_profile(profile))
        delete_btn.pack(side=tk.LEFT, padx=2)
    
    def add_login_profile(self):
        """Thêm profile mới"""
        self.show_add_profile_dialog()
    
    def import_login_profiles(self):
        """Import profiles từ file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Chọn file JSON để import",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                if self.profile_manager.import_profiles(file_path):
                    messagebox.showinfo("Thành công", "Import profiles thành công!")
                    self.refresh_login_profiles()
                else:
                    messagebox.showerror("Lỗi", "Không thể import profiles!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi import: {str(e)}")
    
    def export_login_profiles(self):
        """Export profiles ra file"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Lưu file JSON",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                if self.profile_manager.export_profiles(file_path):
                    messagebox.showinfo("Thành công", f"Export profiles thành công!\nFile: {file_path}")
                else:
                    messagebox.showerror("Lỗi", "Không thể export profiles!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi export: {str(e)}")
    
    def refresh_login_profiles(self):
        """Làm mới danh sách profiles"""
        try:
            # Xóa tất cả rows cũ
            for widget in self.login_scrollable_frame.winfo_children():
                widget.destroy()
            
            # Load lại dữ liệu
            profiles_data = self.profile_manager.get_all_profiles()
            
            # Tạo lại rows
            for i, profile in enumerate(profiles_data):
                self.create_profile_row(self.login_scrollable_frame, profile, i)
            
            # Cập nhật canvas
            self.login_canvas.update_idletasks()
            self.login_canvas.configure(scrollregion=self.login_canvas.bbox("all"))
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể refresh profiles: {str(e)}")
    
    def open_chrome_profile(self, profile):
        """Mở Chrome profile với cải tiến từ phân tích GoLogin"""
        try:
            import subprocess
            import os
            import stat
            import time
            from pathlib import Path
            
            # Lấy thông tin profile từ database
            profile_id = profile['id']
            username = profile['username']
            platform = profile['platform']
            profile_dir_name = profile['profile_dir']
            
            # Tạo đường dẫn profile directory (giống GoLogin)
            profile_dir = Path(f"data/profiles/{profile_dir_name}")
            
            # Đảm bảo thư mục gốc tồn tại
            profiles_root = Path("data/profiles")
            profiles_root.mkdir(parents=True, exist_ok=True)
            
            # Tạo thư mục profile với cấu trúc giống Chrome
            try:
                profile_dir.mkdir(parents=True, exist_ok=True)
                
                # Tạo cấu trúc thư mục con giống Chrome
                default_profile_dir = profile_dir / "Default"
                default_profile_dir.mkdir(exist_ok=True)
                
                # Cấp quyền đầy đủ cho thư mục (Windows)
                if os.name == 'nt':
                    os.chmod(profile_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    os.chmod(default_profile_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    
            except PermissionError:
                messagebox.showerror("Lỗi quyền truy cập", 
                                   f"Không thể tạo thư mục profile.\n"
                                   f"Vui lòng chạy ứng dụng với quyền Administrator\n"
                                   f"hoặc cấp quyền cho thư mục: {profile_dir}")
                return
            
            # Tìm Chrome executable với nhiều đường dẫn hơn
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME')),
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERPROFILE').split('\\')[-1]),
                r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe",
                r"C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
            ]
            
            chrome_exe = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_exe = path
                    break
            
            if not chrome_exe:
                messagebox.showerror("Lỗi", 
                                   "Không tìm thấy Chrome browser!\n"
                                   "Vui lòng cài đặt Google Chrome từ:\n"
                                   "https://www.google.com/chrome/")
                return
            
            # Kiểm tra và đóng Chrome instances cũ (nếu cần)
            self._cleanup_chrome_instances()
            
            # Xác định URL mở mặc định dựa trên platform
            platform_urls = {
                'TikTok': 'https://www.tiktok.com',
                'Instagram': 'https://www.instagram.com',
                'Facebook': 'https://www.facebook.com',
                'YouTube': 'https://www.youtube.com',
                'Twitter': 'https://twitter.com'
            }
            default_url = platform_urls.get(platform, 'https://www.google.com')
            
            # Tạo lệnh Chrome với các tham số tối ưu (giống GoLogin)
            cmd = [
                chrome_exe,
                f"--user-data-dir={profile_dir.absolute()}",
                "--profile-directory=Default",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-extensions-except",
                "--disable-plugins-discovery",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--disable-sync",
                "--disable-translate",
                "--disable-ipc-flooding-protection",
                "--disable-hang-monitor",
                "--disable-prompt-on-repost",
                "--disable-domain-reliability",
                "--disable-client-side-phishing-detection",
                "--disable-component-extensions-with-background-pages",
                "--disable-background-networking",
                "--disable-sync-preferences",
                "--disable-default-apps",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",
                "--disable-javascript",
                "--disable-plugins-discovery",
                "--disable-preconnect",
                "--disable-print-preview",
                "--disable-save-password-bubble",
                "--disable-single-click-autofill",
                "--disable-speech-api",
                "--disable-web-resources",
                "--disable-xss-auditor",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--remote-debugging-port=0",  # Random port để tránh conflict
                "--window-size=1366,768",
                "--start-maximized",
                default_url
            ]
            
            # Chạy Chrome trong thread riêng để không block UI
            def run_chrome():
                try:
                    # Chạy Chrome với subprocess
                    process = subprocess.Popen(
                        cmd, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                    )
                    
                    # Đợi một chút để Chrome khởi động
                    time.sleep(3)
                    
                    # Kiểm tra Chrome có chạy thành công không
                    if process.poll() is None:
                        # Chrome đang chạy thành công
                        self.root.after(0, lambda: self._show_success_message(profile, profile_dir))
                    else:
                        # Chrome đã thoát, có thể có lỗi
                        self.root.after(0, lambda: self._show_chrome_error())
                        
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Không thể khởi chạy Chrome: {str(e)}"))
            
            # Chạy Chrome trong background thread
            threading.Thread(target=run_chrome, daemon=True).start()
            
            # Cập nhật last login trong database
            self.profile_manager.update_last_login(profile_id)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở Chrome profile: {str(e)}")
    
    def _cleanup_chrome_instances(self):
        """Dọn dẹp các Chrome instances cũ nếu cần"""
        try:
            import subprocess
            # Kiểm tra Chrome đang chạy
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq chrome.exe'], 
                                  capture_output=True, text=True)
            if 'chrome.exe' in result.stdout:
                # Có thể đóng Chrome cũ hoặc để nguyên (tùy chọn)
                # subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True)
                pass
        except:
            pass  # Bỏ qua lỗi
    
    def _show_success_message(self, profile, profile_dir):
        """Hiển thị thông báo thành công"""
        messagebox.showinfo("✅ Thành công", 
                          f"Đã mở Chrome profile thành công!\n\n"
                          f"👤 Username: {profile['username']}\n"
                          f"🌐 Platform: {profile['platform']}\n"
                          f"📁 Profile dir: {profile_dir}\n\n"
                          f"Chrome đang chạy độc lập với profile chính của bạn.")
    
    def _show_chrome_error(self):
        """Hiển thị lỗi Chrome"""
        messagebox.showerror("❌ Lỗi Chrome", 
                           "Chrome không thể khởi động!\n\n"
                           "Có thể do:\n"
                           "• Chrome đang chạy với profile khác\n"
                           "• Không đủ quyền truy cập\n"
                           "• Chrome bị lỗi\n\n"
                           "Vui lòng thử lại sau vài giây.")
    
    def delete_profile(self, profile):
        """Xóa profile"""
        result = messagebox.askyesno("Xóa Profile", f"Bạn có chắc muốn xóa profile: {profile['username']}?")
        if result:
            try:
                if self.profile_manager.delete_profile(profile['id']):
                    messagebox.showinfo("Xóa Profile", f"Đã xóa profile: {profile['username']}")
                    # Refresh danh sách
                    self.refresh_login_profiles()
                else:
                    messagebox.showerror("Lỗi", "Không thể xóa profile!")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa profile: {str(e)}")
    
    def show_add_profile_dialog(self):
        """Hiển thị dialog thêm profile mới - Đơn giản và chắc chắn hiển thị"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Thêm Profile Mới")
        dialog.geometry("600x500")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"600x500+{x}+{y}")
        
        # Main container
        main_container = tk.Frame(dialog, bg=self.colors['light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.colors['white'], relief=tk.RAISED, bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame, 
                              text="➕ THÊM PROFILE MỚI",
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors['text_primary'],
                              bg=self.colors['white'])
        title_label.pack(pady=15)
        
        # Định nghĩa hàm save_profile trước
        def save_profile():
            try:
                username = username_entry.get().strip()
                password = password_entry.get().strip()
                platform = platform_var.get()
                status = status_var.get()
                notes = notes_entry.get().strip()
                
                # Validation chi tiết
                if not username:
                    messagebox.showerror("❌ Lỗi", "Vui lòng nhập username/email!")
                    username_entry.focus()
                    return
                
                if not password:
                    messagebox.showerror("❌ Lỗi", "Vui lòng nhập password!")
                    password_entry.focus()
                    return
                
                # Kiểm tra độ dài password
                if len(password) < 6:
                    messagebox.showerror("❌ Lỗi", "Password phải có ít nhất 6 ký tự!")
                    password_entry.focus()
                    return
                
                # Kiểm tra email format cơ bản
                if '@' in username and '.' not in username.split('@')[1]:
                    messagebox.showerror("❌ Lỗi", "Email không hợp lệ!")
                    username_entry.focus()
                    return
                
                # Kiểm tra username đã tồn tại chưa
                if self.profile_manager.get_profile_by_username(username):
                    messagebox.showerror("❌ Lỗi", "Username này đã tồn tại!")
                    username_entry.focus()
                    return
                
                # Hiển thị loading
                save_btn.config(text="💾 Đang lưu...", state='disabled')
                header_save_btn.config(text="💾 Đang lưu...", state='disabled')
                status_label.config(text="Đang xử lý...", fg='#007bff')
                dialog.update()
                
                # Tạo profile data
                profile_data = {
                    'username': username,
                    'password': password,
                    'platform': platform,
                    'status': status,
                    'notes': notes
                }
                
                # Lưu profile
                if self.profile_manager.add_profile(profile_data):
                    messagebox.showinfo("✅ Thành công", f"Đã thêm profile mới!\nUsername: {username}\nPlatform: {platform}")
                    dialog.destroy()
                    self.refresh_login_profiles()
                else:
                    messagebox.showerror("❌ Lỗi", "Không thể thêm profile! Vui lòng thử lại.")
                    save_btn.config(text="💾 LƯU PROFILE", state='normal')
                    header_save_btn.config(text="💾 LƯU PROFILE", state='normal')
                    status_label.config(text="Lỗi khi lưu", fg='#dc3545')
                    
            except Exception as e:
                messagebox.showerror("❌ Lỗi", f"Lỗi không mong muốn: {str(e)}")
                save_btn.config(text="💾 LƯU PROFILE", state='normal')
                header_save_btn.config(text="💾 LƯU PROFILE", state='normal')
                status_label.config(text="Lỗi không mong muốn", fg='#dc3545')
        
        # Nút lưu lớn ở header
        header_save_btn = tk.Button(header_frame,
                                   text="💾 LƯU PROFILE",
                                   font=('Segoe UI', 14, 'bold'),
                                   bg='#28a745',
                                   fg='white',
                                   relief=tk.RAISED,
                                   bd=3,
                                   padx=30,
                                   pady=10,
                                   command=save_profile,
                                   cursor='hand2')
        header_save_btn.pack(pady=(0, 15))
        
        # Form container
        form_frame = tk.Frame(main_container, bg=self.colors['white'], relief=tk.RAISED, bd=1)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Form fields với grid layout để căn chỉnh đều
        fields_container = tk.Frame(form_frame, bg=self.colors['white'])
        fields_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Configure grid weights
        fields_container.grid_columnconfigure(1, weight=1)
        
        # Username field
        tk.Label(fields_container, text="👤 Username/Email:", 
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['white']).grid(row=0, column=0, sticky='w', pady=(0, 5))
        username_entry = tk.Entry(fields_container, font=('Segoe UI', 11))
        username_entry.grid(row=0, column=1, sticky='ew', pady=(0, 15), padx=(10, 0))
        
        # Password field
        tk.Label(fields_container, text="🔒 Password:", 
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['white']).grid(row=1, column=0, sticky='w', pady=(0, 5))
        password_entry = tk.Entry(fields_container, font=('Segoe UI', 11), show="*")
        password_entry.grid(row=1, column=1, sticky='ew', pady=(0, 15), padx=(10, 0))
        
        # Platform field
        tk.Label(fields_container, text="🌐 Platform:", 
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['white']).grid(row=2, column=0, sticky='w', pady=(0, 5))
        platform_var = tk.StringVar(value="TikTok")
        platform_combo = ttk.Combobox(fields_container, textvariable=platform_var, 
                                     values=["TikTok", "Instagram", "Facebook", "YouTube", "Twitter"],
                                     font=('Segoe UI', 11), state="readonly")
        platform_combo.grid(row=2, column=1, sticky='ew', pady=(0, 15), padx=(10, 0))
        
        # Status field
        tk.Label(fields_container, text="📊 Status:", 
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['white']).grid(row=3, column=0, sticky='w', pady=(0, 5))
        status_var = tk.StringVar(value="Active")
        status_combo = ttk.Combobox(fields_container, textvariable=status_var,
                                   values=["Active", "Pending", "Blocked", "Inactive"],
                                   font=('Segoe UI', 11), state="readonly")
        status_combo.grid(row=3, column=1, sticky='ew', pady=(0, 15), padx=(10, 0))
        
        # Notes field
        tk.Label(fields_container, text="📝 Notes:", 
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['white']).grid(row=4, column=0, sticky='w', pady=(0, 5))
        notes_entry = tk.Entry(fields_container, font=('Segoe UI', 11))
        notes_entry.grid(row=4, column=1, sticky='ew', pady=(0, 20), padx=(10, 0))
        
        # Buttons container - CHẮC CHẮN HIỂN THỊ
        buttons_container = tk.Frame(main_container, bg=self.colors['white'], relief=tk.RAISED, bd=2)
        buttons_container.pack(fill=tk.X, pady=(10, 0))
        
        buttons_frame = tk.Frame(buttons_container, bg=self.colors['white'])
        buttons_frame.pack(fill=tk.X, padx=20, pady=25)
        
        
        def cancel():
            dialog.destroy()
        
        # SAVE BUTTON - RẤT LỚN VÀ RÕ RÀNG
        save_btn = tk.Button(buttons_frame,
                            text="💾 LƯU PROFILE",
                            font=('Segoe UI', 16, 'bold'),
                            bg='#28a745',  # Màu xanh lá cây đậm
                            fg='white',
                            relief=tk.RAISED,
                            bd=4,
                            padx=50,
                            pady=25,
                            command=save_profile,
                            cursor='hand2',
                            width=15,
                            height=2)
        save_btn.pack(side=tk.LEFT, padx=(0, 30))
        
        # Status label để hiển thị trạng thái
        status_label = tk.Label(buttons_frame,
                               text="",
                               font=('Segoe UI', 10),
                               fg=self.colors['text_secondary'],
                               bg=self.colors['white'])
        status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # CANCEL BUTTON
        cancel_btn = tk.Button(buttons_frame,
                              text="❌ HỦY",
                              font=('Segoe UI', 16, 'bold'),
                              bg='#dc3545',  # Màu đỏ đậm
                              fg='white',
                              relief=tk.RAISED,
                              bd=4,
                              padx=50,
                              pady=25,
                              command=cancel,
                              cursor='hand2',
                              width=15,
                              height=2)
        cancel_btn.pack(side=tk.LEFT)
        
        # Bind Enter key để lưu profile
        def on_enter_key(event):
            save_profile()
        
        username_entry.bind('<Return>', on_enter_key)
        password_entry.bind('<Return>', on_enter_key)
        notes_entry.bind('<Control-Return>', on_enter_key)  # Ctrl+Enter cho text area
        
        # Focus on username entry
        username_entry.focus()
        
        # Đảm bảo dialog hiển thị
        dialog.lift()
        dialog.focus_force()
    
    def run(self):
        """Chạy ứng dụng"""
        # Tạo thư mục cần thiết
        FileManager.ensure_dir('data/videos')
        FileManager.ensure_dir('data/processed')
        FileManager.ensure_dir('data/music')
        FileManager.ensure_dir('data/fonts')
        FileManager.ensure_dir('data/profiles')
        FileManager.ensure_dir('logs')
        
        # Làm mới danh sách file
        self.refresh_files_list()
        
        # Chạy ứng dụng
        self.root.mainloop()

if __name__ == "__main__":
    app = TikTokReupApp()
    app.run()
