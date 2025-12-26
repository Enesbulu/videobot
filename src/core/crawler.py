from typing import List, Set, Callable, Optional
from urllib.parse import urlparse
from src.core.entities import Video
from src.core.ports import VideoScanner, LinkExtractor
import time


class Crawler:
    """
    Web sitesini örümcek ağı gibi gezerek (Crawling) video arayan sınıf.
    """

    def __init__(self, scanner: VideoScanner, link_extractor: LinkExtractor):
        self.scanner = scanner
        self.link_extractor = link_extractor
        # Ziyaret edilmiş olan linkler (işlemleri bitmiş)
        self.visited_urls: Set[str] = set()
        # Bulunan videoların temizlenmiş URL'lerini burada tutacağız (Hafıza)
        self.seen_video_urls: Set[str] = set()
        # Görülen Video Başlıkları (Aynı isimli videoları engellemek için
        self.seen_titles: Set[str] = set()

    def _get_clean_url(self, url: str) -> str:
        """
        URL'i parametrelerden (?token=...) arındırır ve normalize eder.
        Böylece video.mp4?a=1 ile video.mp4?a=2 aynı sayılır.
        """
        try:
            parsed = urlparse(url)
            # Sadece scheme (https), netloc (site.com) ve path (/video.mp4) kısmını al
            clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            return clean
        except:
            return url

    def start_crawling(
        self,
        start_url: str,
        max_depth: int = 3,
        max_pages: int = 100,
        max_videos: int = 100,
        progress_callback: Optional[Callable[[str, dict], None]] = None,
    ) -> List[Video]:
        """
        Belirtilen URL'den başlar ve max_depth kadar derine inerek tarar.
        Args:
            start_url: Başlangıç adresi.
            max_depth: Ne kadar derine inileceği (0: Sadece ana sayfa, 1: Ana sayfa + linkleri).
        """
        # region Tanımlamalar

        all_videos: List[Video] = []  # toplanan bütün videoları tutar.
        start_domain = urlparse(start_url).netloc.replace("www", "")

        # Hafızaları sıfırla
        self.visited_urls.clear()
        self.seen_video_urls.clear()
        self.seen_titles.clear()

        queued_urls: Set[str] = {
            start_url
        }  # Kuyruğa daha önce eklenmiş linkleri tutar.  visited_urls'den farkı: Henüz ziyaret edilmemiş ama sırada bekleyenleri de bilir.
        queue = [(start_url, 0)]  # iş kuyruğu : URL ve derinlik
        pages_visited_count = 0  # Gezilen sayfa sayacı

        # Tanımlama: Emit Fonksiyonu -- UI mesaj göndermeyi kolaylaştıran yardımcı bir fonksiyon
        def emit(type_str, message, extra_data=None):
            if progress_callback:
                payload = {
                    "message": message,
                    "stats": {
                        "pages": pages_visited_count,
                        "videos": len(all_videos),
                        "queue": len(queue),
                        "max_pages": max_pages,
                    },
                }
                if extra_data:
                    payload.update(extra_data)
                progress_callback(type_str, payload)
            time.sleep(0.02)

        emit(
            "log",
            f"🕷️ Örümcek Modu Başladı: {start_url} (Derinlik: {max_depth} (Limit: {max_pages} Sayfa))",
        )

        print(f"--> İzin Verilen Ana Domain: {start_domain} ")

        # endregion

        while queue:
            time.sleep(0.1)  # sisteme dinlenme süresi vermek için
            # --- 1. Güvenlik Limitleri ---
            # region Güvenlik Tanımlamaları
            # GÜVENLİK FRENİ: Eğer Ziyaret edilecek sayfa limit dolduysa dur!
            if pages_visited_count >= max_pages:
                emit("warning", f"🛑 Sayfa limiti ({max_pages}) doldu.")
                break

            # GÜVENLİK FRENİ: Eğer Toplanacak max video limiti dolduysa dur!
            if len(all_videos) >= max_videos:
                emit("success", f"🎉 Video limiti ({max_videos}) doldu.")
                break

            current_url, current_depth = queue.pop(0)

            # Ziyaret kontrolü
            if current_url in self.visited_urls:
                continue

            self.visited_urls.add(current_url)
            pages_visited_count += 1

            # DURUM GÜNCELLEME (Log olarak basma, sadece status güncelle)
            emit(
                "status",
                f"Taranıyor ({pages_visited_count}/{max_pages}): {current_url}",
            )
            # endregion

            # 2. Video Tara
            # region Video Tarama
            try:
                found = self.scanner.scan(current_url)
                if found:
                    new_videos_count = 0
                    new_videos_in_page = []

                    emit(
                        "status",
                        f"Ziyaret Ediliyor ({pages_visited_count}/{max_pages})",
                        {"url": current_url},
                    )
                    # all_videos.extend(found)
                    for v in found:
                        # --- TEKİLLİK KONTROLÜ (GELİŞMİŞ) ---
                        clean_url = self._get_clean_url(v.url)

                        # Başlık Temizliği (Boşlukları sil, küçük harfe çevir) ---
                        clean_title = v.title.strip().lower() if v.title else ""

                        # Eğer bu temiz URL daha önce görülmediyse ekle
                        if (clean_url not in self.seen_video_urls) and (
                            clean_title not in self.seen_titles
                        ):
                            self.seen_video_urls.add(clean_url)
                            if clean_title:
                                self.seen_titles.add(clean_title)
                            all_videos.append(v)
                            new_videos_in_page.append(v.title)
                            new_videos_count += 1

                        # # video daha önce eklendi mi kontorlü
                        # if not any(
                        #     existing.url == v.url for existing in all_videos
                        # ):  ## existing ==> Generator Expression -- geçici bir değişken (placeholder)
                        #     all_videos.append(v)
                        #     new_videos_count += 1
                        #     new_videos_in_page.append(v.title)

                    if new_videos_count > 0:
                        # Sadece yeni video varsa LOG bas
                        emit(
                            "video_found",
                            f"✅ {new_videos_count} Yeni Video: {', '.join(new_videos_in_page)[:50]}...",
                        )

                else:
                    print(f"   ⚪ Video yok.")
            except Exception as e:
                emit("error", f"⚠️Tarama Hatası: ({current_url}) : {str(e)}")

            # Derinlik limiti kontrolü
            if current_depth >= max_depth:
                print("   🛑 Derinlik limitine ulaşıldı, link aranmayacak.")
                continue
            # endregion

            # 3. LİNK TOPLAMA (LinkExtractor kullanımı)
            # region Link Toplama
            try:
                links = self.link_extractor.extract_links(current_url)
                print(f"   🔗 Sayfadaki Link Sayısı: {len(links)}")
                # new_links_count = 0
                max_len_links = 500
                for link in links:
                    # Güvenlik1 : Kuyruk çok şişerse yeni link alma
                    if len(queue) > max_len_links:
                        break

                    # ---URL Normalizasyonu---
                    # 1. Her şeyi HTTPS yap(http ile https aynı yerdir.)
                    if link.startswith("http://"):
                        link = link.replace("http://", "https://")

                    # 2.Sondaki gereksiz slash işaretini sil(site.com/a/ -> site.com/a gibi)
                    link = link.rstrip("/")

                    # 3. Fragment(yorumlar ) kısmı temizleme
                    if "#" in link:
                        link = link.split("#")[0]

                    # Linkin domainini al ve www.'yu sil
                    link_domain = urlparse(link).netloc.replace("www", "")

                    # Domain Kontrolü (Daha esnek)
                    if start_domain in link_domain:
                        # Hem ziyaret edilmemiş hem de kuyrukta yoksa ekle
                        if link not in self.visited_urls and link not in queued_urls:
                            queue.append((link, current_depth + 1))
                            queued_urls.add(
                                link
                            )  # Artık bunu kuyruğa attık, not alıyoruz
                            # new_links_count += 1
                        else:
                            # Farklı site (Örn: facebook, twitter linkleri)
                            # print(f"   🚫 Dış Link: {link_domain}") # Çok kirlilik yapmasın diye kapalı
                            pass
                    # if new_links_count > 0:
                    #     emit(
                    #         "log",
                    #         f"🔗 Bu sayfadan {new_links_count} yeni link kuyruğa eklendi.",
                    #     )

            except Exception as e:
                emit("error", f"   ⚠️ Link Hatası: {e}")
                continue
        # endregion

        emit(
            "finish",
            f"🏁 --- CRAWLER BİTTİ (Toplam Video: {len(all_videos)}, Toplam Saysa: {pages_visited_count}) ---\n",
        )
        return all_videos
