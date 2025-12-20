import sys
import argparse  # Argümanları okumak için kütüphane


def run_cli():
    """Mevcut Konsol Arayüzünü Başlatır"""
    # CLI kodlarını buraya taşıdık (importlar sadece ihtiyaç olunca yapılır)
    from src.interface.console import ConsoleUI
    from src.infrastructure.factories import ScannerFactory
    from src.infrastructure.downloaders.ytdlp_downloader import YtdlpDownloader
    from src.core.services import VideoServices
    import os

    ui = ConsoleUI()
    ui.show_header()

    target_url = ui.get_input("🔗 Video Linkini Yapıştır:")
    if not target_url:
        return

    try:
        with ui.create_spinner("Analiz ediliyor..."):
            scanner = ScannerFactory.get_scanner(target_url)

        service = VideoServices(scanner=scanner, downloader=YtdlpDownloader())

        ui.show_message(f"📡 Hedef: {target_url}", "blue")
        videos = service.scan_url(target_url)

        if not videos:
            ui.show_error("Video bulunamadı.")
            return

        ui.show_video_table(videos)

        # Otomatik indirme (CLI için)
        video = videos[0]
        with ui.create_spinner("İndiriliyor..."):
            service.download_video(video, os.path.join(os.getcwd(), "downloads"))

        ui.show_success("İşlem Tamamlandı!")

    except Exception as e:
        ui.show_error(str(e))


def run_web():
    """Yeni Web Arayüzünü Başlatır"""
    from src.interface.web.app import start_web_app

    print("🌐 Web Arayüzü Başlatılıyor: http://127.0.0.1:5000")
    start_web_app()


if __name__ == "__main__":
    # Argüman okuyucu (Parser) oluştur
    parser = argparse.ArgumentParser(description="Video Downloader Bot")
    parser.add_argument("--web", action="store_true", help="Web arayüzünü başlatır")

    args = parser.parse_args()

    if args.web:
        run_web()
    else:
        run_cli()
