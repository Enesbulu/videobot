from src.core.ports import VideoScanner, LinkExtractor
from src.infrastructure.scanners.ytdlp_scanner import YTDLPScanner
from src.infrastructure.scanners.bs4_scanner import BS4Scanner
from src.infrastructure.scanners.bs4_link_extractor import Bs4LinkExtractor


class ScannerFactory:
    @staticmethod
    def get_scanner(url: str) -> VideoScanner:
        if "youtube.com" in url or "youtube.be" in url:
            print("🏭 Factory: YouTube altyapısı seçildi.")
            return YTDLPScanner()
        else:
            print("🏭 Factory: Standart HTML5 (Generic) altyapısı seçildi.")
            return BS4Scanner()

    @staticmethod
    def get_link_extractor() -> LinkExtractor:
        return Bs4LinkExtractor()
