import streamlit as st
import requests
import pandas as pd
import json
import html
from urllib.parse import quote
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any, Tuple

# Import our new modules
from config import api_config, cache_config, ui_config, validation_config
from exceptions import (
    GeoServiceException,
    APIConnectionError,
    RateLimitExceededError,
    LocationNotFoundError,
    InvalidCoordinatesError,
    ValidationError,
    InvalidResponseError
)
from logger import logger
from rate_limiter import rate_limiter
from validators import QueryValidator, CoordinateValidator, ResponseValidator
from styles import DESIGN_SYSTEM_CSS

# Configure Streamlit page
st.set_page_config(
    page_title=ui_config.PAGE_TITLE,
    page_icon=ui_config.PAGE_ICON,
    layout=ui_config.LAYOUT,
    initial_sidebar_state="collapsed"
)

@dataclass
class LocationData:
    """Location search result."""
    original_query: str
    address: str
    zip_code: str
    lat: str
    lng: str
    status: str = "OK"
    error_msg: str = ""
    timestamp: str = ""

class AddressService:
    """Geocoding service using OpenStreetMap Nominatim API."""
    
    @staticmethod
    @st.cache_data(
        ttl=cache_config.TTL_SECONDS,
        show_spinner=False,
        max_entries=cache_config.MAX_CACHE_ENTRIES
    )
    def _fetch_from_api(
        url: str, 
        params: Dict[str, Any], 
        force_english: bool
    ) -> Optional[Any]:
        """
        Fetch data from OSM API with rate limiting and error handling.
        
        Rate limiting is applied inside the function body so that
        cached results bypass the rate limiter entirely.
        """
        # Rate limit inside the function so cache hits skip this
        rate_limiter.acquire(blocking=True)

        headers = {'User-Agent': api_config.USER_AGENT}
        request_params = dict(params)

        if force_english:
            headers['Accept-Language'] = 'en-US,en;q=0.9'
            request_params['accept-language'] = 'en'
        
        try:
            logger.debug("API request to: %s", url)
            
            response = requests.get(
                url,
                params=request_params,
                headers=headers,
                timeout=api_config.TIMEOUT_SECONDS
            )
            
            # Check for rate limiting
            if response.status_code == 429:
                logger.warning("Rate limit exceeded (429)")
                raise RateLimitExceededError()
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            # Parse JSON
            data = response.json()
            logger.info("API response successful: %s", type(data))
            return data
            
        except requests.Timeout:
            logger.error("Request timeout after %ss", api_config.TIMEOUT_SECONDS)
            raise APIConnectionError(
                f"Request timed out after {api_config.TIMEOUT_SECONDS} seconds",
                status_code=None
            )
            
        except requests.HTTPError as e:
            logger.error("HTTP error: %s", e.response.status_code)
            raise APIConnectionError(
                f"HTTP error: {e.response.status_code}",
                status_code=e.response.status_code
            )
            
        except requests.RequestException as e:
            logger.error("Request failed: %s", type(e).__name__)
            raise APIConnectionError("Request failed")
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON response received")
            raise InvalidResponseError("Invalid JSON response from API")
    
    def _reverse_geocode(
        self,
        lat: float,
        lng: float,
        query: str
    ) -> List[LocationData]:
        """
        Perform reverse geocoding (coordinates -> address).
        """
        try:
            # Validate coordinates
            lat_valid, lng_valid = CoordinateValidator.validate(lat, lng)
            
            logger.debug("Reverse geocoding: %s, %s", lat_valid, lng_valid)
            
            # Fetch from API
            data = self._fetch_from_api(
                api_config.OSM_REVERSE_URL,
                {
                    'lat': lat_valid,
                    'lon': lng_valid,
                    'format': 'json'
                },
                force_english=True
            )
            
            if not data:
                raise LocationNotFoundError(query)
            
            # Validate response
            ResponseValidator.validate_osm_reverse_response(data)
            
            # Extract data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            address = data.get('display_name', 'Unknown')
            zip_code = data.get('address', {}).get('postcode', '—')
            
            logger.debug("Reverse geocoding successful")
            
            return [LocationData(
                original_query=query,
                address=address,
                zip_code=zip_code,
                lat=str(lat_valid),
                lng=str(lng_valid),
                status="OK",
                timestamp=timestamp
            )]
            
        except GeoServiceException:
            raise
        except Exception as e:
            logger.error("Reverse geocoding failed: %s", type(e).__name__)
            raise APIConnectionError("Reverse geocoding failed") from e
    
    def search(self, raw_query: str) -> List[LocationData]:
        """
        Search for location by query (address or coordinates).
        """
        try:
            # Validate and sanitize input
            query = QueryValidator.validate(raw_query)
            query = QueryValidator.sanitize(query)
            
            logger.debug("Search initiated")
            
            # Try to parse as coordinates first
            coords = CoordinateValidator.parse_from_query(query, strict=True)
            if coords:
                lat, lng = coords
                logger.debug("Query identified as coordinates")
                return self._reverse_geocode(lat, lng, query)
            
            # Search by address — force English so Hebrew queries return English addresses
            logger.debug("Searching by address")
            search_results = self._fetch_from_api(
                api_config.OSM_SEARCH_URL,
                {
                    'q': query,
                    'format': 'json',
                    'limit': api_config.MAX_SEARCH_RESULTS,
                    'countrycodes': api_config.DEFAULT_COUNTRY_CODE,
                    'addressdetails': 1
                },
                force_english=True
            )

            if not search_results:
                raise LocationNotFoundError(query)

            # Validate response
            ResponseValidator.validate_osm_search_response(search_results)

            # Process results directly from search response
            results = []
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for item in search_results:
                lat = item.get('lat')
                lng = item.get('lon')
                address = item.get('display_name')
                zip_code = item.get('address', {}).get('postcode', '')

                if lat and lng and address:
                    # If no postal code from search, try reverse geocode
                    if not zip_code:
                        try:
                            reverse_data = self._fetch_from_api(
                                api_config.OSM_REVERSE_URL,
                                {
                                    'lat': lat,
                                    'lon': lng,
                                    'format': 'json',
                                    'addressdetails': 1
                                },
                                force_english=True
                            )
                            if reverse_data:
                                zip_code = reverse_data.get('address', {}).get('postcode', '—')
                        except Exception:
                            logger.debug("Reverse geocode for postcode failed, skipping")
                            zip_code = '—'
                    
                    results.append(LocationData(
                        original_query=query,
                        address=address,
                        zip_code=zip_code if zip_code else '—',
                        lat=str(lat),
                        lng=str(lng),
                        status="OK",
                        timestamp=timestamp
                    ))
                    continue

                if lat and lng:
                    fallback_results = self._reverse_geocode(
                        float(lat), float(lng), query
                    )
                    results.extend(fallback_results)

            if not results:
                raise LocationNotFoundError(query)

            logger.debug("Search successful: %s results", len(results))
            return results
            
        except GeoServiceException:
            raise
        except Exception as e:
            logger.error("Unexpected error in search: %s", type(e).__name__)
            raise APIConnectionError("Search failed") from e

# ─── UI Rendering Functions ──────────────────────────────────────────────────

def inject_design_system() -> None:
    """Inject CSS design system into the app."""
    st.markdown(DESIGN_SYSTEM_CSS, unsafe_allow_html=True)


def render_search_hero() -> Tuple[str, bool]:
    """Render the hero copy and search form."""
    st.markdown("""
        <section class="hero-shell">
            <div class="hero-badge">NODE_IL // ONLINE</div>
            <h1 class="hero-title">GEOSTUDIO//IL</h1>
        </section>
    """, unsafe_allow_html=True)

    with st.form("search", clear_on_submit=False):
        st.markdown('<div class="search-form-marker"></div>', unsafe_allow_html=True)
        st.markdown('<div class="terminal-label">INPUT :: ADDRESS / COORDINATES</div>', unsafe_allow_html=True)
        query = st.text_input(
            "Search",
            value=st.session_state.get("last_query", ""),
            placeholder="type hebrew address or lat,lon",
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("Search", use_container_width=True)

    return query, submitted


def render_example_chips() -> None:
    """Render example chips in a symmetric two-by-two layout."""
    st.markdown("""
        <div class="example-shell">
            <div class="example-label">Quick examples</div>
        </div>
    """, unsafe_allow_html=True)

    examples = ui_config.EXAMPLE_QUERIES
    for row_start in range(0, len(examples), 2):
        row = st.columns(2)
        for index, example in enumerate(examples[row_start:row_start + 2]):
            with row[index]:
                if st.button(example, key=f"example_{row_start + index}", use_container_width=True):
                    st.session_state.last_query = example
                    st.session_state.auto_search = True
                    st.rerun()


def render_empty_guidance() -> None:
    """Render compact empty guidance under the hero."""
    st.markdown("""
        <section class="empty-guidance">
            <div class="empty-kicker">SYSTEM_IDLE</div>
            <h2 class="empty-title">Awaiting query</h2>
        </section>
    """, unsafe_allow_html=True)


def build_metric_card(
    label: str,
    value: str,
    *,
    mono: bool = False,
    highlight: bool = False,
    query_text: bool = False
) -> str:
    """Build metric card markup."""
    value_classes = ["metric-value"]
    if mono:
        value_classes.append("metric-value--mono")
    if query_text:
        value_classes.append("metric-value--query")

    card_class = "metric-card metric-card--highlight" if highlight else "metric-card"
    return (
        f'<div class="{card_class}">'
        f'<div class="metric-label">{html.escape(label)}</div>'
        f'<div class="{" ".join(value_classes)}">{html.escape(value)}</div>'
        "</div>"
    )


def render_result_overview(data: LocationData) -> None:
    """Render the main result card and the symmetric metric grid."""
    postal_value = data.zip_code if data.zip_code and data.zip_code != "—" else "Not available"
    safe_address = html.escape(data.address)
    metrics_html = "".join([
        build_metric_card("Original query", data.original_query, query_text=True),
        build_metric_card("Postal code", postal_value, mono=True, highlight=True),
        build_metric_card("Latitude", f"{float(data.lat):.6f}", mono=True),
        build_metric_card("Longitude", f"{float(data.lng):.6f}", mono=True),
    ])

    st.markdown(f"""
        <section class="result-shell">
            <div class="result-badge">MATCH_LOCKED</div>
            <div class="result-section-label">ENGLISH_MATCH</div>
            <div class="result-address">{safe_address}</div>
            <div class="metrics-grid">
                {metrics_html}
            </div>
        </section>
        <section class="detail-strip">
            <div class="detail-item">
                <span class="detail-key">Source</span>
                <span class="detail-value">OpenStreetMap Nominatim</span>
            </div>
            <div class="detail-item">
                <span class="detail-key">Resolved at</span>
                <span class="detail-value">{html.escape(data.timestamp)}</span>
            </div>
        </section>
    """, unsafe_allow_html=True)


def render_map_panel(data: LocationData) -> None:
    """Render the map panel."""
    st.markdown("""
        <div class="panel-marker panel-marker--map"></div>
        <div class="panel-heading">
            <div class="panel-kicker">MAP_NODE</div>
            <h3 class="panel-title">GRID</h3>
        </div>
    """, unsafe_allow_html=True)

    try:
        st.map(
            pd.DataFrame({
                "lat": [float(data.lat)],
                "lon": [float(data.lng)],
            }),
            zoom=ui_config.RESULT_MAP_ZOOM
        )
    except Exception as exc:
        logger.error("Map display error: %s", type(exc).__name__)
        render_status_message(
            "Map unavailable",
            "The map could not be rendered for this result.",
            "You can still open the location in Google Maps.",
            "error"
        )


def render_action_panel(data: LocationData) -> None:
    """Render the right-side action panel."""
    st.markdown("""
        <div class="panel-marker panel-marker--actions"></div>
        <div class="panel-heading">
            <div class="panel-kicker">ACTIONS</div>
            <h3 class="panel-title">EXECUTE</h3>
        </div>
    """, unsafe_allow_html=True)

    safe_coords = quote(f"{data.lat},{data.lng}", safe="")
    st.link_button(
        "Open in Google Maps",
        f"https://www.google.com/maps/search/?api=1&query={safe_coords}",
        use_container_width=True
    )
    st.download_button(
        "Export JSON",
        data=json.dumps(asdict(data), indent=2, ensure_ascii=False),
        file_name=f"location_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )
    if st.button("New search", use_container_width=True, key="new_search"):
        st.session_state.last_result = None
        st.rerun()

def render_result_panels(data: LocationData) -> None:
    """Render the symmetric lower two-panel section."""
    left_col, right_col = st.columns(2)

    with left_col:
        render_map_panel(data)

    with right_col:
        render_action_panel(data)


def render_status_message(title: str, body: str, hint: str, variant: str) -> None:
    """Render a structured status card."""
    variant_map = {
        "warning": ("status-card--warning", "WARN"),
        "error": ("status-card--error", "ERROR"),
        "info": ("status-card--info", "INFO"),
    }
    css_class, badge = variant_map.get(variant, variant_map["info"])

    st.markdown(f"""
        <section class="status-card {css_class}">
            <div class="status-meta">{badge}</div>
            <h3 class="status-title">{html.escape(title)}</h3>
            <p class="status-body">{html.escape(body)}</p>
            <p class="status-hint">{html.escape(hint)}</p>
        </section>
    """, unsafe_allow_html=True)


def render_loading_state() -> None:
    """Render a lightweight loading callout."""
    render_status_message(
        "QUERY_RUNNING",
        "Resolving target.",
        "Stand by.",
        "info"
    )


def render_footer() -> None:
    """Render the application footer."""
    st.markdown("""
        <footer class="app-footer">
            <span>GEOSTUDIO//IL</span>
            <span class="footer-divider">::</span>
            <span>NOMINATIM</span>
        </footer>
    """, unsafe_allow_html=True)


def init_session_state() -> None:
    """Initialize Streamlit session state."""
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""


def main() -> None:
    """Main application entry point."""
    inject_design_system()
    init_session_state()

    query, submitted = render_search_hero()
    should_search = submitted
    status_message: Optional[Tuple[str, str, str, str]] = None

    if should_search:
        query_to_search = query or ""
        st.session_state.last_query = query_to_search
        st.session_state.last_result = None
        loading_placeholder = st.empty()

        try:
            service = AddressService()
            with loading_placeholder.container():
                render_loading_state()
            with st.spinner("Searching OpenStreetMap..."):
                results = service.search(query_to_search)

            if results and results[0].status == "OK":
                st.session_state.last_result = results[0]
            else:
                status_message = (
                    "No matching address found",
                    "The geocoder did not return a usable result.",
                    "Try a broader place name or remove extra detail.",
                    "warning",
                )

        except LocationNotFoundError:
            logger.warning("Location not found: %s", query_to_search)
            status_message = (
                "No matching address found",
                "We could not find a result for that query.",
                "Try a broader place name or remove extra detail. Results are limited to Israel.",
                "warning",
            )

        except ValidationError as exc:
            logger.warning("Validation error: %s", exc)
            status_message = (
                "Check the format",
                "Use a street, place name, or coordinates.",
                "Example: קישון 87 תל אביב",
                "warning",
            )

        except InvalidCoordinatesError as exc:
            logger.warning("Invalid coordinates: %s", exc)
            status_message = (
                "Check the format",
                "Coordinates must use valid latitude and longitude values.",
                "Example: 31.7683, 35.2137",
                "warning",
            )

        except RateLimitExceededError:
            logger.warning("Rate limit exceeded")
            status_message = (
                "Too many requests",
                "The geocoding service asked us to slow down.",
                "Wait a few seconds and try again.",
                "warning",
            )

        except APIConnectionError as exc:
            logger.error("API connection error: %s", exc)
            status_message = (
                "Location service is unavailable",
                "We could not reach the geocoding service right now.",
                "Please try again in a moment. The app may be waking up from sleep.",
                "error",
            )

        except GeoServiceException as exc:
            logger.error("Service error: %s", exc)
            status_message = (
                "Location service is unavailable",
                "The lookup failed before a result could be returned.",
                "Please try again in a moment. The app may be waking up from sleep.",
                "error",
            )

        except Exception as exc:
            logger.error("Unexpected error: %s", exc, exc_info=True)
            status_message = (
                "Unexpected error",
                "Something went wrong while processing your query.",
                "Please try again in a moment.",
                "error",
            )

        finally:
            loading_placeholder.empty()

    if status_message:
        render_status_message(*status_message)

    if st.session_state.last_result:
        render_result_overview(st.session_state.last_result)
        render_result_panels(st.session_state.last_result)
    else:
        render_empty_guidance()

    render_footer()

if __name__ == "__main__":
    main()
