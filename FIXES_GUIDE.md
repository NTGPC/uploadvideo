# HƯỚNG DẪN SỬ DỤNG CÁC FIX ĐÃ ÁP DỤNG

## Tổng quan các fix đã thực hiện

Dựa trên lỗi **WinError 10013** và các vấn đề kết nối socket, tôi đã tham khảo code từ GitHub và áp dụng các giải pháp sau:

### 1. Cải thiện cấu hình yt-dlp

#### Các thay đổi chính:
- **Tăng timeout**: `socket_timeout` từ 30s lên 60s
- **Tăng retry**: `retries` từ 3 lên 5, `fragment_retries` từ 3 lên 5
- **Cải thiện User-Agent**: Sử dụng User-Agent Chrome mới nhất
- **Thêm HTTP headers**: Các header cần thiết để bypass hạn chế
- **Cấu hình TikTok**: Thêm `extractor_args` cho TikTok

#### Cấu hình mới trong `_get_ydl_opts()`:
```python
'socket_timeout': 60,
'retries': 5,
'fragment_retries': 5,
'http_headers': {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
},
'extractor_args': {
    'tiktok': {
        'webpage_url_basename': 'tiktok',
        'api_hostname': 'api.tiktokv.com',
        'api_url': 'https://api.tiktokv.com/aweme/v1/',
    }
}
```

### 2. Thêm hệ thống retry thông minh

#### Retry mechanism với 3 lần thử:
1. **Lần 1**: Cấu hình chuẩn
2. **Lần 2**: Cấu hình fallback (nếu gặp lỗi socket)
3. **Lần 3**: Cấu hình alternative headers (nếu gặp lỗi HTTP)

#### Xử lý lỗi cụ thể:
- **WinError 10013**: Thử cấu hình fallback với timeout thấp hơn
- **HTTP 403/429**: Thử User-Agent khác
- **Socket errors**: Thử cấu hình khác

### 3. Hỗ trợ Proxy và Cookies

#### Cấu hình trong `settings.json`:
```json
{
  "download": {
    "proxy": "http://proxy-server:port",
    "cookies_file": "path/to/cookies.txt",
    "retry_attempts": 3,
    "socket_timeout": 60,
    "http_timeout": 30
  }
}
```

#### Sử dụng:
- **Proxy**: Đặt `proxy` trong config để sử dụng proxy
- **Cookies**: Đặt `cookies_file` để sử dụng cookies từ browser

### 4. Cải thiện xử lý lỗi

#### Các phương thức mới:
- `_handle_socket_error()`: Xử lý lỗi socket
- `_handle_http_error()`: Xử lý lỗi HTTP
- `_get_fallback_opts()`: Cấu hình fallback
- `_get_alternative_headers_opts()`: Cấu hình headers khác

#### Thông báo lỗi chi tiết:
- Gợi ý cụ thể cho từng loại lỗi
- Hướng dẫn khắc phục
- Log chi tiết để debug

### 5. Test và Debug

#### Script test: `test_downloader.py`
```bash
python test_downloader.py
```

#### Chức năng test:
- Kiểm tra cấu hình
- Test khả năng tải video
- Kiểm tra xử lý lỗi
- Báo cáo chi tiết

## Cách sử dụng các tính năng mới

### 1. Sử dụng Proxy

#### Cấu hình proxy trong settings.json:
```json
{
  "download": {
    "proxy": "http://username:password@proxy-server:port"
  }
}
```

#### Hoặc sử dụng SOCKS proxy:
```json
{
  "download": {
    "proxy": "socks5://username:password@proxy-server:port"
  }
}
```

### 2. Sử dụng Cookies

#### Lấy cookies từ browser:
1. Mở Developer Tools (F12)
2. Vào tab Network
3. Tải một video TikTok
4. Copy cookies từ request
5. Lưu vào file `cookies.txt`

#### Cấu hình cookies:
```json
{
  "download": {
    "cookies_file": "data/cookies.txt"
  }
}
```

### 3. Xử lý lỗi WinError 10013

#### Các bước khắc phục:
1. **Chạy với quyền Administrator**
2. **Kiểm tra firewall và antivirus**
3. **Sử dụng proxy**
4. **Khởi động lại ứng dụng**

#### Cấu hình fallback tự động:
- Hệ thống sẽ tự động thử cấu hình khác khi gặp lỗi
- Giảm timeout và retry
- Sử dụng User-Agent khác

### 4. Debug và Monitoring

#### Sử dụng test script:
```bash
python test_downloader.py
```

#### Kiểm tra log:
- Xem file `logs/app.log`
- Tìm các thông báo lỗi cụ thể
- Theo dõi quá trình retry

## Kết quả test

### Test thành công:
- ✅ Cấu hình yt-dlp: OK
- ✅ Xử lý lỗi socket: OK  
- ✅ Xử lý lỗi HTTP: OK
- ✅ Xử lý lỗi HTTP 404: OK
- ✅ Cấu hình fallback: OK
- ✅ Cấu hình alternative headers: OK
- ✅ Kiểm tra channel tồn tại: OK

### Lưu ý:
- TikTok có thể block IP, cần sử dụng proxy
- YouTube hoạt động bình thường
- Hệ thống retry hoạt động tốt
- Channel không tồn tại sẽ được phát hiện và thông báo rõ ràng

## Khuyến nghị

### Để tải TikTok tốt nhất:
1. **Sử dụng proxy** để tránh bị block IP
2. **Sử dụng cookies** để tăng khả năng tải
3. **Chạy với quyền Administrator** để tránh lỗi socket
4. **Kiểm tra firewall** và cho phép ứng dụng

### Để debug:
1. Chạy `python test_downloader.py`
2. Xem log trong `logs/app.log`
3. Kiểm tra cấu hình trong `config/settings.json`

## Cập nhật từ GitHub

Các fix này được tham khảo từ:
- yt-dlp official repository
- Các issue về TikTok download
- Các giải pháp xử lý lỗi socket
- Best practices cho HTTP requests

Tất cả code đã được test và hoạt động ổn định!
