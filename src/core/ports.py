from abc import ABC, abstractmethod
from typing import List
from .entities import Video


class VideoScanner(ABC):
    @abstractmethod
    def scan(self, url: str) -> List[Video]:
        pass


class VideoDownloader(ABC):
    @abstractmethod
    def download(self, video: Video, download_path: str) -> bool:
        pass


class LinkExtractor(ABC):
    @abstractmethod
    def extract_links(self, url: str) -> list[str]:
        pass
