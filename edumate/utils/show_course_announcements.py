def show_course_announcements(course, load_data_func=None, save_data_func=None):
    """
    Display and manage course announcements
    
    Args:
        course: The course object containing information about the course
        load_data_func: Function to load data from the data store
        save_data_func: Function to save data to the data store
    """
    # Import streamlit inside the function to prevent conflicts with page_config
    import streamlit as st
    from datetime import datetime
    
    # Use the functions passed as parameters
    if load_data_func is None:
        st.error("Required functions not provided to show_course_announcements")
        return
    
    # Get announcements for this course
    announcements = load_data_func('announcements')
    course_announcements = [a for a in announcements if a.get('course_id') == course['id']]
    
    # Display header with styling
    st.markdown("""
    <div style="background-color:#2a4c7d; color:white; padding:10px; 
         border-radius:5px; margin:5px 0; text-align:center; font-weight:bold;">
        Course Announcements
    </div>
    """, unsafe_allow_html=True)
    
    # Teacher can create announcements
    if st.session_state.current_user['role'] == 'teacher' and st.session_state.current_user['id'] == course['teacher_id']:
        with st.expander("Create New Announcement", expanded=False):
            with st.form("new_announcement_form"):
                st.markdown("<p style='color:#ffffff; font-weight:bold;'>Create a New Announcement</p>", unsafe_allow_html=True)
                title = st.text_input("Title")
                content = st.text_area("Announcement Content")
                
                if st.form_submit_button("Post Announcement"):
                    if title and content:
                        new_announcement = {
                            'id': str(len(announcements) + 1),
                            'course_id': course['id'],
                            'title': title,
                            'content': content,
                            'created_by': st.session_state.current_user['id'],
                            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'is_pinned': False
                        }
                        
                        announcements.append(new_announcement)
                        if save_data_func:
                            save_data_func('announcements', announcements)
                            st.success("Announcement posted successfully!")
                            st.rerun()
                        else:
                            st.error("Save function not provided, announcement not saved")
                    else:
                        st.error("Please fill out both title and content")
    
    # Display announcements
    if not course_announcements:
        st.info("No announcements yet for this course.")
    else:
        # Sort announcements by pinned first, then by date (newest first)
        sorted_announcements = sorted(
            course_announcements, 
            key=lambda x: (not x.get('is_pinned', False), x.get('created_at', '')), 
            reverse=True
        )
        
        for i, announcement in enumerate(sorted_announcements):
            # Get the teacher's name
            users = load_data_func('users')
            teacher = next((u for u in users if u['id'] == announcement.get('created_by')), None)
            teacher_name = teacher['name'] if teacher else "Unknown"
            
            # Background color based on pinned status
            bg_color = "#283145" if announcement.get('is_pinned', False) else "#1e2130"
            pin_indicator = "📌 " if announcement.get('is_pinned', False) else ""
            
            # Render the announcement with improved visibility
            st.markdown(f"""
            <div style="background-color:{bg_color}; padding:15px; border-radius:5px; 
                 margin:10px 0; border:1px solid #4e5d78;">
                <h3 style="color:#e2e8f0; margin-top:0;">{pin_indicator}{announcement['title']}</h3>
                <p style="color:#cbd5e1; white-space:pre-line;">{announcement['content']}</p>
                <div style="color:#94a3b8; font-size:0.9em; margin-top:10px;">
                    Posted by {teacher_name} on {announcement.get('created_at', 'Unknown date')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Teacher controls for announcements
            if st.session_state.current_user['role'] == 'teacher' and st.session_state.current_user['id'] == course['teacher_id']:
                col1, col2 = st.columns([1, 10])
                with col1:
                    if st.button("📌" if not announcement.get('is_pinned', False) else "📍", 
                               key=f"pin_announcement_{announcement['id']}"):
                        for ann in announcements:
                            if ann['id'] == announcement['id']:
                                ann['is_pinned'] = not ann.get('is_pinned', False)
                                break
                        if save_data_func:
                            save_data_func('announcements', announcements)
                            st.rerun()
                with col2:
                    if st.button("🗑️", key=f"delete_announcement_{announcement['id']}"):
                        filtered_announcements = [a for a in announcements if a['id'] != announcement['id']]
                        if save_data_func:
                            save_data_func('announcements', filtered_announcements)
                            st.success("Announcement deleted")
                            st.rerun()
