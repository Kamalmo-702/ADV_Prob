"""App settings, read from environment variables."""
import os
from dataclasses import dataclass, field


def _origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
    return [o.strip() for o in raw.split(",") if o.strip()]


@dataclass(frozen=True)
class Settings:
    allowed_origins: list[str] = field(default_factory=_origins)


settings = Settings()
