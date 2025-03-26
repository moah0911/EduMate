import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from typing import Dict, List
import joblib
from .logger import log_system_event
import os
import json

class CareerPlanner:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.career_data = self.load_career_data()
        self.skill_matrices = self.load_skill_matrices()
        self.course_data = self.load_course_recommendations()

    def load_career_data(self) -> Dict:
        """Load career datasets"""
        try:
            career_file = os.path.join(self.data_dir, 'career_data.json')
            if os.path.exists(career_file):
                with open(career_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            log_system_event(f"Error loading career data: {str(e)}")
            return {}

    def load_skill_matrices(self) -> Dict:
        """Load skill requirement matrices"""
        try:
            skills_file = os.path.join(self.data_dir, 'skill_matrices.json')
            if os.path.exists(skills_file):
                with open(skills_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            log_system_event(f"Error loading skill matrices: {str(e)}")
            return {}

    def load_course_recommendations(self) -> Dict:
        """Load course recommendation data"""
        try:
            courses_file = os.path.join(self.data_dir, 'course_recommendations.json')
            if os.path.exists(courses_file):
                with open(courses_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            log_system_event(f"Error loading course recommendations: {str(e)}")
            return {}

    def get_student_data(self, student_id: int) -> Dict:
        """Get comprehensive student data"""
        try:
            student_file = os.path.join(self.data_dir, f'student_{student_id}.json')
            if os.path.exists(student_file):
                with open(student_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            log_system_event(f"Error loading student data: {str(e)}")
            return {}

    def analyze_student_profile(self, student_id: int) -> Dict:
        """Analyze student's academic performance, interests, and aptitude"""
        try:
            profile = {
                'academic': self.analyze_academic_history(student_id),
                'interests': self.analyze_interest_areas(student_id),
                'aptitude': self.assess_aptitude(student_id),
                'skills': self.evaluate_skills(student_id),
                'personality': self.analyze_personality_traits(student_id)
            }
            return self.generate_career_matches(profile)
        except Exception as e:
            log_system_event(f"Error analyzing student profile: {str(e)}")
            return None

    def generate_career_paths(self, student_id: int) -> Dict:
        """Generate AI-powered career path recommendations"""
        try:
            student_data = self.get_student_data(student_id)
            return {
                'recommended_careers': self.get_career_recommendations(student_data),
                'skill_gaps': self.identify_skill_gaps(student_data),
                'required_qualifications': self.get_required_qualifications(student_data),
                'industry_insights': self.get_industry_insights(student_data),
                'salary_projections': self.calculate_salary_projections(student_data),
                'career_roadmap': self.create_career_roadmap(student_data)
            }
        except Exception as e:
            log_system_event(f"Error generating career paths: {str(e)}")
            return None

    def provide_career_guidance(self, student_id: int) -> Dict:
        """Provide personalized career guidance"""
        return {
            'immediate_steps': self.suggest_immediate_actions(student_id),
            'long_term_plan': self.create_long_term_plan(student_id),
            'skill_development': self.suggest_skill_development(student_id),
            'education_path': self.recommend_education_path(student_id),
            'internship_opportunities': self.find_internship_matches(student_id),
            'mentorship_suggestions': self.suggest_mentors(student_id)
        }

    def analyze_market_trends(self, career_path: str) -> Dict:
        """Analyze job market trends for career paths"""
        return {
            'job_growth': self.analyze_job_growth(career_path),
            'salary_trends': self.analyze_salary_trends(career_path),
            'skill_demands': self.analyze_skill_demands(career_path),
            'industry_changes': self.analyze_industry_changes(career_path),
            'geographical_demand': self.analyze_geographical_demand(career_path),
            'future_outlook': self.predict_future_outlook(career_path)
        }

    def generate_preparation_plan(self, student_id: int, career_path: str) -> Dict:
        """Generate detailed preparation plan"""
        return {
            'academic_preparation': self.plan_academic_path(student_id, career_path),
            'skill_development': self.plan_skill_development(student_id, career_path),
            'certifications': self.recommend_certifications(career_path),
            'experience_needed': self.suggest_experience_building(career_path),
            'timeline': self.create_preparation_timeline(student_id, career_path),
            'resources': self.recommend_learning_resources(career_path)
        }
