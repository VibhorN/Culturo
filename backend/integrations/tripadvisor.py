"""
TripAdvisor API Integration
Handles historical landmarks and destinations data retrieval
"""

import requests
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class TripAdvisorIntegration:
    """Integration with TripAdvisor API for historical landmarks and destinations"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.content.tripadvisor.com/api/v1/location"
        
        self.country_coordinate_mappings = {
            "France": {
                "latLong": "48.8566,2.3522", 
                "radius": "5", 
                "radiusUnit": "m"
            },  
            "Spain": {
                "latLong": "40.4168,-3.7038", 
                "radius": "2", 
                "radiusUnit": "m"
            }, 
            "Japan": {
                "latLong": "35.6895,139.6917", 
                "radius": "5", 
                "radiusUnit": "m"
            },
            "Italy": {
                "latLong": "41.9028,12.4964",
                "radius": "5",
                "radiusUnit": "m"
            },
            "Germany": {
                "latLong": "52.5200,13.4050",
                "radius": "5",
                "radiusUnit": "m"
            },
            "United Kingdom": {
                "latLong": "51.5074,-0.1278",
                "radius": "5",
                "radiusUnit": "m"
            },
            "Brazil": {
                "latLong": "-23.5505,-46.6333",
                "radius": "5",
                "radiusUnit": "m"
            },
            "Mexico": {
                "latLong": "19.4326,-99.1332",
                "radius": "5",
                "radiusUnit": "m"
            },
            "India": {
                "latLong": "28.6139,77.2090",
                "radius": "5",
                "radiusUnit": "m"
            }
        }

    def _normalize_country_name(self, country: str) -> str:
        """Normalize country name to match TripAdvisor mappings"""
        country_mapping = {
            "spain": "Spain",
            "france": "France", 
            "japan": "Japan",
            "italy": "Italy",
            "germany": "Germany",
            "united kingdom": "United Kingdom",
            "uk": "United Kingdom",
            "usa": "United States",
            "united states": "United States",
            "canada": "Canada",
            "australia": "Australia",
            "brazil": "Brazil",
            "mexico": "Mexico",
            "india": "India",
            "china": "China",
            "russia": "Russia"
        }
        
        # Try exact match first
        if country in self.country_coordinate_mappings:
            return country
            
        # Try lowercase mapping
        normalized = country_mapping.get(country.lower(), country)
        
        # If still not found, try title case
        if normalized not in self.country_coordinate_mappings:
            normalized = country.title()
            
        return normalized

    def get_popular_locations(self, country: str, category: str, search_query: str, limit: int = 10) -> Optional[List[Dict]]:
        """
        Get popular locations for a given country, category, and search term.
        Returns a list of dicts with name, description, and photo URL.
        """
        # Normalize country name to match our mappings
        normalized_country = self._normalize_country_name(country)
        
        if normalized_country not in self.country_coordinate_mappings or category not in ["restaurants", "hotels", "attractions"]:
            logger.warning(f"Country {normalized_country} or category {category} not supported")
            return None

        location_params = self.country_coordinate_mappings[normalized_country]
        headers = {"Accept": "application/json"}
        params = {
            "key": self.api_key,
            "searchQuery": search_query,
            "category": category,
            **location_params
        }

        # Step 1: Get location IDs
        locations = self._retrieve_location_ids(headers, params)
        if not locations:
            return []

        # Step 2: For each location, get details & photo
        results = []
        for name, loc_id in list(locations.items())[:limit]:
            description = self._get_location_description(loc_id, headers)
            photo_url = self._get_location_photo(loc_id, headers)
            
            results.append({
                "name": name,
                "location_id": loc_id,
                "description": description,
                "photo": photo_url
            })

        return results

    def _retrieve_location_ids(self, headers: Dict, params: Dict) -> Optional[Dict]:
        """Retrieve location IDs from TripAdvisor API."""
        try:
            url = self.base_url + "/search"
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {place["name"]: place["location_id"] for place in data.get("data", [])}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"TripAdvisor API error: {str(e)}")
            return None

    def _get_location_description(self, location_id: str, headers: Dict) -> Optional[str]:
        """Get the location's description text."""
        try:
            url = f"{self.base_url}/{location_id}/details"
            params = {"key": self.api_key}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json().get("data", {})
            return data.get("description", None)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting location description: {str(e)}")
            return None

    def _get_location_photo(self, location_id: str, headers: Dict) -> Optional[str]:
        """Get the first available photo for a given location."""
        try:
            url = f"{self.base_url}/{location_id}/photos"
            params = {"key": self.api_key, "limit": 1}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json().get("data", [])
            if not data:
                return None
            # pick first image in the returned data
            return data[0].get("images", {}).get("large", {}).get("url")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting location photo: {str(e)}")
            return None

    async def get_historical_landmarks(self, country: str, limit: int = 5) -> Optional[Dict]:
        """Get historical landmarks for a country using TripAdvisor"""
        try:
            # Run in thread pool since get_popular_locations is sync
            import asyncio
            loop = asyncio.get_event_loop()
            landmarks = await loop.run_in_executor(
                None,
                lambda: self.get_popular_locations(
                    country=country,
                    category="attractions",
                    search_query="historical landmarks monuments",
                    limit=limit
                )
            )
            
            if landmarks:
                return {
                    "country": country,
                    "category": "attractions",
                    "locations": landmarks,
                    "total_found": len(landmarks),
                    "source": "tripadvisor"
                }
            
            return None
        except Exception as e:
            logger.error(f"Error getting historical landmarks: {str(e)}")
            return None

    async def get_popular_restaurants(self, country: str, limit: int = 5) -> Optional[Dict]:
        """Get popular restaurants for a country using TripAdvisor"""
        try:
            # Run in thread pool since get_popular_locations is sync
            import asyncio
            loop = asyncio.get_event_loop()
            restaurants = await loop.run_in_executor(
                None,
                lambda: self.get_popular_locations(
                    country=country,
                    category="restaurants",
                    search_query="traditional local cuisine",
                    limit=limit
                )
            )
            
            if restaurants:
                return {
                    "country": country,
                    "category": "restaurants",
                    "locations": restaurants,
                    "total_found": len(restaurants),
                    "source": "tripadvisor"
                }
            
            return None
        except Exception as e:
            logger.error(f"Error getting popular restaurants: {str(e)}")
            return None

    async def get_tourist_destinations(self, country: str, limit: int = 5) -> Optional[Dict]:
        """Get popular tourist destinations for a country using TripAdvisor"""
        try:
            # Run in thread pool since get_popular_locations is sync
            import asyncio
            loop = asyncio.get_event_loop()
            destinations = await loop.run_in_executor(
                None,
                lambda: self.get_popular_locations(
                    country=country,
                    category="attractions",
                    search_query="must visit tourist attractions",
                    limit=limit
                )
            )
            
            if destinations:
                return {
                    "country": country,
                    "category": "attractions",
                    "locations": destinations,
                    "total_found": len(destinations),
                    "source": "tripadvisor"
                }
            
            return None
        except Exception as e:
            logger.error(f"Error getting tourist destinations: {str(e)}")
            return None