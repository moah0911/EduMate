import os
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Try importing the internationalization module
    from edumate.utils.internationalization import internationalization, SUPPORTED_LANGUAGES, EDUCATION_SYSTEMS
    print("Successfully imported internationalization module!")
    print(f"Supported languages: {SUPPORTED_LANGUAGES}")
    print(f"Available education systems: {list(EDUCATION_SYSTEMS.keys())}")
except Exception as e:
    print(f"Error importing internationalization module: {e}")
