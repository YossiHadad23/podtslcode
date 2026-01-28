"""Custom Exceptions."""


class GeoServiceException(Exception):
    """Base exception for geo service errors."""
    
    def __init__(self, message: str, user_message: str = None):
        super().__init__(message)
        self.user_message = user_message or message


class APIConnectionError(GeoServiceException):
    """API connection error."""
    
    def __init__(self, message: str, status_code: int = None):
        user_msg = "Unable to connect to location service. Please check your internet connection."
        super().__init__(message, user_msg)
        self.status_code = status_code


class RateLimitExceededError(GeoServiceException):
    """Rate limit exceeded."""
    
    def __init__(self, wait_time: float = None):
        message = "API rate limit exceeded"
        user_msg = "Too many requests. Please wait a moment and try again."
        super().__init__(message, user_msg)
        self.wait_time = wait_time


class LocationNotFoundError(GeoServiceException):
    """Location not found."""
    
    def __init__(self, query: str):
        message = f"Location not found for query: {query}"
        user_msg = "📍 Location not found. Try different search terms or check spelling."
        super().__init__(message, user_msg)
        self.query = query


class InvalidCoordinatesError(GeoServiceException):
    """Invalid coordinates."""
    
    def __init__(self, lat: float = None, lng: float = None, message: str = None):
        if message is None:
            message = f"Invalid coordinates: lat={lat}, lng={lng}"
        user_msg = "Invalid GPS coordinates. Latitude must be -90 to 90, Longitude must be -180 to 180."
        super().__init__(message, user_msg)
        self.lat = lat
        self.lng = lng


class ValidationError(GeoServiceException):
    """Input validation error."""
    
    def __init__(self, message: str, field: str = None):
        user_msg = f"Invalid input: {message}"
        super().__init__(message, user_msg)
        self.field = field


class InvalidResponseError(GeoServiceException):
    """Invalid API response."""
    
    def __init__(self, message: str = "Invalid API response"):
        user_msg = "Received unexpected response from location service. Please try again."
        super().__init__(message, user_msg)
