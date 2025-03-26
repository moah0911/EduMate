import streamlit as st
import json
import os

def show_language_selector():
    """
    Display a language selector in the sidebar and handle language switching
    
    Supports multiple languages: English, Hindi, Spanish, French, Chinese, and Arabic
    """
    # Define available languages with their display names and codes
    languages = {
        "English": "en",
        "हिंदी (Hindi)": "hi",
        "Español (Spanish)": "es", 
        "Français (French)": "fr",
        "中文 (Chinese)": "zh",
        "العربية (Arabic)": "ar"
    }
    
    # Get current language from session state or set default
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
        
    # Create a container with styled header
    st.sidebar.markdown("""
    <div style="background-color:#2a4c7d; color:white; padding:10px; 
         border-radius:5px; margin:5px 0; text-align:center; font-weight:bold;">
        Language / भाषा / Idioma
    </div>
    """, unsafe_allow_html=True)
    
    # Create a selectbox for language selection
    selected_language_name = st.sidebar.selectbox(
        "Select Language",
        list(languages.keys()),
        index=list(languages.values()).index(st.session_state.language),
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
    translations_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'translations')
    translation_file = os.path.join(translations_path, f"{language}.json")
    
    try:
        if os.path.exists(translation_file):
            with open(translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
                if key in translations:
                    return translations[key]
    except Exception as e:
        print(f"Error loading translation: {e}")
    
    # Fallback to English or the key itself
    if language != 'en':
        try:
            english_file = os.path.join(translations_path, "en.json")
            if os.path.exists(english_file):
                with open(english_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                    if key in translations:
                        return translations[key]
        except Exception:
            pass
    
    return key