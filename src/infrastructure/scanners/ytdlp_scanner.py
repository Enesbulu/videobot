from src.core.entities import Video
from src.core.ports import VideoScanner
import yt_dlp
from typing import List

class YTDLPScanner(VideoScanner):
    def scan(self,url:str)-> List[Video]:
        print(f"🔍 '{url}' adresi taranıyor...")
        ydl_opts={
            'quiet': True,
            'extract_flat':True,
            'no_warning':True
        }

        found_videos=[]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url,download=False)
                if 'entries' in info:
                    entries = info['entries ]']
                else:
                    entries = [info]
                for entry in entries:
                    video= Video(
                        url=entry.get('webpage_url') or entry.get('url'),
                        title=entry.get('title', 'Bilinmeyen Başlık'),
                        duration=str(entry.get('duration')), # Saniye cinsinden gelir
                        resolution=entry.get('resolution', 'Belirsiz'),
                        thumbnail_url=entry.get('thumbnail')
                    )
                    found_videos.append(video)
        except Exception as e:
            print(f"❌ Hata oluştu: {e}")
        return found_videos if found_videos else []
    