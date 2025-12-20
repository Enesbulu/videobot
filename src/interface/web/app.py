from flask import Flask, render_template, request, jsonify
import os

from src.core.services import VideoServices
from src.infrastructure.factories import ScannerFactory
from src.infrastructure.downloaders.ytdlp_downloader import YtdlpDownloader
from src.core.entities import Video

app = Flask(__name__)
app.secret_key = os.urandom(24)


def start_web_app():
    app.run(debug=True, port=5000)


@app.route("/", methods=["GET", "POST"])
def index():
    video = []
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            try:
                scanner = ScannerFactory.get_scanner(url)
                downloader = YtdlpDownloader()
                service = VideoServices(scanner=scanner, downloader=downloader)
                videos = service.scan_url(url)

                if not videos:
                    return render_template(
                        "index.html", "Video Bulunamadı", "danger", url=url
                    )
                else:
                    return render_template("index.html", videos=videos, url=url), 200

            except Exception as e:
                return render_template("index.html", error=str(e), url=url)
        else:
            return render_template(
                "index.html", error="Lütfen geçerli bir URL girin", url=url
            )
    return render_template("index.html", videos=videos, url=search_url)


@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.json
    url = data.get("url")
    title = data.get("title")

    if not url:
        return jsonify({"success": False, "message": "Geçersiz URL"}), 400
    try:
        scanner = ScannerFactory.get_scanner(url)
        downloader = YtdlpDownloader()
        service = VideoServices(scanner=scanner, downloader=downloader)

        video = Video(url=url, title=title)

        download_path = os.path.join(os.getcwd(), "downloads")
        success = service.download_video(video, download_path)
        if success:
            return jsonify({"success": True, "message": "İndirme Başarılı!"})
        else:

            return jsonify({"success": False, "message": "İndirme Başarısız Oldu!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
