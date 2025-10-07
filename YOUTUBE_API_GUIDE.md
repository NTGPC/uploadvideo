# HƯỚNG DẪN SỬ DỤNG YOUTUBE API

## Tổng quan

Ứng dụng đã được cập nhật với 2 tab riêng biệt:
- **📚 Download List Channel TikTok**: Sử dụng yt-dlp (như cũ)
- **📺 Download List Channel YouTube**: Sử dụng YouTube Data API v3 (mới)

## Cài đặt YouTube API

### Bước 1: Tạo Google Cloud Project
1. Truy cập [Google Cloud Console](https://console.developers.google.com/)
2. Đăng nhập bằng tài khoản Google
3. Tạo project mới hoặc chọn project hiện có

### Bước 2: Bật YouTube Data API v3
1. Trong Google Cloud Console, chọn project của bạn
2. Vào **APIs & Services** > **Library**
3. Tìm kiếm "YouTube Data API v3"
4. Click **Enable**

### Bước 3: Tạo API Key
1. Vào **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **API Key**
3. Copy API key được tạo
4. (Tùy chọn) Click **Restrict Key** để giới hạn quyền sử dụng

### Bước 4: Cấu hình trong ứng dụng
1. Mở ứng dụng TikTok Reup Offline
2. Vào tab **⚙️ Settings**
3. Tìm phần **Cài đặt YouTube API**
4. Dán API key vào ô **YouTube API Key**
5. Click **Lưu cài đặt**

## Sử dụng YouTube Tab

### Kiểm tra API
1. Vào tab **📺 Download List Channel YouTube**
2. Xem trạng thái API ở phần **Trạng thái API**
3. Click **Test API** để kiểm tra kết nối

### Lấy danh sách video
1. Nhập URL kênh YouTube vào ô **URL Kênh YouTube**
   - Hỗ trợ các format:
     - `https://www.youtube.com/@username`
     - `https://www.youtube.com/c/channelname`
     - `https://www.youtube.com/channel/CHANNEL_ID`
2. Click **Lấy danh sách**
3. Xem thông tin channel và danh sách video

### Tải video
1. Chọn video muốn tải (click vào cột **Tải?**)
2. Click **Tải đã chọn** hoặc **Tải tất cả**
3. Theo dõi tiến trình tải

## So sánh TikTok vs YouTube

| Tính năng | TikTok Tab | YouTube Tab |
|-----------|------------|-------------|
| **Công nghệ** | yt-dlp | YouTube Data API v3 |
| **Tốc độ** | Chậm hơn | Nhanh hơn |
| **Ổn định** | Có thể bị block | Rất ổn định |
| **Thông tin** | Cơ bản | Chi tiết (views, likes, etc.) |
| **Rate limit** | Thấp | Cao (10,000 requests/day) |
| **Cần API key** | Không | Có |

## Lợi ích của YouTube API

### ✅ Ưu điểm:
- **Không bị block IP** như yt-dlp
- **Rate limit cao** (10,000 requests/ngày)
- **Thông tin chi tiết** hơn (views, likes, comments)
- **Ổn định** và đáng tin cậy
- **Tốc độ nhanh** hơn

### ⚠️ Hạn chế:
- **Cần API key** (miễn phí)
- **Chỉ hỗ trợ YouTube** (không phải TikTok)
- **Có quota limit** (nhưng rất cao)

## Troubleshooting

### Lỗi "YouTube API chưa được cấu hình"
- **Nguyên nhân**: Chưa nhập API key
- **Giải pháp**: Vào Settings và nhập API key

### Lỗi "YouTube API quota đã hết"
- **Nguyên nhân**: Đã sử dụng hết quota (10,000 requests/ngày)
- **Giải pháp**: Chờ reset vào ngày hôm sau

### Lỗi "Channel không tồn tại"
- **Nguyên nhân**: URL không đúng hoặc channel bị xóa
- **Giải pháp**: Kiểm tra URL trên trình duyệt

### Lỗi "API key không hợp lệ"
- **Nguyên nhân**: API key sai hoặc chưa enable API
- **Giải pháp**: Kiểm tra lại API key và enable YouTube Data API v3

## Tips sử dụng

### 1. Tối ưu hóa API usage:
- Chỉ lấy video cần thiết (không lấy tất cả)
- Sử dụng filter để lấy video mới nhất
- Tránh refresh liên tục

### 2. Quản lý video:
- Sử dụng **Chọn tất cả** / **Bỏ chọn tất cả** để tiết kiệm thời gian
- **Tải lại video lỗi** để retry những video bị fail
- **Xóa video đã chọn** để loại bỏ video không cần

### 3. Monitoring:
- Theo dõi **Trạng thái API** để biết API có hoạt động không
- Xem **Thông tin Channel** để verify đúng channel
- Kiểm tra **Tiến trình** để biết video nào đang tải

## Cấu trúc dữ liệu

### Thông tin Channel:
```json
{
  "id": "UCxxxxx",
  "title": "Channel Name",
  "subscriber_count": 1000000,
  "video_count": 500,
  "view_count": 10000000,
  "thumbnail": "https://...",
  "country": "VN"
}
```

### Thông tin Video:
```json
{
  "id": "video_id",
  "title": "Video Title",
  "description": "Video Description",
  "url": "https://www.youtube.com/watch?v=...",
  "thumbnail": "https://...",
  "duration": 120,
  "view_count": 10000,
  "like_count": 500,
  "comment_count": 50,
  "published_at": "2024-01-01T00:00:00Z"
}
```

## Kết luận

YouTube API tab cung cấp trải nghiệm tải video YouTube tốt hơn nhiều so với yt-dlp:
- **Nhanh hơn** và **ổn định hơn**
- **Thông tin chi tiết** hơn
- **Không bị block IP**
- **Rate limit cao**

Chỉ cần cấu hình API key một lần là có thể sử dụng thoải mái!
