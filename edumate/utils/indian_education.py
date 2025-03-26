import pandas as pd
from typing import Dict, List, Optional
from .logger import log_system_event
import json
from datetime import datetime
from pathlib import Path

class IndianEducation:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.board_data = self.load_board_data()
        self.competitive_exams = self.load_competitive_exams()

    def manage_board_curriculum(self, board: str, class_level: str) -> Dict:
        """Manage different board curriculums (CBSE/ICSE/State)"""
        return {
            'syllabus': self.get_board_syllabus(board, class_level),
            'practice_papers': self.get_practice_papers(board, class_level),
            'sample_papers': self.get_sample_papers(board, class_level),
            'previous_papers': self.get_previous_papers(board, class_level),
            'marking_scheme': self.get_marking_scheme(board, class_level)
        }

    def manage_competitive_prep(self, exam_type: str, student_id: int) -> Dict:
        """Manage competitive exam preparation"""
        return {
            'study_plan': self.create_study_plan(exam_type, student_id),
            'mock_tests': self.schedule_mock_tests(exam_type, student_id),
            'performance_tracking': self.track_exam_performance(exam_type, student_id),
            'weak_areas': self.identify_weak_areas(exam_type, student_id),
            'recommendations': self.generate_recommendations(exam_type, student_id)
        }

    def manage_practical_labs(self, class_id: str, subject: str) -> Dict:
        """Manage practical laboratory sessions"""
        return {
            'experiments': self.get_practical_experiments(class_id, subject),
            'materials': self.manage_lab_materials(class_id, subject),
            'assessment': self.assess_practical_skills(class_id, subject),
            'safety': self.manage_lab_safety(class_id, subject),
            'reports': self.generate_practical_reports(class_id, subject)
        }

    def generate_board_reports(self, student_id: int, board: str) -> Dict:
        """Generate comprehensive board exam reports"""
        return {
            'academic_progress': self.track_academic_progress(student_id),
            'test_performance': self.analyze_test_performance(student_id),
            'attendance_record': self.get_attendance_record(student_id),
            'behavior_assessment': self.assess_behavior(student_id),
            'parent_feedback': self.get_parent_feedback(student_id)
        }

    def manage_institution_type(self, institution_type: str, institution_id: int) -> Dict:
        """Manage different types of educational institutions"""
        if institution_type == "school":
            return self.manage_school(institution_id)
        elif institution_type == "coaching":
            return self.manage_coaching_center(institution_id)
        elif institution_type == "college":
            return self.manage_college(institution_id)
        elif institution_type == "university":
            return self.manage_university(institution_id)

    def manage_coaching_center(self, center_id: int) -> Dict:
        """Manage coaching center operations with limited resources"""
        return {
            'batch_management': {
                'large_batches': self.organize_large_batches(center_id),
                'rotation_schedule': self.create_teacher_rotation(center_id),
                'student_groups': self.manage_student_groups(center_id),
                'peer_learning': self.setup_peer_learning_groups(center_id)
            },
            'resource_optimization': {
                'teacher_allocation': self.optimize_teacher_allocation(center_id),
                'classroom_utilization': self.maximize_space_usage(center_id),
                'digital_resources': self.manage_shared_resources(center_id),
                'recorded_lectures': self.manage_recorded_content(center_id)
            },
            'student_support': {
                'doubt_clearing': self.manage_doubt_sessions(center_id),
                'study_materials': self.distribute_study_materials(center_id),
                'online_support': self.setup_online_support(center_id),
                'practice_tests': self.manage_practice_tests(center_id)
            },
            'quality_assurance': {
                'performance_tracking': self.track_batch_performance(center_id),
                'feedback_system': self.manage_student_feedback(center_id),
                'improvement_plans': self.generate_improvement_plans(center_id)
            }
        }

    def manage_college(self, college_id: int) -> Dict:
        """Manage college-specific operations"""
        return {
            'academic_programs': {
                'departments': self.manage_departments(college_id),
                'courses': self.manage_college_courses(college_id),
                'electives': self.manage_elective_subjects(college_id),
                'projects': self.manage_student_projects(college_id)
            },
            'faculty_management': {
                'workload': self.manage_faculty_workload(college_id),
                'research': self.track_research_activities(college_id),
                'development': self.plan_faculty_development(college_id)
            },
            'infrastructure': {
                'labs': self.manage_laboratories(college_id),
                'library': self.manage_library_system(college_id),
                'facilities': self.manage_campus_facilities(college_id)
            },
            'industry_connect': {
                'placements': self.manage_placements(college_id),
                'internships': self.coordinate_internships(college_id),
                'industry_projects': self.manage_industry_projects(college_id)
            }
        }

    def manage_university(self, university_id: int) -> Dict:
        """Manage university-level operations"""
        return {
            'academic_affairs': {
                'programs': self.manage_university_programs(university_id),
                'research': self.manage_research_programs(university_id),
                'collaborations': self.manage_academic_collaborations(university_id),
                'grants': self.manage_research_grants(university_id)
            },
            'administrative': {
                'departments': self.manage_university_departments(university_id),
                'faculty': self.manage_faculty_affairs(university_id),
                'admissions': self.manage_admissions_process(university_id)
            },
            'student_services': {
                'housing': self.manage_student_housing(university_id),
                'support': self.provide_student_services(university_id),
                'activities': self.manage_student_activities(university_id)
            },
            'evaluation': {
                'examination': self.manage_examination_system(university_id),
                'grading': self.manage_grading_system(university_id),
                'certifications': self.manage_certification_process(university_id)
            }
        }

    def manage_faculty_resources(self, institution_id: int, faculty_count: int) -> Dict:
        """Manage resources for institutions with limited faculty"""
        return {
            'workload_distribution': self.optimize_faculty_workload(institution_id, faculty_count),
            'teaching_aids': self.provide_teaching_support(institution_id),
            'digital_resources': self.manage_digital_content(institution_id),
            'automation': self.automate_administrative_tasks(institution_id)
        }

class IndianEducationSystem:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / 'data' / 'education'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._init_data()

    def _init_data(self):
        """Initialize education system data if not exists"""
        exam_calendar_file = self.data_dir / 'exam_calendar.json'
        if not exam_calendar_file.exists():
            default_calendar = {
                "entrance_exams": [
                    {
                        "name": "JEE Main",
                        "dates": ["January", "April"],
                        "description": "Joint Entrance Examination for Engineering"
                    },
                    {
                        "name": "NEET",
                        "dates": ["May"],
                        "description": "National Eligibility cum Entrance Test for Medical"
                    }
                ],
                "board_exams": [
                    {
                        "name": "CBSE 10th",
                        "dates": ["February-March"],
                        "description": "Central Board Secondary Education Class 10"
                    },
                    {
                        "name": "CBSE 12th",
                        "dates": ["February-March"],
                        "description": "Central Board Secondary Education Class 12"
                    }
                ]
            }
            with open(exam_calendar_file, 'w') as f:
                json.dump(default_calendar, f, indent=4)

    def get_exam_calendar(self, year):
        """Get the exam calendar for a specific year"""
        try:
            with open(self.data_dir / 'exam_calendar.json', 'r') as f:
                calendar = json.load(f)
            return calendar
        except Exception as e:
            print(f"Error loading exam calendar: {e}")
            return None

    def get_board_info(self, board_name):
        """Get information about a specific education board"""
        boards = {
            "CBSE": {
                "name": "Central Board of Secondary Education",
                "website": "http://cbse.nic.in",
                "pattern": "National curriculum focused on comprehensive learning"
            },
            "ICSE": {
                "name": "Indian Certificate of Secondary Education",
                "website": "http://cisce.org",
                "pattern": "Emphasis on English language and broad-based knowledge"
            }
        }
        return boards.get(board_name, {})

    def get_stream_info(self, stream):
        """Get information about academic streams"""
        streams = {
            "Science (PCM)": {
                "subjects": ["Physics", "Chemistry", "Mathematics"],
                "career_options": ["Engineering", "Architecture", "Research"],
                "entrance_exams": ["JEE", "BITSAT"]
            },
            "Science (PCB)": {
                "subjects": ["Physics", "Chemistry", "Biology"],
                "career_options": ["Medical", "Biotechnology", "Research"],
                "entrance_exams": ["NEET", "AIIMS"]
            }
        }
        return streams.get(stream, {})

    def get_board_details(self, board_name):
        """Get detailed information about a specific education board"""
        board_details = {
            "CBSE": {
                "name": "Central Board of Secondary Education",
                "website": "http://cbse.nic.in",
                "pattern": "National curriculum focused on comprehensive learning",
                "headquarters": "New Delhi",
                "subjects_10th": ["Mathematics", "Science", "Social Science", "English", "Second Language"],
                "subjects_12th": {
                    "Science": ["Physics", "Chemistry", "Mathematics/Biology", "English", "Optional Subject"],
                    "Commerce": ["Accountancy", "Business Studies", "Economics", "English", "Optional Subject"],
                    "Arts": ["History", "Political Science", "Geography/Psychology", "English", "Optional Subject"]
                },
                "evaluation": {
                    "term_system": "Two terms per academic year",
                    "grading": "Marks and grades both provided",
                    "passing_criteria": "33% in each subject and overall"
                },
                "special_features": [
                    "Continuous and Comprehensive Evaluation (CCE)",
                    "NCERT curriculum",
                    "Focus on practical knowledge",
                    "Regular teacher training programs"
                ]
            },
            "ICSE": {
                "name": "Indian Certificate of Secondary Education",
                "website": "http://cisce.org",
                "pattern": "Emphasis on English language and broad-based knowledge",
                "headquarters": "New Delhi",
                "subjects_10th": ["English", "Second Language", "Mathematics", "Science", "Social Studies", "Computer Applications"],
                "subjects_12th": {
                    "Science": ["Physics", "Chemistry", "Mathematics/Biology", "English", "Optional Subject"],
                    "Commerce": ["Accounts", "Commerce", "Economics", "English", "Optional Subject"],
                    "Arts": ["Literature", "History", "Geography", "English", "Optional Subject"]
                },
                "evaluation": {
                    "term_system": "Annual examination system",
                    "grading": "Primarily percentage-based",
                    "passing_criteria": "35% in each subject and overall"
                },
                "special_features": [
                    "Strong emphasis on English language",
                    "Project-based learning",
                    "Comprehensive curriculum",
                    "International recognition"
                ]
            },
            "State Board": {
                "name": "State Board of Education",
                "website": "Varies by state",
                "pattern": "State-specific curriculum and evaluation",
                "headquarters": "State capital",
                "subjects_10th": ["First Language", "English", "Mathematics", "Science", "Social Science"],
                "subjects_12th": {
                    "Science": ["Physics", "Chemistry", "Mathematics/Biology", "English", "Optional Subject"],
                    "Commerce": ["Accountancy", "Business Studies", "Economics", "English", "Optional Subject"],
                    "Arts": ["History", "Political Science", "Geography", "English", "Optional Subject"]
                },
                "evaluation": {
                    "term_system": "Varies by state",
                    "grading": "Usually percentage-based",
                    "passing_criteria": "Varies by state (typically 35%)"
                },
                "special_features": [
                    "Regional language focus",
                    "State-specific content",
                    "Affordable education",
                    "Local context integration"
                ]
            }
        }
        return board_details.get(board_name, {})

    def get_subject_details(self, board_name, stream, class_level):
        """Get detailed subject information for a specific board, stream and class"""
        board_details = self.get_board_details(board_name)
        if not board_details:
            return {}
        
        if class_level == "10th":
            return {"subjects": board_details.get("subjects_10th", [])}
        elif class_level == "12th":
            streams = board_details.get("subjects_12th", {})
            return {"subjects": streams.get(stream, [])}
        return {}

    def get_evaluation_system(self, board_name):
        """Get evaluation system details for a specific board"""
        board_details = self.get_board_details(board_name)
        return board_details.get("evaluation", {})

    def get_board_features(self, board_name):
        """Get special features of a specific board"""
        board_details = self.get_board_details(board_name)
        return board_details.get("special_features", [])

    def get_education_paths(self):
        """Get comprehensive information about Indian education pathways"""
        education_paths = {
            'school_education': {
                'Primary Education': {
                    'description': 'Classes 1-5 (ages 6-11) focusing on foundational skills in language, mathematics, environmental studies, arts, and physical education.',
                    'age_range': '6-11 years',
                    'curriculum_options': ['CBSE', 'ICSE', 'State Board', 'International Boards (IB, Cambridge)']
                },
                'Middle School': {
                    'description': 'Classes 6-8 (ages 11-14) introducing more subjects and deeper concepts while continuing to build on foundational knowledge.',
                    'age_range': '11-14 years',
                    'curriculum_options': ['CBSE', 'ICSE', 'State Board', 'International Boards (IB, Cambridge)']
                },
                'Secondary Education': {
                    'description': 'Classes 9-10 (ages 14-16) preparing students for board examinations and helping them choose future academic streams.',
                    'age_range': '14-16 years',
                    'curriculum_options': ['CBSE', 'ICSE', 'State Board', 'International Boards (IB, Cambridge)']
                },
                'Higher Secondary': {
                    'description': 'Classes 11-12 (ages 16-18) with specialized streams (Science, Commerce, Arts) preparing students for higher education.',
                    'age_range': '16-18 years',
                    'curriculum_options': ['CBSE', 'ICSE', 'State Board', 'International Boards (IB, Cambridge)'],
                    'streams': ['Science (PCM)', 'Science (PCB)', 'Commerce', 'Arts/Humanities']
                }
            },
            'higher_education': {
                'Undergraduate': {
                    'description': 'Bachelor\'s degree programs across various disciplines, typically 3-4 years in duration.',
                    'duration': '3-4 years',
                    'fields': [
                        'Engineering (B.Tech/B.E.)', 
                        'Medicine (MBBS)', 
                        'Commerce (B.Com)', 
                        'Science (B.Sc)', 
                        'Arts (B.A.)', 
                        'Law (LLB)',
                        'Architecture (B.Arch)',
                        'Design (B.Des)',
                        'Computer Applications (BCA)'
                    ]
                },
                'Postgraduate': {
                    'description': 'Master\'s degree programs offering specialized knowledge in chosen fields, typically 2 years in duration.',
                    'duration': '1-2 years',
                    'fields': [
                        'Engineering (M.Tech/M.E.)', 
                        'Medicine (MD/MS)', 
                        'Commerce (M.Com)', 
                        'Science (M.Sc)', 
                        'Arts (M.A.)', 
                        'Business Administration (MBA)',
                        'Computer Applications (MCA)'
                    ]
                },
                'Doctoral': {
                    'description': 'Ph.D. programs focusing on research and advanced study in specialized areas.',
                    'duration': '3-5 years',
                    'fields': ['All academic disciplines']
                }
            },
            'professional_courses': [
                {
                    'name': 'Engineering',
                    'description': 'Programs focusing on various engineering disciplines.',
                    'duration': '4 years (B.Tech/B.E.)',
                    'eligibility': '10+2 with PCM, entrance exams like JEE Main/Advanced',
                    'career_prospects': ['Software Engineer', 'Mechanical Engineer', 'Civil Engineer', 'Electronics Engineer']
                },
                {
                    'name': 'Medicine',
                    'description': 'Programs for medical professionals including doctors, dentists, and more.',
                    'duration': '5.5 years (MBBS including internship)',
                    'eligibility': '10+2 with PCB, entrance exam NEET',
                    'career_prospects': ['Doctor', 'Surgeon', 'Medical Researcher', 'Public Health Professional']
                },
                {
                    'name': 'Law',
                    'description': 'Programs for legal education and practice.',
                    'duration': '3 years (LLB) or 5 years (integrated BA LLB)',
                    'eligibility': 'Bachelor\'s degree or 10+2, entrance exams like CLAT',
                    'career_prospects': ['Lawyer', 'Legal Consultant', 'Judge', 'Corporate Legal Advisor']
                },
                {
                    'name': 'Management',
                    'description': 'Programs focusing on business administration and management.',
                    'duration': '2 years (MBA)',
                    'eligibility': 'Bachelor\'s degree, entrance exams like CAT, XAT, MAT',
                    'career_prospects': ['Business Manager', 'Marketing Executive', 'Finance Manager', 'HR Professional']
                },
                {
                    'name': 'Chartered Accountancy',
                    'description': 'Professional course for accounting and finance.',
                    'duration': '3-4 years (including articleship)',
                    'eligibility': '10+2 or Bachelor\'s degree, CA Foundation exam',
                    'career_prospects': ['Chartered Accountant', 'Financial Analyst', 'Tax Consultant', 'Auditor']
                }
            ],
            'entrance_exams': [
                {
                    'name': 'JEE Main',
                    'type': 'Engineering Entrance',
                    'level': 'National',
                    'frequency': 'Multiple sessions per year',
                    'description': 'Joint Entrance Examination for admission to NITs, IIITs, and other engineering colleges.',
                    'eligibility': '10+2 with PCM',
                    'website': 'https://jeemain.nta.nic.in/'
                },
                {
                    'name': 'JEE Advanced',
                    'type': 'Engineering Entrance',
                    'level': 'National',
                    'frequency': 'Once a year',
                    'description': 'Entrance exam for admission to IITs, conducted for top rankers of JEE Main.',
                    'eligibility': 'Qualification in JEE Main',
                    'website': 'https://jeeadv.ac.in/'
                },
                {
                    'name': 'NEET',
                    'type': 'Medical Entrance',
                    'level': 'National',
                    'frequency': 'Once a year',
                    'description': 'National Eligibility cum Entrance Test for admission to medical colleges.',
                    'eligibility': '10+2 with PCB',
                    'website': 'https://neet.nta.nic.in/'
                },
                {
                    'name': 'CLAT',
                    'type': 'Law Entrance',
                    'level': 'National',
                    'frequency': 'Once a year',
                    'description': 'Common Law Admission Test for admission to National Law Universities.',
                    'eligibility': '10+2 or Bachelor\'s degree',
                    'website': 'https://consortiumofnlus.ac.in/'
                },
                {
                    'name': 'CAT',
                    'type': 'Management Entrance',
                    'level': 'National',
                    'frequency': 'Once a year',
                    'description': 'Common Admission Test for admission to IIMs and other management institutes.',
                    'eligibility': 'Bachelor\'s degree',
                    'website': 'https://iimcat.ac.in/'
                }
            ]
        }
        
        return education_paths
