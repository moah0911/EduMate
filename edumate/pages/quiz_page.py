import streamlit as st
import json
import os
from datetime import datetime
import time
import random

def show_quizzes(quiz_manager):
    """Display quizzes for students"""
    st.header("📝 Quizzes and Assessments")
    
    # Get all available quizzes
    all_quizzes = quiz_manager.get_all_quizzes()
    
    if not all_quizzes:
        st.info("No quizzes are currently available.")
        return
    
    # Create subject filter
    subjects = sorted(list(set(quiz['subject'] for quiz in all_quizzes)))
    selected_subject = st.selectbox("Filter by Subject", ["All Subjects"] + subjects)
    
    # Filter quizzes by subject
    if selected_subject != "All Subjects":
        filtered_quizzes = [quiz for quiz in all_quizzes if quiz['subject'] == selected_subject]
    else:
        filtered_quizzes = all_quizzes
    
    # Display quizzes
    if not filtered_quizzes:
        st.info(f"No quizzes available for {selected_subject}.")
        return
    
    st.write(f"### Available Quizzes ({len(filtered_quizzes)})")
    
    # Get student quiz attempts if logged in as student
    student_attempts = []
    if st.session_state.logged_in and st.session_state.current_user['role'] == 'student':
        student_id = st.session_state.current_user['id']
        student_attempts = quiz_manager.get_student_quiz_attempts(student_id)
    
    # Create columns for quiz cards
    col1, col2 = st.columns(2)
    
    for i, quiz in enumerate(filtered_quizzes):
        # Alternate between columns
        with col1 if i % 2 == 0 else col2:
            with st.container():
                st.markdown(f"""
                <div style="padding: 15px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 10px;">
                    <h4>{quiz['title']}</h4>
                    <p><strong>Subject:</strong> {quiz['subject']}</p>
                    <p><strong>Difficulty:</strong> {quiz['difficulty']}</p>
                    <p><strong>Time Limit:</strong> {quiz['time_limit_minutes']} minutes</p>
                    <p><strong>Questions:</strong> {len(quiz['questions'])}</p>
                    <p><small>{quiz['description']}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Check if student has attempted this quiz before
                attempts = [a for a in student_attempts if a['quiz_id'] == quiz['id']]
                if attempts:
                    best_score = max([a['score'] for a in attempts])
                    st.write(f"Your best score: {best_score:.1f}%")
                    
                    # Take quiz again button
                    if st.button(f"Take Quiz Again", key=f"take_again_{quiz['id']}"):
                        st.session_state.selected_quiz = quiz['id']
                        st.session_state.current_page = 'take_quiz'
                        st.rerun()
                else:
                    # Take quiz button
                    if st.button(f"Take Quiz", key=f"take_{quiz['id']}"):
                        st.session_state.selected_quiz = quiz['id']
                        st.session_state.current_page = 'take_quiz'
                        st.rerun()

def show_take_quiz(quiz_manager):
    """Display interface for taking a quiz"""
    if 'selected_quiz' not in st.session_state:
        st.error("No quiz selected")
        if st.button("Back to Quizzes"):
            st.session_state.current_page = 'quizzes'
            st.rerun()
        return
    
    quiz = quiz_manager.get_quiz_by_id(st.session_state.selected_quiz)
    if not quiz:
        st.error("Quiz not found")
        if st.button("Back to Quizzes"):
            st.session_state.current_page = 'quizzes'
            st.rerun()
        return
    
    # Check if quiz is already in progress
    if 'quiz_in_progress' not in st.session_state:
        st.session_state.quiz_in_progress = False
        st.session_state.quiz_answers = []
        st.session_state.quiz_current_question = 0
        st.session_state.quiz_start_time = None
        st.session_state.quiz_time_remaining = quiz['time_limit_minutes'] * 60
    
    # Display quiz header
    st.header(f"Quiz: {quiz['title']}")
    st.write(f"Subject: {quiz['subject']} | Difficulty: {quiz['difficulty']} | Time Limit: {quiz['time_limit_minutes']} minutes")
    
    # Quiz not started yet
    if not st.session_state.quiz_in_progress:
        st.write(f"### {quiz['description']}")
        st.write(f"Number of questions: {len(quiz['questions'])}")
        st.write(f"Passing score: {quiz['passing_score']}%")
        
        st.warning("Once you start the quiz, the timer will begin. You must complete the quiz within the time limit.")
        
        # Start quiz button
        if st.button("Start Quiz"):
            st.session_state.quiz_in_progress = True
            st.session_state.quiz_start_time = time.time()
            st.session_state.quiz_answers = [None] * len(quiz['questions'])
            # Randomize question order for each attempt
            st.session_state.quiz_question_order = list(range(len(quiz['questions'])))
            random.shuffle(st.session_state.quiz_question_order)
            st.rerun()
    else:
        # Quiz in progress
        # Calculate time remaining
        elapsed_time = time.time() - st.session_state.quiz_start_time
        time_remaining = max(0, quiz['time_limit_minutes'] * 60 - elapsed_time)
        st.session_state.quiz_time_remaining = time_remaining
        
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        
        # Display timer
        st.write(f"Time remaining: {minutes:02d}:{seconds:02d}")
        
        progress = st.session_state.quiz_current_question / len(quiz['questions'])
        st.progress(progress)
        
        # Check if time is up
        if time_remaining <= 0:
            st.error("Time's up! Submitting your quiz.")
            _submit_quiz(quiz_manager, quiz)
            return
        
        # Get current question
        question_idx = st.session_state.quiz_question_order[st.session_state.quiz_current_question]
        question = quiz['questions'][question_idx]
        
        # Display question
        st.write(f"### Question {st.session_state.quiz_current_question + 1} of {len(quiz['questions'])}")
        st.write(question['text'])
        
        # Show options
        if question['type'] == 'multiple_choice':
            answer = st.radio("Select your answer:", question['options'], key=f"q_{question_idx}")
            
            # Store answer
            current_answer_idx = st.session_state.quiz_current_question
            if st.session_state.quiz_answers[current_answer_idx] != answer:
                st.session_state.quiz_answers[current_answer_idx] = answer
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.quiz_current_question > 0:
                if st.button("Previous Question"):
                    st.session_state.quiz_current_question -= 1
                    st.rerun()
        
        with col2:
            if st.session_state.quiz_current_question < len(quiz['questions']) - 1:
                if st.button("Next Question"):
                    st.session_state.quiz_current_question += 1
                    st.rerun()
            else:
                if st.button("Submit Quiz"):
                    _submit_quiz(quiz_manager, quiz)

def _submit_quiz(quiz_manager, quiz):
    """Submit the quiz and calculate score"""
    # Calculate score
    correct_answers = 0
    total_questions = len(quiz['questions'])
    
    # Prepare detailed answers for recording
    detailed_answers = {}
    
    for i, question_idx in enumerate(st.session_state.quiz_question_order):
        question = quiz['questions'][question_idx]
        user_answer = st.session_state.quiz_answers[i]
        
        # Skip unanswered questions
        if user_answer is None:
            user_answer = ""
        
        # Prepare the submission format
        question_id = str(question_idx)
        detailed_answers[question_id] = user_answer
    
    # Submit to quiz service for grading
    try:
        result = quiz_manager.quiz_service.grade_quiz_submission(quiz['id'], {"answers": detailed_answers})
        
        # Store results in session state
        st.session_state.quiz_results = {
            'quiz_id': quiz['id'],
            'quiz_title': quiz['title'],
            'total_questions': result['total'],
            'correct_answers': result['score'],
            'score_percentage': result['percentage'],
            'passing_score': quiz.get('passing_score', 70),
            'passed': result['percentage'] >= quiz.get('passing_score', 70),
            'detailed_answers': result['question_results'],
            'feedback': result.get('feedback', '')
        }
    except Exception as e:
        # Fallback to basic scoring if AI grading fails
        for i, question_idx in enumerate(st.session_state.quiz_question_order):
            question = quiz['questions'][question_idx]
            user_answer = st.session_state.quiz_answers[i]
            
            # Skip unanswered questions
            if user_answer is None:
                user_answer = ""
            
            # Simple matching for fallback
            is_correct = False
            if user_answer and 'correct_answer' in question:
                is_correct = str(user_answer).lower() == str(question['correct_answer']).lower()
            
            if is_correct:
                correct_answers += 1
                
        # Calculate percentage score
        score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Create basic results without AI
        st.session_state.quiz_results = {
            'quiz_id': quiz['id'],
            'quiz_title': quiz['title'],
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score_percentage': score_percentage,
            'passing_score': quiz.get('passing_score', 70),
            'passed': score_percentage >= quiz.get('passing_score', 70),
            'detailed_answers': [],
            'feedback': f"You scored {score_percentage:.1f}% on the quiz. AI feedback could not be generated."
        }
    
    # Record the attempt if user is logged in
    if st.session_state.logged_in:
        quiz_manager.record_quiz_attempt(
            st.session_state.current_user['id'],
            quiz['id'],
            st.session_state.quiz_results['score_percentage'],
            detailed_answers
        )
    
    # Reset quiz progress
    st.session_state.quiz_in_progress = False
    
    # Show results page
    st.session_state.current_page = 'quiz_results'
    st.rerun()

def show_quiz_results(quiz_manager):
    """Display quiz results"""
    if 'quiz_results' not in st.session_state:
        st.error("No quiz results to display")
        if st.button("Back to Quizzes"):
            st.session_state.current_page = 'quizzes'
            st.rerun()
        return
    
    results = st.session_state.quiz_results
    
    # Display header
    st.header(f"Quiz Results: {results['quiz_title']}")
    
    # Display score
    st.write(f"### Your Score: {results['score_percentage']:.1f}%")
    
    # Display pass/fail status
    if results['passed']:
        st.success(f"Congratulations! You passed the quiz. (Passing score: {results['passing_score']}%)")
    else:
        st.error(f"You did not pass the quiz. (Passing score: {results['passing_score']}%)")
    
    # Display score statistics
    st.write(f"Correct answers: {results['correct_answers']} out of {results['total_questions']}")
    
    # Display AI feedback if available
    if 'feedback' in results and results['feedback']:
        st.markdown("### Feedback")
        st.markdown(results['feedback'])
    
    # Display detailed results
    st.write("### Detailed Results")
    
    # Handle different result structures
    if 'detailed_answers' in results:
        if isinstance(results['detailed_answers'], list):
            # Handle the new structure from AI grading
            for i, result_item in enumerate(results['detailed_answers']):
                q_id = result_item.get('question_id', str(i))
                
                # Get question text from original quiz
                quiz = quiz_manager.get_quiz_by_id(results['quiz_id'])
                question_text = f"Question {int(q_id) + 1}"
                if quiz and 'questions' in quiz and int(q_id) < len(quiz['questions']):
                    question = quiz['questions'][int(q_id)]
                    question_text = question.get('text', question_text)
                
                with st.expander(f"Question {i+1}: {question_text}"):
                    st.write(f"Your answer: {result_item.get('student_answer', 'Not provided')}")
                    st.write(f"Correct answer: {result_item.get('correct_answer', 'Not available')}")
                    
                    if result_item.get('is_correct', False):
                        st.success("Correct!")
                    else:
                        st.error("Incorrect")
                    
                    if 'explanation' in result_item and result_item['explanation']:
                        st.info(f"Explanation: {result_item['explanation']}")
        else:
            # No detailed results available
            st.info("Detailed results are not available for this quiz attempt.")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Take Another Quiz"):
            st.session_state.current_page = 'quizzes'
            # Clear results
            if 'quiz_results' in st.session_state:
                del st.session_state.quiz_results
            st.rerun()
    
    with col2:
        if st.button("Back to Dashboard"):
            st.session_state.current_page = 'dashboard'
            # Clear results
            if 'quiz_results' in st.session_state:
                del st.session_state.quiz_results
            st.rerun()

def show_quiz_management(quiz_manager):
    """Teacher interface for managing quizzes"""
    st.header("Quiz Management")
    
    # Get course ID if quiz is being created for a specific course
    course_id = None
    if 'create_quiz_for_course' in st.session_state:
        course_id = st.session_state.create_quiz_for_course
        # Get course details
        from app import get_course_by_id
        course = get_course_by_id(course_id)
        if course:
            st.info(f"Creating quiz for course: {course['name']} ({course['code']})")
    
    # Get all quizzes
    all_quizzes = quiz_manager.get_all_quizzes()
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["All Quizzes", "Create Quiz", "Statistics"])
    
    with tab1:
        if not all_quizzes:
            st.info("No quizzes available. Create your first quiz!")
        else:
            st.write(f"### Quizzes ({len(all_quizzes)})")
            
            # Create subject filter
            subjects = sorted(list(set(quiz['subject'] for quiz in all_quizzes)))
            selected_subject = st.selectbox("Filter by Subject", ["All Subjects"] + subjects, key="manage_subject_filter")
            
            # Filter quizzes by subject
            if selected_subject != "All Subjects":
                filtered_quizzes = [quiz for quiz in all_quizzes if quiz['subject'] == selected_subject]
            else:
                filtered_quizzes = all_quizzes
            
            # Display quizzes
            for quiz in filtered_quizzes:
                course_text = ""
                if 'course_id' in quiz and quiz['course_id']:
                    from app import get_course_by_id
                    course = get_course_by_id(quiz['course_id'])
                    if course:
                        course_text = f" - Course: {course['name']}"
                
                with st.expander(f"{quiz['title']} ({quiz['subject']}){course_text}"):
                    st.write(f"**Description:** {quiz['description']}")
                    st.write(f"**Difficulty:** {quiz['difficulty']}")
                    st.write(f"**Time Limit:** {quiz['time_limit_minutes']} minutes")
                    st.write(f"**Passing Score:** {quiz['passing_score']}%")
                    st.write(f"**Questions:** {len(quiz['questions'])}")
                    
                    # View statistics button
                    if st.button("View Statistics", key=f"stats_{quiz['id']}"):
                        st.session_state.selected_quiz_stats = quiz['id']
                        st.rerun()
                    
                    # Edit button
                    if st.button("Edit Quiz", key=f"edit_{quiz['id']}"):
                        st.session_state.edit_quiz_id = quiz['id']
                        st.rerun()
                    
                    # Delete button
                    if st.button("Delete Quiz", key=f"delete_{quiz['id']}"):
                        if quiz_manager.delete_quiz(quiz['id']):
                            st.success("Quiz deleted successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to delete quiz.")
    
    with tab2:
        st.write("### Create a New Quiz")
        
        with st.form("create_quiz_form"):
            title = st.text_input("Quiz Title")
            description = st.text_area("Description")
            subject = st.text_input("Subject")
            
            col1, col2 = st.columns(2)
            with col1:
                difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
                time_limit = st.number_input("Time Limit (minutes)", min_value=5, max_value=180, value=30)
            
            with col2:
                passing_score = st.slider("Passing Score (%)", min_value=50, max_value=100, value=70)
                num_questions = st.number_input("Number of Questions", min_value=1, max_value=50, value=5)
            
            # Create quiz button
            submit_button = st.form_submit_button("Create Quiz Template")
            
            if submit_button:
                if not title or not description or not subject:
                    st.error("Please fill in all fields.")
                else:
                    # Create question templates
                    questions = []
                    for i in range(int(num_questions)):
                        questions.append({
                            "id": i + 1,
                            "text": f"Question {i + 1}",
                            "type": "multiple_choice",
                            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                            "correct_answer": "Option 1",
                            "explanation": ""
                        })
                    
                    # Create quiz data
                    quiz_data = {
                        "title": title,
                        "description": description,
                        "subject": subject,
                        "time_limit_minutes": time_limit,
                        "passing_score": passing_score,
                        "difficulty": difficulty,
                        "questions": questions
                    }
                    
                    # Add course ID if creating quiz for a specific course
                    if course_id:
                        quiz_data["course_id"] = course_id
                    
                    # Add quiz
                    if quiz_manager.add_quiz(quiz_data):
                        st.success("Quiz template created successfully! Now you can edit the questions.")
                        # Clear the course_id if it was set
                        if 'create_quiz_for_course' in st.session_state:
                            del st.session_state.create_quiz_for_course
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to create quiz.")
    
    with tab3:
        st.write("### Quiz Statistics")
        
        # Check if a quiz is selected for statistics
        if 'selected_quiz_stats' in st.session_state:
            quiz = quiz_manager.get_quiz_by_id(st.session_state.selected_quiz_stats)
            if quiz:
                stats = quiz_manager.get_quiz_statistics(quiz['id'])
                
                st.write(f"#### Statistics for: {quiz['title']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Attempts", stats['attempts'])
                    st.metric("Average Score", f"{stats['average_score']:.1f}%")
                
                with col2:
                    st.metric("Passing Rate", f"{stats['passing_rate']:.1f}%")
                    st.metric("Highest Score", f"{stats['highest_score']:.1f}%")
                
                if st.button("Back to Quiz List"):
                    del st.session_state.selected_quiz_stats
                    st.rerun()
            else:
                st.error("Quiz not found.")
        else:
            st.info("Select a quiz from the 'All Quizzes' tab to view its statistics.")
