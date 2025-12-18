import os
import yt_dlp
from src.core.entities import Video
from src.core.ports import VideoDownloader

class YtdlpDownloader(VideoDownloader):
    def download(self,video:Video,download_path:str)->bool:
        print (f"İndirme Başlatılıyor: {video.title}...")
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        
        ydl_opts={
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'format':'22/18',
            'noprogress':False,
            'quiet':False,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video.url])
            print(f"✅ İndirme Tamamlandı: {video.title}")
            return True
        except Exception as e:
            print(f"❌ İndirme Hatası: {e}")
            return False
