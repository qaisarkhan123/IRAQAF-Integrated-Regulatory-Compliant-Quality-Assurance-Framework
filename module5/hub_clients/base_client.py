"""
Base Hub Client - Common functionality for all hub clients
"""

import requests
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseHubClient:
    """Base class for all hub clients."""

    def __init__(self, host: str = "127.0.0.1", port: int = 0, timeout: int = 10):
        """
        Initialize hub client.

        Args:
            host: Hub server host
            port: Hub server port
            timeout: Request timeout in seconds
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make GET request to hub API.

        Args:
            endpoint: API endpoint (e.g., '/api/score')
            params: Query parameters

        Returns:
            JSON response as dict

        Raises:
            ConnectionError: If hub is not reachable
            ValueError: If response is invalid
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            logger.error(
                f"Cannot connect to {self.__class__.__name__} at {self.base_url}: {e}")
            raise ConnectionError(f"Hub unreachable: {self.base_url}") from e
        except requests.exceptions.Timeout as e:
            logger.error(
                f"Timeout connecting to {self.__class__.__name__}: {e}")
            raise TimeoutError(f"Hub timeout: {self.base_url}") from e
        except Exception as e:
            logger.error(f"Error fetching from {self.__class__.__name__}: {e}")
            raise ValueError(f"Invalid response from hub: {str(e)}") from e

    def post(
        self, endpoint: str, json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make POST request to hub API.

        Args:
            endpoint: API endpoint
            json_data: JSON payload

        Returns:
            JSON response as dict
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.post(url, json=json_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error posting to {self.__class__.__name__}: {e}")
            raise

    def health_check(self) -> bool:
        """Check if hub is accessible."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=2)
            return response.status_code < 500
        except Exception:
            return False
