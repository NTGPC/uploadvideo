# Hướng dẫn sử dụng chức năng lưu Profile

## Tổng quan
Chức năng lưu profile trong TikTok Reup Offline cho phép bạn quản lý các tài khoản đăng nhập một cách an toàn và tiện lợi.

## Cách sử dụng

### 1. Thêm Profile mới
1. Mở ứng dụng TikTok Reup Offline
2. Chuyển đến tab **"👤 Login Profile"**
3. Nhấn nút **"➕ Thêm Profile"**
4. Điền thông tin:
   - **Username/Email**: Tên đăng nhập hoặc email
   - **Password**: Mật khẩu (tối thiểu 6 ký tự)
   - **Platform**: Chọn nền tảng (TikTok, Instagram, Facebook, YouTube)
   - **Status**: Trạng thái tài khoản (Active, Pending, Blocked)
   - **Notes**: Ghi chú thêm (tùy chọn)
5. Nhấn **"💾 LƯU PROFILE"** hoặc nhấn **Enter**

### 2. Tính năng bảo mật
- **Mã hóa mật khẩu**: Mật khẩu được mã hóa bằng Fernet encryption
- **Validation**: Kiểm tra định dạng email và độ dài mật khẩu
- **Kiểm tra trùng lặp**: Không cho phép tạo profile trùng username

### 3. Phím tắt
- **Enter**: Lưu profile (trong các trường username/password)
- **Ctrl+Enter**: Lưu profile (trong trường notes)
- **Escape**: Đóng dialog

### 4. Quản lý Profile
- **Xem danh sách**: Tất cả profiles hiển thị trong bảng
- **Mở Profile**: Nhấn "Mở Profile" để khởi chạy Chrome với profile đó
- **Xóa Profile**: Nhấn nút xóa để xóa profile
- **Refresh**: Nhấn "Refresh" để làm mới danh sách

### 5. Import/Export
- **Import Profiles**: Nhập profiles từ file JSON
- **Export Profiles**: Xuất profiles ra file JSON để backup

## Lưu ý quan trọng

### Bảo mật
- Mật khẩu được mã hóa trước khi lưu
- Không lưu mật khẩu dạng plain text
- Sử dụng key mã hóa cố định (có thể cải thiện trong tương lai)

### Validation
- Username không được để trống
- Password phải có ít nhất 6 ký tự
- Email phải có định dạng hợp lệ (@ và .)
- Username không được trùng lặp

### Lỗi thường gặp
1. **"Username này đã tồn tại!"**: Chọn username khác
2. **"Password phải có ít nhất 6 ký tự!"**: Nhập password dài hơn
3. **"Email không hợp lệ!"**: Kiểm tra định dạng email
4. **"Không thể thêm profile!"**: Kiểm tra quyền ghi file

## Cấu trúc dữ liệu

Profile được lưu trong file `data/profiles.json` với cấu trúc:

```json
{
  "id": "profile_001",
  "username": "user@example.com",
  "password": "encrypted_password",
  "platform": "TikTok",
  "status": "Active",
  "last_login": "2024-01-15 14:30:00",
  "notes": "Main Account",
  "created_at": "2024-01-10 10:00:00",
  "updated_at": "2024-01-15 14:30:00",
  "profile_dir": "user_example_com",
  "proxy_settings": {
    "enabled": false,
    "host": "",
    "port": "",
    "username": "",
    "password": ""
  }
}
```

## Cài đặt thư viện

Để sử dụng mã hóa mạnh, cài đặt thư viện cryptography:

```bash
pip install cryptography>=41.0.0
```

Hoặc chạy:

```bash
pip install -r requirements.txt
```

## Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. File `data/profiles.json` có tồn tại và có quyền ghi
2. Thư mục `data/profiles/` có tồn tại
3. Đã cài đặt đầy đủ dependencies
4. Xem log trong file `logs/app.log`
