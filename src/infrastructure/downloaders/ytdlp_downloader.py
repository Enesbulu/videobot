import os, yt_dlp, re
from src.core.entities import Video
from src.core.ports import VideoDownloader


class YtdlpDownloader(VideoDownloader):
    def download(self, video: Video, download_path: str) -> bool:
        print(f"İndirme Başlatılıyor: {video.title}...")
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        # 1. Dosya ismini temizle (Windows uyumlu hale getir) Örn: "Gloria | Jean's" -> "Gloria  Jeans"
        safe_title = self._sanitize_filename(video.title)
        if not safe_title:
            safe_title = "video_download"

        # 2. Şablonu belirle: Klasör / Başlık.uzantı. Bu satır sayesinde artık hepsi "original.mp4" OLMAYACAK.
        output_template = os.path.join(download_path, f"{safe_title}.%(ext)s")

        ydl_opts = {
            "format": "22/18/best",
            "outtmpl": output_template,  # f"{download_path}/%(title)s.%(ext)s",
            "noprogress": False,
            "quiet": False,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            },
        }
        try:
            print(f"⬇️ Servis İndiriyor: {safe_title}...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video.url])
            print(f"✅ İndirme Tamamlandı: {video.title}")
            return True
        except Exception as e:
            print(f"❌ İndirme Hatası ({video.title}): {e}")
            return False

    def _sanitize_filename(self, title: str) -> str:
        if not title:
            return ""
        # Yasaklı karakterleri silme
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
        return safe_title.strip()
