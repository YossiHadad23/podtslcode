"""Configuration Module."""

from dataclasses import dataclass
from typing import Final, Tuple


@dataclass(frozen=True)
class APIConfig:
    """API configuration."""
    OSM_SEARCH_URL: str = "https://nominatim.openstreetmap.org/search"
    OSM_REVERSE_URL: str = "https://nominatim.openstreetmap.org/reverse"
    USER_AGENT: str = "GeoStudioAI/2.0"
    TIMEOUT_SECONDS: int = 10
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_FACTOR: float = 2.0
    MAX_REQUESTS_PER_SECOND: float = 1.0
    MAX_SEARCH_RESULTS: int = 3
    DEFAULT_COUNTRY_CODE: str = "il"


@dataclass(frozen=True)
class CacheConfig:
    """Caching configuration."""
    TTL_SECONDS: int = 3600
    MAX_CACHE_ENTRIES: int = 1000


@dataclass(frozen=True)
class UIConfig:
    """UI configuration."""
    PAGE_TITLE: str = "GeoStudio AI"
    PAGE_ICON: str = "◉"
    LAYOUT: str = "wide"
    MAX_HISTORY_ITEMS: int = 50
    DISPLAY_HISTORY_ITEMS: int = 5
    MAX_QUERY_LENGTH: int = 500
    MAX_ADDRESS_DISPLAY_LENGTH: int = 60
    EXAMPLE_QUERIES: Tuple[str, ...] = (
        "קישון 87 תל אביב",
        "דיזנגוף סנטר תל אביב",
        "31.7683, 35.2137",
        "Ben Gurion Airport",
    )
    SEARCH_HELP_TEXT: str = "Hebrew queries are supported. Results are normalized to English."
    RESULT_MAP_ZOOM: int = 15
    RESULT_NOTE: str = "Results use the best available OpenStreetMap match for Israel."


@dataclass(frozen=True)
class ValidationConfig:
    """Input validation settings."""
    MIN_LATITUDE: float = -90.0
    MAX_LATITUDE: float = 90.0
    MIN_LONGITUDE: float = -180.0
    MAX_LONGITUDE: float = 180.0
    MIN_QUERY_LENGTH: int = 1
    MAX_QUERY_LENGTH: int = 500


api_config: Final = APIConfig()
cache_config: Final = CacheConfig()
ui_config: Final = UIConfig()
validation_config: Final = ValidationConfig()
