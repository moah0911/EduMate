def show_course_students(course):
    """Display students enrolled in the course with options to manage enrollment"""
    # Only import streamlit inside the function to prevent conflicts with page_config
    import streamlit as st
    
    # Get all users
    from app import load_data, enroll_student
    
    st.subheader("Enrolled Students")
    
    # Get all users
    users = load_data('users')
    
    # Get students enrolled in the course
    enrolled_students = [user for user in users if user['role'] == 'student' and user['id'] in course.get('students', [])]
    
    # Display enrolled students
    if not enrolled_students:
        st.info("No students enrolled in this course yet.")
    else:
        # Display student count with highlighted background
        st.markdown(f"""
        <div style="background-color:#2a4c7d; color:white; padding:8px; 
             border-radius:5px; margin:5px 0; text-align:center; font-weight:bold;">
            Total students: {len(enrolled_students)}
        </div>
        """, unsafe_allow_html=True)
        
        # Create a list of students with improved visibility
        for i, student in enumerate(enrolled_students, 1):
            username = student.get('username', 'No username')
            st.markdown(f"""
            <div style="background-color:#1e2130; padding:10px; border-radius:5px; margin:8px 0; border:1px solid #555;">
                <span style="color:white; font-weight:bold;">{i}. {student['name']}</span> - 
                <span style="color:#4cc9f0;">{username}</span> 
                <span style="color:#dddddd;">({student['email']})</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Teacher options to add students
    if st.session_state.current_user['role'] == 'teacher' and st.session_state.current_user['id'] == course['teacher_id']:
        with st.expander("Add New Students"):
            # Get all students not enrolled in the course
            available_students = [user for user in users if user['role'] == 'student' and user['id'] not in course.get('students', [])]
            
            if available_students:
                # Create a selectbox with student names and IDs
                student_options = {f"{user['name']} ({user.get('username', user['email'])})": user['id'] for user in available_students}
                
                st.markdown("""
                <div style="background-color:#2a4c7d; color:white; padding:5px; 
                     border-radius:5px; margin:5px 0 10px 0; text-align:center;">
                    <span style="font-weight:bold;">Available Students</span>
                </div>
                """, unsafe_allow_html=True)
                
                selected_student = st.selectbox("Select a student", list(student_options.keys()))
                
                if st.button("Add Student"):
                    student_id = student_options[selected_student]
                    success, message = enroll_student(course['id'], student_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("All students are already enrolled in this course.")
