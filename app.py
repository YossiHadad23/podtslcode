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
    @rate_limiter.wait()
    def _fetch_from_api(
        url: str, 
        params: Dict[str, Any], 
        force_english: bool
    ) -> Optional[Any]:
        """
        Fetch data from OSM API with rate limiting and error handling.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            force_english: Whether to force English language response
            
        Returns:
            Parsed JSON response or None if request fails
            
        Raises:
            APIConnectionError: On network/HTTP errors
            InvalidResponseError: On invalid JSON response
        """
        headers = {'User-Agent': api_config.USER_AGENT}
        request_params = dict(params)

        if force_english:
            headers['Accept-Language'] = 'en-US,en;q=0.9'
            request_params['accept-language'] = 'en'
        
        try:
            logger.debug(f"API request to: {url}")
            
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
            logger.info(f"API response successful: {type(data)}")
            return data
            
        except requests.Timeout:
            logger.error(f"Request timeout after {api_config.TIMEOUT_SECONDS}s")
            raise APIConnectionError(
                f"Request timed out after {api_config.TIMEOUT_SECONDS} seconds",
                status_code=None
            )
            
        except requests.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code}")
            raise APIConnectionError(
                f"HTTP error: {e.response.status_code}",
                status_code=e.response.status_code
            )
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {type(e).__name__}")
            raise APIConnectionError(f"Request failed")
            
        except json.JSONDecodeError as e:
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
        
        Args:
            lat: Latitude
            lng: Longitude
            query: Original query string
            
        Returns:
            List containing single LocationData result
        """
        try:
            # Validate coordinates
            lat_valid, lng_valid = CoordinateValidator.validate(lat, lng)
            
            logger.debug(f"Reverse geocoding: {lat_valid}, {lng_valid}")
            
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
            logger.error(f"Reverse geocoding failed: {type(e).__name__}")
            raise APIConnectionError("Reverse geocoding failed") from e
    
    def search(self, raw_query: str) -> List[LocationData]:
        """
        Search for location by query (address or coordinates).
        
        Args:
            raw_query: User's search query
            
        Returns:
            List of LocationData results
        """
        try:
            # Validate and sanitize input
            query = QueryValidator.validate(raw_query)
            query = QueryValidator.sanitize(query)
            
            logger.debug("Search initiated")
            
            # Try to parse as coordinates first
            coords = CoordinateValidator.parse_from_query(query)
            if coords:
                lat, lng = coords
                logger.debug("Query identified as coordinates")
                return self._reverse_geocode(lat, lng, query)
            
            # Search by address
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
                force_english=False
            )

            if not search_results:
                raise LocationNotFoundError(query)

            # Validate response
            ResponseValidator.validate_osm_search_response(search_results)

            # Process results directly from search response; reverse only as fallback
            results = []
            direct_results_count = 0
            fallback_reverse_count = 0
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for item in search_results:
                lat = item.get('lat')
                lng = item.get('lon')
                address = item.get('display_name')
                zip_code = item.get('address', {}).get('postcode', '—')

                if lat and lng and address:
                    results.append(LocationData(
                        original_query=query,
                        address=address,
                        zip_code=zip_code,
                        lat=str(lat),
                        lng=str(lng),
                        status="OK",
                        timestamp=timestamp
                    ))
                    direct_results_count += 1
                    continue

                if lat and lng:
                    fallback_results = self._reverse_geocode(lat, lng, query)
                    results.extend(fallback_results)
                    fallback_reverse_count += len(fallback_results)

            if not results:
                raise LocationNotFoundError(query)

            logger.debug(
                "Search successful: %s results (%s direct, %s fallback reverse)",
                len(results),
                direct_results_count,
                fallback_reverse_count
            )
            return results
            
        except GeoServiceException:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Catch any unexpected errors
            logger.error(f"Unexpected error in search: {type(e).__name__}")
            raise APIConnectionError("Search failed") from e

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
    """Render the empty state."""
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
    st.write("")
    
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
    
    with col2:
        if st.button("🏢 Azrieli Tower, Tel Aviv", use_container_width=True, key="ex1"):
            st.session_state.search_query = "Azrieli Tower, Tel Aviv"
            st.rerun()
    with col3:
        if st.button("📍 31.7683, 35.2137", use_container_width=True, key="ex2"):
            st.session_state.search_query = "31.7683, 35.2137"
            st.rerun()
    with col4:
        if st.button("🌊 Tel Aviv Port", use_container_width=True, key="ex3"):
            st.session_state.search_query = "Tel Aviv Port"
            st.rerun()

def render_result_card(data: LocationData) -> None:
    """Render the result card with location data."""
    # Security: Escape HTML entities to prevent XSS
    safe_address = html.escape(data.address)
    
    # Main Result Card
    st.markdown(f"""
        <div class="result-card">
            <div class="result-status">Location Found</div>
            <div class="result-address">{safe_address}</div>
        </div>
    """, unsafe_allow_html=True)

    # Action Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            "📥 Export Data",
            data=json.dumps(asdict(data), indent=2, ensure_ascii=False),
            file_name=f"location_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Security: URL-encode coordinates to prevent injection
        safe_coords = quote(f"{data.lat},{data.lng}", safe='')
        st.link_button(
            "🗺️ Open Map",
            f"https://www.google.com/maps/search/?api=1&query={safe_coords}",
            use_container_width=True
        )

    st.write("")
    
    # Postal Code Display
    # Security: Escape HTML entities
    postal_value = data.zip_code if data.zip_code and data.zip_code != "—" else "Not Available"
    safe_postal = html.escape(postal_value)
    st.markdown(f"""
        <div class="data-card">
            <div class="data-label">📮 Postal Code</div>
            <div class="data-value">{safe_postal}</div>
        </div>
    """, unsafe_allow_html=True)

    # Map Section
    st.write("")
    with st.expander("🗺️ Interactive Map & Coordinates"):
        st.markdown('<div class="data-label">📍 GPS Coordinates</div>', unsafe_allow_html=True)
        st.code(f"{float(data.lat):.6f}, {float(data.lng):.6f}", language=None)
        st.write("")
        
        try:
            st.map(pd.DataFrame({'lat': [float(data.lat)], 'lon': [float(data.lng)]}), zoom=15)
        except Exception as e:
            logger.error(f"Map display error: {type(e).__name__}")
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
            submitted = st.form_submit_button("Search", use_container_width=True)
    
    if 'search_query' in st.session_state:
        del st.session_state.search_query
    
    return q, submitted



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
            # Create service and search
            service = AddressService()
            
            with st.spinner("🔍 Searching..."):
                results = service.search(query)
            
            # Store result
            if results and results[0].status == "OK":
                st.session_state.last_result = results[0]
                st.rerun()
                
        except LocationNotFoundError as e:
            logger.warning(f"Location not found: {query}")
            st.warning(e.user_message)
            
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            st.warning(f"⚠️ {e.user_message}")
            
        except InvalidCoordinatesError as e:
            logger.warning(f"Invalid coordinates: {e}")
            st.warning(e.user_message)
            
        except RateLimitExceededError as e:
            logger.warning("Rate limit exceeded")
            st.warning(e.user_message)
            
        except APIConnectionError as e:
            logger.error(f"API connection error: {e}")
            st.error(f"❌ {e.user_message}")
            
        except GeoServiceException as e:
            logger.error(f"Service error: {e}")
            st.error(f"❌ {e.user_message}")
            
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error: {e}", exc_info=True)
            st.error("❌ An unexpected error occurred. Please try again.")

    # Display Results or Empty State
    if st.session_state.last_result:
        render_result_card(st.session_state.last_result)
    else:
        render_empty_state()

if __name__ == "__main__":
    main()