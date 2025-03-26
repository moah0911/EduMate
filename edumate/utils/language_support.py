"""
Language support module for EduMate.

This module provides a simple approach to multi-language support
without relying on complex internationalization frameworks.
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

# Education systems information by country
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

# Default translations for common phrases
DEFAULT_TRANSLATIONS = {
    'en': {
        'welcome': 'Welcome to EduMate',
        'login': 'Login',
        'register': 'Register',
        'dashboard': 'Dashboard',
        'courses': 'Courses',
        'assignments': 'Assignments',
        'education_systems': 'Education Systems',
        'language': 'Language',
        'education_system': '🏫 Education Systems Around the World',
        'education_system_description': 'Explore education systems from different countries to understand their structure, examinations, and pathways.',
        'education_structure': 'Education Structure',
        'boards_of_education': 'Boards of Education',
        'important_examinations': 'Important Examinations',
        'higher_education_institutions': 'Higher Education Institutions',
        'competitive_examinations': 'Competitive Examinations',
        'higher_education': 'Higher Education',
        'standardized_tests': 'Standardized Tests',
        'qualifications': 'Qualifications',
        'resources': 'Resources',
        'resources_description': 'Useful websites for more information:'
    },
    'hi': {
        'welcome': 'EduMate में आपका स्वागत है',
        'login': 'लॉग इन करें',
        'register': 'पंजीकरण करें',
        'dashboard': 'डैशबोर्ड',
        'courses': 'पाठ्यक्रम',
        'assignments': 'असाइनमेंट',
        'education_systems': 'शिक्षा प्रणालियां',
        'language': 'भाषा',
        'education_system': '🏫 दुनिया भर की शिक्षा प्रणालियां',
        'education_system_description': 'विभिन्न देशों की शिक्षा प्रणालियों का अन्वेषण करें ताकि उनकी संरचना, परीक्षाओं और मार्गों को समझ सकें।',
        'education_structure': 'शिक्षा संरचना',
        'boards_of_education': 'शिक्षा बोर्ड',
        'important_examinations': 'महत्वपूर्ण परीक्षाएं',
        'higher_education_institutions': 'उच्च शिक्षा संस्थान',
        'competitive_examinations': 'प्रतियोगी परीक्षाएं',
        'higher_education': 'उच्च शिक्षा',
        'standardized_tests': 'मानकीकृत परीक्षण',
        'qualifications': 'योग्यता',
        'resources': 'संसाधन',
        'resources_description': 'अधिक जानकारी के लिए उपयोगी वेबसाइटें:'
    }
}


def get_current_language():
    """Get the current language code from session state.
    
    Returns:
        str: Language code (e.g., 'en', 'hi')
    """
    return st.session_state.get('language', 'en')


def set_language(language_code):
    """Set the language in session state.
    
    Args:
        language_code (str): Language code to set
        
    Returns:
        bool: Success status
    """
    if language_code in SUPPORTED_LANGUAGES:
        st.session_state.language = language_code
        return True
    return False


def translate(key, default=None):
    """Translate a key to the current language.
    
    Args:
        key (str): Translation key
        default (str, optional): Default text if translation not found
        
    Returns:
        str: Translated text or default/key if not found
    """
    language = get_current_language()
    
    # Get translations for the current language
    translations = DEFAULT_TRANSLATIONS.get(language, {})
    
    # Try to get from custom translations if they exist
    try:
        file_path = os.path.join('data', 'translations', f"{language}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                custom_translations = json.load(f)
                translations.update(custom_translations)
    except Exception:
        pass
    
    # Return translation if found
    if key in translations:
        return translations[key]
    
    # Fall back to English if not found in current language
    if language != 'en' and key in DEFAULT_TRANSLATIONS.get('en', {}):
        return DEFAULT_TRANSLATIONS['en'][key]
    
    # Return default or key if translation not found
    return default if default is not None else key


def get_education_system(country_code):
    """Get education system information for a specific country.
    
    Args:
        country_code (str): Country code (e.g., 'india', 'usa')
        
    Returns:
        dict: Education system information or None if not found
    """
    return EDUCATION_SYSTEMS.get(country_code.lower())
