# Hướng dẫn sử dụng TikTok Reup Offline

## 🚀 Cài đặt

### Bước 1: Cài đặt Python
- Tải và cài đặt Python 3.8+ từ [python.org](https://python.org)
- Đảm bảo chọn "Add Python to PATH" khi cài đặt

### Bước 2: Cài đặt ứng dụng
1. Chạy file `install.bat` để cài đặt tự động
2. Hoặc chạy thủ công:
   ```bash
   pip install -r requirements.txt
   ```

### Bước 3: Cài đặt FFmpeg
1. Tải FFmpeg từ [ffmpeg.org](https://ffmpeg.org/download.html)
2. Giải nén và copy file `ffmpeg.exe` vào thư mục `tools/`
3. Hoặc cài đặt FFmpeg system-wide

### Bước 4: Chạy ứng dụng
- Chạy file `run.bat` hoặc `python main.py`

## 📥 Tab Download

### Tải video từ URL
1. Nhập URL video vào ô "URL Video"
2. Click "Download" để bắt đầu tải
3. Xem thông tin video trong khung "Thông tin Video"
4. File đã tải sẽ hiển thị trong danh sách "Files đã tải"

### Các nền tảng được hỗ trợ
- ✅ TikTok
- ✅ YouTube  
- ✅ Facebook
- ✅ Instagram
- ✅ Twitter/X

### Quản lý file
- **Xóa file**: Chọn file và click "Xóa file"
- **Mở thư mục**: Click "Mở thư mục" để mở thư mục chứa video
- **Refresh**: Click "Refresh" để cập nhật danh sách file

## ✂️ Tab Process

### Chọn file video
1. Click "Browse" để chọn file video cần xử lý
2. Hoặc nhập đường dẫn file trực tiếp

### Tùy chọn xử lý

#### Cắt video
- **Không cắt**: Giữ nguyên video gốc
- **1min, 3min, 5min, 10min, 30min**: Cắt video theo thời gian

#### Watermark
- ✅ **Thêm watermark**: Thêm text lên video
- **Text**: Nhập nội dung watermark (mặc định: "TikTok Reup Offline")

#### Tốc độ
- **Thanh trượt**: Điều chỉnh tốc độ từ 0.5x đến 2.0x
- **1.0x**: Tốc độ bình thường

#### Lật video
- **Không**: Giữ nguyên hướng video
- **Ngang**: Lật video theo chiều ngang
- **Dọc**: Lật video theo chiều dọc

#### Các tùy chọn khác
- ✅ **Chuyển 9:16**: Chuyển đổi tỷ lệ video thành 9:16 (TikTok format)
- ✅ **Thay đổi MD5**: Thay đổi metadata để tránh duplicate detection

### Xử lý video
1. Chọn các tùy chọn xử lý
2. Click "Xử lý Video" để bắt đầu
3. Xem log xử lý trong khung "Log xử lý"
4. File đã xử lý sẽ được lưu trong thư mục `data/processed/`

## 📤 Tab Upload

### Chọn file video
1. Click "Browse" để chọn file video cần upload
2. Hoặc nhập đường dẫn file trực tiếp

### Chọn nền tảng
- **TikTok**: Upload lên TikTok
- **YouTube**: Upload lên YouTube
- **Facebook**: Upload lên Facebook

### Nhập nội dung
- **Tiêu đề**: Tiêu đề video
- **Mô tả**: Mô tả video (YouTube, Facebook)
- **Hashtags**: Hashtags (TikTok)

### Upload video
1. Điền đầy đủ thông tin
2. Click "Upload Video" để bắt đầu
3. Xem log upload trong khung "Log upload"
4. Đăng nhập vào tài khoản khi browser mở

## ⚙️ Tab Settings

### Cài đặt Download
- **Độ phân giải**: Chọn độ phân giải video tải về (360p, 480p, 720p, 1080p)
- **Thư mục lưu**: Chọn thư mục lưu video đã tải

### Cài đặt xử lý
- **Thư mục xử lý**: Chọn thư mục lưu video đã xử lý

### Cài đặt FFmpeg
- **Đường dẫn FFmpeg**: Chọn đường dẫn đến file ffmpeg.exe

### Lưu cài đặt
- Click "Lưu cài đặt" để lưu các thay đổi
- Click "Reset" để reset về cài đặt mặc định

## 🔧 Tính năng nâng cao

### Xử lý hàng loạt
- Có thể xử lý nhiều video cùng lúc
- Tự động áp dụng các tùy chọn xử lý cho tất cả file

### Upload hàng loạt
- Upload nhiều video lên cùng một nền tảng
- Tự động delay giữa các lần upload

### Quản lý file
- Tự động tạo thư mục cần thiết
- Làm sạch tên file tự động
- Hỗ trợ nhiều định dạng video

## 🛠️ Troubleshooting

### Lỗi thường gặp

#### "FFmpeg không tìm thấy"
- Đảm bảo đã cài đặt FFmpeg và đặt đúng đường dẫn
- Kiểm tra file `tools/ffmpeg.exe` có tồn tại

#### "Lỗi tải video"
- Kiểm tra URL có đúng không
- Kiểm tra kết nối internet
- Thử tải video khác

#### "Lỗi upload"
- Đảm bảo đã đăng nhập vào tài khoản
- Kiểm tra kết nối internet
- Thử upload thủ công trước

#### "Lỗi xử lý video"
- Kiểm tra file video có hợp lệ không
- Kiểm tra FFmpeg có hoạt động không
- Thử với file video khác

### Log files
- Log được lưu trong thư mục `logs/`
- Kiểm tra file `logs/app.log` để xem chi tiết lỗi

## 📁 Cấu trúc thư mục

```
TikTokReupOffline/
├── main.py                 # File chính
├── requirements.txt        # Dependencies
├── install.bat            # Script cài đặt
├── run.bat               # Script chạy
├── config/               # Cấu hình
│   ├── settings.json     # Cài đặt chính
│   └── templates.json    # Templates xử lý
├── src/                  # Source code
│   ├── utils.py         # Utilities
│   ├── downloader.py    # Tải video
│   ├── processor.py     # Xử lý video
│   └── uploader.py      # Upload video
├── data/                # Dữ liệu
│   ├── videos/          # Video đã tải
│   ├── processed/       # Video đã xử lý
│   ├── music/           # Nhạc nền
│   └── fonts/           # Font chữ
├── tools/               # Công cụ
│   └── ffmpeg.exe       # FFmpeg
└── logs/                # Log files
    └── app.log          # Log chính
```

## 🆘 Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log files trong thư mục `logs/`
2. Đảm bảo đã cài đặt đầy đủ dependencies
3. Kiểm tra FFmpeg có hoạt động không
4. Thử với file video khác

## 📝 Ghi chú

- Ứng dụng hoàn toàn offline, không cần server
- Không cần đăng ký tài khoản
- Không cần license key
- Tất cả dữ liệu được lưu local
- Hỗ trợ đa nền tảng (Windows, Linux, macOS)
