import streamlit as st
import json
import os

def show_language_selector():
    """
    Display a language selector in the sidebar and handle language switching
    
    Supports multiple languages with focus on Indian languages
    """
    # Define available languages with their display names and codes
    languages = {
        "English": "en",
        "हिंदी (Hindi)": "hi",
        "తెలుగు (Telugu)": "te",
        "தமிழ் (Tamil)": "ta",
        "ಕನ್ನಡ (Kannada)": "kn"
    }
    
    # Get current language from session state or set default
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
        
    # Create a container with styled header
    st.sidebar.markdown("""
    <div style="background-color:#2a4c7d; color:white; padding:10px; 
         border-radius:5px; margin:5px 0; text-align:center; font-weight:bold;">
        Languages of India / भारत की भाषाएँ
    </div>
    """, unsafe_allow_html=True)
    
    # Create a selectbox for language selection
    selected_language_name = st.sidebar.selectbox(
        "Select Language",
        list(languages.keys()),
        index=list(languages.values()).index(st.session_state.language) if st.session_state.language in languages.values() else 0,
        key="language_selector"
    )
    
    # Update session state when language is changed
    new_language_code = languages[selected_language_name]
    if new_language_code != st.session_state.language:
        st.session_state.language = new_language_code
        st.rerun()
    
    return st.session_state.language

def get_translation(key, language=None):
    """
    Get a translated string for the given key and language
    
    Args:
        key: The translation key
        language: Language code, falls back to session state language if not provided
    
    Returns:
        str: Translated string or the key itself if translation not found
    """
    if language is None:
        language = st.session_state.get('language', 'en')
    
    # Try to load translations from JSON files
    # First check in data/translations
    data_translations_path = os.path.join('data', 'translations')
    translation_file = os.path.join(data_translations_path, f"{language}.json")
    
    translations = {}
    
    try:
        # Try data/translations directory first
        if os.path.exists(translation_file):
            with open(translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
                if key in translations:
                    return translations[key]
        
        # Fall back to edumate/translations if needed
        edumate_translations_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'translations')
        edumate_translation_file = os.path.join(edumate_translations_path, f"{language}.json")
        
        if os.path.exists(edumate_translation_file):
            with open(edumate_translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
                if key in translations:
                    return translations[key]
        
        # If translation not found and language is not English, try English
        if language != 'en':
            en_file = os.path.join(data_translations_path, "en.json")
            if os.path.exists(en_file):
                with open(en_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                    if key in translations:
                        return translations[key]
    except Exception as e:
        st.error(f"Error loading translation: {e}")
    
    # If we get here, no translation was found
    return key