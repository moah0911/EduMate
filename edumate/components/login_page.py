def show_enhanced_login_page():
    """
    Display an enhanced, visually appealing login page for EduMate
    """
    import streamlit as st
    from edumate.components.language_selector import get_translation
    import base64
    import time
    
    # Check if function exists in session state
    if 'login_function' not in st.session_state:
        st.error("Login function not available. Please reload the application.")
        return
    
    # Define available languages focusing on Indian languages
    languages = {
        "English": "en",
        "हिंदी": "hi",
        "తెలుగు": "te",
        "தமிழ்": "ta",
        "ಕನ್ನಡ": "kn"
    }
    
    # Make sure language is initialized in session state
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    # CSS for modern, impressive UI
    st.markdown("""
    <style>
    /* Fullwidth container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 45rem;
    }
    
    /* Background gradients and animations */
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    .stApp {
        background-color: #4169E1; /* Royal Blue background */
    }
    
    /* Logo styling */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 70px;
        width: 70px;
        background-color: white;
        border-radius: 50%;
        margin: 0 auto 15px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Card styles */
    .login-card {
        background-color: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        max-width: 450px;
        margin: 0 auto;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .login-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.3);
    }
    
    /* Fancy button */
    .login-btn {
        background: linear-gradient(90deg, #6366f1, #06b6d4);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 20px;
        font-weight: bold;
        width: 100%;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 10px;
    }
    
    .login-btn:hover {
        background: linear-gradient(90deg, #06b6d4, #6366f1);
        transform: translateY(-3px);
        box-shadow: 0 10px 20px -5px rgba(99, 102, 241, 0.4);
    }
    
    /* Custom inputs */
    .login-input {
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        padding: 12px 15px 12px 45px;
        font-size: 16px;
        width: 100%;
        transition: all 0.2s;
        margin-bottom: 20px;
        background-color: white;
    }
    
    .login-input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
        outline: none;
    }
    
    /* Input icons */
    .input-container {
        position: relative;
        margin-bottom: 20px;
    }
    
    .input-icon {
        position: absolute;
        left: 15px;
        top: 50%;
        transform: translateY(-50%);
        color: #6366f1;
        font-size: 18px;
    }
    
    /* Divider */
    .divider {
        display: flex;
        align-items: center;
        margin: 20px 0;
        color: #9ca3af;
    }
    
    .divider::before, .divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background-color: #e5e7eb;
    }
    
    .divider span {
        padding: 0 1rem;
        font-size: 14px;
    }
    
    /* Social login */
    .social-login {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-bottom: 20px;
    }
    
    .social-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 50px;
        height: 50px;
        border-radius: 10px;
        color: white;
        text-decoration: none;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .social-btn:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.2);
    }

    .google { background-color: #DB4437; }
    .facebook { background-color: #4267B2; }
    .twitter { background-color: #1DA1F2; }
    
    /* Typing animation */
    @keyframes typing {
        from { width: 0 }
        to { width: 100% }
    }
    
    @keyframes blink {
        50% { border-color: transparent }
    }
    
    .typing {
        overflow: hidden;
        display: inline-block;
        border-right: 3px solid #6366f1;
        white-space: nowrap;
        margin: 0 auto;
        animation: typing 2.5s steps(40, end), blink .75s step-end infinite;
    }
    
    /* Make Streamlit elements look nicer */
    div[data-testid="stForm"] {
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        background-color: transparent !important;
    }
    
    button[kind="formSubmit"] {
        display: none !important;
    }
    
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #6366f1, #06b6d4);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 20px;
        font-weight: bold;
        width: 100%;
        margin-top: 10px;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:first-child:hover {
        background: linear-gradient(90deg, #06b6d4, #6366f1);
        transform: translateY(-3px);
        box-shadow: 0 10px 20px -5px rgba(99, 102, 241, 0.4);
    }
    
    .remember-forgot {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    /* Remember me styling */
    .remember-me {
        display: flex;
        align-items: center;
    }
    
    .remember-me label {
        color: #000000;
        font-size: 14px;
        margin-left: 5px;
        font-weight: 500;
    }
    
    .remember-me input {
        accent-color: #6366f1;
    }
    
    /* Right-to-left support for Arabic */
    .rtl {
        direction: rtl;
        text-align: right;
    }
    
    .rtl .input-icon {
        left: auto;
        right: 15px;
    }
    
    .rtl .login-input {
        padding: 12px 45px 12px 15px;
        text-align: right;
    }
    
    /* Hide Streamlit sidebar hamburger menu */
    .css-1rs6os {
        visibility: hidden;
    }
    
    /* Fix language dropdown styling */
    .language-select {
        margin-bottom: 25px;
    }
    
    .stSelectbox > div {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
    }
    
    .stSelectbox label {
        color: white;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    /* Fix for empty containers */
    .stApp div:empty {
        display: none !important;
    }
    
    div[data-baseweb="select"] ~ div:empty {
        display: none !important;
    }
    
    div[data-testid="stVerticalBlock"] > div:empty {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Hide empty whitespace in forms */
    form[data-testid="stForm"] > div:empty {
        display: none !important;
    }
    
    .stTextInput ~ div:empty {
        display: none !important;
    }
    
    /* Hide empty password fields and login page spacers */
    input[type="password"]:empty,
    .stTextInput:has(input:empty) ~ div:empty {
        opacity: 1 !important;
        height: auto !important;
        min-height: auto !important;
        padding: inherit !important;
        margin: 0 !important;
    }

    .login-form-container div:empty {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Handle language selection from URL params
    if 'lang' in st.query_params and st.query_params['lang'] in languages.values():
        # Set language from URL parameter
        st.session_state.language = st.query_params['lang']
    
    # Layout with columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # JavaScript for font awesome
        st.markdown('''
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        ''', unsafe_allow_html=True)
        
        # Logo and header
        st.markdown('''
        <div style="text-align: center; padding: 20px 0;">
            <div class="logo-container" style="margin: 0 auto 15px;">
                <i class="fas fa-graduation-cap" style="font-size: 40px; color: #6366f1;"></i>
            </div>
            <div style="background-color: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h1 style="margin: 0; color: #111827; font-weight: 800; font-size: 2.8rem; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">EduMate</h1>
                <div style="margin-top: 8px;">
                    <span style="color: #6366f1; font-weight: 600; font-size: 1.25rem;">AI-Powered Education</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Language dropdown selector at the top with modified container
        st.markdown("<div class='language-select' style='margin-bottom: 0;'>", unsafe_allow_html=True)
        lang_options = list(languages.keys())
        selected_lang_name = next((name for name, code in languages.items() if code == st.session_state.language), "English")
        selected_lang = st.selectbox(
            get_translation("select_language"), 
            options=lang_options,
            index=lang_options.index(selected_lang_name),
            key="language_selector",
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Update language when dropdown changes
        if selected_lang and languages[selected_lang] != st.session_state.language:
            st.session_state.language = languages[selected_lang]
            # Update URL parameter
            st.query_params["lang"] = st.session_state.language
            st.rerun()
        
        # Login card container
        st.markdown(f'<div class="login-card">', unsafe_allow_html=True)
        
        # Form header
        st.markdown(f'<h2 style="text-align: center; font-size: 1.5rem; margin-bottom: 25px; color: #111827; background-color: rgba(255, 255, 255, 0.9); padding: 10px; border-radius: 8px;">{get_translation("welcome")}</h2>', unsafe_allow_html=True)
        
        # Custom form
        with st.form("login_form", clear_on_submit=False):
            # Email input with Streamlit
            st.text_input(
                get_translation("email_or_username"),
                key="login_id",
                placeholder=get_translation("email_or_username")
            )
            
            # Password input with Streamlit
            password = st.text_input(
                get_translation("password"),
                type="password",
                key="password",
                placeholder=get_translation("password")
            )
            
            # Remember me and forgot password
            col1, col2 = st.columns([1, 1])
            with col1:
                remember = st.checkbox(get_translation("remember_me"), value=True)
            with col2:
                st.markdown(f'<div style="text-align: right;"><a href="#" style="color: #6366f1; text-decoration: none; font-size: 14px;">{get_translation("forgot_password")}</a></div>', unsafe_allow_html=True)
            
            # Submit button
            submit = st.form_submit_button(get_translation("sign_in"))
            
            # Process form submission
            if submit:
                # Use the login function from session state instead of importing
                login_id = st.session_state.login_id.strip() if 'login_id' in st.session_state else ""
                password = st.session_state.password if 'password' in st.session_state else ""
                
                if not login_id:
                    st.error(get_translation("please_enter_email_username"))
                    return
                
                if not password:
                    st.error(get_translation("please_enter_password"))
                    return
                
                # Call the login function from session state
                success, result = st.session_state.login_function(login_id, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.current_user = result
                    st.session_state.current_page = 'dashboard'
                    st.success(get_translation("login_successful"))
                    time.sleep(1)  # Small delay to show success message before redirect
                    st.rerun()
                else:
                    st.error(result)
            
            # Divider
            st.markdown(f'''
            <div class="divider">
                <span>{get_translation('or_continue_with').replace('_', ' ')}</span>
            </div>
            ''', unsafe_allow_html=True)
            
            # Social login
            st.markdown('''
            <div class="social-login">
                <div class="social-btn google">
                    <i class="fab fa-google"></i>
                </div>
                <div class="social-btn facebook">
                    <i class="fab fa-facebook-f"></i>
                </div>
                <div class="social-btn twitter">
                    <i class="fab fa-twitter"></i>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Close login card div
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add functional Create Account button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Single clear button for account creation
            if st.button(get_translation('create_account'), key="single_register_btn", use_container_width=True):
                st.session_state.current_page = 'register'
                st.rerun()
        
        # Footer
        st.markdown(f'''
        <div style="text-align: center; margin-top: 30px; color: white; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);">
            <p>&copy; 2025 EduMate. {get_translation('all_rights_reserved')}</p>
        </div>
        ''', unsafe_allow_html=True)
