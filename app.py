import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import re
import random
import string
import uuid
import hashlib
import time
import logging
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import requests
import zipfile
import tempfile
import shutil
import sys
import fitz  # PyMuPDF
import docx
import nltk
import networkx as nx
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import Part
import google.generativeai as genai
from vertexai.preview.generative_models import (
    GenerativeModel as PreviewGenerativeModel,
)

# Import EduMate modules
from edumate.utils.encryption import Encryptor
from edumate.utils.analytics import Analytics
from edumate.utils.audit import AuditTrail
from edumate.utils.career_planner import CareerPlanner
from edumate.utils.indian_education import IndianEducationSystem
from edumate.utils.exam_manager import ExamManager
from edumate.utils.course_search import CourseSearch
from edumate.utils.show_course_announcements import show_course_announcements
from edumate.components.login_page import show_enhanced_login_page
from edumate.components.language_selector import get_translation

# Import utilities
from edumate.utils.logger import log_system_event, log_access, log_error, log_audit
from edumate.utils.teacher_tools import TeacherTools
from edumate.utils.quiz_manager import QuizManager
from edumate.utils.show_course_students import show_course_students
from edumate.utils.ai_career_advisor import AICareerAdvisor
from edumate.utils.classroom_manager import ClassroomManager

# Load environment variables from .env file
load_dotenv()

# Load CSS
def load_css():
    with open('edumate/static/style.css', 'r') as f:
        css = f.read()
    return css

# Set page configuration
st.set_page_config(
    page_title="EduMate - AI-Powered Education Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global CSS
st.markdown(f'<style>{load_css()}</style>', unsafe_allow_html=True)

# Add Font Awesome (required for the icons)
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">', unsafe_allow_html=True)

# Initialize utilities
encryptor = Encryptor()
analytics = Analytics('data')
audit_trail = AuditTrail('data')
career_planner = CareerPlanner('data')
indian_education = IndianEducationSystem()
exam_manager = ExamManager('data')
classroom_manager = ClassroomManager('data')
teacher_tools = TeacherTools(data_dir="data/teacher_tools")  # Updated path
quiz_manager = QuizManager('data')
course_search = CourseSearch()
ai_career_advisor = AICareerAdvisor()

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'  # Default to login page
if 'language' not in st.session_state:
    st.session_state.language = 'en'  # Default language is English

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Create teacher tools data directory if it doesn't exist
if not os.path.exists('data/teacher_tools'):
    os.makedirs('data/teacher_tools')

# Create uploads directory if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Create career data directory if it doesn't exist
if not os.path.exists('data/career'):
    os.makedirs('data/career')

# Initialize data files if they don't exist
if not os.path.exists('data/users.json'):
    with open('data/users.json', 'w') as f:
        json.dump([], f)

if not os.path.exists('data/courses.json'):
    with open('data/courses.json', 'w') as f:
        json.dump([], f)

if not os.path.exists('data/assignments.json'):
    with open('data/assignments.json', 'w') as f:
        json.dump([], f)

if not os.path.exists('data/submissions.json'):
    with open('data/submissions.json', 'w') as f:
        json.dump([], f)

# Initialize career planning data files
if not os.path.exists('data/career/skill_matrices.json'):
    with open('data/career/skill_matrices.json', 'w') as f:
        json.dump({
            "software_engineering": {
                "programming": 9,
                "problem_solving": 8,
                "system_design": 7,
                "teamwork": 6,
                "communication": 6
            },
            "data_science": {
                "statistics": 9,
                "programming": 7,
                "data_visualization": 8,
                "machine_learning": 8,
                "communication": 7
            },
            "product_management": {
                "business_acumen": 8,
                "communication": 9,
                "leadership": 8,
                "technical_understanding": 7,
                "problem_solving": 8
            }
        }, f, indent=4)

if not os.path.exists('data/career/course_recommendations.json'):
    with open('data/career/course_recommendations.json', 'w') as f:
        json.dump({
            "programming": [
                {"title": "Python for Everybody", "platform": "Coursera", "url": "https://www.coursera.org/specializations/python"},
                {"title": "The Complete Web Developer Course", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-web-developer-course-2"}
            ],
            "data_analysis": [
                {"title": "Data Science Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/jhu-data-science"},
                {"title": "Data Analyst Nanodegree", "platform": "Udacity", "url": "https://www.udacity.com/course/data-analyst-nanodegree--nd002"}
            ],
            "communication": [
                {"title": "Effective Communication", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/topics/communication"},
                {"title": "Public Speaking", "platform": "Coursera", "url": "https://www.coursera.org/learn/public-speaking"}
            ]
        }, f, indent=4)

# Load data
def load_data(file_name):
    with open(f'data/{file_name}.json', 'r') as f:
        return json.load(f)

def save_data(data, file_name):
    # Handle cases where parameters might be passed in reverse order
    # This happens due to inconsistent usage in show_course_announcements.py
    if isinstance(file_name, list) and isinstance(data, str):
        # Parameters are in reversed order, swap them
        data, file_name = file_name, data
        
    # Ensure data directory exists
    import os
    os.makedirs('data', exist_ok=True)
    
    with open(f'data/{file_name}.json', 'w') as f:
        json.dump(data, f, indent=4)

# Generate unique course code
def generate_unique_course_code():
    """Generate a unique 6-character alphanumeric code for courses"""
    courses = load_data('courses')
    existing_codes = {course.get('code', '') for course in courses}
    
    while True:
        # Generate a random 6-character alphanumeric code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in existing_codes:
            return code

# Ensure all courses have unique codes
def ensure_all_courses_have_codes():
    """Check all courses and generate unique codes for those without one"""
    courses = load_data('courses')
    updated = False
    
    for course in courses:
        if 'code' not in course or not course['code']:
            course['code'] = generate_unique_course_code()
            updated = True
    
    if updated:
        save_data(courses, 'courses')
        print("Updated courses with missing codes")

# User authentication functions
def register_user(email, password, name, role, username, date_of_birth):
    users = load_data('users')
    
    # Check if user already exists
    if any(user['email'] == email for user in users):
        return False, "Email already registered"
    
    # Create new user
    new_user = {
        'id': len(users) + 1,
        'email': email,
        'username': username,
        'password': password,  # In a real app, you would hash this
        'name': name,
        'role': role,
        'date_of_birth': date_of_birth,
        'created_at': datetime.now().isoformat()
    }
    
    users.append(new_user)
    save_data(users, 'users')
    return True, "Registration successful"

def login_user(login_id, password):
    """Login user with logging"""
    users = load_data('users')
    
    for user in users:
        # Allow login with email or username
        if (user['email'] == login_id or user.get('username') == login_id) and user['password'] == password:
            log_access(user['id'], "User logged in")
            return True, user
    
    log_error("Failed login attempt", {"login_id": login_id})
    return False, "Invalid username/email or password"

# Course management functions
def create_course(name, description, teacher_id, start_date, end_date, code=None):
    courses = load_data('courses')
    
    # Generate a unique code if not provided
    if not code:
        code = generate_unique_course_code()
    # Check if course code already exists
    elif any(course.get('code', '') == code for course in courses):
        return False, "Course code already exists"
    
    # Create new course
    new_course = {
        'id': len(courses) + 1,
        'name': name,
        'code': code,
        'description': description,
        'teacher_id': teacher_id,
        'start_date': start_date,
        'end_date': end_date,
        'created_at': datetime.now().isoformat(),
        'students': []
    }
    
    courses.append(new_course)
    save_data(courses, 'courses')
    return True, new_course

def get_teacher_courses(teacher_id):
    courses = load_data('courses')
    return [course for course in courses if course['teacher_id'] == teacher_id]

def get_student_courses(student_id):
    courses = load_data('courses')
    return [course for course in courses if student_id in course['students']]

def enroll_student(course_id, student_id):
    courses = load_data('courses')
    
    for i, course in enumerate(courses):
        if course['id'] == course_id:
            if student_id not in course['students']:
                courses[i]['students'].append(student_id)
                save_data(courses, 'courses')
                return True, "Enrolled successfully"
            else:
                return False, "Already enrolled"
    
    return False, "Course not found"

def join_course_by_code(course_code, student_id):
    """Allow students to join a course using the course code"""
    courses = load_data('courses')
    
    for i, course in enumerate(courses):
        if course.get('code', '') == course_code:
            if student_id not in course['students']:
                courses[i]['students'].append(student_id)
                save_data(courses, 'courses')
                return True, "Joined course successfully"
            else:
                return False, "Already enrolled in this course"
    
    return False, "Invalid course code"

# Assignment management functions
def create_assignment(title, description, course_id, teacher_id, due_date, points=100):
    assignments = load_data('assignments')
    
    # Create new assignment
    new_assignment = {
        'id': len(assignments) + 1,
        'title': title,
        'description': description,
        'course_id': course_id,
        'teacher_id': teacher_id,
        'due_date': due_date,
        'points': points,
        'created_at': datetime.now().isoformat()
    }
    
    assignments.append(new_assignment)
    save_data(assignments, 'assignments')
    return True, "Assignment created successfully"

def get_course_assignments(course_id):
    assignments = load_data('assignments')
    return [assignment for assignment in assignments if assignment['course_id'] == course_id]

def delete_assignment(assignment_id, teacher_id):
    """Delete assignment with audit trail"""
    assignments = load_data('assignments')
    
    # Find the assignment
    assignment_index = None
    for i, assignment in enumerate(assignments):
        if assignment['id'] == assignment_id:
            if assignment['teacher_id'] != teacher_id:
                return False, "You don't have permission to delete this assignment"
            assignment_index = i
            break
    
    if assignment_index is None:
        return False, "Assignment not found"
    
    # Check if there are any submissions for this assignment
    submissions = load_data('submissions')
    assignment_submissions = [sub for sub in submissions if sub['assignment_id'] == assignment_id]
    
    if assignment_submissions:
        # If there are submissions, we should handle them
        # Option 1: Delete all submissions (implemented here)
        # Option 2: Prevent deletion if submissions exist (alternative approach)
        
        # Delete all related submissions and their files
        for submission in assignment_submissions:
            # Delete any attached files
            if submission.get('file_info') and submission['file_info'].get('file_path'):
                file_path = submission['file_info']['file_path']
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting file: {e}")
        
        # Remove all submissions for this assignment
        submissions = [sub for sub in submissions if sub['assignment_id'] != assignment_id]
        save_data(submissions, 'submissions')
    
    # Remove the assignment
    deleted_assignment = assignments.pop(assignment_index)
    save_data(assignments, 'assignments')
    
    audit_trail.add_entry(
        teacher_id,
        "delete_assignment",
        {"assignment_id": assignment_id}
    )
    
    return True, "Assignment deleted successfully"

def submit_assignment(assignment_id, student_id, content, uploaded_file=None):
    submissions = load_data('submissions')
    
    # Check if already submitted
    if any(sub['assignment_id'] == assignment_id and sub['student_id'] == student_id for sub in submissions):
        return False, "You have already submitted this assignment"
    
    # Handle file upload if provided
    file_info = None
    if uploaded_file is not None:
        # Create directory for this assignment if it doesn't exist
        assignment_dir = f"uploads/assignment_{assignment_id}"
        if not os.path.exists(assignment_dir):
            os.makedirs(assignment_dir)
        
        # Save the file
        file_path = f"{assignment_dir}/{student_id}_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Store file information
        file_info = {
            'filename': uploaded_file.name,
            'file_path': file_path,
            'file_type': uploaded_file.type,
            'file_size': uploaded_file.size
        }
    
    # Create new submission
    new_submission = {
        'id': len(submissions) + 1,
        'assignment_id': assignment_id,
        'student_id': student_id,
        'content': content,
        'file_info': file_info,
        'submitted_at': datetime.now().isoformat(),
        'status': 'submitted',
        'score': None,
        'feedback': None,
        'ai_feedback': None
    }
    
    submissions.append(new_submission)
    save_data(submissions, 'submissions')
    return True, "Assignment submitted successfully"

def grade_submission(submission_id, score, feedback, use_ai_grading=False):
    submissions = load_data('submissions')
    
    for submission in submissions:
        if submission['id'] == submission_id:
            submission['score'] = score
            submission['feedback'] = feedback
            if use_ai_grading:
                submission['ai_feedback'] = generate_ai_feedback(submission)
            submission['status'] = 'graded'
            submission['graded_at'] = datetime.now().isoformat()
            save_data(submissions, 'submissions')
            return True, "Submission graded successfully"
    
    return False, "Submission not found"

def delete_submission(submission_id, student_id):
    """Delete a student's submission if it hasn't been graded yet."""
    submissions = load_data('submissions')
    
    # Find the submission
    submission_index = None
    for i, submission in enumerate(submissions):
        if submission['id'] == submission_id and submission['student_id'] == student_id:
            submission_index = i
            break
    
    if submission_index is None:
        return False, "Submission not found"
    
    # Check if the submission has been graded
    if submissions[submission_index]['status'] in ['graded', 'auto-graded']:
        return False, "Cannot delete a submission that has already been graded"
    
    # Delete the file if it exists
    if submissions[submission_index].get('file_info'):
        file_path = submissions[submission_index]['file_info'].get('file_path')
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                # Continue even if file deletion fails
                print(f"Error deleting file: {e}")
    
    # Remove the submission from the list
    deleted_submission = submissions.pop(submission_index)
    save_data(submissions, 'submissions')
    
    return True, "Submission deleted successfully"

# Add Gemini API configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_MODELS = {
    "gemini-1.5-pro": "Improved model with better accuracy",
    "gemini-1.5-flash": "Fast and efficient model for quick responses",
    "gemini-2.0-flash": "Efficient on large scale"
}
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1/models"

def analyze_with_gemini(content_type, file_path, prompt, mime_type, model="gemini-1.5-pro"):
    """Analyze content using specific Gemini model"""
    if not GEMINI_API_KEY:
        st.error("Gemini API key not found. Please add GEMINI_API_KEY to your .env file.")
        return "Error: Valid Gemini API key not configured."
    
    try:
        # Read the file and encode it as base64
        with open(file_path, "rb") as file:
            file_data = base64.b64encode(file.read()).decode('utf-8')
        
        # Prepare the request payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": file_data
                            }
                        }
                    ]
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }
        
        api_url = f"{GEMINI_API_BASE_URL}/{model}:generateContent"
        
        st.info(f"Using model: {model}...")
        response = requests.post(
            api_url,
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                if 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content']:
                    for part in result['candidates'][0]['content']['parts']:
                        if 'text' in part:
                            st.success(f"Successfully used model: {model}")
                            return part['text']
        
        return f"Model {model} failed: {response.text}"
        
    except Exception as e:
        return f"Error analyzing with {model}: {str(e)}"

def analyze_image_with_gemini(image_path, prompt):
    """
    Analyze an image using Google Gemini API
    """
    return analyze_with_gemini('image', image_path, prompt, 'image/jpeg')

def analyze_pdf_with_gemini(pdf_path, prompt):
    """
    Analyze a PDF file directly using Google Gemini API
    This function sends the PDF file directly to Gemini without extracting images
    """
    return analyze_with_gemini('pdf', pdf_path, prompt, 'application/pdf')

def extract_images_from_pdf(pdf_path, output_dir):
    """Extract images from a PDF file using PyMuPDF"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    image_paths = []
    
    try:
        if pymupdf is None:
            raise ImportError("PyMuPDF is not installed")

        # Open the PDF using PyMuPDF
        pdf_document = pymupdf.open(pdf_path)
        
        # Rest of the function remains the same
        for page_num, page in enumerate(pdf_document):
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                image_filename = f"page{page_num+1}_img{img_index+1}.{image_ext}"
                image_path = os.path.join(output_dir, image_filename)
                
                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)
                
                image_paths.append(image_path)
        
        # If no images found, try extracting as whole page images
        if not image_paths:
            for page_num, page in enumerate(pdf_document):
                pix = page.get_pixmap()
                image_filename = f"page{page_num+1}.png"
                image_path = os.path.join(output_dir, image_filename)
                pix.save(image_path)
                image_paths.append(image_path)
        
        return image_paths

    except ImportError as e:
        st.error(f"Error: {str(e)}. Please install PyMuPDF using: pip install PyMuPDF")
        return []
    except Exception as e:
        st.error(f"Error extracting images from PDF: {str(e)}")
        return []

def auto_grade_submission(submission_id):
    """Automatically grade a submission using AI"""
    submissions = load_data('submissions')
    submission = next((sub for sub in submissions if sub['id'] == submission_id), None)
    
    if not submission:
        return False, "Submission not found"
    
    assignment = get_assignment_by_id(submission['assignment_id'])
    
    # Analyze text content
    content = submission['content']
    
    # Also analyze file content if available
    file_content = ""
    file_analysis = ""
    gemini_analysis = ""
    
    if submission.get('file_info'):
        file_info = submission.get('file_info')
        file_path = file_info['file_path']
        
        if os.path.exists(file_path):
            try:
                # Extract text based on file type
                if file_info['file_type'].endswith('pdf'):
                    # First try to extract text
                    file_content = extract_text_from_pdf(file_path)
                    
                    # If it's likely a handwritten PDF (little text extracted), process with Gemini
                    if len(file_content.split()) < 20 or "[PDF content extracted" in file_content:
                        # Send the PDF directly to Gemini for analysis
                        prompt = f"This is a PDF submission for the assignment: '{assignment['title']}'. Please analyze the content, including any handwritten text. Extract all text if possible, and evaluate the answer in terms of correctness, completeness, and clarity. If there are handwritten portions, please transcribe them and include them in your analysis."
                        gemini_analysis = analyze_pdf_with_gemini(file_path, prompt)
                        
                        # Format the analysis for display
                        if gemini_analysis and not gemini_analysis.startswith("Error"):
                            gemini_analysis = "## PDF Content Analysis\n\n" + gemini_analysis
                
                elif file_info['file_type'].endswith('docx'):
                    file_content = extract_text_from_docx(file_path)
                else:
                    # For text files or other formats
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                
                # Analyze the file content
                file_analysis = analyze_file_content(file_content, file_info['filename'])
            except Exception as e:
                file_analysis = f"Error analyzing file: {str(e)}"
    
    # Simple auto-grading logic (in a real app, this would use more sophisticated AI)
    max_points = assignment['points']
    
    # Combine text and file content for analysis
    combined_content = content + "\n" + file_content
    word_count = len(combined_content.split())
    
    # Base score on word count and quality indicators
    if word_count < 50:
        score = max_points * 0.6  # 60% for very brief answers
    elif word_count < 100:
        score = max_points * 0.7  # 70% for short answers
    elif word_count < 200:
        score = max_points * 0.8  # 80% for medium answers
    else:
        score = max_points * 0.9  # 90% for long answers
    
    # If we have Gemini analysis, adjust the score based on that
    if gemini_analysis:
        # Give a higher base score for handwritten submissions that were analyzed
        score = max_points * 0.85
    
    # Adjust score based on quality indicators
    if "because" in combined_content.lower() or "therefore" in combined_content.lower():
        score += max_points * 0.05  # Bonus for reasoning
    
    if len(combined_content.split('.')) > 5:
        score += max_points * 0.05  # Bonus for good structure
    
    # Round the score
    score = round(min(score, max_points))
    
    # Generate AI feedback
    ai_feedback = generate_ai_feedback(submission, file_content, file_analysis, gemini_analysis)
    
    # Update the submission
    for i, sub in enumerate(submissions):
        if sub['id'] == submission_id:
            submissions[i]['score'] = score
            submissions[i]['ai_feedback'] = ai_feedback
            submissions[i]['status'] = 'auto-graded'
            submissions[i]['graded_at'] = datetime.now().isoformat()
            save_data(submissions, 'submissions')
            return True, f"Submission auto-graded with score {score}/{max_points}"
    
    return False, "Failed to update submission"

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file"""
    # In a real app, you would use a library like PyPDF2 or pdfplumber
    # For this simplified version, we'll return a placeholder
    return f"[PDF content extracted from {os.path.basename(file_path)}]"

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file"""
    # In a real app, you would use a library like python-docx
    # For this simplified version, we'll return a placeholder
    return f"[DOCX content extracted from {os.path.basename(file_path)}]"

def analyze_file_content(content, filename):
    """Analyze the content of a file"""
    # This is a simplified analysis
    file_ext = os.path.splitext(filename)[1].lower()
    
    analysis = f"## File Analysis: {filename}\n\n"
    
    # Word count
    words = content.split()
    word_count = len(words)
    analysis += f"- Word count: {word_count}\n"
    
    # Sentence count
    sentences = re.split(r'[.!?]+', content)
    sentence_count = len([s for s in sentences if s.strip()])
    analysis += f"- Sentence count: {sentence_count}\n"
    
    # Average sentence length
    if sentence_count > 0:
        avg_sentence_length = word_count / sentence_count
        analysis += f"- Average sentence length: {avg_sentence_length:.1f} words\n"
    
    # File type specific analysis
    if file_ext == '.pdf':
        analysis += "- Document appears to be a PDF, which typically indicates a formal submission.\n"
    elif file_ext == '.docx':
        analysis += "- Document is in Word format, which is appropriate for academic submissions.\n"
    elif file_ext == '.txt':
        analysis += "- Document is in plain text format. Consider using a more formatted document type for future submissions.\n"
    
    return analysis

def generate_ai_feedback(submission, file_content="", file_analysis="", gemini_analysis=""):
    """Generate AI feedback for a submission"""
    # Get the assignment and student details
    assignment = get_assignment_by_id(submission['assignment_id'])
    student = get_user_by_id(submission['student_id'])
    
    # Analyze the submission content
    content = submission['content']
    word_count = len(content.split())
    
    # Generate feedback based on content length and quality
    strengths = []
    improvements = []
    
    # Text content analysis
    if word_count < 50:
        improvements.append("Your text submission is quite brief. Consider expanding your answer with more details.")
    else:
        strengths.append("You provided a detailed text response with good length.")
    
    if "because" in content.lower() or "therefore" in content.lower():
        strengths.append("Good use of reasoning and logical connections in your answer.")
    else:
        improvements.append("Try to include more reasoning and logical connections in your answer.")
    
    if len(content.split('.')) > 5:
        strengths.append("Good structure with multiple sentences in your text submission.")
    else:
        improvements.append("Consider structuring your text answer with more complete sentences.")
    
    # File submission analysis
    if submission.get('file_info'):
        file_info = submission.get('file_info')
        strengths.append(f"You submitted a file ({file_info['filename']}) which demonstrates thoroughness.")
        
        # Add file-specific feedback
        if file_info['file_type'].endswith('pdf'):
            strengths.append("Your PDF submission is in a professional format suitable for academic work.")
            
            # If we have Gemini analysis, it means it was a handwritten or complex PDF
            if gemini_analysis:
                strengths.append("Your PDF was analyzed directly by our AI system, including any handwritten content.")
                
                # Check if the analysis mentions handwritten content
                if "handwritten" in gemini_analysis.lower() or "handwriting" in gemini_analysis.lower():
                    strengths.append("Your handwritten work shows dedication and personal effort in your submission.")
        elif file_info['file_type'].endswith('docx'):
            strengths.append("Your Word document submission follows standard academic formatting.")
        elif file_info['file_type'].endswith('txt'):
            improvements.append("Consider using a more formatted document type (like PDF or DOCX) for future submissions.")
    else:
        improvements.append("Consider attaching a file with your submission for more comprehensive work.")
    
    # Generate personalized feedback
    feedback = f"# AI-Generated Feedback for {student['name']}\n\n"
    feedback += f"## Assignment: {assignment['title']}\n\n"
    
    feedback += "### Strengths:\n"
    for strength in strengths:
        feedback += f"- {strength}\n"
    
    feedback += "\n### Areas for Improvement:\n"
    for improvement in improvements:
        feedback += f"- {improvement}\n"
    
    # Add file analysis if available
    if file_analysis:
        feedback += f"\n{file_analysis}\n"
    
    # Add Gemini analysis of PDF content if available
    if gemini_analysis:
        feedback += f"\n{gemini_analysis}\n"
    
    feedback += "\n### Summary:\n"
    feedback += "This automated feedback is based on an analysis of your submission. "
    
    if submission.get('file_info'):
        if gemini_analysis:
            feedback += "Your PDF was analyzed directly using Google Gemini AI, which can process both text and handwritten content. "
        else:
            feedback += "Both your text response and uploaded file were evaluated. "
    else:
        feedback += "Your text response was evaluated. "
    
    feedback += "It's designed to help you improve your work. "
    feedback += "Please review the teacher's manual feedback as well for more personalized guidance."
    
    return feedback

def get_file_download_link(file_path, filename):
    """Generate a download link for a file"""
    if not os.path.exists(file_path):
        return "File not found"
    
    with open(file_path, "rb") as f:
        data = f.read()
    
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

def check_api_key_status():
    """Check if the Gemini API key is configured"""
    if not GEMINI_API_KEY:
        return "❌ Not configured", "Please add GEMINI_API_KEY to your .env file."
    else:
        # Only show that the key is configured, not the actual key
        return "✅ Configured", "API key is set and ready to use."

def get_assignment_submissions(assignment_id):
    submissions = load_data('submissions')
    return [sub for sub in submissions if sub['assignment_id'] == assignment_id]

def get_student_submissions(student_id):
    submissions = load_data('submissions')
    return [sub for sub in submissions if sub['student_id'] == student_id]

# Helper functions
def get_user_by_id(user_id):
    users = load_data('users')
    for user in users:
        if user['id'] == user_id:
            return user
    return None

def get_course_by_id(course_id):
    courses = load_data('courses')
    for course in courses:
        if course['id'] == course_id:
            return course
    return None

def get_assignment_by_id(assignment_id):
    assignments = load_data('assignments')
    for assignment in assignments:
        if assignment['id'] == assignment_id:
            return assignment
    return None

def get_submission_by_id(submission_id):
    submissions = load_data('submissions')
    for submission in submissions:
        if submission['id'] == submission_id:
            return submission
    return None

# Navigation functions
def set_page(page):
    st.session_state.current_page = page

# UI Components
def show_login_page():
    st.title("Login to EduMate")
    
    with st.form("login_form"):
        login_id = st.text_input("Email or Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            success, result = st.session_state.login_function(login_id, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.current_user = result
                st.session_state.current_page = 'dashboard'
                st.rerun()
            else:
                st.error(result)
    
    st.markdown("---")
    st.write("Don't have an account?")
    if st.button("Register", key="login_register_btn"):
        st.session_state.current_page = 'register'
        st.rerun()

def show_register_page():
    st.title("Register for EduMate")
    
    # Remove all custom scripts and styles that might be causing issues
    
    with st.form("register_form", clear_on_submit=False):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        username = st.text_input("Username (must be unique)")
        date_of_birth = st.date_input("Date of Birth")
        
        # Create two columns
        pw_col1, pw_col2 = st.columns([3, 1])
        
        with pw_col1:
            # Use the simplest possible password field solution
            # No type="password" which causes input problems
            password = st.text_input("Password", type="text", key="register_pwd")
        
        with pw_col2:
            # Add simple note about password visibility
            st.write(" ")  # Add some space
            st.caption("For security, consider typing in a private location")
        
        role = st.selectbox("Role", ["teacher", "student"])
        submit = st.form_submit_button("Register")
        
        if submit:
            if not name or not email or not password or not username:
                st.error("Please fill in all required fields")
            else:
                success, message = register_user(email, password, name, role, username, date_of_birth.isoformat())
                if success:
                    st.success(message)
                    st.session_state.current_page = 'login'
                    st.rerun()
                else:
                    st.error(message)
    
    st.markdown("---")
    st.write("Already have an account?")
    if st.button("Login", key="register_login_btn"):
        st.session_state.current_page = 'login'
        st.rerun()

def show_dashboard():
    st.title(f"Welcome, {st.session_state.current_user['name']}!")
    
    # Header section with consistent styling
    st.markdown('''
    <div class="header-section">
        <div class="logo-container">
            <i class="fas fa-graduation-cap" style="font-size: 40px; color: #6366f1;"></i>
        </div>
        <h1 class="app-title">EduMate</h1>
        <p class="app-subtitle">AI-Powered Education</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Display different content based on user role
    if st.session_state.current_user['role'] == 'teacher':
        show_teacher_dashboard()
    else:
        show_student_dashboard()

def show_teacher_dashboard():
    # Welcome message with modern styling
    st.markdown(f'''
    <div class="card">
        <h2><i class="fas fa-chalkboard-teacher"></i> {get_translation("welcome")}, {st.session_state.current_user['name']}!</h2>
        <p style="color: #4b5563; font-size: 1.1rem;">{get_translation("teacher_dashboard_desc")}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Get teacher's courses
    teacher_id = st.session_state.current_user['id']
    courses = get_teacher_courses(teacher_id)
    
    st.title("Teacher Dashboard")
    
    # Dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["My Courses", "Create Course", "Create Test", "Analytics", "Teacher Tools"])
    
    with tab1:
        st.header("My Courses")
        if not courses:
            st.info("You haven't created any courses yet.")
        else:
            for course in courses:
                with st.container():
                    st.markdown(f"### {course['name']}")
                    
                    # Display course code with a distinct background for visibility
                    code = course.get('code', 'No code')
                    st.markdown(f"""
                    <div style="background-color:rgba(255, 255, 255, 0.9); padding:15px; border-radius:10px; 
                         margin:5px 0; text-align:center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                        <h3 style="margin:0; color:#111827; font-weight:600;">Course Code: {code}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write(course.get('description', 'No description available.')[:100] + 
                             ("..." if len(course.get('description', '')) > 100 else ''))
                    
                    if st.button("View Course", key=f"view_course_{course['id']}"):
                        st.session_state.current_course = course
                        st.session_state.current_page = 'course_detail'
                        st.rerun()
                    
                    if st.button("Add Assignment", key=f"add_assignment_{course['id']}"):
                        st.session_state.current_course = course
                        st.session_state.current_page = 'create_assignment'
                        st.rerun()
                
                st.markdown("<hr style='margin: 15px 0px; border: 1px solid #444444;'>", unsafe_allow_html=True)
    
    with tab2:
        st.header("Create New Course")
        with st.form(key="create_course_form"):
            course_name = st.text_input("Course Name")
            course_description = st.text_area("Description")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
            with col2:
                end_date = st.date_input("End Date")
            
            submit_button = st.form_submit_button("Create Course")
            
            if submit_button:
                if not course_name:
                    st.error("Course name is required.")
                elif start_date >= end_date:
                    st.error("End date must be after start date.")
                else:
                    # Create the course
                    new_course = create_course(
                        name=course_name,
                        description=course_description,
                        teacher_id=teacher_id,
                        start_date=start_date.isoformat(),
                        end_date=end_date.isoformat()
                    )
                    
                    if new_course:
                        st.success(f"Course '{course_name}' created successfully!")
                        # Log the action
                        log_audit(
                            teacher_id,
                            'create',
                            'course',
                            new_course['id'],
                            True,
                            f"Created course: {course_name}"
                        )
                        # Refresh the page
                        st.rerun()
                    else:
                        st.error("Failed to create course. Please try again.")
    
    with tab3:
        show_test_creator()
    
    with tab4:
        st.header("Analytics")
        
        # Course selection for analytics
        if not courses:
            st.info("You need to create courses to view analytics.")
        else:
            selected_course = st.selectbox(
                "Select Course",
                options=courses,
                format_func=lambda x: f"{x['name']} ({x['code']})",
                key="analytics_course_select"  # Add unique key here
            )
            
            if selected_course:
                # Get assignments for the selected course
                course_assignments = get_course_assignments(selected_course['id'])
                
                if not course_assignments:
                    st.info("No assignments found for this course.")
                else:
                    # Display assignment completion stats
                    st.subheader("Assignment Completion")
                    
                    # Calculate completion rates
                    completion_data = []
                    for assignment in course_assignments:
                        submissions = get_assignment_submissions(assignment['id'])
                        enrolled_count = len([s for s in selected_course.get('students_enrolled', []) 
                                            if isinstance(s, dict) and s.get('status') == 'active'])
                        
                        if enrolled_count > 0:
                            completion_rate = (len(submissions) / enrolled_count) * 100
                        else:
                            completion_rate = 0
                        
                        completion_data.append({
                            'Assignment': assignment['title'],
                            'Completion Rate (%)': completion_rate,
                            'Submissions': len(submissions),
                            'Total Students': enrolled_count
                        })
                    
                    if completion_data:
                        completion_df = pd.DataFrame(completion_data)
                        st.bar_chart(completion_df.set_index('Assignment')['Completion Rate (%)'])
                        st.dataframe(completion_df)
                    
                    # Display grade distribution
                    st.subheader("Grade Distribution")
                    
                    # Calculate grade distribution
                    all_grades = []
                    for assignment in course_assignments:
                        submissions = get_assignment_submissions(assignment['id'])
                        for submission in submissions:
                            if submission.get('score') is not None:
                                all_grades.append({
                                    'Assignment': assignment['title'],
                                    'Score': submission['score'],
                                    'Student': get_user_by_id(submission['student_id'])['name']
                                })
                    
                    if all_grades:
                        grades_df = pd.DataFrame(all_grades)
                        
                        # Histogram of grades
                        fig, ax = plt.subplots()
                        ax.hist(grades_df['Score'], bins=10, range=(0, 100))
                        ax.set_xlabel('Score')
                        ax.set_ylabel('Frequency')
                        ax.set_title('Grade Distribution')
                        st.pyplot(fig)
                        
                        # Average scores by assignment
                        st.subheader("Average Scores by Assignment")
                        avg_scores = grades_df.groupby('Assignment')['Score'].mean().reset_index()
                        st.bar_chart(avg_scores.set_index('Assignment')['Score'])
    
    with tab5:
        show_teacher_tools()

def show_teacher_tools():
    """Display teacher tools and resources."""
    st.header("Teacher Tools")
    
    # Create tabs for different teacher tools
    tools_tab1, tools_tab2, tools_tab3, tools_tab4 = st.tabs([
        "Lesson Planning", 
        "Assessment Tools", 
        "Resource Library",
        "Professional Development"
    ])
    
    with tools_tab1:
        st.subheader("Lesson Planning")
        
        # Get lesson plan templates from teacher tools
        lesson_templates = teacher_tools.get_lesson_templates()
        
        if lesson_templates:
            st.write("Select a lesson plan template to get started:")
            
            for template in lesson_templates:
                with st.expander(template.get('name', 'Unnamed Template')):
                    st.write(f"**Description:** {template.get('description', 'No description available.')}")
                    
                    # Display template structure
                    if template.get('structure'):
                        st.write("**Template Structure:**")
                        for section in template.get('structure'):
                            st.write(f"- {section}")
                    
                    # Download template button
                    if st.button("Use This Template", key=f"use_template_{template.get('id', '0')}"):
                        # In a real app, this would download or open the template
                        st.success(f"Template '{template.get('name')}' selected. You can now customize it.")
                        
                        # Show template form
                        with st.form(f"lesson_plan_{template.get('id', '0')}"):
                            st.write("### Customize Your Lesson Plan")
                            
                            lesson_title = st.text_input("Lesson Title")
                            lesson_objectives = st.text_area("Learning Objectives")
                            lesson_duration = st.number_input("Duration (minutes)", min_value=15, max_value=180, value=45, step=5)
                            
                            # Materials needed
                            materials = st.text_area("Materials Needed")
                            
                            # Lesson structure
                            st.write("### Lesson Structure")
                            
                            intro = st.text_area("Introduction/Warm-up (5-10 minutes)")
                            main_activity = st.text_area("Main Activity (20-30 minutes)")
                            conclusion = st.text_area("Conclusion/Wrap-up (5-10 minutes)")
                            assessment = st.text_area("Assessment/Evaluation")
                            
                            # Additional notes
                            notes = st.text_area("Additional Notes")
                            
                            # Submit button
                            submit_lesson = st.form_submit_button("Save Lesson Plan")
                            
                            if submit_lesson:
                                if not lesson_title:
                                    st.error("Please enter a lesson title.")
                                else:
                                    # In a real app, this would save the lesson plan
                                    st.success(f"Lesson plan '{lesson_title}' saved successfully!")
        else:
            st.info("No lesson plan templates available.")
        
        # AI Lesson Plan Generator
        st.subheader("AI Lesson Plan Generator")
        
        with st.form("ai_lesson_generator"):
            st.write("Let AI help you create a lesson plan based on your requirements.")
            
            # Required fields with red asterisks
            st.markdown("**Required Fields**")
            col1, col2 = st.columns([10, 1])
            with col1:
                ai_subject = st.text_input("Subject")
            with col2:
                st.markdown('<p style="color:red; font-size:20px; margin-top:15px">*</p>', unsafe_allow_html=True)
                
            col1, col2 = st.columns([10, 1])
            with col1:
                ai_topic = st.text_input("Specific Topic")
            with col2:
                st.markdown('<p style="color:red; font-size:20px; margin-top:15px">*</p>', unsafe_allow_html=True)
            
            # Optional fields
            st.markdown("**Optional Fields**")
            ai_grade = st.selectbox("Grade Level", ["Elementary", "Middle School", "High School", "College"])
            ai_duration = st.number_input("Lesson Duration (minutes)", min_value=15, max_value=180, value=45, step=5)
            
            # Special requirements
            ai_requirements = st.text_area("Special Requirements or Notes")
            
            # Generate button
            generate_button = st.form_submit_button("Generate Lesson Plan")
            
            if generate_button:
                if not ai_subject or not ai_topic:
                    st.error("Please fill in all required fields (marked with red asterisk).")
                else:
                    with st.spinner("Generating lesson plan..."):
                        # Simulate AI processing
                        import time
                        time.sleep(3)
                        
                        # Display generated lesson plan
                        st.success("Lesson plan generated successfully!")
                        
                        st.write(f"## {ai_topic} - {ai_grade} Lesson Plan")
                        st.write(f"**Subject:** {ai_subject}")
                        st.write(f"**Duration:** {ai_duration} minutes")
                        
                        # Generate more relevant content based on subject and topic
                        if ai_subject.lower() in ["math", "mathematics"]:
                            objectives = [
                                f"Explain the key concepts and principles of {ai_topic} in their own words",
                                f"Solve various problems involving {ai_topic} using appropriate techniques",
                                f"Apply {ai_topic} concepts to real-world situations and explain their relevance"
                            ]
                            materials = [
                                "Graphing calculators or appropriate math tools",
                                f"Worksheets with {ai_topic} problems of varying difficulty",
                                f"Visual aids showing {ai_topic} concepts and applications"
                            ]
                            activities = [
                                f"Begin by asking students what they already know about {ai_topic}",
                                f"Demonstrate how {ai_topic} works using interactive examples",
                                f"Guide students through increasingly complex {ai_topic} problems",
                                f"Have students work in pairs to explain {ai_topic} to each other"
                            ]
                            assessment = [
                                f"Ask students to explain a {ai_topic} concept in their own words",
                                f"Have students solve 3-5 problems involving {ai_topic}",
                                f"Assign homework that connects {ai_topic} to real-world applications"
                            ]
                            topic_intro = f"Begin the lesson by connecting {ai_topic} to something students are familiar with. For example, you might discuss how {ai_topic} appears in everyday situations or how it builds on concepts they already know. Ask open-ended questions to gauge their current understanding."
                        elif ai_subject.lower() in ["science", "biology", "chemistry", "physics"]:
                            objectives = [
                                f"Describe the fundamental principles of {ai_topic} using scientific terminology",
                                f"Analyze primary and secondary sources related to {ai_topic}",
                                f"Evaluate the historical significance and modern relevance of {ai_topic}"
                            ]
                            materials = [
                                f"Historical maps, timelines, or artifacts related to {ai_topic}",
                                f"Primary source documents from the {ai_topic} period or event",
                                f"Video clips or multimedia resources about {ai_topic}"
                            ]
                            activities = [
                                f"Begin with an intriguing question or demonstration about {ai_topic}",
                                f"Guide students through analysis of sources related to {ai_topic}",
                                f"Have students collect and analyze data related to {ai_topic}",
                                f"Facilitate a discussion about different perspectives on {ai_topic}"
                            ]
                            assessment = [
                                f"Ask students to analyze a primary source related to {ai_topic}",
                                f"Have students write a brief argument about the significance of {ai_topic}",
                                f"Evaluate students' ability to connect {ai_topic} to current events or issues"
                            ]
                            topic_intro = f"Begin by posing a thought-provoking question about {ai_topic} that challenges students to consider its significance. You might use a compelling image, quote, or artifact to spark curiosity. Consider starting with a brief anecdote that humanizes the historical figures or events involved in {ai_topic}."
                        elif ai_subject.lower() in ["english", "language arts", "literature"]:
                            objectives = [
                                f"Analyze key elements and themes of {ai_topic} using textual evidence",
                                f"Evaluate different perspectives and interpretations of {ai_topic}",
                                f"Express thoughtful ideas about {ai_topic} through discussion and writing"
                            ]
                            materials = [
                                f"Text excerpts or complete works related to {ai_topic}",
                                f"Discussion prompts and guiding questions about {ai_topic}",
                                "Writing materials or digital tools for response"
                            ]
                            activities = [
                                f"Begin with a compelling quote or passage about {ai_topic}",
                                f"Guide students through close reading of text related to {ai_topic}",
                                f"Facilitate a structured discussion exploring different aspects of {ai_topic}",
                                f"Have students write reflectively about {ai_topic}"
                            ]
                            assessment = [
                                f"Ask students to analyze a passage related to {ai_topic} using specific textual evidence",
                                f"Evaluate student participation in discussion about {ai_topic}",
                                f"Collect written responses that demonstrate understanding of {ai_topic}"
                            ]
                            topic_intro = f"Begin by connecting {ai_topic} to students' experiences or current events. You might ask students to reflect on their own encounters with themes related to {ai_topic} or show how {ai_topic} remains relevant today. This personal connection helps students see the value in studying this topic."
                        elif ai_subject.lower() in ["history", "social studies"]:
                            objectives = [
                                f"Explain the key events, figures, and developments in {ai_topic}",
                                f"Analyze primary and secondary sources related to {ai_topic}",
                                f"Evaluate the historical significance and modern relevance of {ai_topic}"
                            ]
                            materials = [
                                f"Historical maps, timelines, or artifacts related to {ai_topic}",
                                f"Primary source documents from the {ai_topic} period or event",
                                f"Video clips or multimedia resources about {ai_topic}"
                            ]
                            activities = [
                                f"Begin with an engaging historical question about {ai_topic}",
                                f"Guide students through analysis of sources related to {ai_topic}",
                                f"Have students create timelines or maps illustrating aspects of {ai_topic}",
                                f"Facilitate a discussion about different perspectives on {ai_topic}"
                            ]
                            assessment = [
                                f"Ask students to analyze a primary source related to {ai_topic}",
                                f"Have students write a brief argument about the significance of {ai_topic}",
                                f"Evaluate students' ability to connect {ai_topic} to current events or issues"
                            ]
                            topic_intro = f"Begin by posing a thought-provoking question about {ai_topic} that challenges students to consider its significance. You might use a compelling image, quote, or artifact to spark curiosity. Consider starting with a brief anecdote that humanizes the historical figures or events involved in {ai_topic}."
                        else:
                            objectives = [
                                f"Explain the fundamental concepts and principles of {ai_topic}",
                                f"Apply knowledge of {ai_topic} to relevant problems or situations",
                                f"Analyze and evaluate information related to {ai_topic}"
                            ]
                            materials = [
                                f"Textbooks or digital resources covering {ai_topic}",
                                f"Worksheets or handouts with {ai_topic} exercises",
                                f"Visual aids or presentation slides illustrating {ai_topic}"
                            ]
                            activities = [
                                f"Begin with an engaging hook related to {ai_topic}",
                                f"Present key concepts of {ai_topic} with relevant examples",
                                f"Guide students through practice activities related to {ai_topic}",
                                f"Have students apply their understanding of {ai_topic} independently"
                            ]
                            assessment = [
                                f"Ask questions throughout the lesson to check understanding of {ai_topic}",
                                f"Have students complete a brief quiz or exit ticket about {ai_topic}",
                                f"Assign homework that reinforces learning about {ai_topic}"
                            ]
                            topic_intro = f"Begin by connecting {ai_topic} to students' prior knowledge or experiences. Ask what they already know about {ai_topic} or related concepts. You might use a brief demonstration, video clip, or real-world example to show why {ai_topic} is important and relevant to their lives."
                        
                        # Display learning objectives
                        st.write("### Learning Objectives")
                        st.write("By the end of this lesson, students will be able to:")
                        for i, objective in enumerate(objectives, 1):
                            st.write(f"{i}. {objective}")
                        
                        # Display materials needed
                        st.write("### Materials Needed")
                        for material in materials:
                            st.write(f"- {material}")
                        
                        # Display lesson structure
                        st.write("### Lesson Structure")
                        
                        st.write("**Introduction (10 minutes)**")
                        st.write(topic_intro)
                        
                        st.write("**Main Activity (25 minutes)**")
                        for activity in activities:
                            st.write(f"- {activity}")
                        
                        st.write("**Conclusion (10 minutes)**")
                        st.write(f"- Have students summarize the key points about {ai_topic} in their own words")
                        st.write("- Address any questions or misconceptions that arose during the lesson")
                        st.write(f"- Preview how {ai_topic} connects to upcoming content")
                        
                        # Display assessment
                        st.write("### Assessment")
                        for assess in assessment:
                            st.write(f"- {assess}")
                        
                        # Add suggested next steps and resources
                        st.write("### Next Steps and Resources")
                        
                        # Generate relevant resources based on subject and topic
                        if ai_subject.lower() in ["math", "mathematics"]:
                            resources = [
                                {"name": f"Khan Academy: {ai_topic}", "url": f"https://www.khanacademy.org/search?referer=%2F&page_search_query={ai_topic.replace(' ', '+')}"},
                                {"name": f"Desmos Activities for {ai_topic}", "url": f"https://teacher.desmos.com/search?q={ai_topic.replace(' ', '+')}"},
                                {"name": "NCTM Illuminations", "url": "https://illuminations.nctm.org/"}
                            ]
                            online_courses = [
                                {"name": f"Coursera: Mathematics for {ai_grade} Level", "url": f"https://www.coursera.org/search?query={ai_topic}%20{ai_subject}&index=prod_all_launched_products_term_optimization"},
                                {"name": f"edX: {ai_topic} Courses", "url": f"https://www.edx.org/search?q={ai_topic}+{ai_subject}"},
                                {"name": f"Udemy: {ai_topic} in Mathematics", "url": f"https://www.udemy.com/courses/search/?src=ukw&q={ai_topic}+{ai_subject}"}
                            ]
                            books_articles = [
                                {"name": f"OpenStax: Free Mathematics Textbooks", "url": "https://openstax.org/subjects/math"},
                                {"name": f"JSTOR Articles on {ai_topic}", "url": f"https://www.jstor.org/action/doBasicSearch?Query={ai_topic}"},
                                {"name": f"arXiv Mathematics Papers on {ai_topic}", "url": f"https://arxiv.org/search/?query={ai_topic}+{ai_subject}"}
                            ]
                            videos_podcasts = [
                                {"name": f"3Blue1Brown: Visual Mathematics", "url": "https://www.3blue1brown.com/"},
                                {"name": f"Numberphile Videos on {ai_topic}", "url": f"https://www.youtube.com/user/numberphile/search?query={ai_topic}"},
                                {"name": f"Math Ed Podcast", "url": "https://www.podomatic.com/podcasts/mathed"}
                            ]
                            next_topics = [
                                f"Advanced applications of {ai_topic} in real-world contexts",
                                f"Connecting {ai_topic} to related mathematical concepts",
                                f"Using technology tools to explore {ai_topic} more deeply"
                            ]
                        elif ai_subject.lower() in ["science", "biology", "chemistry", "physics"]:
                            resources = [
                                {"name": f"PhET Interactive Simulations: {ai_topic}", "url": f"https://phet.colorado.edu/en/simulations/filter?subjects=biology,chemistry,earth-science,physics&type=html,prototype&search={ai_topic.replace(' ', '+')}"},
                                {"name": f"NASA Education Resources on {ai_topic}", "url": f"https://www.nasa.gov/education/resources/?search={ai_topic.replace(' ', '+')}"},
                                {"name": f"National Geographic: {ai_topic}", "url": f"https://www.nationalgeographic.org/education/search/?q={ai_topic.replace(' ', '+')}"},
                                {"name": f"HHMI BioInteractive: {ai_topic}", "url": f"https://www.biointeractive.org/search?keywords={ai_topic.replace(' ', '+')}"},
                                {"name": f"Science Friday Podcasts on {ai_topic}", "url": f"https://www.sciencefriday.com/search/?s={ai_topic}"}
                            ]
                            online_courses = [
                                {"name": f"Coursera: {ai_subject} Courses on {ai_topic}", "url": f"https://www.coursera.org/search?query={ai_topic}%20{ai_subject}&index=prod_all_launched_products_term_optimization"},
                                {"name": f"edX: {ai_topic} in {ai_subject}", "url": f"https://www.edx.org/search?q={ai_topic}+{ai_subject}"},
                                {"name": f"FutureLearn: {ai_subject} Courses", "url": f"https://www.futurelearn.com/search?q={ai_topic}+{ai_subject}"}
                            ]
                            books_articles = [
                                {"name": f"OpenStax: Free {ai_subject} Textbooks", "url": f"https://openstax.org/subjects/{ai_subject.lower()}"},
                                {"name": f"Science Direct Articles on {ai_topic}", "url": f"https://www.sciencedirect.com/search?qs={ai_topic}"},
                                {"name": f"Nature: Research on {ai_topic}", "url": f"https://www.nature.com/search?q={ai_topic}&journal="}
                            ]
                            videos_podcasts = [
                                {"name": f"Crash Course {ai_subject}", "url": f"https://www.youtube.com/c/crashcourse/search?query={ai_topic}"},
                                {"name": f"TED-Ed Science Videos", "url": f"https://ed.ted.com/search?qs={ai_topic}"}
                            ]
                            next_topics = [
                                f"Designing more complex investigations of {ai_topic}",
                                f"Exploring current scientific research related to {ai_topic}",
                                f"Examining real-world applications and technologies based on {ai_topic}"
                            ]
                        elif ai_subject.lower() in ["english", "language arts", "literature"]:
                            resources = [
                                {"name": f"ReadWriteThink: {ai_topic} Resources", "url": f"http://www.readwritethink.org/search/?resource_type=6-8&q={ai_topic.replace(' ', '+')}"},
                                {"name": f"CommonLit: {ai_topic} Texts", "url": f"https://www.commonlit.org/en/texts?search_term={ai_topic.replace(' ', '+')}"},
                                {"name": f"Poetry Foundation: {ai_topic}", "url": f"https://www.poetryfoundation.org/search?query={ai_topic.replace(' ', '+')}"},
                                {"name": f"Purdue OWL: Writing about {ai_topic}", "url": "https://owl.purdue.edu/owl/general_writing/index.html"}
                            ]
                            online_courses = [
                                {"name": f"Coursera: {ai_topic} in Literature", "url": f"https://www.coursera.org/search?query={ai_topic}%20literature&index=prod_all_launched_products_term_optimization"},
                                {"name": f"edX: Courses on {ai_topic}", "url": f"https://www.edx.org/search?q={ai_topic}+literature"},
                                {"name": f"Udemy: {ai_topic} Analysis", "url": f"https://www.udemy.com/courses/search/?src=ukw&q={ai_topic}+literature"}
                            ]
                            books_articles = [
                                {"name": f"Project Gutenberg: Free Classic Texts", "url": f"https://www.gutenberg.org/ebooks/search/?query={ai_topic}"},
                                {"name": f"JSTOR Articles on {ai_topic}", "url": f"https://www.jstor.org/action/doBasicSearch?Query={ai_topic}+literature"},
                                {"name": f"Google Scholar: Research on {ai_topic}", "url": f"https://scholar.google.com/scholar?q={ai_topic}+literature"}
                            ]
                            videos_podcasts = [
                                {"name": f"Crash Course Literature", "url": f"https://www.youtube.com/playlist?list=PL8dPuuaLjXtOeEc9ME62zTfqc0h6Pe8vb"},
                                {"name": f"The Literary Life Podcast", "url": "https://www.literarylife.org/podcast"},
                                {"name": f"TED Talks on Literature", "url": f"https://www.ted.com/search?q={ai_topic}+literature"}
                            ]
                            next_topics = [
                                f"Comparative analysis of different works addressing {ai_topic}",
                                f"Creative writing projects inspired by {ai_topic}",
                                f"Multimedia exploration of {ai_topic} through film, art, or music"
                            ]
                        elif ai_subject.lower() in ["history", "social studies"]:
                            resources = [
                                {"name": f"Library of Congress: {ai_topic}", "url": f"https://www.loc.gov/search/?q={ai_topic.replace(' ', '+')}"},
                                {"name": f"National Archives: {ai_topic} Documents", "url": f"https://www.archives.gov/research/search?q={ai_topic.replace(' ', '+')}"},
                                {"name": f"Stanford History Education Group: {ai_topic}", "url": f"https://sheg.stanford.edu/search?search={ai_topic.replace(' ', '+')}"},
                                {"name": f"Facing History: {ai_topic}", "url": f"https://www.facinghistory.org/search?keys={ai_topic.replace(' ', '+')}&type=All"}
                            ]
                            online_courses = [
                                {"name": f"Coursera: {ai_topic} in History", "url": f"https://www.coursera.org/search?query={ai_topic}%20history&index=prod_all_launched_products_term_optimization"},
                                {"name": f"edX: Historical Analysis of {ai_topic}", "url": f"https://www.edx.org/search?q={ai_topic}+history"},
                                {"name": f"FutureLearn: {ai_topic} Courses", "url": f"https://www.futurelearn.com/search?q={ai_topic}+history"}
                            ]
                            books_articles = [
                                {"name": f"JSTOR Articles on {ai_topic}", "url": f"https://www.jstor.org/action/doBasicSearch?Query={ai_topic}+history"},
                                {"name": f"Google Books on {ai_topic}", "url": f"https://www.google.com/search?tbm=bks&q={ai_topic}+history"},
                                {"name": f"Internet History Sourcebooks", "url": "https://sourcebooks.fordham.edu/"}
                            ]
                            videos_podcasts = [
                                {"name": f"Crash Course History", "url": f"https://www.youtube.com/c/crashcourse/search?query={ai_topic}+history"},
                                {"name": f"Dan Carlin's Hardcore History", "url": "https://www.dancarlin.com/hardcore-history-series/"},
                                {"name": f"BBC History Podcasts", "url": "https://www.bbc.co.uk/sounds/category/factual-history"}
                            ]
                            next_topics = [
                                f"Examining different historical perspectives on {ai_topic}",
                                f"Investigating the long-term impacts and legacy of {ai_topic}",
                                f"Connecting {ai_topic} to current events and contemporary issues"
                            ]
                        else:
                            resources = [
                                {"name": f"TED-Ed: {ai_topic}", "url": f"https://ed.ted.com/search?qs={ai_topic.replace(' ', '+')}"},
                                {"name": f"PBS Learning Media: {ai_topic}", "url": f"https://www.pbslearningmedia.org/search/?q={ai_topic.replace(' ', '+')}"},
                                {"name": f"Smithsonian Education: {ai_topic}", "url": f"https://www.si.edu/search/education-resources?edan_q={ai_topic.replace(' ', '+')}"},
                                {"name": f"OER Commons: {ai_topic}", "url": f"https://www.oercommons.org/search?f.search={ai_topic.replace(' ', '+')}&f.general_subject=arts"}
                            ]
                            online_courses = [
                                {"name": f"Coursera: {ai_topic} Courses", "url": f"https://www.coursera.org/search?query={ai_topic}&index=prod_all_launched_products_term_optimization"},
                                {"name": f"edX: Learn about {ai_topic}", "url": f"https://www.edx.org/search?q={ai_topic}"},
                                {"name": f"Udemy: {ai_topic} Classes", "url": f"https://www.udemy.com/courses/search/?src=ukw&q={ai_topic}"}
                            ]
                            books_articles = [
                                {"name": f"Google Scholar: Research on {ai_topic}", "url": f"https://scholar.google.com/scholar?q={ai_topic}"},
                                {"name": f"Open Textbook Library", "url": "https://open.umn.edu/opentextbooks/"},
                                {"name": f"JSTOR Articles on {ai_topic}", "url": f"https://www.jstor.org/action/doBasicSearch?Query={ai_topic}"}
                            ]
                            videos_podcasts = [
                                {"name": f"YouTube Educational Videos on {ai_topic}", "url": f"https://www.youtube.com/results?search_query={ai_topic}+education"},
                                {"name": f"TED Talks on {ai_topic}", "url": f"https://www.ted.com/search?q={ai_topic}"},
                                {"name": f"Educational Podcasts on {ai_topic}", "url": f"https://player.fm/search/{ai_topic}"}
                            ]
                            next_topics = [
                                f"Deeper exploration of advanced concepts in {ai_topic}",
                                f"Interdisciplinary connections between {ai_topic} and other subjects",
                                f"Project-based learning activities centered on {ai_topic}"
                            ]
                        
                        # Display suggested next topics
                        st.write("**Suggested Next Topics:**")
                        for topic in next_topics:
                            st.write(f"- {topic}")
                        
                        # Display comprehensive resource sections
                        st.write("### Comprehensive Learning Resources")
                        
                        # Interactive Teaching Tools
                        st.write("**Interactive Teaching Tools:**")
                        for resource in resources:
                            st.markdown(f"- [{resource['name']}]({resource['url']}) - Interactive resources for teaching {ai_topic}")
                        
                        # Online Courses
                        st.write("**Online Courses:**")
                        for course in online_courses:
                            st.markdown(f"- [{course['name']}]({course['url']}) - Structured learning about {ai_topic}")
                        
                        # Books and Articles
                        st.write("**Books and Academic Articles:**")
                        for book in books_articles:
                            st.markdown(f"- [{book['name']}]({book['url']}) - In-depth reading materials")
                        
                        # Videos and Podcasts
                        st.write("**Videos and Podcasts:**")
                        for media in videos_podcasts:
                            st.markdown(f"- [{media['name']}]({media['url']}) - Multimedia learning resources")
                        
                        # Store the lesson plan data in session state for download
                        st.session_state.lesson_plan_data = f"""# {ai_topic} - {ai_grade} Lesson Plan

Subject: {ai_subject}
Duration: {ai_duration} minutes

## Learning Objectives
By the end of this lesson, students will be able to:
{chr(10).join(f"{i+1}. {obj}" for i, obj in enumerate(objectives))}

## Materials Needed
{chr(10).join(f"- {material}" for material in materials)}

## Lesson Structure

### Introduction (10 minutes)
{topic_intro}

### Main Activity (25 minutes)
{chr(10).join(f"- {activity}" for activity in activities)}

### Conclusion (10 minutes)
- Have students summarize the key points about {ai_topic} in their own words
- Address any questions or misconceptions that arose during the lesson
- Preview how {ai_topic} connects to upcoming content

## Assessment
{chr(10).join(f"- {assess}" for assess in assessment)}

## Next Steps and Resources

### Suggested Next Topics:
{chr(10).join(f"- {topic}" for topic in next_topics)}

### Interactive Teaching Tools:
{chr(10).join(f"- {resource['name']}: {resource['url']}" for resource in resources)}

### Online Courses:
{chr(10).join(f"- {course['name']}: {course['url']}" for course in online_courses)}

### Books and Academic Articles:
{chr(10).join(f"- {book['name']}: {book['url']}" for book in books_articles)}

### Videos and Podcasts:
{chr(10).join(f"- {media['name']}: {media['url']}" for media in videos_podcasts)}
"""
    
    with tools_tab2:
        st.subheader("Assessment Tools")
        
        # Assessment types
        assessment_type = st.selectbox(
            "Select Assessment Type",
            options=["Quizzes", "Rubrics", "Peer Assessment", "Self-Assessment"]
        )
        
        if assessment_type == "Quizzes":
            st.write("### Quiz Generator")
            
            with st.form("quiz_generator"):
                quiz_subject = st.text_input("Subject")
                quiz_topic = st.text_input("Topic")
                quiz_level = st.select_slider("Difficulty Level", options=["Easy", "Medium", "Hard"])
                quiz_questions = st.number_input("Number of Questions", min_value=5, max_value=30, value=10)
                
                # Question types
                question_types = st.multiselect(
                    "Question Types",
                    options=["Multiple Choice", "True/False", "Short Answer", "Fill in the Blank"],
                    default=["Multiple Choice", "True/False"]
                )
                
                # Generate button
                generate_quiz = st.form_submit_button("Generate Quiz")
                
                if generate_quiz:
                    if not quiz_subject or not quiz_topic:
                        st.error("Please fill in all required fields (marked with red asterisk).")
                    elif not question_types:
                        st.error("Please select at least one question type.")
                    else:
                        with st.spinner("Generating quiz..."):
                            # Simulate AI processing
                            import time
                            time.sleep(2)
                            
                            # Display generated quiz
                            st.success("Quiz generated successfully!")
                            
                            st.write(f"## {quiz_topic} Quiz")
                            st.write(f"**Subject:** {quiz_subject}")
                            st.write(f"**Difficulty:** {quiz_level}")
                            st.write(f"**Total Questions:** {quiz_questions}")
                            
                            # Sample questions
                            st.write("### Sample Questions")
                            
                            if "Multiple Choice" in question_types:
                                st.write("**Multiple Choice**")
                                st.write("1. What is the main concept of this topic?")
                                st.write("   a) Option A")
                                st.write("   b) Option B")
                                st.write("   c) Option C")
                                st.write("   d) Option D")
                            
                            if "True/False" in question_types:
                                st.write("**True/False**")
                                st.write("2. This statement about the topic is correct.")
                                st.write("   True / False")
                            
                            if "Short Answer" in question_types:
                                st.write("**Short Answer**")
                                st.write("3. Explain the relationship between concept A and concept B.")
                            
                            if "Fill in the Blank" in question_types:
                                st.write("**Fill in the Blank**")
                                st.write("4. The process of ________ is essential to understanding this topic.")
                            
                            # Download option
                            st.session_state.quiz_created = True
                            st.session_state.quiz_data = {
                                "topic": quiz_topic,
                                "subject": quiz_subject,
                                "level": quiz_level,
                                "num_questions": quiz_questions
                            }
            
            # Display download button outside the form
            if st.session_state.get("quiz_created", False):
                quiz_data = st.session_state.quiz_data
                st.download_button(
                    label="Download Quiz",
                    data=f"# {quiz_data['topic']} Quiz\n\nDifficulty: {quiz_data['level']}\nTotal Questions: {quiz_data['num_questions']}\n\n...",
                    file_name=f"{quiz_data['topic'].replace(' ', '_')}_quiz.txt",
                    mime="text/plain"
                )
        
        elif assessment_type == "Rubrics":
            st.write("### Rubric Creator")
            
            # Get rubric templates from teacher tools
            rubric_templates = teacher_tools.get_rubric_templates()
            
            if rubric_templates:
                st.write("Select a rubric template to customize:")
                
                selected_template = st.selectbox(
                    "Rubric Template",
                    options=[template.get('name') for template in rubric_templates],
                    format_func=lambda x: x
                )
                
                # Find the selected template
                template = next((t for t in rubric_templates if t.get('name') == selected_template), None)
                
                if template:
                    st.write(f"**Description:** {template.get('description', 'No description available.')}")
                    
                    # Display and edit criteria
                    st.write("### Customize Criteria")
                    
                    criteria = template.get('criteria', [])
                    updated_criteria = []
                    
                    for i, criterion in enumerate(criteria):
                        st.write(f"**Criterion {i+1}**")
                        criterion_name = st.text_input(f"Name", value=criterion.get('name', ''), key=f"criterion_name_{i}")
                        criterion_description = st.text_area(f"Description", value=criterion.get('description', ''), key=f"criterion_desc_{i}")
                        
                        # Levels
                        st.write("Performance Levels:")
                        levels = criterion.get('levels', [])
                        updated_levels = []
                        
                        for j, level in enumerate(levels):
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                level_name = st.text_input(f"Level Name", value=level.get('name', ''), key=f"level_name_{i}_{j}")
                            with col2:
                                level_description = st.text_input(f"Description", value=level.get('description', ''), key=f"level_desc_{i}_{j}")
                            
                            updated_levels.append({
                                'name': level_name,
                                'description': level_description,
                                'points': level.get('points', 0)
                            })
                        
                        updated_criteria.append({
                            'name': criterion_name,
                            'description': criterion_description,
                            'levels': updated_levels
                        })
                    
                    # Save button
                    if st.button("Save Rubric"):
                        st.success("Rubric saved successfully!")
                        
                        # Preview the rubric
                        st.write("### Rubric Preview")
                        
                        # Create a DataFrame for the rubric
                        rubric_data = []
                        for criterion in updated_criteria:
                            row = {'Criterion': criterion['name']}
                            for level in criterion['levels']:
                                row[level['name']] = level['description']
                            rubric_data.append(row)
                        
                        if rubric_data:
                            st.dataframe(pd.DataFrame(rubric_data))
                            
                            # Store the template name for the download button
                            st.session_state.rubric_template = selected_template
                            st.success("Rubric generated successfully!")
            
            # Download button for rubric - placed outside any form
            if st.session_state.get("rubric_template"):
                template_name = st.session_state.rubric_template
                st.download_button(
                    label="Download Rubric",
                    data=f"# {template_name} Rubric\n\n...",
                    file_name=f"{template_name.replace(' ', '_')}_rubric.txt",
                    mime="text/plain"
                )
        
        elif assessment_type == "Peer Assessment":
            st.write("### Peer Assessment Setup")
            
            with st.form("peer_assessment"):
                assessment_title = st.text_input("Assessment Title")
                assessment_description = st.text_area("Description")
                
                # Peer review questions
                st.write("### Review Questions")
                
                questions = []
                for i in range(5):
                    question = st.text_input(f"Question {i+1}", key=f"peer_q_{i}")
                    if question:
                        questions.append(question)
                
                # Settings
                st.write("### Settings")
                anonymous = st.checkbox("Anonymous Reviews", value=True)
                deadline = st.date_input("Deadline")
                
                # Submit button
                submit_assessment = st.form_submit_button("Create Peer Assessment")
                
                if submit_assessment:
                    if not assessment_title:
                        st.error("Please enter an assessment title.")
                    elif not questions:
                        st.error("Please add at least one review question.")
                    else:
                        st.success(f"Peer assessment '{assessment_title}' created successfully!")
        
        elif assessment_type == "Self-Assessment":
            st.write("### Self-Assessment Creator")
            
            with st.form("self_assessment"):
                assessment_title = st.text_input("Assessment Title")
                assessment_description = st.text_area("Description")
                
                # Self-assessment questions
                st.write("### Assessment Questions")
                
                questions = []
                for i in range(5):
                    question = st.text_input(f"Question {i+1}", key=f"self_q_{i}")
                    if question:
                        questions.append(question)
                
                # Rating scale
                st.write("### Rating Scale")
                scale_type = st.selectbox("Scale Type", ["1-5 Likert Scale", "1-10 Scale", "Custom Scale"])
                
                if scale_type == "Custom Scale":
                    scale_options = st.text_input("Enter scale options separated by commas (e.g., Poor, Fair, Good, Excellent)")
                
                # Submit button
                submit_assessment = st.form_submit_button("Create Self-Assessment")
                
                if submit_assessment:
                    if not assessment_title:
                        st.error("Please enter an assessment title.")
                    elif not questions:
                        st.error("Please add at least one assessment question.")
                    else:
                        st.success(f"Self-assessment '{assessment_title}' created successfully!")
    
    with tools_tab3:
        st.subheader("Resource Library")
        
        # Get resources from teacher tools
        resources = teacher_tools.get_teaching_resources()
        
        if resources:
            # Resource categories
            resource_categories = {}
            for resource in resources:
                category = resource.get('category', 'Other')
                if category not in resource_categories:
                    resource_categories[category] = []
                resource_categories[category].append(resource)
            
            # Display resources by category
            for category, category_resources in resource_categories.items():
                st.write(f"### {category}")
                
                for resource in category_resources:
                    with st.expander(resource.get('title', 'Unknown Resource')):
                        st.write(f"**Description:** {resource.get('description', 'No description available.')}")
                        
                        # Display resource details
                        st.write(f"**Type:** {resource.get('type', 'N/A')}")
                        st.write(f"**Subject:** {resource.get('subject', 'N/A')}")
                        st.write(f"**Grade Level:** {resource.get('grade_level', 'All levels')}")
                        
                        # Display link if available
                        if resource.get('url'):
                            st.markdown(f"**[Access Resource]({resource.get('url')})**")
                        
                        # Display tags
                        if resource.get('tags'):
                            st.write("**Tags:**")
                            tags_html = " ".join([f'<span style="background-color: #2a4c7d; color: white; padding: 4px 8px; border-radius: 10px; margin-right: 5px; display: inline-block; margin-bottom: 5px;">{tag}</span>' for tag in resource.get('tags')])
                            st.markdown(f'<div style="margin-top: 5px;">{tags_html}</div>', unsafe_allow_html=True)
            
            # Search resources
            st.write("### Search Resources")
            search_query = st.text_input("Search for resources by keyword")
            
            if search_query:
                # Filter resources by search query
                search_results = []
                for resource in resources:
                    # Search in title, description, and tags
                    title = resource.get('title', '').lower()
                    description = resource.get('description', '').lower()
                    tags = ' '.join(resource.get('tags', [])).lower()
                    
                    if search_query.lower() in title or search_query.lower() in description or search_query.lower() in tags:
                        search_results.append(resource)
                
                if search_results:
                    st.write(f"Found {len(search_results)} resources matching '{search_query}'")
                    for resource in search_results:
                        st.markdown(f"**[{resource.get('title')}]({resource.get('url')})**")
                        st.write(resource.get('description', 'No description available.'))
                        st.markdown("---")
                else:
                    st.info("No resources found matching your search query.")
        else:
            st.info("No teaching resources available.")
        
        # Upload resource
        st.write("### Share Your Resources")
        
        with st.form("resource_upload"):
            resource_title = st.text_input("Resource Title")
            resource_description = st.text_area("Description")
            resource_type = st.selectbox("Resource Type", ["Lesson Plan", "Worksheet", "Presentation", "Activity", "Assessment", "Other"])
            resource_subject = st.text_input("Subject")
            resource_grade = st.multiselect("Grade Level", ["Elementary", "Middle School", "High School", "College"])
            resource_url = st.text_input("Resource URL (optional)")
            resource_file = st.file_uploader("Upload File (optional)")
            
            # Tags
            resource_tags = st.text_input("Tags (comma-separated)")
            
            # Submit button
            submit_resource = st.form_submit_button("Share Resource")
            
            if submit_resource:
                if not resource_title or not resource_description or not resource_subject:
                    st.error("Please fill in all required fields.")
                else:
                    st.success(f"Resource '{resource_title}' shared successfully!")
    
    with tools_tab4:
        st.subheader("Professional Development")
        
        # Get professional development resources from teacher tools
        pd_resources = teacher_tools.get_professional_development()
        
        if pd_resources:
            # PD categories
            pd_categories = {}
            for resource in pd_resources:
                category = resource.get('category', 'Other')
                if category not in pd_categories:
                    pd_categories[category] = []
                pd_categories[category].append(resource)
            
            # Display PD resources by category
            for category, category_resources in pd_categories.items():
                st.write(f"### {category}")
                
                for resource in category_resources:
                    with st.expander(resource.get('title', 'Unknown Resource')):
                        st.write(f"**Description:** {resource.get('description', 'No description available.')}")
                        
                        # Display resource details
                        st.write(f"**Type:** {resource.get('type', 'N/A')}")
                        st.write(f"**Duration:** {resource.get('duration', 'N/A')}")
                        
                        # Display link if available
                        if resource.get('url'):
                            st.markdown(f"**[Access Resource]({resource.get('url')})**")
                        
                        # Display provider
                        if resource.get('provider'):
                            st.write(f"**Provider:** {resource.get('provider')}")
                        
                        # Display certification
                        if resource.get('certification'):
                            st.write(f"**Certification:** {resource.get('certification')}")
        else:
            st.info("No professional development resources available.")
        
        # Professional Learning Communities
        st.write("### Professional Learning Communities")
        
        plc_options = [
            "Technology Integration", 
            "Project-Based Learning", 
            "Differentiated Instruction",
            "Assessment Strategies",
            "Classroom Management"
        ]
        
        selected_plc = st.selectbox("Join a Professional Learning Community", plc_options)
        
        if selected_plc:
            st.write(f"**{selected_plc} Community**")
            st.write("Connect with other educators interested in this topic.")
            
            # Simulated community features
            st.write("### Recent Discussions")
            st.write("- Best practices for implementing this approach")
            st.write("- Resources and tools that have worked well")
            st.write("- Challenges and solutions from experienced educators")
            
            # Join button
            if st.button("Join This Community"):
                st.success(f"You have joined the {selected_plc} community!")
                
                # Show community features
                st.write("### Community Features")
                st.write("- Monthly virtual meetings")
                st.write("- Resource sharing platform")
                st.write("- Mentorship opportunities")
                st.write("- Collaborative projects")

def show_student_dashboard():
    # Welcome message with modern styling
    st.markdown(f'''
    <div class="card">
        <h2><i class="fas fa-user-graduate"></i> {get_translation("welcome")}, {st.session_state.current_user['name']}!</h2>
        <p style="color: #4b5563; font-size: 1.1rem;">{get_translation("student_dashboard_desc")}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Get student's courses
    courses = get_student_courses(st.session_state.current_user['id'])
    
    # Dashboard tabs
    tab1, tab2, tab3 = st.tabs(["Overview", "My Courses", "Join Course"])
    
    with tab1:
        # Display stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Enrolled Courses", len(courses))
        
        with col2:
            # Count assignments
            assignment_count = 0
            for course in courses:
                assignments = get_course_assignments(course['id'])
                assignment_count += len(assignments)
            st.metric("Assignments", assignment_count)
        
        with col3:
            # Count submissions
            submissions = get_student_submissions(st.session_state.current_user['id'])
            st.metric("Submissions", len(submissions))
    
    with tab2:
        # Display enrolled courses
        st.subheader("My Courses")
        
        if not courses:
            st.info("You are not enrolled in any courses yet. Join a course by entering a course code in the 'Join Course' tab.")
        else:
            # Display courses in a grid layout with two columns
            cols = st.columns(2)
            for i, course in enumerate(courses):
                col_idx = i % 2
                with cols[col_idx]:
                    # Create a visually distinct course card with better contrast
                    st.markdown(f"""
                    <div style="border:1px solid #555; border-radius:8px; padding:15px; margin-bottom:15px; background-color:#1e2130;">
                        <h3 style="color:#ffffff; margin-top:0;">{course['name']}</h3>
                        <div style="background-color:#4169E1; color:white; padding:8px; 
                            border-radius:5px; margin:10px 0; text-align:center; font-weight:bold;">
                            Course Code: {course.get('code', 'No code')}
                        </div>
                        <p style="color:#dddddd; margin:10px 0;">{course.get('description', 'No description available.')[:100] + 
                             ("..." if len(course.get('description', '')) > 100 else '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("View Course", key=f"view_course_{course['id']}"):
                        st.session_state.current_course = course
                        st.session_state.current_page = 'course_detail'
                        st.rerun()
    
    with tab3:
        # Join course by code only
        st.subheader("Join a Course")
        
        # Create a styled container for the join course form with instructions
        st.markdown("""
        <div style="padding:10px; border-radius:5px; background-color:#1f2937; margin-bottom:15px; border:1px solid #4e5d78;">
            <p style="color:#e2e8f0; font-size:16px; margin:0;">Enter the course code provided by your teacher to join a course.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a form with a more visible course code input
        with st.form("join_course_form"):
            st.markdown("<p style='color:#ffffff; font-weight:bold; font-size:18px;'>Course Code:</p>", unsafe_allow_html=True)
            
            # Add a more visible text input
            course_code = st.text_input("", 
                                      placeholder="Enter 6-character course code",
                                      key="course_code_input")
            
            # Make the join button more visible
            submit = st.form_submit_button("Join Course")
            
            if submit:
                if not course_code:
                    st.error("Please enter a course code")
                else:
                    # Standardize code format before checking
                    formatted_code = course_code.strip().upper()
                    success, message = join_course_by_code(formatted_code, st.session_state.current_user['id'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

def show_course_detail():
    course = st.session_state.current_course
    st.title(course['name'])
    
    # Display course code prominently
    code = course.get('code', 'No code assigned')
    st.markdown(f'''
    <div style="background-color:rgba(255, 255, 255, 0.9); padding:15px; border-radius:10px; 
         margin-bottom:20px; text-align:center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <h3 style="margin:0; color:#111827; font-weight:600;">Course Code: {code}</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    # Course info
    st.write(course['description'])
    teacher = get_user_by_id(course['teacher_id'])
    st.write(f"**Teacher:** {teacher['name']}")
    st.write(f"**Period:** {course.get('start_date', 'Not specified')} to {course.get('end_date', 'Not specified')}")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Assignments", "Quizzes", "Students", "Announcements"])
    
    with tab1:
        show_course_assignments(course)
    
    with tab2:
        show_course_quizzes(course)
    
    with tab3:
        show_course_students(course, load_data_func=load_data, enroll_student_func=enroll_student)
    
    with tab4:
        show_course_announcements(course, load_data_func=load_data, save_data_func=save_data)
    
    # Back button
    if st.button("Back to Dashboard", key="back_to_dashboard_btn"):
        st.session_state.current_page = 'dashboard'
        st.rerun()

def show_course_assignments(course):
    """Display assignments for a specific course"""
    st.subheader("Assignments")
    
    # Create new assignment (teacher only)
    if st.session_state.current_user['role'] == 'teacher' and st.session_state.current_user['id'] == course['teacher_id']:
        with st.expander("Create New Assignment"):
            with st.form("new_assignment_form"):
                title = st.text_input("Assignment Title")
                description = st.text_area("Description")
                
                col1, col2 = st.columns(2)
                with col1:
                    due_date = st.date_input("Due Date")
                with col2:
                    points = st.number_input("Points", min_value=1, value=10)
                
                submit = st.form_submit_button("Create Assignment")
                
                if submit:
                    if not title:
                        st.error("Please provide a title for the assignment")
                    else:
                        success, message = create_assignment(
                            title=title,
                            description=description,
                            course_id=course['id'],
                            teacher_id=st.session_state.current_user['id'],
                            due_date=due_date.isoformat(),
                            points=points
                        )
                        if success:
                            st.success("Assignment created successfully!")
                            st.rerun()
                        else:
                            st.error(message)
    
    # Get assignments for this course
    assignments = get_course_assignments(course['id'])
    
    if not assignments:
        st.info("No assignments available for this course yet.")
    else:
        for assignment in assignments:
            with st.expander(f"{assignment['title']} - Due: {assignment.get('due_date', 'No due date')}"):
                st.write(assignment.get('description', 'No description provided.'))
                st.write(f"**Points:** {assignment.get('points', 0)}")
                
                # Show different options based on user role
                if st.session_state.current_user['role'] == 'teacher':
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View Submissions", key=f"view_submissions_{assignment['id']}"):
                            st.session_state.current_assignment = assignment
                            st.session_state.current_page = 'assignment_submissions'
                            st.rerun()
                    with col2:
                        if st.button("Delete Assignment", key=f"delete_assignment_{assignment['id']}"):
                            success, message = delete_assignment(assignment['id'], st.session_state.current_user['id'])
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                else:
                    # Check if student has already submitted
                    submissions = get_assignment_submissions(assignment['id'])
                    student_submission = None
                    
                    for submission in submissions:
                        if submission['student_id'] == st.session_state.current_user['id']:
                            student_submission = submission
                            break
                    
                    if student_submission:
                        st.write("**Your submission:**")
                        st.write(student_submission.get('content', 'No content provided'))
                        
                        if student_submission.get('grade'):
                            st.write(f"**Grade:** {student_submission['grade']}/{assignment['points']}")
                            if student_submission.get('feedback'):
                                st.write(f"**Feedback:** {student_submission['feedback']}")
                    else:
                        with st.form(key=f"submit_assignment_{assignment['id']}"):
                            submission_content = st.text_area("Your submission")
                            submit_button = st.form_submit_button("Submit Assignment")
                            
                            if submit_button:
                                if not submission_content:
                                    st.error("Please provide content for your submission")
                                else:
                                    success, message = submit_assignment(
                                        assignment_id=assignment['id'],
                                        student_id=st.session_state.current_user['id'],
                                        content=submission_content
                                    )
                                    if success:
                                        st.success("Assignment submitted successfully!")
                                        st.rerun()
                                    else:
                                        st.error(message)

def show_course_quizzes(course):
    st.subheader("Quizzes")
    
    # Create new quiz (teacher only)
    if st.session_state.current_user['role'] == 'teacher' and st.session_state.current_user['id'] == course['teacher_id']:
        if st.button("Create New Quiz"):
            # Store the current course ID for quiz creation
            st.session_state.create_quiz_for_course = course['id']
            st.session_state.current_page = 'quiz_management'
            st.rerun()
    
    # Get quizzes for this course
    course_quizzes = quiz_manager.get_quizzes_by_course(course['id'])
    
    if not course_quizzes:
        st.info("No quizzes available for this course.")
    else:
        for quiz in course_quizzes:
            with st.expander(f"{quiz['title']} - {quiz['difficulty']}"):
                st.write(f"**Description:** {quiz['description']}")
                st.write(f"**Time Limit:** {quiz['time_limit_minutes']} minutes")
                st.write(f"**Questions:** {len(quiz['questions'])}")
                st.write(f"**Passing Score:** {quiz['passing_score']}%")
                
                # Different actions based on role
                if st.session_state.current_user['role'] == 'teacher':
                    col1, col2 = st.columns(2)
                    with col1:
                        # View quiz statistics
                        if st.button("View Results", key=f"view_quiz_results_{quiz['id']}"):
                            st.session_state.selected_quiz_stats = quiz['id']
                            st.session_state.current_page = 'quiz_management'
                            st.rerun()
                    with col2:
                        # Edit quiz
                        if st.button("Edit Quiz", key=f"edit_quiz_{quiz['id']}"):
                            st.session_state.edit_quiz_id = quiz['id']
                            st.session_state.current_page = 'quiz_management'
                            st.rerun()
                else:
                    # Student view - take quiz
                    student_id = st.session_state.current_user['id']
                    attempts = quiz_manager.get_student_quiz_attempts(student_id)
                    quiz_attempts = [a for a in attempts if a['quiz_id'] == quiz['id']]
                    
                    if quiz_attempts:
                        best_score = max([a['score'] for a in quiz_attempts])
                        st.write(f"Your best score: {best_score:.1f}%")
                        
                        # Take quiz again
                        if st.button("Take Quiz Again", key=f"retake_quiz_{quiz['id']}"):
                            st.session_state.selected_quiz = quiz['id']
                            st.session_state.current_page = 'take_quiz'
                            st.rerun()
                    else:
                        # Take quiz for the first time
                        if st.button("Take Quiz", key=f"take_quiz_{quiz['id']}"):
                            st.session_state.selected_quiz = quiz['id']
                            st.session_state.current_page = 'take_quiz'
                            st.rerun()

def show_assignment_submissions():
    assignment = st.session_state.current_assignment
    st.title(f"Submissions for {assignment['title']}")
    
    # Get course and submissions
    course = get_course_by_id(assignment['course_id'])
    submissions = get_assignment_submissions(assignment['id'])
    
    st.write(f"**Course:** {course['name']} ({course['code']})")
    st.write(f"**Due Date:** {assignment['due_date']}")
    st.write(f"**Total Submissions:** {len(submissions)}")
    
    # Add model selection with descriptions
    with st.expander("AI Grading Settings"):
        st.write("Select Gemini Models for Evaluation:")
        selected_models = {}
        for model, description in GEMINI_MODELS.items():
            col1, col2 = st.columns([1, 3])
            with col1:
                selected = st.checkbox(model, key=f"model_{model}")
            with col2:
                st.caption(description)
            if selected:
                selected_models[model] = description
        
        if not selected_models:
            st.warning("Please select at least one model for evaluation")
    
    # Display submissions
    if not submissions:
        st.info("No submissions yet.")
    else:
        for submission in submissions:
            student = get_user_by_id(submission['student_id'])
            with st.expander(f"Submission by {student['name']} - {submission['submitted_at'].split('T')[0]}"):
                # Display text content
                st.write("**Content:**")
                st.text_area("", submission['content'], height=200, key=f"content_{submission['id']}", disabled=True)
                
                # Display file if available
                if submission.get('file_info'):
                    st.write("**Attached File:**")
                    file_info = submission['file_info']
                    st.markdown(get_file_download_link(file_info['file_path'], file_info['filename']), unsafe_allow_html=True)
                    st.write(f"File type: {file_info['file_type']}, Size: {file_info['file_size']/1024:.1f} KB")
                
                # Display AI feedback if available
                if submission.get('ai_feedback'):
                    st.write("**AI-Generated Feedback:**")
                    st.markdown(submission['ai_feedback'])
                
                # AI Auto-grading button
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("Auto-Grade", key=f"auto_grade_{submission['id']}"):
                        success, message = auto_grade_submission(submission['id'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                # Manual Grading form
                with st.form(f"grade_submission_{submission['id']}"):
                    st.write("**Manual Grading:**")
                    score = st.number_input("Score", min_value=0, max_value=assignment['points'], value=submission.get('score', 0) or 0)
                    feedback = st.text_area("Feedback", value=submission.get('feedback', ''))
                    use_ai_grading = st.checkbox("Include AI Feedback")
                    submit_grade = st.form_submit_button("Submit Grade")
                    
                    if submit_grade:
                        success, message = grade_submission(
                            submission['id'],
                            score,
                            feedback,
                            use_ai_grading
                        )
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        
                # Add model-based grading option
                if selected_models:
                    if st.button("Evaluate with Selected Models", key=f"model_grade_{submission['id']}"):
                        model_results = {}
                        progress_bar = st.progress(0)
                        for i, (model, _) in enumerate(selected_models.items()):
                            result = analyze_with_gemini(
                                'text',
                                None,
                                submission['content'],
                                'text/plain',
                                model=model
                            )
                            model_results[model] = result
                            progress_bar.progress((i + 1) / len(selected_models))
                        
                        # Store results and update submission
                        submission['model_evaluations'] = model_results
                        st.success("Evaluation complete!")
                        st.rerun()
                
                # Display model evaluations if available
                if submission.get('model_evaluations'):
                    st.write("### Model Evaluations")
                    for model, result in submission.get('model_evaluations').items():
                        with st.expander(f"Results from {model}"):
                            st.write(result)
                
                # Display AI suggestions if available
                if submission.get('ai_suggestions'):
                    show_ai_suggestions(submission['ai_suggestions'])
    
    # Back button
    if st.button("Back to Course", key="back_to_course_btn"):
        st.session_state.current_page = 'course_detail'
        st.rerun()

def show_ai_suggestions(suggestions):
    """Display AI-generated suggestions"""
    st.write("### AI Analysis and Suggestions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Content Analysis:**")
        st.write(f"- Word count: {suggestions['content_analysis']['length']}")
        st.write(f"- Sentences: {suggestions['content_analysis']['sentence_count']}")
        st.write("- Key terms: " + ", ".join(suggestions['content_analysis']['key_terms']))
    
    with col2:
        st.write("**Sentiment Analysis:**")
        sentiment = suggestions['content_analysis']['sentiment']
        st.write(f"- Positive: {sentiment['pos']:.2f}")
        st.write(f"- Negative: {sentiment['neg']:.2f}")
        st.write(f"- Neutral: {sentiment['neu']:.2f}")
    
    st.write("**Strengths:**")
    for strength in suggestions['strengths']:
        st.write(f"✅ {strength}")
    
    st.write("**Areas for Improvement:**")
    for area in suggestions['improvement_areas']:
        st.write(f"📝 {area}")

def show_home_page():
    st.title("EduMate - AI-Powered Education Platform")
    
    # Hero section
    st.markdown("<h1 style='text-align: center;'>Welcome to EduMate</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>AI-Powered Education Platform</h3>", unsafe_allow_html=True)
    
    # Image
    st.image("https://img.freepik.com/free-vector/online-learning-isometric-concept_1284-17947.jpg")
    
    # Features section
    st.markdown("---")
    st.subheader("Key Features")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🤖 AI-Powered Grading")
        st.write("Save hours of time with automated grading for essays, code assignments, and quizzes.")
    
    with col2:
        st.markdown("### 📊 Insightful Analytics")
        st.write("Track student progress and identify learning gaps with comprehensive analytics.")
    
    with col3:
        st.markdown("### 📝 Personalized Feedback")
        st.write("Students receive detailed, personalized feedback to improve their learning.")
    
    # How it works
    st.markdown("---")
    st.subheader("How It Works")
    
    tab1, tab2, tab3 = st.tabs(["For Teachers", "For Students", "For Institutions"])
    
    with tab1:
        st.markdown("""
        1. **Create Classes and Assignments** - Easily set up your courses and create various types of assignments
        2. **AI Grades Submissions** - Our AI technology automatically grades submissions based on your criteria
        3. **Review and Provide Feedback** - Review AI-generated grades and add your own feedback
        4. **Track Progress** - Monitor student performance and identify areas for improvement
        """)
    
    with tab2:
        st.markdown("""
        1. **Join Classes** - Enroll in courses using course codes provided by your teachers
        2. **Complete Assignments** - Submit your work directly through the platform
        3. **Receive Feedback** - Get detailed feedback to understand your strengths and weaknesses
        4. **Track Your Progress** - Monitor your performance across all your courses
        """)
    
    with tab3:
        st.markdown("""
        1. **Streamline Administration** - Simplify course management and grading processes
        2. **Improve Learning Outcomes** - Enhance student performance with personalized feedback
        3. **Save Teacher Time** - Reduce grading workload by up to 70%
        4. **Data-Driven Insights** - Make informed decisions based on comprehensive analytics
        """)

# Create demo data if no users exist
users = load_data('users')
if not users:
    # Create demo teacher
    register_user('teacher@edumate.com', 'teacher123', 'Demo Teacher', 'teacher')
    
    # Create demo student
    register_user('student@edumate.com', 'student123', 'Demo Student', 'student')
    
    # Create demo course
    create_course(
        'Introduction to Computer Science',
        'CS101',
        'An introductory course covering the basics of computer science and programming.',
        1,  # Teacher ID
        (datetime.now() - timedelta(days=30)).isoformat(),
        (datetime.now() + timedelta(days=60)).isoformat()
    )
    
    # Enroll demo student
    enroll_student(1, 2)  # Course ID 1, Student ID 2
    
    # Create demo assignment
    create_assignment(
        'Python Basics',
        'Write a Python program that calculates the factorial of a number.',
        1,  # Course ID
        1,  # Teacher ID
        (datetime.now() + timedelta(days=7)).isoformat()
    )

# Main app logic
def main():
    # Ensure all courses have unique codes
    ensure_all_courses_have_codes()
    
    # Initialize session state variables if they don't exist
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'  # Default to login page
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    if 'login_function' not in st.session_state:
        st.session_state.login_function = login_user
    
    # Show sidebar navigation, but hide it on login and registration pages
    if st.session_state.current_page in ['login', 'register']:
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/graduation-cap.png", width=50)
        st.title("EduMate")
        
        st.divider()
        
        if st.session_state.logged_in:
            st.write(f"Logged in as: {st.session_state.current_user['name']}")
            st.write(f"Role: {st.session_state.current_user['role'].capitalize()}")
            
            st.markdown("---")
            
            # Navigation
            st.button("Dashboard", key="sidebar_dashboard_btn", on_click=set_page, args=('dashboard',), use_container_width=True)
            
            # Logout button
            if st.button("Logout", key="sidebar_logout_btn", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.session_state.current_page = 'home'
                st.rerun()
        else:
            st.button("Home", key="sidebar_home_btn", on_click=set_page, args=('home',), use_container_width=True)
            st.button("Login", key="sidebar_login_btn", on_click=set_page, args=('login',), use_container_width=True)
            st.button("Register", key="sidebar_register_btn", on_click=set_page, args=('register',), use_container_width=True)
    
    # Main content
    if st.session_state.current_page == 'home':
        show_home_page()
    elif st.session_state.current_page == 'login':
        from edumate.components.login_page import show_enhanced_login_page
        show_enhanced_login_page()
        
        # Remove the duplicate register button - the enhanced login page already has one
        # st.markdown("---")
        # st.write("Don't have an account?")
        # if st.button("Register Now", key="direct_register_btn"):
        #     st.session_state.current_page = 'register'
        #     st.rerun()
    elif st.session_state.current_page == 'register':
        show_register_page()
    elif st.session_state.current_page == 'dashboard':
        if st.session_state.logged_in:
            show_dashboard()
        else:
            st.session_state.current_page = 'login'
            st.rerun()
    elif st.session_state.current_page == 'course_detail':
        if st.session_state.logged_in and hasattr(st.session_state, 'current_course'):
            show_course_detail()
        else:
            st.session_state.current_page = 'dashboard'
            st.rerun()
    elif st.session_state.current_page == 'assignment_submissions':
        if st.session_state.logged_in and hasattr(st.session_state, 'current_assignment'):
            show_assignment_submissions()
        else:
            st.session_state.current_page = 'dashboard'
            st.rerun()
    elif st.session_state.current_page == 'quizzes':
        if st.session_state.logged_in:
            from edumate.pages.quiz_page import show_quizzes
            show_quizzes(quiz_manager)
        else:
            st.session_state.current_page = 'login'
            st.rerun()
    elif st.session_state.current_page == 'take_quiz':
        if st.session_state.logged_in:
            from edumate.pages.quiz_page import show_take_quiz
            show_take_quiz(quiz_manager)
        else:
            st.session_state.current_page = 'login'
            st.rerun()
    elif st.session_state.current_page == 'quiz_results':
        if st.session_state.logged_in:
            from edumate.pages.quiz_page import show_quiz_results
            show_quiz_results(quiz_manager)
        else:
            st.session_state.current_page = 'login'
            st.rerun()
    elif st.session_state.current_page == 'quiz_management':
        if st.session_state.logged_in and st.session_state.current_user['role'] == 'teacher':
            from edumate.pages.quiz_page import show_quiz_management
            show_quiz_management(quiz_manager)
        else:
            st.session_state.current_page = 'login'
            st.rerun()
    # AI-powered career course search page
    elif st.session_state.current_page == 'career_courses':
        if st.session_state.logged_in and st.session_state.current_user['role'] == 'student':
            show_career_courses()
        else:
            st.session_state.current_page = 'login'
            st.rerun()

def show_exam_information():
    """Display exam information and preparation resources."""
    st.header("Exam Information")
    
    # Get available exams from exam manager
    exams = exam_manager.get_available_exams()
    
    if not exams:
        st.info("No exam information available at this time.")
        return
    
    # Create exam categories
    exam_categories = {}
    for exam in exams:
        category = exam.get('category', 'Other')
        if category not in exam_categories:
            exam_categories[category] = []
        exam_categories[category].append(exam)
    
    # Display exams by category
    for category, category_exams in exam_categories.items():
        st.subheader(category)
        
        for exam in category_exams:
            with st.expander(exam.get('name', 'Unknown Exam')):
                st.write(f"**Full Name:** {exam.get('full_name', 'N/A')}")
                st.write(f"**Description:** {exam.get('description', 'No description available.')}")
                
                # Display dates if available
                if exam.get('dates'):
                    st.write("**Important Dates:**")
                    for date_item in exam.get('dates', []):
                        st.write(f"- {date_item.get('event')}: {date_item.get('date')}")
                
                # Display eligibility criteria
                if exam.get('eligibility'):
                    st.write("**Eligibility Criteria:**")
                    for criteria in exam.get('eligibility', []):
                        st.write(f"- {criteria}")
                
                # Display exam pattern
                if exam.get('pattern'):
                    st.write("**Exam Pattern:**")
                    for section in exam.get('pattern', []):
                        st.write(f"- {section}")
                
                # Display preparation resources
                if exam.get('resources'):
                    st.write("**Preparation Resources:**")
                    for resource in exam.get('resources', []):
                        if resource.get('url'):
                            st.markdown(f"- [{resource.get('name')}]({resource.get('url')})")
                        else:
                            st.write(f"- {resource.get('name')}")
                
                # Display official website
                if exam.get('website'):
                    st.write(f"**Official Website:** [{exam.get('website')}]({exam.get('website')})")
                
                # Exam preparation button
                if st.button("Prepare for this Exam", key=f"prepare_{exam.get('id', '0')}"):
                    st.session_state.selected_exam = exam.get('id')
                    st.rerun()

def show_indian_education_options():
    """Display information about the Indian education system."""
    st.header("Indian Education System")
    
    # Get education system information from the utility
    education_paths = indian_education.get_education_paths()
    
    if not education_paths:
        st.info("Education system information is not available at this time.")
        return
    
    # Create tabs for different education levels
    education_levels = ["School Education", "Higher Education", "Professional Courses", "Entrance Exams"]
    tabs = st.tabs(education_levels)
    
    # School Education tab
    with tabs[0]:
        st.subheader("School Education in India")
        
        # Display school education structure
        school_structure = education_paths.get('school_education', {})
        
        if school_structure:
            for level, details in school_structure.items():
                with st.expander(level):
                    st.write(details.get('description', 'No description available'))
                    
                    if details.get('age_range'):
                        st.write(f"**Age Range:** {details.get('age_range')}")
                    
                    if details.get('curriculum_options'):
                        st.write("**Curriculum Options:**")
                        for curriculum in details.get('curriculum_options', []):
                            st.write(f"- {curriculum}")
    
    # Higher Education tab
    with tabs[1]:
        st.subheader("Higher Education in India")
        
        # Display higher education options
        higher_education = education_paths.get('higher_education', {})
        
        if higher_education:
            for degree_type, details in higher_education.items():
                with st.expander(degree_type):
                    st.write(details.get('description', 'No description available'))
                    
                    if details.get('duration'):
                        st.write(f"**Duration:** {details.get('duration')}")
                    
                    if details.get('fields'):
                        st.write("**Popular Fields:**")
                        for field in details.get('fields', []):
                            st.write(f"- {field}")
    
    # Professional Courses tab
    with tabs[2]:
        st.subheader("Professional Courses")
        
        # Display professional course options
        professional_courses = education_paths.get('professional_courses', [])
        
        if professional_courses:
            for course in professional_courses:
                with st.expander(course.get('name', 'Unknown Course')):
                    st.write(course.get('description', 'No description available'))
                    
                    if course.get('duration'):
                        st.write(f"**Duration:** {course.get('duration')}")
                    
                    if course.get('eligibility'):
                        st.write(f"**Eligibility:** {course.get('eligibility')}")
                    
                    if course.get('career_prospects'):
                        st.write("**Career Prospects:**")
                        for prospect in course.get('career_prospects', []):
                            st.write(f"- {prospect}")
    
    # Entrance Exams tab
    with tabs[3]:
        st.subheader("Important Entrance Exams")
        
        # Display entrance exam information
        entrance_exams = education_paths.get('entrance_exams', [])
        
        if entrance_exams:
            # Create a DataFrame for better display
            exam_data = []
            
            for exam in entrance_exams:
                # Make sure exam is a dictionary before using .get()
                if isinstance(exam, dict):
                    exam_data.append({
                        "Exam": exam.get('name', 'Unknown'),
                        "Type": exam.get('type', 'N/A'),
                        "Level": exam.get('level', 'N/A'),
                        "Frequency": exam.get('frequency', 'N/A')
                    })
                else:
                    # If exam is a string, create a simple entry
                    exam_data.append({
                        "Exam": exam,
                        "Type": "N/A",
                        "Level": "N/A",
                        "Frequency": "N/A"
                    })
            
            # Display as a table
            if exam_data:
                st.dataframe(pd.DataFrame(exam_data))
            
            # Detailed exam information
            for exam in entrance_exams:
                if isinstance(exam, dict):
                    with st.expander(exam.get('name', 'Unknown Exam')):
                        st.write(exam.get('description', 'No description available'))
                        
                        if exam.get('eligibility'):
                            st.write(f"**Eligibility:** {exam.get('eligibility')}")
                        
                        if exam.get('pattern'):
                            st.write(f"**Exam Pattern:** {exam.get('pattern')}")
                        
                        if exam.get('preparation_tips'):
                            st.write("**Preparation Tips:**")
                            for tip in exam.get('preparation_tips', []):
                                st.write(f"- {tip}")
                        
                        if exam.get('website'):
                            st.markdown(f"**[Official Website]({exam.get('website')})**")

# Add the new function for test creation
def show_test_creator():
    """Display the test creation interface for teachers."""
    st.header("Create Test")
    
    # Get teacher's courses for selection
    teacher_id = st.session_state.current_user['id']
    courses = get_teacher_courses(teacher_id)
    
    if not courses:
        st.info("You need to create a course first before creating tests.")
        return
    
    # Course selection
    selected_course = st.selectbox(
        "Select Course",
        options=courses,
        format_func=lambda x: f"{x['name']} ({x['code']})",
        key="test_creator_course_select"  # Add unique key here
    )
    
    # Test creation form
    with st.form("create_test_form"):
        test_title = st.text_input("Test Title")
        test_description = st.text_area("Test Description")
        
        # Test settings
        col1, col2, col3 = st.columns(3)
        with col1:
            total_points = st.number_input("Total Points", min_value=10, max_value=500, value=100, step=10)
        with col2:
            due_date = st.date_input("Due Date")
        with col3:
            time_limit = st.number_input("Time Limit (minutes)", min_value=5, max_value=180, value=60, step=5)
        
        # Test type selection
        test_type = st.radio("Test Type", ["Multiple Choice", "Essay", "Mixed"])
        
        # Question section
        st.subheader("Questions")
        
        # Initialize questions in session state if not present
        if 'test_questions' not in st.session_state:
            st.session_state.test_questions = []
        
        # Add question button
        add_question = st.checkbox("Add Question")
        
        if add_question:
            question_type = st.selectbox("Question Type", ["Multiple Choice", "True/False", "Short Answer", "Fill in the Blank"])
            question_text = st.text_area("Question Text")
            question_points = st.number_input("Points", min_value=1, max_value=100, value=10)
            
            # Different inputs based on question type
            if question_type == "Multiple Choice":
                options = []
                for i in range(4):
                    option = st.text_input(f"Option {i+1}", key=f"option_{i}")
                    options.append(option)
                
                correct_answer = st.selectbox("Correct Answer", options, format_func=lambda x: x if x else "Select correct answer")
                
                if st.button("Add This Question"):
                    if question_text and correct_answer and all(options):
                        new_question = {
                            'id': len(st.session_state.test_questions) + 1,
                            'type': question_type,
                            'text': question_text,
                            'points': question_points,
                            'options': options,
                            'correct_answer': correct_answer
                        }
                        st.session_state.test_questions.append(new_question)
                        st.success("Question added!")
                        st.rerun()
            elif question_type == "True/False":
                correct_answer = st.radio("Correct Answer", ["True", "False"])
                
                if st.button("Add This Question"):
                    if question_text:
                        new_question = {
                            'id': len(st.session_state.test_questions) + 1,
                            'type': question_type,
                            'text': question_text,
                            'points': question_points,
                            'options': ["True", "False"],
                            'correct_answer': correct_answer
                        }
                        st.session_state.test_questions.append(new_question)
                        st.success("Question added!")
                        st.rerun()
            elif question_type == "Short Answer":
                correct_answer = st.text_input("Correct Answer")
                
                if st.button("Add This Question"):
                    if question_text and correct_answer:
                        new_question = {
                            'id': len(st.session_state.test_questions) + 1,
                            'type': question_type,
                            'text': question_text,
                            'points': question_points,
                            'correct_answer': correct_answer
                        }
                        st.session_state.test_questions.append(new_question)
                        st.success("Question added!")
                        st.rerun()
            elif question_type == "Essay":
                word_limit = st.number_input("Word Limit", min_value=50, max_value=2000, value=500, step=50)
                
                if st.button("Add This Question"):
                    if question_text:
                        new_question = {
                            'id': len(st.session_state.test_questions) + 1,
                            'type': question_type,
                            'text': question_text,
                            'points': question_points,
                            'word_limit': word_limit
                        }
                        st.session_state.test_questions.append(new_question)
                        st.success("Question added!")
                        st.rerun()
        
        # Display added questions
        if st.session_state.test_questions:
            st.subheader("Added Questions")
            for i, question in enumerate(st.session_state.test_questions):
                with st.expander(f"Question {i+1}: {question['text'][:50]}... ({question['points']} pts)"):
                    st.write(f"**Type:** {question['type']}")
                    st.write(f"**Question:** {question['text']}")
                    st.write(f"**Points:** {question['points']}")
                    
                    if question['type'] == "Multiple Choice":
                        st.write("**Options:**")
                        for j, option in enumerate(question['options']):
                            if option == question['correct_answer']:
                                st.write(f"- {option} ✓")
                            else:
                                st.write(f"- {option}")
                    
                    elif question['type'] == "True/False":
                        st.write(f"**Correct Answer:** {question['correct_answer']}")
                    
                    elif question['type'] == "Short Answer":
                        st.write(f"**Correct Answer:** {question['correct_answer']}")
                    
                    elif question['type'] == "Essay":
                        st.write(f"**Word Limit:** {question['word_limit']}")
                    
                    # Delete question button
                    if st.button("Delete Question", key=f"delete_q_{i}"):
                        st.session_state.test_questions.pop(i)
                        st.success("Question deleted!")
                        st.rerun()
            
        # AI assistance for test creation
        st.subheader("AI Test Generation")
        use_ai = st.checkbox("Use AI to generate questions")
        
        if use_ai:
            ai_topic = st.text_input("Topic")
            ai_difficulty = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard"])
            ai_num_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=5)
            ai_question_types = st.multiselect(
                "Question Types",
                options=["Multiple Choice", "True/False", "Short Answer", "Essay"],
                default=["Multiple Choice", "True/False"]
            )
            
            if st.button("Generate Questions with AI"):
                if ai_topic:
                    with st.spinner("Generating questions with AI..."):
                        # Simulate AI processing
                        import time
                        time.sleep(2)
                        
                        # Display generated questions
                        st.success("Questions generated successfully!")
                        
                        st.write(f"## {ai_topic} Questions")
                        st.write(f"**Difficulty:** {ai_difficulty}")
                        st.write(f"**Total Questions:** {ai_num_questions}")
                        
                        # Sample questions
                        st.write("### Sample Questions")
                        
                        if "Multiple Choice" in ai_question_types:
                            st.write("**Multiple Choice**")
                            st.write("1. What is the main concept of this topic?")
                            st.write("   a) Option A")
                            st.write("   b) Option B")
                            st.write("   c) Option C")
                            st.write("   d) Option D")
                        
                        if "True/False" in ai_question_types:
                            st.write("**True/False**")
                            st.write("2. This statement about the topic is correct.")
                            st.write("   True / False")
                        
                        if "Short Answer" in ai_question_types:
                            st.write("**Short Answer**")
                            st.write("3. Explain the relationship between concept A and concept B.")
                        
                        if "Essay" in ai_question_types:
                            st.write("**Essay**")
                            st.write("4. Describe the process of ________ in detail.")
                        
                        # Download option
                        st.session_state.quiz_created = True
                        st.session_state.quiz_data = {
                            "topic": ai_topic,
                            "difficulty": ai_difficulty,
                            "num_questions": ai_num_questions
                        }
            
            # Display download button outside the form
            if st.session_state.get("quiz_created", False):
                quiz_data = st.session_state.quiz_data
                st.download_button(
                    label="Download Quiz",
                    data=f"# {quiz_data['topic']} Quiz\n\nDifficulty: {quiz_data['difficulty']}\nTotal Questions: {quiz_data['num_questions']}\n\n...",
                    file_name=f"{quiz_data['topic'].replace(' ', '_')}_quiz.txt",
                    mime="text/plain"
                )
        
        # Submit button for the entire form
        submit_test = st.form_submit_button("Create Test")
        
        if submit_test:
            if not test_title:
                st.error("Test title is required.")
            elif not st.session_state.test_questions:
                st.error("Please add at least one question to the test.")
            else:
                # Create the test as an assignment
                test_data = {
                    'title': test_title,
                    'description': test_description,
                    'course_id': selected_course['id'],
                    'teacher_id': teacher_id,
                    'type': 'test',
                    'points': total_points,
                    'due_date': due_date.isoformat(),
                    'time_limit': time_limit,
                    'questions': st.session_state.test_questions
                }
                
                # Save the test
                assignments = load_data('assignments')
                test_data['id'] = len(assignments) + 1
                test_data['created_at'] = datetime.now().isoformat()
                assignments.append(test_data)
                save_data(assignments, 'assignments')
                
                # Log the action
                log_audit(
                    teacher_id,
                    'create',
                    'test',
                    test_data['id'],
                    True,
                    f"Created test: {test_title}"
                )
                
                # Clear the questions
                st.session_state.test_questions = []
                
                st.success(f"Test '{test_title}' created successfully!")
                st.rerun()

if __name__ == "__main__":
    main()