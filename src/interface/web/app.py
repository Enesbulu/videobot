from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    Response,
    stream_with_context,
)
import json, threading, queue, time, os
from src.core.services import VideoServices
from src.infrastructure.factories import ScannerFactory
from src.infrastructure.downloaders.ytdlp_downloader import YtdlpDownloader
from src.core.entities import Video

app = Flask(__name__)
app.secret_key = os.urandom(24)
# Global değişkenler (Basit tutmak için)
crawled_videos = []  # Sonuçları burada toplayacağız


def start_web_app():
    app.run(debug=True, port=5000, threaded=True)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


# region empty_code
# videos = []
# search_url = ""

# if request.method == "POST":
#     search_url = request.form.get("url")
#     is_crawl_mode = request.form.get("crawl_mode") == "on"
#     if search_url:
#         try:
#             scanner = ScannerFactory.get_scanner(search_url)
#             link_extractor = ScannerFactory.get_link_extractor()
#             downloader = YtdlpDownloader()

#             service = VideoServices(
#                 scanner=scanner,
#                 downloader=downloader,
#                 link_extractor=link_extractor,
#             )

#             if is_crawl_mode:
#                 videos = service.craw_url(search_url, max_depth=2, max_pages=5)
#             else:
#                 videos = service.scan_url(search_url)

#             if not videos:
#                 pass
#             #     return render_template(
#             #         "index.html", "Video Bulunamadı", "danger", url=search_url
#             #     )
#             # else:
#             #     return (
#             #         render_template("index.html", videos=videos, url=search_url),
#             #         200,
#             #     )

#         except Exception as e:
#             return render_template("index.html", error=str(e), url=search_url)
#     else:
#         return render_template(
#             "index.html", error="Lütfen geçerli bir URL girin", url=search_url
#         )
# return render_template("index.html", videos=videos, url=search_url)
# endregion


@app.route("/stream_crawl")
def stream_crawl():
    """Server-Sent Events (SSE) ile anlık log akışı sağlar."""
    target_url = request.args.get("url")
    use_crawler = request.args.get("crawler") == "true"

    # KULLANICI AYARLARINI AL (Yoksa Varsayılanı Kullan)
    try:
        p_depth = int(request.args.get("depth", 3))
        p_pages = int(request.args.get("pages", 100))
        p_videos = int(request.args.get("videos", 100))
    except ValueError:
        p_depth = 3
        p_pages = 100
        p_videos = 100

    if not target_url:
        return jsonify({"error": "URL yok"}, 400)

    def generate():
        # Arka plandaki thread ile bu generator arasında köprü olacak kuyruk
        msg_queue = queue.Queue()

        # Crawler'ın çağıracağı callback fonksiyonu
        def on_progress(type_str, payload):
            # Python dict'i JSON stringe çeviriyoruz
            msg = json.dumps({"type": type_str, "payload": payload})
            # SSE formatında (data: ...) kuyruğa atıyoruz
            msg_queue.put(f"data: {msg}\n\n")

        # İşlemi yapan fonksiyon (Thread içinde çalışacak)
        def run_task():
            global crawled_videos
            crawled_videos = []  # Her aramada sıfırla

            try:
                # Servisleri hazırlıyoruz
                scanner = ScannerFactory.get_scanner(target_url)
                link_extractor = ScannerFactory.get_link_extractor()
                download = YtdlpDownloader()
                service = VideoServices(
                    scanner=scanner, downloader=download, link_extractor=link_extractor
                )

                if use_crawler:
                    # Örümcek Modu
                    crawled_videos = service.craw_url(
                        target_url,
                        max_depth=p_depth,
                        max_pages=p_pages,
                        max_videos=p_videos,
                        callback=on_progress,  # Logları buraya akıtıyoruz.
                    )

                else:
                    # Tekil Mode
                    on_progress("log", {"message": "Tekil sayfa taranıyor..."})
                    crawled_videos = service.scan_url(target_url)
                    on_progress(
                        "video_found",
                        {
                            "count": len(crawled_videos),
                            "videos": [v.title for v in crawled_videos],
                        },
                    )
                    on_progress("finish", {"total_videos": len(crawled_videos)})
            except Exception as e:
                on_progress("error", {"message": str(e)})
            finally:
                msg_queue.put("DONE")  # Bitiş sinyali

        # Thread'i başlat (Arka planda çalışsın)
        thread = threading.Thread(target=run_task)
        thread.start()

        # Kuyruktan gelen mesajları tarayıcıya iletme(Stream)
        while True:
            msg = msg_queue.get()
            if msg == "DONE":
                break
            yield msg

    # Tarayıcıya "Bu bir canlı yayındır" diyoruz (mimetype='text/event-stream')
    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/get_results")
def get_results():
    """Tarama bitince videoları JSON olarak döner (Tabloyu doldurmak için)"""
    global crawled_videos
    results = [
        {
            "url": v.url,
            "title": v.title,
            "resolution": v.resolution,
            "duration": v.duration,
        }
        for v in crawled_videos
    ]
    return jsonify(results)


@app.route("/api/download", methods=["POST"])
def api_download():
    """İndirme işlemini yapan endpoint"""
    data = request.json
    video_url = data.get("url")
    video_title = data.get("title")

    if not video_url:
        return jsonify({"success": False, "message": "Geçersiz URL"}), 400
    try:
        scanner = ScannerFactory.get_scanner(video_url)
        downloader = YtdlpDownloader()
        service = VideoServices(scanner=scanner, downloader=downloader)

        video = Video(url=video_url, title=video_title)

        download_path = os.path.join(os.getcwd(), "downloads")
        success = service.download_video(video, download_path)
        if success:
            return jsonify({"success": True, "message": "İndirme Başarılı!"})
        else:

            return jsonify({"success": False, "message": "İndirme Başarısız Oldu!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
