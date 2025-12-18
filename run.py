import os
from src.core.services import VideoServices
from src.infrastructure.scanners.bs4_scanner import BS4Scanner
from src.infrastructure.downloaders.ytdlp_downloader import YtdlpDownloader

def main():
    print("🚀 Video Botu Başlatılıyor (Service Mimarisili)...")
    print("-" * 50)
    my_scanner = BS4Scanner()
    my_downloader = YtdlpDownloader()
    services = VideoServices(scanner=my_scanner,downloader=my_downloader)

    test_url = "https://www.w3schools.com/html/html5_video.asp"
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
           
    