import os
import sys
from src.core.services import VideoServices
from src.infrastructure.factories import ScannerFactory
from src.infrastructure.downloaders.ytdlp_downloader import YtdlpDownloader
from src.interface.console import ConsoleUI


def main():
    ui = ConsoleUI()
    ui.show_header()

    # print("🚀 Akıllı Video Botu (v0.2 Factory)")
    # print("-" * 50)

    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = ui.get_input("🔗 Video Linkini Yapıştır: ").strip()

    if not target_url:
        ui.show_error("Link girmediniz.")
        return

    download_folder = os.path.join(os.getcwd(), "downloads")
    print("Hedef URL :", target_url)
    print("-" * 20)

    try:
        with ui.create_spinner("Fabrika uygun tarayıcıyı seçiyor..."):
            selected_scanner = ScannerFactory.get_scanner(target_url)
        downloader = YtdlpDownloader()
        services = VideoServices(scanner=selected_scanner, downloader=downloader)
    except Exception as e:
        ui.show_error(f"❌ Fabrika Hatası: {e}")
        return

    ui.show_message(
        f"📡 Analiz Ediliyor: [underline]{target_url}[/underline]", style="yellow"
    )
    found_videos = []
    with ui.create_spinner("Videolar aranıyor..."):
        found_videos = services.scan_url(target_url)

    if not found_videos:
        ui.show_error("❌ Video bulunamadı.")
        return
    ui.show_video_table(found_videos)
    chosen_video = found_videos[0]

    ui.show_message(f"\n⬇️  İndirme Başlatılıyor: [bold]{chosen_video.title}[/bold]")
    with ui.create_spinner("İndiriliyor..."):
        succes = services.download_video(chosen_video, download_folder)

    if succes:
        ui.show_success(f"🎉 İşlem Başarılı! \n📂 Konum: {download_folder}")
    else:
        ui.show_error("❌ İndirme başarısız.")


if __name__ == "__main__":
    main()
