"""
Module upload video lên các nền tảng
"""
import os
import time
import random
import logging
from typing import Dict, Any, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from .utils import ConfigManager, FileManager, Logger

class VideoUploader:
    """Upload video lên các nền tảng"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.browser_config = self.config.get('browser', {})
        self.upload_config = self.config.get('upload', {})
        self.driver = None
        
        # Cấu hình browser
        self.headless = self.browser_config.get('headless', False)
        self.user_agent = self.browser_config.get('user_agent', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.window_size = self.browser_config.get('window_size', '1920,1080')
        self.timeout = self.browser_config.get('timeout', 30)
    
    def _setup_browser(self) -> bool:
        """Thiết lập browser"""
        try:
            # Cấu hình Chrome options
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless')
            
            options.add_argument(f'--user-agent={self.user_agent}')
            options.add_argument(f'--window-size={self.window_size}')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Khởi tạo driver
            self.driver = uc.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            Logger.log_info("Browser đã được khởi tạo")
            return True
            
        except Exception as e:
            Logger.log_error(f"Lỗi khởi tạo browser: {e}")
            return False
    
    def _close_browser(self):
        """Đóng browser"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                Logger.log_info("Browser đã được đóng")
        except Exception as e:
            Logger.log_error(f"Lỗi đóng browser: {e}")
    
    def upload_to_tiktok(self, video_path: str, title: str = "", 
                        hashtags: str = "") -> bool:
        """Upload video lên TikTok"""
        try:
            if not self._setup_browser():
                return False
            
            if not os.path.exists(video_path):
                Logger.log_error(f"File video không tồn tại: {video_path}")
                return False
            
            # Mở TikTok Creator Studio
            self.driver.get("https://www.tiktok.com/upload")
            time.sleep(3)
            
            # Đợi trang load
            wait = WebDriverWait(self.driver, self.timeout)
            
            # Tìm và click nút upload
            try:
                upload_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-e2e='upload-btn']"))
                )
                upload_button.click()
                time.sleep(2)
            except TimeoutException:
                Logger.log_error("Không tìm thấy nút upload TikTok")
                return False
            
            # Upload file
            try:
                file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                file_input.send_keys(os.path.abspath(video_path))
                time.sleep(5)
            except NoSuchElementException:
                Logger.log_error("Không tìm thấy input file TikTok")
                return False
            
            # Đợi video load
            time.sleep(10)
            
            # Nhập title và hashtags
            if title or hashtags:
                try:
                    caption_input = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='video-caption']"))
                    )
                    caption_text = f"{title} {hashtags}".strip()
                    caption_input.clear()
                    caption_input.send_keys(caption_text)
                    time.sleep(2)
                except TimeoutException:
                    Logger.log_warning("Không tìm thấy ô nhập caption")
            
            # Click nút Post
            try:
                post_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-e2e='publish-button']"))
                )
                post_button.click()
                time.sleep(5)
                
                Logger.log_info("Upload TikTok thành công")
                return True
                
            except TimeoutException:
                Logger.log_error("Không tìm thấy nút Post TikTok")
                return False
                
        except Exception as e:
            Logger.log_error(f"Lỗi upload TikTok: {e}")
            return False
        finally:
            self._close_browser()
    
    def upload_to_youtube(self, video_path: str, title: str = "", 
                         description: str = "", tags: str = "") -> bool:
        """Upload video lên YouTube"""
        try:
            if not self._setup_browser():
                return False
            
            if not os.path.exists(video_path):
                Logger.log_error(f"File video không tồn tại: {video_path}")
                return False
            
            # Mở YouTube Studio
            self.driver.get("https://studio.youtube.com")
            time.sleep(3)
            
            # Đợi trang load
            wait = WebDriverWait(self.driver, self.timeout)
            
            # Click nút Create
            try:
                create_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Create']"))
                )
                create_button.click()
                time.sleep(2)
                
                # Click Upload videos
                upload_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Upload videos']"))
                )
                upload_button.click()
                time.sleep(2)
                
            except TimeoutException:
                Logger.log_error("Không tìm thấy nút Create YouTube")
                return False
            
            # Upload file
            try:
                file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                file_input.send_keys(os.path.abspath(video_path))
                time.sleep(10)
            except NoSuchElementException:
                Logger.log_error("Không tìm thấy input file YouTube")
                return False
            
            # Đợi video process
            time.sleep(30)
            
            # Nhập thông tin video
            if title:
                try:
                    title_input = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#textbox"))
                    )
                    title_input.clear()
                    title_input.send_keys(title)
                    time.sleep(2)
                except TimeoutException:
                    Logger.log_warning("Không tìm thấy ô nhập title")
            
            if description:
                try:
                    description_input = self.driver.find_element(By.CSS_SELECTOR, "#textbox")
                    description_input.send_keys(Keys.TAB)
                    description_input.send_keys(description)
                    time.sleep(2)
                except NoSuchElementException:
                    Logger.log_warning("Không tìm thấy ô nhập description")
            
            # Click nút Publish
            try:
                publish_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Publish']"))
                )
                publish_button.click()
                time.sleep(5)
                
                Logger.log_info("Upload YouTube thành công")
                return True
                
            except TimeoutException:
                Logger.log_error("Không tìm thấy nút Publish YouTube")
                return False
                
        except Exception as e:
            Logger.log_error(f"Lỗi upload YouTube: {e}")
            return False
        finally:
            self._close_browser()
    
    def upload_to_facebook(self, video_path: str, title: str = "", 
                          description: str = "") -> bool:
        """Upload video lên Facebook"""
        try:
            if not self._setup_browser():
                return False
            
            if not os.path.exists(video_path):
                Logger.log_error(f"File video không tồn tại: {video_path}")
                return False
            
            # Mở Facebook
            self.driver.get("https://www.facebook.com")
            time.sleep(3)
            
            # Đợi trang load
            wait = WebDriverWait(self.driver, self.timeout)
            
            # Tìm nút tạo bài viết
            try:
                create_post = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Tạo bài viết']"))
                )
                create_post.click()
                time.sleep(2)
            except TimeoutException:
                Logger.log_error("Không tìm thấy nút tạo bài viết Facebook")
                return False
            
            # Click thêm video/ảnh
            try:
                add_media = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Thêm ảnh/video']"))
                )
                add_media.click()
                time.sleep(2)
            except TimeoutException:
                Logger.log_error("Không tìm thấy nút thêm media Facebook")
                return False
            
            # Upload file
            try:
                file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                file_input.send_keys(os.path.abspath(video_path))
                time.sleep(10)
            except NoSuchElementException:
                Logger.log_error("Không tìm thấy input file Facebook")
                return False
            
            # Nhập nội dung
            if title or description:
                try:
                    text_area = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Bạn đang nghĩ gì?']"))
                    )
                    text_content = f"{title}\n\n{description}".strip()
                    text_area.send_keys(text_content)
                    time.sleep(2)
                except TimeoutException:
                    Logger.log_warning("Không tìm thấy ô nhập nội dung")
            
            # Click nút Đăng
            try:
                post_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Đăng']"))
                )
                post_button.click()
                time.sleep(5)
                
                Logger.log_info("Upload Facebook thành công")
                return True
                
            except TimeoutException:
                Logger.log_error("Không tìm thấy nút Đăng Facebook")
                return False
                
        except Exception as e:
            Logger.log_error(f"Lỗi upload Facebook: {e}")
            return False
        finally:
            self._close_browser()
    
    def batch_upload(self, video_files: List[str], platform: str, 
                    titles: List[str] = None, descriptions: List[str] = None) -> List[bool]:
        """Upload hàng loạt"""
        try:
            results = []
            delay = self.upload_config.get('delay_between_uploads', 30)
            
            for i, video_file in enumerate(video_files):
                Logger.log_info(f"Uploading {i+1}/{len(video_files)}: {video_file}")
                
                title = titles[i] if titles and i < len(titles) else ""
                description = descriptions[i] if descriptions and i < len(descriptions) else ""
                
                if platform.lower() == 'tiktok':
                    success = self.upload_to_tiktok(video_file, title)
                elif platform.lower() == 'youtube':
                    success = self.upload_to_youtube(video_file, title, description)
                elif platform.lower() == 'facebook':
                    success = self.upload_to_facebook(video_file, title, description)
                else:
                    Logger.log_error(f"Platform không được hỗ trợ: {platform}")
                    success = False
                
                results.append(success)
                
                if success:
                    Logger.log_info(f"Upload thành công: {video_file}")
                else:
                    Logger.log_error(f"Upload thất bại: {video_file}")
                
                # Delay giữa các upload
                if i < len(video_files) - 1:
                    Logger.log_info(f"Đợi {delay} giây trước khi upload tiếp...")
                    time.sleep(delay)
            
            success_count = sum(results)
            Logger.log_info(f"Upload hàng loạt hoàn thành: {success_count}/{len(video_files)} thành công")
            return results
            
        except Exception as e:
            Logger.log_error(f"Lỗi upload hàng loạt: {e}")
            return [False] * len(video_files)
    
    def get_upload_status(self, platform: str) -> Dict[str, Any]:
        """Lấy trạng thái upload"""
        try:
            if not self._setup_browser():
                return {"status": "error", "message": "Không thể khởi tạo browser"}
            
            if platform.lower() == 'tiktok':
                self.driver.get("https://www.tiktok.com/upload")
            elif platform.lower() == 'youtube':
                self.driver.get("https://studio.youtube.com")
            elif platform.lower() == 'facebook':
                self.driver.get("https://www.facebook.com")
            else:
                return {"status": "error", "message": "Platform không được hỗ trợ"}
            
            time.sleep(3)
            
            return {
                "status": "success",
                "platform": platform,
                "url": self.driver.current_url,
                "title": self.driver.title
            }
            
        except Exception as e:
            Logger.log_error(f"Lỗi lấy trạng thái upload: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            self._close_browser()
