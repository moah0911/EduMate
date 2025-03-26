"""
Internationalization utilities for EduMate.

This module provides utilities for handling multiple languages and
internationalization features in the EduMate platform.
"""

import os
import json
import streamlit as st

# Supported languages with their codes and names
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'es': 'Spanish',
    'fr': 'French',
    'zh': 'Chinese',
    'ar': 'Arabic'
}

# Education systems by country
EDUCATION_SYSTEMS = {
    'india': {
        'name': 'Indian Education System',
        'structure': [
            {'level': 'Primary', 'grades': '1-5', 'age': '6-10'},
            {'level': 'Upper Primary', 'grades': '6-8', 'age': '11-13'},
            {'level': 'Secondary', 'grades': '9-10', 'age': '14-15'},
            {'level': 'Higher Secondary', 'grades': '11-12', 'age': '16-17'},
            {'level': 'Undergraduate', 'duration': '3-4 years', 'age': '18+'},
            {'level': 'Postgraduate', 'duration': '1-3 years', 'age': '21+'},
            {'level': 'Doctorate', 'duration': '3-5 years', 'age': '23+'}
        ],
        'boards': ['CBSE', 'ICSE', 'State Boards'],
        'exams': ['JEE', 'NEET', 'UPSC', 'CAT', 'GATE']
    },
    'usa': {
        'name': 'US Education System',
        'structure': [
            {'level': 'Elementary School', 'grades': 'K-5', 'age': '5-10'},
            {'level': 'Middle School', 'grades': '6-8', 'age': '11-13'},
            {'level': 'High School', 'grades': '9-12', 'age': '14-18'},
            {'level': 'Undergraduate', 'duration': '4 years', 'age': '18+'},
            {'level': 'Graduate', 'duration': '1-2 years', 'age': '22+'},
            {'level': 'Doctorate', 'duration': '4-7 years', 'age': '24+'}
        ],
        'boards': ['State Education Departments'],
        'exams': ['SAT', 'ACT', 'GRE', 'GMAT', 'MCAT', 'LSAT']
    },
    'uk': {
        'name': 'UK Education System',
        'structure': [
            {'level': 'Primary School', 'years': '1-6', 'age': '5-11'},
            {'level': 'Secondary School', 'years': '7-11', 'age': '11-16'},
            {'level': 'Sixth Form/College', 'years': '12-13', 'age': '16-18'},
            {'level': 'Undergraduate', 'duration': '3-4 years', 'age': '18+'},
            {'level': 'Postgraduate', 'duration': '1-2 years', 'age': '21+'},
            {'level': 'Doctorate', 'duration': '3-4 years', 'age': '23+'}
        ],
        'boards': ['AQA', 'Edexcel', 'OCR', 'WJEC'],
        'exams': ['GCSE', 'A-Levels', 'UCAS']
    },
    'australia': {
        'name': 'Australian Education System',
        'structure': [
            {'level': 'Primary School', 'years': 'K-6', 'age': '5-12'},
            {'level': 'Secondary School', 'years': '7-12', 'age': '12-18'},
            {'level': 'Undergraduate', 'duration': '3-4 years', 'age': '18+'},
            {'level': 'Postgraduate', 'duration': '1-2 years', 'age': '21+'},
            {'level': 'Doctorate', 'duration': '3-4 years', 'age': '23+'}
        ],
        'boards': ['State Education Departments'],
        'exams': ['ATAR', 'NAPLAN']
    },
    'canada': {
        'name': 'Canadian Education System',
        'structure': [
            {'level': 'Elementary School', 'grades': 'K-6', 'age': '5-12'},
            {'level': 'Junior High School', 'grades': '7-9', 'age': '12-15'},
            {'level': 'High School', 'grades': '10-12', 'age': '15-18'},
            {'level': 'Undergraduate', 'duration': '3-4 years', 'age': '18+'},
            {'level': 'Graduate', 'duration': '1-3 years', 'age': '22+'},
            {'level': 'Doctorate', 'duration': '4-7 years', 'age': '25+'}
        ],
        'boards': ['Provincial Ministries of Education'],
        'exams': ['Provincial Exams']
    }
}


class Internationalization:
    """Class to handle internationalization features for EduMate."""
    
    def __init__(self, data_dir='data'):
        """Initialize the internationalization utilities.
        
        Args:
            data_dir: Directory for storing translation data
        """
        self.data_dir = data_dir
        self.translations_dir = os.path.join(data_dir, 'translations')
        
        # Create translations directory if it doesn't exist
        if not os.path.exists(self.translations_dir):
            os.makedirs(self.translations_dir)
    
    def get_locale(self):
        """Get the current locale based on user preference.
        
        Returns:
            str: Language code (e.g., 'en', 'hi')
        """
        # Check if language is set in session state
        if 'language' in st.session_state:
            return st.session_state.language
        
        # Default to English
        return 'en'
    
    def set_language(self, language_code):
        """Set the user's preferred language.
        
        Args:
            language_code (str): Language code (e.g., 'en', 'hi')
            
        Returns:
            bool: Success status
        """
        if language_code in SUPPORTED_LANGUAGES:
            st.session_state.language = language_code
            return True
        return False
    
    def get_supported_languages(self):
        """Get list of supported languages.
        
        Returns:
            dict: Dictionary of language codes and names
        """
        return SUPPORTED_LANGUAGES
    
    def get_current_language(self):
        """Get the current language code.
        
        Returns:
            str: Current language code
        """
        return self.get_locale()
    
    def get_education_systems(self):
        """Get information about education systems by country.
        
        Returns:
            dict: Dictionary of education systems by country
        """
        return EDUCATION_SYSTEMS
    
    def get_education_system(self, country_code):
        """Get education system information for a specific country.
        
        Args:
            country_code (str): Country code (e.g., 'india', 'usa')
            
        Returns:
            dict: Education system information or None if not found
        """
        return EDUCATION_SYSTEMS.get(country_code.lower())
    
    def translate(self, key, default=None):
        """Translate a key to the current language.
        
        Args:
            key (str): Translation key
            default (str, optional): Default text if translation not found
            
        Returns:
            str: Translated text or default/key if not found
        """
        language = self.get_locale()
        translations = self.load_translations(language)
        
        # Return translation if found
        if key in translations:
            return translations[key]
        
        # Return default or key if translation not found
        return default if default is not None else key
    
    def save_translations(self, translations, language_code):
        """Save translations for a specific language.
        
        Args:
            translations (dict): Dictionary of translations
            language_code (str): Language code
            
        Returns:
            bool: Success status
        """
        if language_code not in SUPPORTED_LANGUAGES:
            return False
        
        file_path = os.path.join(self.translations_dir, f"{language_code}.json")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=4)
            return True
        except Exception:
            return False
    
    def load_translations(self, language_code):
        """Load translations for a specific language.
        
        Args:
            language_code (str): Language code
            
        Returns:
            dict: Dictionary of translations or empty dict if not found
        """
        file_path = os.path.join(self.translations_dir, f"{language_code}.json")
        
        if not os.path.exists(file_path):
            # Fall back to English if translation file doesn't exist
            if language_code != 'en':
                return self.load_translations('en')
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}


# Initialize the internationalization utility
i18n = Internationalization()
