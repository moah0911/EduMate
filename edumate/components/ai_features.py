"""
AI Features component for EduMate.

This module provides a Streamlit component for displaying and interacting with
the advanced AI features of the EduMate platform.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import json

from edumate.utils.personalized_learning import PersonalizedLearningPath
from edumate.utils.plagiarism_detector import PlagiarismDetector
from edumate.utils.ai_tutor import AITutor

def show_ai_features():
    """Display the AI features interface.
    
    This function creates a tabbed interface that allows users to interact with
    the advanced AI features of the EduMate platform.
    """
    st.title("🤖 Advanced AI Features")
    st.write("Leverage the power of artificial intelligence to enhance your learning experience.")
    
    # Initialize AI components
    personalized_learning = PersonalizedLearningPath()
    plagiarism_detector = PlagiarismDetector()
    ai_tutor = AITutor()
    
    # Create tabs for different AI features
    tabs = st.tabs(["Personalized Learning", "Plagiarism Detection", "AI Tutor"])
    
    # Personalized Learning tab
    with tabs[0]:
        show_personalized_learning(personalized_learning)
    
    # Plagiarism Detection tab
    with tabs[1]:
        show_plagiarism_detection(plagiarism_detector)
    
    # AI Tutor tab
    with tabs[2]:
        show_ai_tutor(ai_tutor)

def show_personalized_learning(personalized_learning):
    """Display the personalized learning interface.
    
    Args:
        personalized_learning: PersonalizedLearningPath instance
    """
    st.header("Personalized Learning Paths")
    st.write("Get a customized learning path based on your performance and learning style.")
    
    # Check if user is a student
    if not st.session_state.get("logged_in", False) or st.session_state.get("user_role") != "student":
        st.warning("Please log in as a student to access personalized learning paths.")
        return
    
    # Get student ID and enrolled courses
    student_id = st.session_state.get("user_id")
    
    # For demonstration, create some sample course data
    # In a real application, this would come from the database
    sample_courses = [
        {"id": "course1", "name": "Introduction to Computer Science"},
        {"id": "course2", "name": "Data Structures and Algorithms"},
        {"id": "course3", "name": "Web Development Fundamentals"}
    ]
    
    # Course selection
    selected_course = st.selectbox(
        "Select a course",
        options=[course["id"] for course in sample_courses],
        format_func=lambda x: next((c["name"] for c in sample_courses if c["id"] == x), x)
    )
    
    # Check if a learning path exists for this student and course
    existing_path = personalized_learning.get_learning_path(student_id, selected_course)
    
    if existing_path:
        st.success("Your personalized learning path is ready!")
        
        # Display learning path details
        st.subheader("Your Learning Path")
        
        # Display learning style
        learning_style = existing_path.get("learning_style", "Not determined")
        st.write(f"**Learning Style:** {learning_style}")
        
        # Display modules
        st.write("**Learning Modules:**")
        
        for i, module in enumerate(existing_path.get("path_modules", [])):
            with st.expander(f"{i+1}. {module.get('topic')} ({module.get('difficulty').title()})"):
                st.write(f"**Type:** {module.get('type', 'standard').title()}")
                st.write(f"**Estimated Time:** {module.get('estimated_time', 'N/A')}")
                st.write(f"**Priority:** {module.get('priority', 'medium').title()}")
                
                # Display resources
                st.write("**Resources:**")
                for resource in module.get("resources", []):
                    st.write(f"- [{resource.get('title')}]({resource.get('url')}): {resource.get('description')}")
    else:
        st.info("No personalized learning path found. Let's create one!")
        
        # Learning style selection
        st.subheader("Learning Style Questionnaire")
        st.write("Please answer the following questions to help us determine your learning style.")
        
        q1 = st.radio(
            "When learning something new, I prefer to:",
            ["See diagrams and visual aids", "Hear explanations", "Read and write about it", "Try it hands-on"]
        )
        
        q2 = st.radio(
            "I remember information best when:",
            ["I see it written or in a diagram", "I hear it or discuss it", "I take notes or read about it", "I physically practice it"]
        )
        
        q3 = st.radio(
            "When solving a problem, I tend to:",
            ["Visualize the solution", "Talk through the steps", "Write down the steps", "Try different approaches"]
        )
        
        # Map responses to learning styles
        style_mapping = {
            "See diagrams and visual aids": "visual",
            "Hear explanations": "auditory",
            "Read and write about it": "reading/writing",
            "Try it hands-on": "kinesthetic",
            "I see it written or in a diagram": "visual",
            "I hear it or discuss it": "auditory",
            "I take notes or read about it": "reading/writing",
            "I physically practice it": "kinesthetic",
            "Visualize the solution": "visual",
            "Talk through the steps": "auditory",
            "Write down the steps": "reading/writing",
            "Try different approaches": "kinesthetic"
        }
        
        # Sample performance data (in a real app, this would come from the database)
        sample_performance = {
            "assignments": [
                {"topic": "Variables and Data Types", "score": 85, "topics": ["programming basics", "variables"]},
                {"topic": "Control Structures", "score": 75, "topics": ["conditionals", "loops"]},
                {"topic": "Functions", "score": 90, "topics": ["functions", "parameters"]}
            ],
            "quizzes": [
                {"topic": "Programming Basics", "score": 80, "topics": ["programming basics", "syntax"]},
                {"topic": "Control Flow", "score": 70, "topics": ["conditionals", "loops", "branching"]}
            ],
            "participation": [
                {"topic": "Class Discussion", "score": 85},
                {"topic": "Group Work", "score": 90}
            ]
        }
        
        if st.button("Generate Learning Path"):
            # Analyze performance
            analysis = personalized_learning.analyze_student_performance(student_id, sample_performance)
            
            # Create learning path
            path = personalized_learning.create_learning_path(student_id, selected_course, analysis)
            
            st.success("Your personalized learning path has been created!")
            st.experimental_rerun()

def show_plagiarism_detection(plagiarism_detector):
    """Display the plagiarism detection interface.
    
    Args:
        plagiarism_detector: PlagiarismDetector instance
    """
    st.header("Plagiarism Detection")
    
    # Check user role
    user_role = st.session_state.get("user_role")
    
    if user_role == "teacher":
        show_teacher_plagiarism_view(plagiarism_detector)
    elif user_role == "student":
        show_student_plagiarism_view(plagiarism_detector)
    else:
        st.warning("Please log in as a teacher or student to access plagiarism detection features.")

def show_teacher_plagiarism_view(plagiarism_detector):
    """Display the teacher view for plagiarism detection.
    
    Args:
        plagiarism_detector: PlagiarismDetector instance
    """
    st.subheader("Check Student Submissions for Plagiarism")
    
    # Sample assignments and submissions (in a real app, this would come from the database)
    sample_assignments = [
        {"id": "assignment1", "name": "Essay on Climate Change"},
        {"id": "assignment2", "name": "Research Paper on Renewable Energy"},
        {"id": "assignment3", "name": "Literature Review on Sustainable Development"}
    ]
    
    # Assignment selection
    selected_assignment = st.selectbox(
        "Select an assignment",
        options=[a["id"] for a in sample_assignments],
        format_func=lambda x: next((a["name"] for a in sample_assignments if a["id"] == x), x)
    )
    
    # Get reports for the selected assignment
    reports = plagiarism_detector.get_reports_by_assignment(selected_assignment)
    
    if reports:
        st.write(f"Found {len(reports)} plagiarism reports for this assignment.")
        
        # Display reports in a table
        report_data = []
        for report in reports:
            report_data.append({
                "Student ID": report.get("student_id", "Unknown"),
                "Similarity Score": f"{report.get('similarity_score', 0) * 100:.1f}%",
                "Plagiarism Detected": "Yes" if report.get("plagiarism_detected", False) else "No",
                "Report ID": report.get("id", "")
            })
        
        df = pd.DataFrame(report_data)
        st.dataframe(df)
        
        # View detailed report
        selected_report_id = st.selectbox("Select a report to view details", options=[r.get("id", "") for r in reports])
        
        if selected_report_id:
            selected_report = plagiarism_detector.get_report(selected_report_id)
            
            if selected_report:
                st.subheader("Detailed Report")
                
                # Display summary
                st.write("**Summary:**")
                st.write(selected_report.get("summary", "No summary available."))
                
                # Display matched sources
                if selected_report.get("matched_sources"):
                    st.write("**Matched Student Submissions:**")
                    for i, match in enumerate(selected_report.get("matched_sources")):
                        st.write(f"Match {i+1}:")
                        st.write(f"- Student ID: {match.get('student_id', 'Unknown')}")
                        st.write(f"- Similarity: {match.get('similarity_score', 0) * 100:.1f}%")
                        
                        if match.get("matching_sentences"):
                            with st.expander("View matching sentences"):
                                for j, sentence_match in enumerate(match.get("matching_sentences")):
                                    st.write(f"**Pair {j+1}:**")
                                    st.write(f"Original: \"{sentence_match.get('text1_sentence', '')}\"")
                                    st.write(f"Matched: \"{sentence_match.get('text2_sentence', '')}\"")
                                    st.write(f"Similarity: {sentence_match.get('similarity', 0) * 100:.1f}%")
                                    st.write("---")
                
                # Display web matches
                if selected_report.get("web_matches"):
                    st.write("**Matched Web Sources:**")
                    for i, match in enumerate(selected_report.get("web_matches")):
                        st.write(f"Match {i+1}:")
                        st.write(f"- Source: {match.get('source_title', 'Unknown')}")
                        st.write(f"- URL: {match.get('source_url', 'N/A')}")
                        st.write(f"- Similarity: {match.get('similarity_score', 0) * 100:.1f}%")
                        
                        if match.get("matched_text"):
                            with st.expander("View matched text"):
                                st.write(match.get("matched_text", ""))
    else:
        st.info("No plagiarism reports found for this assignment.")
        
        st.subheader("Check New Submission")
        
        # Text area for submission
        submission_text = st.text_area("Paste submission text to check", height=200)
        
        # Student selection (in a real app, this would be a list of students)
        student_id = st.text_input("Student ID")
        
        # Check web option
        check_web = st.checkbox("Check against web sources", value=True)
        
        # Threshold slider
        threshold = st.slider("Similarity threshold", min_value=0.5, max_value=0.95, value=0.8, step=0.05)
        
        if st.button("Check for Plagiarism") and submission_text and student_id:
            # Check for plagiarism
            results = plagiarism_detector.check_plagiarism(
                submission_text,
                student_id,
                selected_assignment,
                check_web=check_web,
                threshold=threshold
            )
            
            # Display results
            if results.get("plagiarism_detected", False):
                st.error(f"Plagiarism detected with a similarity score of {results.get('similarity_score', 0) * 100:.1f}%")
            else:
                st.success("No plagiarism detected.")
            
            # Show detailed results
            st.json(results)

def show_student_plagiarism_view(plagiarism_detector):
    """Display the student view for plagiarism detection.
    
    Args:
        plagiarism_detector: PlagiarismDetector instance
    """
    st.subheader("Check Your Work for Plagiarism")
    st.write("Use this tool to check your work for unintentional plagiarism before submitting.")
    
    # Text area for submission
    submission_text = st.text_area("Paste your text to check", height=200)
    
    # Assignment selection (in a real app, this would be the student's assignments)
    assignment_id = st.text_input("Assignment ID")
    
    # Check web option
    check_web = st.checkbox("Check against web sources", value=True)
    
    if st.button("Check for Plagiarism") and submission_text and assignment_id:
        student_id = st.session_state.get("user_id", "student1")  # Default for demonstration
        
        # Check for plagiarism
        results = plagiarism_detector.check_plagiarism(
            submission_text,
            student_id,
            assignment_id,
            check_web=check_web
        )
        
        # Display results
        if results.get("plagiarism_detected", False):
            st.warning(f"Potential plagiarism detected with a similarity score of {results.get('similarity_score', 0) * 100:.1f}%")
            
            # Show suggestions
            st.subheader("Suggestions")
            st.write("Consider revising the following sections:")
            
            # Display matched sources if any
            if results.get("matched_sources"):
                for i, match in enumerate(results.get("matched_sources")):
                    if match.get("matching_sentences"):
                        for j, sentence_match in enumerate(match.get("matching_sentences")):
                            st.write(f"- \"{sentence_match.get('text1_sentence', '')}\"")
            
            # Display web matches if any
            if results.get("web_matches"):
                for i, match in enumerate(results.get("web_matches")):
                    if match.get("matched_text"):
                        st.write(f"- \"{match.get('matched_text', '')}\"")
            
            st.write("Tips to avoid plagiarism:")
            st.write("1. Always cite your sources")
            st.write("2. Paraphrase in your own words")
            st.write("3. Use quotation marks for direct quotes")
            st.write("4. Keep track of your research sources")
        else:
            st.success("No plagiarism detected. Your work appears to be original.")

def show_ai_tutor(ai_tutor):
    """Display the AI tutor interface.
    
    Args:
        ai_tutor: AITutor instance
    """
    st.header("AI Tutor")
    st.write("Get instant answers to your questions about course content.")
    
    # Check if user is logged in
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in to access the AI Tutor.")
        return
    
    # Get user ID and role
    user_id = st.session_state.get("user_id", "user1")  # Default for demonstration
    user_role = st.session_state.get("user_role", "student")
    
    # Sample courses (in a real app, this would come from the database)
    sample_courses = [
        {"id": "course1", "name": "Introduction to Computer Science"},
        {"id": "course2", "name": "Data Structures and Algorithms"},
        {"id": "course3", "name": "Web Development Fundamentals"}
    ]
    
    # Course selection
    selected_course = st.selectbox(
        "Select a course",
        options=[course["id"] for course in sample_courses],
        format_func=lambda x: next((c["name"] for c in sample_courses if c["id"] == x), x)
    )
    
    # Initialize or get chat history
    if "ai_tutor_history" not in st.session_state:
        st.session_state.ai_tutor_history = []
    
    # Display chat history
    for message in st.session_state.ai_tutor_history:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**AI Tutor:** {message['content']}")
    
    # Question input
    question = st.text_input("Ask a question about the course content")
    
    # Tutoring style selection
    tutoring_styles = {
        "direct": "Direct explanations",
        "socratic": "Guiding questions",
        "example_based": "Examples and illustrations",
        "analogy": "Analogies and comparisons"
    }
    
    tutoring_style = st.selectbox(
        "Preferred tutoring style",
        options=list(tutoring_styles.keys()),
        format_func=lambda x: tutoring_styles.get(x, x)
    )
    
    if st.button("Ask") and question:
        # Get answer from AI tutor
        response = ai_tutor.answer_question(
            question,
            user_id,
            selected_course,
            preferred_style=tutoring_style
        )
        
        # Add to chat history
        st.session_state.ai_tutor_history.append({"role": "user", "content": question})
        st.session_state.ai_tutor_history.append({"role": "assistant", "content": response["answer"]})
        
        # Rerun to update the display
        st.experimental_rerun()
    
    # Teacher-specific features
    if user_role == "teacher":
        st.subheader("Knowledge Base Management")
        
        # Add content to knowledge base
        with st.expander("Add content to knowledge base"):
            content_text = st.text_area("Content", height=200)
            content_topic = st.text_input("Topic")
            
            if st.button("Add to Knowledge Base") and content_text and content_topic:
                metadata = {
                    "course_id": selected_course,
                    "topic": content_topic,
                    "added_by": user_id,
                    "date_added": datetime.now().isoformat()
                }
                
                # Add to knowledge base
                entry_id = ai_tutor.add_to_knowledge_base(content_text, metadata)
                
                st.success(f"Content added to knowledge base with ID: {entry_id}")
        
        # View question analytics
        with st.expander("Question Analytics"):
            # Get question patterns
            analysis = ai_tutor.analyze_question_patterns(course_id=selected_course)
            
            if "error" in analysis:
                st.info(analysis["error"])
            else:
                st.write(f"Total questions: {analysis.get('total_questions', 0)}")
                st.write(f"Average confidence: {analysis.get('average_confidence', 0) * 100:.1f}%")
                st.write(f"Number of students: {analysis.get('student_count', 0)}")
                
                # Display top words
                st.subheader("Most Common Topics")
                top_words = analysis.get("top_words", [])
                
                if top_words:
                    # Create data for bar chart
                    words = [word for word, count in top_words[:10]]
                    counts = [count for word, count in top_words[:10]]
                    
                    # Create bar chart
                    fig, ax = plt.subplots()
                    ax.bar(words, counts)
                    ax.set_xlabel("Words")
                    ax.set_ylabel("Frequency")
                    ax.set_title("Most Common Words in Student Questions")
                    plt.xticks(rotation=45, ha="right")
                    plt.tight_layout()
                    
                    st.pyplot(fig)
                
                # Display questions by day
                st.subheader("Questions by Day")
                questions_by_day = analysis.get("questions_by_day", {})
                
                if questions_by_day:
                    # Create data for line chart
                    days = list(questions_by_day.keys())
                    counts = list(questions_by_day.values())
                    
                    # Sort by date
                    sorted_data = sorted(zip(days, counts), key=lambda x: x[0])
                    days = [d for d, c in sorted_data]
                    counts = [c for d, c in sorted_data]
                    
                    # Create line chart
                    fig, ax = plt.subplots()
                    ax.plot(days, counts, marker='o')
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Number of Questions")
                    ax.set_title("Questions per Day")
                    plt.xticks(rotation=45, ha="right")
                    plt.tight_layout()
                    
                    st.pyplot(fig)
