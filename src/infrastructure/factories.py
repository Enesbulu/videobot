from src.core.ports import videoScanner
from src.infrastructure.scanners.ytdlp_scanner import YTDLPScanner
from src.infrastructure.scanners.bs4_scanner import BS4Scanner

class ScannerFactory:
    @staticmethod
    def get_scanner(url: str) -> videoScanner:
        if "youtube.com" in url or "youtube.be" in url:
            print("🏭 Factory: YouTube altyapısı seçildi.")
            return YTDLPScanner()
        else:
            print("🏭 Factory: Standart HTML5 (Generic) altyapısı seçildi.")
            return BS4Scanner()
