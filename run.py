import os
import sys 
from src.core.services import VideoServices
from src.infrastructure.factories import ScannerFactory
from src.infrastructure.downloaders.ytdlp_downloader import YtdlpDownloader 

def main():
    print("🚀 Akıllı Video Botu (v0.2 Factory)")
    print("-" * 50)
   
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = input("🔗 Video Linkini Yapıştır: ").strip()

    if not target_url:
        print("❌ Link girmediniz.")
        return
    
    download_folder= os.path.join(os.getcwd(),"downloads")
    print("Hedef URL :", target_url)
    print("-"*20)

    try:
        selected_scanner = ScannerFactory.get_scanner(target_url)
    except Exception as e:
        print(f"❌ Fabrika Hatası: {e}")
        return
    
    downloader = YtdlpDownloader()
    services = VideoServices(scanner=selected_scanner,downloader=downloader)

    print(f"📡 Analiz Ediliyor: {target_url}")
    found_videos = services.scan_url(target_url)

    if not found_videos:
        print("❌ Video bulunamadı.")
        return

    # Bulunan videoları listele
    print(f"\n✅ {len(found_videos)} video bulundu:")
    for i, v in enumerate(found_videos, 1):
        print(f"{i}. {v.title} ({v.resolution})")

    # Otomatik olarak ilkini indir (İleride seçim yaptırabiliriz)
    chosen_video = found_videos[0]
    
    print(f"\n⬇️  İndiriliyor: {chosen_video.title}")
    success = services.download_video(chosen_video, download_folder)

    if success:
        print(f"🎉 İşlem Başarılı! \n📂 Konum: {download_folder}")
    else:
        print("❌ İndirme başarısız.")



if __name__=="__main__":
    main()
           
    