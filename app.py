import streamlit as st
import requests
import pandas as pd
import json
import html
import time
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

def render_header() -> None:
    """Render the application header."""
    st.markdown("""
        <div class="brand-header">
            <div class="brand-logo">
                <span class="brand-logo-icon">◉</span>
            </div>
            <h1 class="brand-title">GeoStudio AI</h1>
            <p class="brand-tagline">Location Intelligence Platform</p>
        </div>
    """, unsafe_allow_html=True)

def render_empty_state() -> None:
    """Render the empty state with example search suggestions."""
    st.markdown("""
        <div class="empty-state">
            <div class="empty-illustration">🌍</div>
            <h2 class="empty-title">Discover Any Location</h2>
            <p class="empty-description">
                Search by address, city name, or GPS coordinates to get verified location data with interactive maps.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    # Example buttons — centered with proper spacing
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏢 Azrieli Tower, Tel Aviv", use_container_width=True, key="ex1"):
            st.session_state.search_query = "Azrieli Tower, Tel Aviv"
            st.rerun()
    with col2:
        if st.button("📍 31.7683, 35.2137", use_container_width=True, key="ex2"):
            st.session_state.search_query = "31.7683, 35.2137"
            st.rerun()
    with col3:
        if st.button("🌊 Tel Aviv Port", use_container_width=True, key="ex3"):
            st.session_state.search_query = "Tel Aviv Port"
            st.rerun()

def render_result_card(data: LocationData) -> None:
    """Render the unified result card with location data."""
    # Security: Escape HTML entities to prevent XSS
    safe_address = html.escape(data.address)
    postal_value = data.zip_code if data.zip_code and data.zip_code != "—" else "Not Available"
    safe_postal = html.escape(postal_value)
    
    # Main Result Card — unified layout with all data
    st.markdown(f"""
        <div class="result-card">
            <div class="result-status">Location Found</div>
            <div class="result-address">{safe_address}</div>
            <div class="result-data-grid">
                <div class="result-data-item">
                    <div class="data-label">📮 Postal Code</div>
                    <div class="data-value">{safe_postal}</div>
                </div>
                <div class="result-data-item">
                    <div class="data-label">📍 Latitude</div>
                    <div class="data-value">{float(data.lat):.6f}</div>
                </div>
                <div class="result-data-item">
                    <div class="data-label">📍 Longitude</div>
                    <div class="data-value">{float(data.lng):.6f}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Action Buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "📥 Export JSON",
            data=json.dumps(asdict(data), indent=2, ensure_ascii=False),
            file_name=f"location_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Security: URL-encode coordinates to prevent injection
        safe_coords = quote(f"{data.lat},{data.lng}", safe='')
        st.link_button(
            "🗺️ Open in Google Maps",
            f"https://www.google.com/maps/search/?api=1&query={safe_coords}",
            use_container_width=True
        )
    
    with col3:
        if st.button("🔄 New Search", use_container_width=True, key="new_search"):
            st.session_state.last_result = None
            st.rerun()

    # Interactive Map (expanded by default for better UX)
    st.write("")
    with st.expander("🗺️ Interactive Map", expanded=True):
        try:
            st.map(
                pd.DataFrame({
                    'lat': [float(data.lat)], 
                    'lon': [float(data.lng)]
                }),
                zoom=15
            )
        except Exception as e:
            logger.error("Map display error: %s", type(e).__name__)
            st.error("Could not display map")

def render_search() -> Tuple[str, bool]:
    """
    Render the search form.
    
    Returns:
        Tuple of (query, submitted)
    """
    with st.form("search", clear_on_submit=False):
        col1, col2 = st.columns([5, 1])
        with col1:
            q = st.text_input(
                "Search",
                value=st.session_state.get('search_query', ''),
                placeholder="Enter address, city, or coordinates...",
                label_visibility="collapsed"
            )
        with col2:
            submitted = st.form_submit_button("🔍 Search", use_container_width=True)
    
    # Only consume the search_query after it's been used
    if 'search_query' in st.session_state:
        del st.session_state.search_query
    
    return q, submitted

def render_error(message: str, error_type: str = "warning") -> None:
    """Render a styled error message."""
    icon = "⚠️" if error_type == "warning" else "❌"
    css_class = "error-card--warning" if error_type == "warning" else "error-card--error"
    safe_message = html.escape(message)
    
    st.markdown(f"""
        <div class="error-card {css_class}">
            <span class="error-icon">{icon}</span>
            <span class="error-message">{safe_message}</span>
        </div>
    """, unsafe_allow_html=True)

def render_footer() -> None:
    """Render the application footer."""
    st.markdown("""
        <div class="app-footer">
            <span>GeoStudio AI</span>
            <span class="footer-sep">·</span>
            <span>Powered by OpenStreetMap Nominatim</span>
            <span class="footer-sep">·</span>
            <span>v2.0</span>
        </div>
    """, unsafe_allow_html=True)

def init_session_state() -> None:
    """Initialize Streamlit session state."""
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None

def main() -> None:
    """Main application entry point."""
    # Setup
    inject_design_system()
    render_header()
    init_session_state()

    # Search Interface
    query, submitted = render_search()

    # Handle Search
    if submitted and query:
        try:
            service = AddressService()
            
            with st.spinner("🔍 Searching..."):
                results = service.search(query)
            
            # Store result
            if results and results[0].status == "OK":
                st.session_state.last_result = results[0]
                st.rerun()
                
        except LocationNotFoundError as e:
            logger.warning("Location not found: %s", query)
            render_error(e.user_message, "warning")
            
        except ValidationError as e:
            logger.warning("Validation error: %s", e)
            render_error(e.user_message, "warning")
            
        except InvalidCoordinatesError as e:
            logger.warning("Invalid coordinates: %s", e)
            render_error(e.user_message, "warning")
            
        except RateLimitExceededError as e:
            logger.warning("Rate limit exceeded")
            render_error(e.user_message, "warning")
            
        except APIConnectionError as e:
            logger.error("API connection error: %s", e)
            render_error(e.user_message, "error")
            
        except GeoServiceException as e:
            logger.error("Service error: %s", e)
            render_error(e.user_message, "error")
            
        except Exception as e:
            logger.error("Unexpected error: %s", e, exc_info=True)
            render_error("An unexpected error occurred. Please try again.", "error")

    # Display Results or Empty State
    if st.session_state.last_result:
        render_result_card(st.session_state.last_result)
    else:
        render_empty_state()

    # Footer
    render_footer()

if __name__ == "__main__":
    main()