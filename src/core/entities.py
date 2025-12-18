from dataclasses import dataclass
from typing import Optional


@dataclass
class Video:
    url: str
    title: str
    duration: Optional[int] = None  # Duration in seconds
    resolution: Optional[str] = None  # e.g., '1080p', '720p'
    thumbnail_url: Optional[str] = None
    file_size: Optional[int] = None  # File size in bytes

    def __str__(self):
        return f"[{self.resolution or 'Unknown Resolution'}] {self.title} ({self.duration or 'Unknown Duration'}s)"