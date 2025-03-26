# EduMate - AI-Powered Education Platform

EduMate is a simplified educational platform built with Streamlit that helps teachers manage courses, assignments, and student submissions.

## Features

- **User Authentication**: Register and login as a teacher or student
- **Course Management**: Create courses, enroll students, and manage course content
- **Assignment Management**: Create assignments, submit solutions, and grade submissions
- **User Dashboard**: View statistics and manage your courses and assignments

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone this repository or download the files
2. Install the required packages:

```bash
pip install streamlit pandas
```

### Running the Application

Run the application with the following command:

```bash
streamlit run streamlit_app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Usage

### Demo Accounts

The application comes with pre-configured demo accounts:

- **Teacher Account**:
  - Email: teacher@edumate.com
  - Password: teacher123

- **Student Account**:
  - Email: student@edumate.com
  - Password: student123

### For Teachers

1. **Login** with your teacher account
2. **Create Courses** from your dashboard
3. **Add Assignments** to your courses
4. **View and Grade Submissions** from students

### For Students

1. **Login** with your student account
2. **Enroll in Courses** from your dashboard
3. **View Assignments** in your enrolled courses
4. **Submit Solutions** to assignments
5. **View Feedback** and grades from teachers

## Data Storage

All data is stored locally in JSON files in the `data` directory:

- `users.json`: User account information
- `courses.json`: Course details and enrollments
- `assignments.json`: Assignment details
- `submissions.json`: Student submissions and grades

## Future Enhancements

- AI-powered automatic grading for assignments
- File upload for assignments and submissions
- Rich text editor for better content creation
- Analytics dashboard for tracking student progress
- Notification system for new assignments and grades

## License

This project is licensed under the MIT License - see the LICENSE file for details. 