from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    shorts_count: int = 5
    x_count: int = 10
    instagram_count: int = 3
    line_count: int = 1
    title_count: int = 5
    thumbnail_count: int = 5
    x_max_chars: int = 280
    model: str = "gpt-5.4"
    api_url: str = "https://api.openai.com/v1/responses"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            model=os.getenv("TOSHIKUN_MODEL", cls.model),
            api_url=os.getenv("TOSHIKUN_API_URL", cls.api_url),
        )

    def counts(self) -> dict[str, int]:
        return {
            "shorts": self.shorts_count,
            "x_posts": self.x_count,
            "instagram": self.instagram_count,
            "line": self.line_count,
            "youtube_titles": self.title_count,
            "thumbnail_phrases": self.thumbnail_count,
        }
