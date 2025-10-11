"""
Profile Manager - Quản lý profiles đăng nhập
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class ProfileManager:
    """Quản lý profiles đăng nhập với JSON storage"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.profiles_file = self.data_dir / "profiles.json"
        self.profiles_data = []
        self.load_profiles()
    
    def load_profiles(self):
        """Tải danh sách profiles từ file JSON"""
        try:
            if self.profiles_file.exists():
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    self.profiles_data = json.load(f)
            else:
                # Tạo file mới với dữ liệu mẫu
                self.profiles_data = self._get_sample_profiles()
                self.save_profiles()
        except Exception as e:
            print(f"Lỗi khi tải profiles: {e}")
            self.profiles_data = self._get_sample_profiles()
    
    def save_profiles(self):
        """Lưu danh sách profiles vào file JSON"""
        try:
            # Đảm bảo thư mục tồn tại
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.profiles_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu profiles: {e}")
            return False
    
    def _get_sample_profiles(self) -> List[Dict]:
        """Tạo dữ liệu mẫu cho profiles"""
        return [
            {
                "id": "profile_001",
                "username": "john.doe@email.com",
                "password": "encrypted_password_1",
                "platform": "TikTok",
                "status": "Active",
                "last_login": "2024-01-15 14:30",
                "notes": "Main Account",
                "created_at": "2024-01-10 10:00:00",
                "updated_at": "2024-01-15 14:30:00",
                "profile_dir": "john_doe_email_com",
                "proxy_settings": {
                    "enabled": False,
                    "host": "",
                    "port": "",
                    "username": "",
                    "password": ""
                }
            },
            {
                "id": "profile_002",
                "username": "jane.smith@email.com",
                "password": "encrypted_password_2",
                "platform": "Instagram",
                "status": "Pending",
                "last_login": "2024-01-14 09:15",
                "notes": "Backup Account",
                "created_at": "2024-01-11 11:00:00",
                "updated_at": "2024-01-14 09:15:00",
                "profile_dir": "jane_smith_email_com",
                "proxy_settings": {
                    "enabled": False,
                    "host": "",
                    "port": "",
                    "username": "",
                    "password": ""
                }
            },
            {
                "id": "profile_003",
                "username": "mike.wilson@email.com",
                "password": "encrypted_password_3",
                "platform": "Facebook",
                "status": "Blocked",
                "last_login": "2024-01-10 16:45",
                "notes": "Test Account",
                "created_at": "2024-01-08 15:00:00",
                "updated_at": "2024-01-10 16:45:00",
                "profile_dir": "mike_wilson_email_com",
                "proxy_settings": {
                    "enabled": False,
                    "host": "",
                    "port": "",
                    "username": "",
                    "password": ""
                }
            },
            {
                "id": "profile_004",
                "username": "sarah.jones@email.com",
                "password": "encrypted_password_4",
                "platform": "YouTube",
                "status": "Active",
                "last_login": "2024-01-15 11:20",
                "notes": "Business Account",
                "created_at": "2024-01-12 09:00:00",
                "updated_at": "2024-01-15 11:20:00",
                "profile_dir": "sarah_jones_email_com",
                "proxy_settings": {
                    "enabled": False,
                    "host": "",
                    "port": "",
                    "username": "",
                    "password": ""
                }
            }
        ]
    
    def get_all_profiles(self) -> List[Dict]:
        """Lấy tất cả profiles"""
        return self.profiles_data
    
    def get_profile_by_id(self, profile_id: str) -> Optional[Dict]:
        """Lấy profile theo ID"""
        for profile in self.profiles_data:
            if profile['id'] == profile_id:
                return profile
        return None
    
    def get_profile_by_username(self, username: str) -> Optional[Dict]:
        """Lấy profile theo username"""
        for profile in self.profiles_data:
            if profile['username'] == username:
                return profile
        return None
    
    def add_profile(self, profile_data: Dict) -> bool:
        """Thêm profile mới"""
        try:
            # Tạo ID mới
            new_id = f"profile_{len(self.profiles_data) + 1:03d}"
            
            # Tạo profile directory name
            profile_dir = profile_data['username'].replace('@', '_').replace('.', '_')
            
            # Tạo profile object
            new_profile = {
                "id": new_id,
                "username": profile_data['username'],
                "password": self._encrypt_password(profile_data.get('password', '')),
                "platform": profile_data.get('platform', 'TikTok'),
                "status": profile_data.get('status', 'Active'),
                "last_login": "",
                "notes": profile_data.get('notes', ''),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "profile_dir": profile_dir,
                "proxy_settings": profile_data.get('proxy_settings', {
                    "enabled": False,
                    "host": "",
                    "port": "",
                    "username": "",
                    "password": ""
                })
            }
            
            self.profiles_data.append(new_profile)
            return self.save_profiles()
            
        except Exception as e:
            print(f"Lỗi khi thêm profile: {e}")
            return False
    
    def update_profile(self, profile_id: str, update_data: Dict) -> bool:
        """Cập nhật profile"""
        try:
            for i, profile in enumerate(self.profiles_data):
                if profile['id'] == profile_id:
                    # Cập nhật các trường được chỉ định
                    for key, value in update_data.items():
                        if key in profile and key not in ['id', 'created_at']:
                            if key == 'password' and value:
                                profile[key] = self._encrypt_password(value)
                            else:
                                profile[key] = value
                    
                    # Cập nhật thời gian
                    profile['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Cập nhật profile directory nếu username thay đổi
                    if 'username' in update_data:
                        profile['profile_dir'] = update_data['username'].replace('@', '_').replace('.', '_')
                    
                    self.profiles_data[i] = profile
                    return self.save_profiles()
            
            return False
            
        except Exception as e:
            print(f"Lỗi khi cập nhật profile: {e}")
            return False
    
    def delete_profile(self, profile_id: str) -> bool:
        """Xóa profile"""
        try:
            # Tìm và xóa profile
            for i, profile in enumerate(self.profiles_data):
                if profile['id'] == profile_id:
                    # Xóa thư mục profile nếu tồn tại
                    profile_dir = Path(f"data/profiles/{profile['profile_dir']}")
                    if profile_dir.exists():
                        import shutil
                        shutil.rmtree(profile_dir)
                    
                    # Xóa khỏi danh sách
                    del self.profiles_data[i]
                    return self.save_profiles()
            
            return False
            
        except Exception as e:
            print(f"Lỗi khi xóa profile: {e}")
            return False
    
    def update_last_login(self, profile_id: str) -> bool:
        """Cập nhật thời gian đăng nhập cuối"""
        try:
            for profile in self.profiles_data:
                if profile['id'] == profile_id:
                    profile['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    profile['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    return self.save_profiles()
            return False
        except Exception as e:
            print(f"Lỗi khi cập nhật last login: {e}")
            return False
    
    def _encrypt_password(self, password: str) -> str:
        """Mã hóa mật khẩu với Fernet encryption"""
        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Tạo key từ một string cố định (trong thực tế nên lưu key an toàn)
            key_string = "TikTokReupOffline2024SecretKey123456789"
            key = base64.urlsafe_b64encode(key_string.encode()[:32])
            f = Fernet(key)
            
            encrypted_password = f.encrypt(password.encode())
            return encrypted_password.decode()
        except ImportError:
            # Fallback về base64 nếu không có cryptography
            import base64
            return base64.b64encode(password.encode()).decode()
        except Exception as e:
            print(f"Lỗi mã hóa password: {e}")
            # Fallback về base64
            import base64
            return base64.b64encode(password.encode()).decode()
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """Giải mã mật khẩu"""
        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Tạo key từ một string cố định (trong thực tế nên lưu key an toàn)
            key_string = "TikTokReupOffline2024SecretKey123456789"
            key = base64.urlsafe_b64encode(key_string.encode()[:32])
            f = Fernet(key)
            
            decrypted_password = f.decrypt(encrypted_password.encode())
            return decrypted_password.decode()
        except ImportError:
            # Fallback về base64 nếu không có cryptography
            try:
                import base64
                return base64.b64decode(encrypted_password.encode()).decode()
            except:
                return ""
        except Exception as e:
            print(f"Lỗi giải mã password: {e}")
            # Fallback về base64
            try:
                import base64
                return base64.b64decode(encrypted_password.encode()).decode()
            except:
                return ""
    
    def get_decrypted_password(self, profile_id: str) -> str:
        """Lấy mật khẩu đã giải mã"""
        profile = self.get_profile_by_id(profile_id)
        if profile:
            return self._decrypt_password(profile['password'])
        return ""
    
    def export_profiles(self, export_file: str) -> bool:
        """Export profiles ra file JSON"""
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.profiles_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Lỗi khi export profiles: {e}")
            return False
    
    def import_profiles(self, import_file: str) -> bool:
        """Import profiles từ file JSON"""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # Merge với dữ liệu hiện tại
            for profile in imported_data:
                # Kiểm tra xem profile đã tồn tại chưa
                existing = self.get_profile_by_username(profile['username'])
                if not existing:
                    # Tạo ID mới
                    profile['id'] = f"profile_{len(self.profiles_data) + 1:03d}"
                    profile['profile_dir'] = profile['username'].replace('@', '_').replace('.', '_')
                    self.profiles_data.append(profile)
            
            return self.save_profiles()
            
        except Exception as e:
            print(f"Lỗi khi import profiles: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Lấy thống kê profiles"""
        total = len(self.profiles_data)
        active = len([p for p in self.profiles_data if p['status'] == 'Active'])
        pending = len([p for p in self.profiles_data if p['status'] == 'Pending'])
        blocked = len([p for p in self.profiles_data if p['status'] == 'Blocked'])
        
        platforms = {}
        for profile in self.profiles_data:
            platform = profile['platform']
            platforms[platform] = platforms.get(platform, 0) + 1
        
        return {
            'total': total,
            'active': active,
            'pending': pending,
            'blocked': blocked,
            'platforms': platforms
        }
