from src.infrastructure.scanners.ytdlp_scanner import YTDLPScanner
import os
from src.infrastructure.downloaders.ytdlp_downloader import YtdlpDownloader
from src.core.services import VideoServices

def main():
    print("🚀 Video Botu Başlatılıyor (Service Mimarisili)...")
    print("-" * 50)

    my_scanner= YTDLPScanner()
    my_downloader = YtdlpDownloader()
    services = VideoServices(scanner=my_scanner,downloader=my_downloader)

    test_url = "https://www.youtube.com/watch?v=xg_7Kw0NpDw"
    download_folder= os.path.join(os.getcwd(),"downloads")
    print("Hedef URL :", test_url)
    print("-"*20)


    try:
        found_videos = services.scan_url(test_url)
    except Exception as e:
        print(f"\n❌ Tarama Hatası: {e}")
        return
    if not found_videos:
        print("\n❌ Tarama Başarısız: Hiç video bulunamadı.")
        return

    video_to_download = found_videos[0]
    print(f"\n✅ Video Bulundu:")
    print(f"   Başlık: {video_to_download.title}")
    print(f"   Kalite: {video_to_download.resolution}")
    print("-" * 50)

    print(f'indirme Başlıyor...')
    print(f"📂 İndirme Konumu: {download_folder}")

    success = services.download_video(video_to_download, download_folder)

    if success:
        print("\n🎉 İŞLEM BAŞARILI!")
        print(f"Video şuraya indirildi: {download_folder}")
    else:
        print("\n❌ İndirme başarısız oldu.")



if __name__=="__main__":
    main()
           
    