from typing import List, Optional, Callable
from src.core.entities import Video
from src.core.ports import VideoScanner, VideoDownloader, LinkExtractor
from core.crawler import Crawler


class VideoServices:
    """
    Uygulamanın iş mantığını (Business Logic) yöneten servis.
    """

    def __init__(
        self,
        scanner: VideoScanner,
        downloader: VideoDownloader,
        link_extractor: Optional[LinkExtractor] = None,
    ):
        self.scanner = scanner
        self.downloader = downloader
        self.link_extractor = link_extractor

    def scan_url(self, url: str) -> List[Video]:
        """Tek bir sayfayı tarar."""
        print(f"🕵️ Servis Analiz Ediyor: {url}")
        try:
            video = self.scanner.scan(url)
            return video
        except Exception as e:
            print(f"❌ Servis Analiz Hatası: {e}")
            return []

    def craw_url(
        self,
        url: str,
        max_depth: int = 2,
        max_pages: int = 10,
        max_videos: int = 50,
        callback: Optional[Callable] = None,
    ) -> List[Video]:
        """
        Siteyi örümcek gibi gezerek tarar.
        """
        if not self.link_extractor:
            if callback:
                callback("error", {"message": "LinkExtractor yok!"})
            else:
                print("❌ Hata: Crawler için LinkExtractor tanımlanmamış.")
            return []

        # Loglama (Callback varsa ona gönder, yoksa print yap)
        msg = f"🕸️ Crawling Başlatılıyor: {url}"
        if callback:
            callback("log", msg)
        else:
            print(msg)

        spider = Crawler(scanner=self.scanner, link_extractor=self.link_extractor)

        # Parametreleri Crawler'a iletiyoruz
        return spider.start_crawling(
            start_url=url,
            max_depth=max_depth,
            max_pages=max_pages,
            max_videos=max_videos,
            progress_callback=callback,  # Dikkat: Crawler'daki parametre adı "progress_callback", buradaki adı "callback"
        )

    def download_video(self, video: Video, path: str) -> bool:
        """Videoyu indirir."""
        if not video.url:
            print("❌ Geçersiz video URL'si.")
            return False

        print(f"⬇️ Servis İndiriyor: {video.url} -> {path}")
        return self.downloader.download(video, path)
