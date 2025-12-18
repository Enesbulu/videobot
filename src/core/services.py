from typing import List, Optional
from src.core.entities import Video
from src.core.ports import videoScanner,VideoDownloader

class VideoServices:
    def __init__(self,scanner:videoScanner,downloader:VideoDownloader):
        self.scanner = scanner
        self.downloader = downloader

    def scan_url(self,url:str)->List[Video]:
        print(f"🕵️ Servis Analiz Ediyor: {url}")
        try:
            video=self.scanner.scan(url)
            return video
        except Exception as e:
            print(f"❌ Servis Analiz Hatası: {e}")
            return []
    
    def download_video(self, video:Video,path:str)->bool:
        if not video.url:
            print("❌ Geçersiz video URL'si.")
            return False
        
        print(f"⬇️ Servis İndiriyor: {video.url} -> {path}")
        return self.downloader.download(video,path)