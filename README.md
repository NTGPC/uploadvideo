# TikTok Reup Offline

Ứng dụng offline để tải xuống, xử lý và tải lên lại video TikTok và các nền tảng khác.

## Tính năng chính

### 📥 Tải xuống video
- Hỗ trợ TikTok, YouTube, Facebook, Instagram
- Tải với độ phân giải cao (1080p FullHD)
- Sử dụng yt-dlp (thay thế youtube-dl)

### ✂️ Xử lý video
- Cắt video: 1min, 3min, 5min, 10min, 30min
- Thay đổi MD5 để tránh duplicate detection
- Thêm nhạc nền từ thư viện
- Thêm text/watermark
- Chuyển đổi tỷ lệ (9:16)
- Tăng tốc độ và lật video

### 📤 Upload tự động
- Upload lên TikTok, YouTube, Facebook
- Multi-threading cho hiệu suất cao
- Auto delete file sau khi xử lý

### 🔧 Tính năng khác
- Hoàn toàn offline (không cần server)
- Không cần login/authentication
- Không cần license key
- Giao diện đơn giản, dễ sử dụng

## Công nghệ sử dụng

- **Python 3.8+** - Ngôn ngữ chính
- **tkinter** - Giao diện desktop
- **yt-dlp** - Tải video
- **FFmpeg** - Xử lý video
- **Selenium** - Browser automation
- **SQLite** - Lưu trữ dữ liệu local

## Cài đặt

1. Clone repository
2. Cài đặt dependencies: `pip install -r requirements.txt`
3. Tải FFmpeg và đặt vào thư mục `tools/`
4. Chạy: `python main.py`

## Cấu trúc thư mục

```
TikTokReupOffline/
├── main.py                 # File chính
├── src/
│   ├── downloader.py       # Tải video
│   ├── processor.py        # Xử lý video
│   ├── uploader.py         # Upload video
│   ├── browser_manager.py  # Quản lý browser
│   └── utils.py           # Utilities
├── config/
│   ├── settings.json      # Cấu hình
│   └── templates.json     # Template xử lý
├── data/
│   ├── videos/            # Video tải về
│   ├── processed/         # Video đã xử lý
│   ├── music/             # Nhạc nền
│   └── fonts/             # Font chữ
├── tools/
│   ├── ffmpeg.exe         # FFmpeg
│   └── yt-dlp.exe         # yt-dlp
└── requirements.txt       # Dependencies
```
