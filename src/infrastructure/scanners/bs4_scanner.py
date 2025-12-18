import requests
from  bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List
from src.core.entities import Video
from src.core.ports import videoScanner

class BS4Scanner(videoScanner):
    def scan(self,url:str)->List[Video]:
        print ("🔍 BS4 Tarayıcı ile tarama yapılıyor...")
        found_videos = []
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        
        try:
            response=requests.get(url,headers = headers,timeout=10)
            response.raise_for_status()
            soup=BeautifulSoup(response.text,'html.parser')
            page_title= soup.title.string.strip() if soup.title else "No Title"
            video_tags =soup.find_all('video')
            for tag in video_tags:
                video_url = None
                if tag.get('src'):
                    video_url=tag.get('src')

                else: 
                    source_tag=tag.find('source')
                    if source_tag and source_tag.get('src'):
                        video_url=source_tag.get('src')

                if video_url:
                    if video_url.startswith("blob:"):
                        print("⚠️  Blob linki bulundu (BS4 bunu indiremez, atlanıyor).")
                        continue

                    full_url= urljoin(url,video_url)
                    video= Video(
                        url=full_url,
                        title=f"{page_title} - Video",
                        resolution="Unknown (HTML5 Video)",
                        duration="Bilinmiyor"
                    )
                    found_videos.append(video)
        except Exception as e:
            print(f"❌ BS4 Tarama Hatası: {e}")
            return []
        return found_videos