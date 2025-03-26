import os
import json
import requests
from typing import List, Dict, Any
import logging
from .logger import log_system_event, log_error

class CourseSearch:
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = "9a7b5e959afa44c98"  # Default search engine ID for educational content
        
    def search_courses(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for courses using Google Search API
        
        Args:
            query: Search query for courses
            limit: Maximum number of results to return
            
        Returns:
            List of course results with title, link, and description
        """
        if not self.api_key:
            log_error("Google Search API key not configured")
            return []
            
        try:
            # Enhance the query to focus on courses
            enhanced_query = f"{query} online course tutorial learn"
            
            # Make the API request
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': enhanced_query,
                'num': limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Process the results
            data = response.json()
            results = []
            
            if 'items' in data:
                for item in data['items']:
                    result = {
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'description': item.get('snippet', ''),
                        'source': self._extract_domain(item.get('link', ''))
                    }
                    results.append(result)
                    
            return results
        
        except Exception as e:
            log_error(f"Error searching for courses: {str(e)}")
            return []
    
    def search_courses_by_skill(self, skill: str, level: str = "beginner") -> List[Dict[str, Any]]:
        """
        Search for courses based on a specific skill and level
        
        Args:
            skill: The skill to search courses for
            level: Skill level (beginner, intermediate, advanced)
            
        Returns:
            List of relevant courses
        """
        query = f"{skill} {level} course"
        return self.search_courses(query)
    
    def search_courses_by_career(self, career_path: str) -> List[Dict[str, Any]]:
        """
        Search for courses relevant to a specific career path
        
        Args:
            career_path: The career path to search courses for
            
        Returns:
            List of relevant courses
        """
        query = f"courses for {career_path} career path"
        return self.search_courses(query)
    
    def _extract_domain(self, url: str) -> str:
        """Extract and clean domain name from URL"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            
            # Remove www. if present
            if domain.startswith('www.'):
                domain = domain[4:]
                
            return domain
        except Exception:
            return "unknown"
    
    def get_recommended_platforms(self) -> List[Dict[str, str]]:
        """Return a list of recommended learning platforms"""
        return [
            {"name": "Coursera", "url": "https://www.coursera.org/", "description": "Offers courses from top universities"},
            {"name": "edX", "url": "https://www.edx.org/", "description": "Free courses from Harvard, MIT, and more"},
            {"name": "Udemy", "url": "https://www.udemy.com/", "description": "Wide variety of courses on many subjects"},
            {"name": "Khan Academy", "url": "https://www.khanacademy.org/", "description": "Free courses on math, science, and more"},
            {"name": "Codecademy", "url": "https://www.codecademy.com/", "description": "Interactive coding courses"},
            {"name": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/", "description": "Professional development courses"},
            {"name": "Skillshare", "url": "https://www.skillshare.com/", "description": "Creative and practical skills courses"}
        ]
