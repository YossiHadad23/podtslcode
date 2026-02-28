"""Input Validation Module."""

import re
from typing import Tuple, Optional

from config import validation_config
from exceptions import ValidationError, InvalidCoordinatesError
from logger import logger


class QueryValidator:
    """Validates search queries."""
    
    @staticmethod
    def validate(query: str) -> str:
        """Validate query."""
        if not query:
            raise ValidationError("Query cannot be empty", field="query")
        
        query = query.strip()
        
        if len(query) < validation_config.MIN_QUERY_LENGTH:
            raise ValidationError(
                f"Query too short (min {validation_config.MIN_QUERY_LENGTH} characters)",
                field="query"
            )
        
        if len(query) > validation_config.MAX_QUERY_LENGTH:
            raise ValidationError(
                f"Query too long (max {validation_config.MAX_QUERY_LENGTH} characters)",
                field="query"
            )
        
        logger.debug(f"Query validated: {query[:50]}...")
        return query
    
    @staticmethod
    def sanitize(query: str) -> str:
        """Sanitize query."""
        sanitized = re.sub(r'[^\w\s\u0590-\u05FF\d"\'.,()+-]', ' ', query)
        sanitized = ' '.join(sanitized.split())
        
        if sanitized != query:
            logger.debug(f"Query sanitized")
        
        return sanitized


class CoordinateValidator:
    """Validates GPS coordinates."""
    
    @staticmethod
    def validate(lat: float, lng: float) -> Tuple[float, float]:
        """Validate coordinates."""
        try:
            lat_float = float(lat)
            lng_float = float(lng)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid coordinate format: lat={lat}, lng={lng}")
            raise InvalidCoordinatesError(message=f"Coordinates must be numbers: {e}")
        
        if not (validation_config.MIN_LATITUDE <= lat_float <= validation_config.MAX_LATITUDE):
            logger.warning(f"Latitude out of range: {lat_float}")
            raise InvalidCoordinatesError(
                lat=lat_float,
                lng=lng_float,
                message=f"Latitude must be between {validation_config.MIN_LATITUDE} and {validation_config.MAX_LATITUDE}"
            )
        
        if not (validation_config.MIN_LONGITUDE <= lng_float <= validation_config.MAX_LONGITUDE):
            logger.warning(f"Longitude out of range: {lng_float}")
            raise InvalidCoordinatesError(
                lat=lat_float,
                lng=lng_float,
                message=f"Longitude must be between {validation_config.MIN_LONGITUDE} and {validation_config.MAX_LONGITUDE}"
            )
        
        logger.debug(f"Coordinates validated: {lat_float:.6f}, {lng_float:.6f}")
        return lat_float, lng_float
    
    @staticmethod
    def parse_from_query(query: str, strict: bool = False) -> Optional[Tuple[float, float]]:
        """Extract coordinates from query.

        Args:
            query: Raw user query
            strict: When True, raise InvalidCoordinatesError if query format
                looks like coordinates but values are out of range/invalid.
        """
        normalized_query = query.strip()

        patterns = [
            # Strict coordinate pair: "31.7683, 35.2137" or "31 35"
            r"^\s*([-+]?\d{1,3}(?:\.\d+)?)\s*[,\s]\s*([-+]?\d{1,3}(?:\.\d+)?)\s*$",
            # Labeled coordinate pair: "lat: 31.7683, lon: 35.2137"
            r"^\s*lat(?:itude)?\s*[:=]\s*([-+]?\d{1,3}(?:\.\d+)?)\s*[,\s]+"
            r"(?:lon|lng|longitude)\s*[:=]\s*([-+]?\d{1,3}(?:\.\d+)?)\s*$",
        ]

        for pattern in patterns:
            match = re.match(pattern, normalized_query, re.IGNORECASE)
            if not match:
                continue

            try:
                lat, lng = CoordinateValidator.validate(match.group(1), match.group(2))
                logger.info(f"Extracted coordinates: {lat}, {lng}")
                return lat, lng
            except InvalidCoordinatesError:
                logger.debug("Query looks like coordinates but values are invalid")
                if strict:
                    raise
                return None

        return None


class ResponseValidator:
    """Validates API responses."""
    
    @staticmethod
    def validate_osm_search_response(data: list) -> list:
        """Validate search response."""
        if not isinstance(data, list):
            raise ValidationError("Expected list response from API")
        logger.debug(f"Search response validated: {len(data)} results")
        return data
    
    @staticmethod
    def validate_osm_reverse_response(data: dict) -> dict:
        """Validate reverse geocoding response."""
        if not isinstance(data, dict):
            raise ValidationError("Expected dict response from reverse API")
        
        if 'display_name' not in data:
            raise ValidationError("Missing 'display_name' in API response")
        
        logger.debug("Reverse geocoding response validated")
        return data
