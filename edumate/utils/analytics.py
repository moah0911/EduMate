import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import seaborn as sns
from typing import List, Dict
from .logger import log_system_event
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import json
# Download required NLTK data
try:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('vader_lexicon')
except Exception as e:
    log_system_event(f"Error downloading NLTK data: {str(e)}")

class Analytics:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.reports_dir = os.path.join(data_dir, 'reports')
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def generate_course_analytics(self, course_data, submissions_data):
        """Generate analytics for a course"""
        try:
            # Convert to pandas dataframes
            submissions_df = pd.DataFrame(submissions_data)
            
            # Basic statistics
            total_submissions = len(submissions_df)
            avg_score = submissions_df['score'].mean()
            submission_rate = len(submissions_df) / len(course_data['students']) * 100
            
            # Generate charts
            plt.figure(figsize=(10, 6))
            submissions_df['score'].hist(bins=10)
            plt.title(f"Score Distribution - {course_data['name']}")
            plt.xlabel('Score')
            plt.ylabel('Number of Submissions')
            
            # Save chart
            chart_path = os.path.join(self.reports_dir, f"course_{course_data['id']}_scores.png")
            plt.savefig(chart_path)
            plt.close()
            
            return {
                'course_id': course_data['id'],
                'course_name': course_data['name'],
                'total_submissions': total_submissions,
                'average_score': round(avg_score, 2),
                'submission_rate': round(submission_rate, 2),
                'chart_path': chart_path,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            log_system_event(f"Error generating course analytics: {str(e)}")
            return None

    def generate_student_progress_report(self, student_id, courses_data, submissions_data):
        """Generate a progress report for a student"""
        try:
            # Filter submissions for the student
            student_submissions = [s for s in submissions_data if s['student_id'] == student_id]
            submissions_df = pd.DataFrame(student_submissions)
            
            # Calculate statistics
            total_assignments = sum(len(c['assignments']) for c in courses_data)
            completed_assignments = len(student_submissions)
            completion_rate = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0
            average_score = submissions_df['score'].mean() if not submissions_df.empty else 0
            
            # Track progress over time
            submissions_df['submitted_at'] = pd.to_datetime(submissions_df['submitted_at'])
            submissions_df = submissions_df.sort_values('submitted_at')
            
            plt.figure(figsize=(10, 6))
            plt.plot(submissions_df['submitted_at'], submissions_df['score'])
            plt.title('Student Progress Over Time')
            plt.xlabel('Submission Date')
            plt.ylabel('Score')
            plt.xticks(rotation=45)
            
            # Save chart
            chart_path = os.path.join(self.reports_dir, f"student_{student_id}_progress.png")
            plt.savefig(chart_path)
            plt.close()
            
            return {
                'student_id': student_id,
                'total_assignments': total_assignments,
                'completed_assignments': completed_assignments,
                'completion_rate': round(completion_rate, 2),
                'average_score': round(average_score, 2),
                'chart_path': chart_path,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            log_system_event(f"Error generating student progress report: {str(e)}")
            return None

    def analyze_test_results(self, test_data, submissions):
        """Analyze test results and generate statistics"""
        try:
            results_df = pd.DataFrame(submissions)
            
            analysis = {
                'test_id': test_data['id'],
                'test_name': test_data['title'],
                'total_submissions': len(results_df),
                'statistics': {
                    'mean': results_df['score'].mean(),
                    'median': results_df['score'].median(),
                    'std': results_df['score'].std(),
                    'max': results_df['score'].max(),
                    'min': results_df['score'].min(),
                },
                'charts': {}
            }
            
            # Generate score distribution chart
            plt.figure(figsize=(10, 6))
            results_df['score'].hist(bins=10)
            plt.title(f"Score Distribution - {test_data['title']}")
            plt.xlabel('Score')
            plt.ylabel('Number of Students')
            
            chart_path = os.path.join(self.reports_dir, f"test_{test_data['id']}_scores.png")
            plt.savefig(chart_path)
            plt.close()
            
            analysis['charts']['distribution'] = chart_path
            
            # Generate CSV report
            csv_path = os.path.join(self.reports_dir, f"test_{test_data['id']}_results.csv")
            results_df.to_csv(csv_path, index=False)
            analysis['csv_report'] = csv_path
            
            return analysis
        except Exception as e:
            log_system_event(f"Error analyzing test results: {str(e)}")
            return None

    def generate_feedback_suggestions(self, submission_content, model_scores):
        """Generate AI feedback suggestions based on submission content and model scores"""
        try:
            # Tokenize content
            sentences = sent_tokenize(submission_content)
            words = word_tokenize(submission_content)
            
            # Analyze sentiment
            sia = SentimentIntensityAnalyzer()
            sentiment = sia.polarity_scores(submission_content)
            
            # Extract key phrases using TF-IDF
            vectorizer = TfidfVectorizer(max_features=10)
            tfidf_matrix = vectorizer.fit_transform([submission_content])
            key_terms = vectorizer.get_feature_names_out()
            
            # Analyze model scores
            model_analysis = {}
            for model, score in model_scores.items():
                model_analysis[model] = {
                    'score': score,
                    'confidence': np.random.uniform(0.7, 0.95)  # Simulated confidence
                }
            
            # Generate feedback suggestions
            suggestions = {
                'content_analysis': {
                    'length': len(words),
                    'sentence_count': len(sentences),
                    'key_terms': list(key_terms),
                    'sentiment': sentiment
                },
                'model_analysis': model_analysis,
                'improvement_areas': [],
                'strengths': []
            }
            
            # Add improvement suggestions
            if len(words) < 100:
                suggestions['improvement_areas'].append("Consider providing more detailed explanations")
            if sentiment['compound'] < 0:
                suggestions['improvement_areas'].append("Try to maintain a more positive or neutral tone")
            if len(sentences) < 5:
                suggestions['improvement_areas'].append("Structure your answer with more complete sentences")
            
            # Add strength recognitions
            if len(key_terms) > 5:
                suggestions['strengths'].append("Good use of subject-specific vocabulary")
            if len(words) > 200:
                suggestions['strengths'].append("Comprehensive response with good detail")
            if sentiment['compound'] > 0.5:
                suggestions['strengths'].append("Clear and positive communication style")
            
            return suggestions
        except Exception as e:
            log_system_event(f"Error generating feedback suggestions: {str(e)}")
            return None

    def analyze_attendance(self, course_id: int, date_range: tuple) -> Dict:
        """Analyze attendance patterns for a course"""
        try:
            start_date, end_date = date_range
            attendance_df = pd.DataFrame(self.load_attendance_data(course_id))
            
            if attendance_df.empty:
                return None
            
            # Filter by date range
            attendance_df['date'] = pd.to_datetime(attendance_df['date'])
            mask = (attendance_df['date'] >= start_date) & (attendance_df['date'] <= end_date)
            filtered_df = attendance_df.loc[mask]
            
            # Calculate statistics
            total_days = len(filtered_df['date'].unique())
            student_attendance = filtered_df.groupby('student_id')['present'].agg(['count', 'sum'])
            student_attendance['percentage'] = (student_attendance['sum'] / total_days) * 100
            
            # Generate charts
            plt.figure(figsize=(12, 6))
            student_attendance['percentage'].hist(bins=10)
            plt.title('Attendance Distribution')
            plt.xlabel('Attendance Percentage')
            plt.ylabel('Number of Students')
            
            chart_path = os.path.join(self.reports_dir, f"attendance_{course_id}.png")
            plt.savefig(chart_path)
            plt.close()
            
            return {
                'total_days': total_days,
                'average_attendance': student_attendance['percentage'].mean(),
                'chart_path': chart_path,
                'below_75_percent': len(student_attendance[student_attendance['percentage'] < 75]),
                'student_details': student_attendance.to_dict('index')
            }
        except Exception as e:
            log_system_event(f"Error analyzing attendance: {str(e)}")
            return None

    def generate_report_card(self, student_id: int, term: str) -> Dict:
        """Generate term report card with detailed analysis"""
        try:
            assessments = self.load_student_assessments(student_id, term)
            if not assessments:
                return None
            
            df = pd.DataFrame(assessments)
            
            # Calculate overall grades and statistics
            subject_grades = df.groupby('subject')['score'].agg([
                'count', 'mean', 'min', 'max'
            ]).round(2)
            
            # Calculate term GPA
            total_gpa = self.calculate_gpa(df['score'].tolist())
            
            # Generate performance chart
            plt.figure(figsize=(10, 6))
            df.boxplot(column='score', by='subject')
            plt.title('Subject-wise Performance Distribution')
            plt.xticks(rotation=45)
            
            chart_path = os.path.join(self.reports_dir, f"report_{student_id}_{term}.png")
            plt.savefig(chart_path)
            plt.close()
            
            return {
                'student_id': student_id,
                'term': term,
                'subject_grades': subject_grades.to_dict('index'),
                'overall_gpa': total_gpa,
                'chart_path': chart_path,
                'areas_of_improvement': self.identify_weak_areas(df),
                'remarks': self.generate_performance_remarks(df)
            }
        except Exception as e:
            log_system_event(f"Error generating report card: {str(e)}")
            return None

    def analyze_question_paper(self, questions: List[Dict]) -> Dict:
        """Analyze question paper for balance and coverage"""
        try:
            df = pd.DataFrame(questions)
            
            analysis = {
                'total_marks': df['marks'].sum(),
                'difficulty_distribution': df['difficulty'].value_counts().to_dict(),
                'topic_coverage': df['topic'].value_counts().to_dict(),
                'bloom_taxonomy': df['bloom_level'].value_counts().to_dict(),
                'time_estimate': self.estimate_completion_time(df),
                'suggestions': []
            }
            
            # Add suggestions for improvement
            if df['difficulty'].value_counts().std() > 0.5:
                analysis['suggestions'].append("Consider balancing difficulty levels")
            
            if len(df['topic'].unique()) < 3:
                analysis['suggestions'].append("Include questions from more topics")
            
            return analysis
        except Exception as e:
            log_system_event(f"Error analyzing question paper: {str(e)}")
            return None

    def generate_class_insights(self, course_id: int) -> Dict:
        """Generate comprehensive class insights"""
        try:
            # Load all relevant data
            attendance = self.load_attendance_data(course_id)
            assessments = self.load_course_assessments(course_id)
            homework = self.load_homework_data(course_id)
            
            insights = {
                'attendance_trends': self.analyze_attendance_trends(attendance),
                'performance_metrics': self.analyze_performance_metrics(assessments),
                'homework_completion': self.analyze_homework_completion(homework),
                'student_engagement': self.calculate_engagement_scores(attendance, assessments, homework),
                'recommendations': []
            }
            
            # Generate recommendations
            if insights['attendance_trends']['declining_students']:
                insights['recommendations'].append({
                    'type': 'attendance',
                    'message': 'Schedule parent meetings for students with declining attendance',
                    'affected_students': insights['attendance_trends']['declining_students']
                })
            
            if insights['performance_metrics']['struggling_students']:
                insights['recommendations'].append({
                    'type': 'performance',
                    'message': 'Consider remedial classes for struggling students',
                    'affected_students': insights['performance_metrics']['struggling_students']
                })
            
            return insights
        except Exception as e:
            log_system_event(f"Error generating class insights: {str(e)}")
            return None

    def generate_advanced_insights(self, data: Dict) -> Dict:
        """Generate advanced insights using machine learning"""
        insights = {
            'student_clusters': self.cluster_students(data['performance']),
            'performance_prediction': self.predict_performance(data['history']),
            'risk_analysis': self.analyze_risk_factors(data),
            'improvement_suggestions': self.generate_improvement_plan(data),
            'teaching_effectiveness': self.analyze_teaching_effectiveness(data),
            'resource_utilization': self.analyze_resource_usage(data)
        }
        return insights

    def analyze_student_behavior(self, student_data: Dict) -> Dict:
        """Analyze student behavior patterns"""
        return {
            'attendance_pattern': self.analyze_attendance_patterns(student_data),
            'submission_pattern': self.analyze_submission_patterns(student_data),
            'engagement_level': self.calculate_engagement_level(student_data),
            'interaction_analysis': self.analyze_class_interactions(student_data),
            'learning_style': self.identify_learning_style(student_data),
            'recommendations': self.generate_personalized_recommendations(student_data)
        }

    def generate_comprehensive_reports(self, class_data: Dict) -> Dict:
        """Generate comprehensive class reports"""
        reports = {
            'academic_performance': self.analyze_academic_performance(class_data),
            'behavioral_analysis': self.analyze_behavioral_patterns(class_data),
            'attendance_analysis': self.analyze_detailed_attendance(class_data),
            'improvement_trends': self.analyze_improvement_trends(class_data),
            'class_dynamics': self.analyze_class_dynamics(class_data),
            'resource_effectiveness': self.analyze_resource_effectiveness(class_data)
        }
        return reports

    def analyze_student_performance(self, student_id: int) -> Dict:
        """Deep analysis of student performance"""
        try:
            performance_data = self.load_student_data(student_id)
            
            analysis = {
                'overall_metrics': self.calculate_overall_metrics(performance_data),
                'subject_analysis': self.analyze_subject_wise_performance(performance_data),
                'trend_analysis': self.analyze_performance_trends(performance_data),
                'skill_gaps': self.identify_skill_gaps(performance_data),
                'recommendations': self.generate_student_recommendations(performance_data)
            }
            
            # Generate visualizations
            self.generate_performance_visualizations(performance_data, student_id)
            
            return analysis
        except Exception as e:
            log_system_event(f"Error analyzing student performance: {str(e)}")
            return None

    def analyze_class_performance(self, class_id: int) -> Dict:
        """Comprehensive class performance analysis"""
        try:
            class_data = self.load_class_data(class_id)
            
            analysis = {
                'class_metrics': self.calculate_class_metrics(class_data),
                'student_grouping': self.cluster_students_by_performance(class_data),
                'subject_insights': self.analyze_subject_performance(class_data),
                'improvement_areas': self.identify_class_improvement_areas(class_data),
                'teaching_strategy': self.suggest_teaching_strategies(class_data)
            }
            
            # Generate class reports
            self.generate_class_reports(class_data, class_id)
            
            return analysis
        except Exception as e:
            log_system_event(f"Error analyzing class performance: {str(e)}")
            return None

    def generate_teaching_insights(self, teacher_id: int) -> Dict:
        """Generate insights for teaching improvement"""
        try:
            teaching_data = self.load_teacher_data(teacher_id)
            
            insights = {
                'effectiveness': self.analyze_teaching_effectiveness(teaching_data),
                'student_engagement': self.analyze_student_engagement(teaching_data),
                'methodology_impact': self.analyze_teaching_methods(teaching_data),
                'resource_utilization': self.analyze_resource_usage(teaching_data),
                'recommendations': self.suggest_improvements(teaching_data)
            }
            
            # Generate visualization reports
            self.generate_teaching_reports(teaching_data, teacher_id)
            
            return insights
        except Exception as e:
            log_system_event(f"Error generating teaching insights: {str(e)}")
            return None

    def predict_student_outcomes(self, student_id: int) -> Dict:
        """Predict student outcomes using ML models"""
        try:
            historical_data = self.load_historical_data(student_id)
            current_data = self.load_current_data(student_id)
            
            predictions = {
                'academic_forecast': self.predict_academic_performance(historical_data, current_data),
                'risk_assessment': self.assess_dropout_risk(historical_data),
                'growth_trajectory': self.predict_learning_growth(historical_data),
                'intervention_needs': self.identify_intervention_needs(current_data),
                'success_probability': self.calculate_success_probability(historical_data)
            }
            
            return predictions
        except Exception as e:
            log_system_event(f"Error predicting student outcomes: {str(e)}")
            return None

    def analyze_board_exam_prep(self, class_id: str, board: str) -> Dict:
        """Analyze board exam preparation status"""
        students = self.get_class_students(class_id)
        syllabus = self.get_board_syllabus(board)
        
        analysis = {
            'completion_status': self.analyze_syllabus_completion(class_id, syllabus),
            'student_readiness': self.assess_student_readiness(students, syllabus),
            'weak_areas': self.identify_class_weak_areas(students, syllabus),
            'mock_test_analysis': self.analyze_mock_tests(class_id),
            'remedial_needs': self.identify_remedial_needs(students),
            'predicted_performance': self.predict_board_performance(students)
        }
        
        self.generate_board_prep_reports(analysis, class_id)
        return analysis

    def analyze_competitive_exam_prep(self, students: List[Dict], exam_type: str) -> Dict:
        """Analyze competitive exam preparation (JEE/NEET/etc)"""
        return {
            'subject_wise_analysis': self.analyze_subject_preparation(students, exam_type),
            'mock_test_performance': self.analyze_mock_test_trends(students, exam_type),
            'topic_wise_strength': self.analyze_topic_strength(students, exam_type),
            'time_management': self.analyze_time_management(students, exam_type),
            'recommendations': self.generate_prep_recommendations(students, exam_type)
        }

    def analyze_career_potential(self, student_id: int) -> Dict:
        """Analyze student's career potential using ML"""
        try:
            # Get student data
            academic_data = self.load_student_academic_data(student_id)
            skill_data = self.load_student_skill_data(student_id)
            interest_data = self.load_student_interest_data(student_id)
            
            # Prepare features
            features = self.prepare_career_features(
                academic_data,
                skill_data,
                interest_data
            )
            
            # Generate predictions
            predictions = {
                'suitable_fields': self.predict_suitable_fields(features),
                'success_probability': self.predict_success_probability(features),
                'skill_alignment': self.analyze_skill_alignment(features),
                'growth_potential': self.predict_growth_potential(features),
                'recommendations': self.generate_career_recommendations(features)
            }
            
            return predictions
        except Exception as e:
            log_system_event(f"Error analyzing career potential: {str(e)}")
            return None

    def predict_career_success(self, student_id: int, career_path: str) -> Dict:
        """Predict success probability in chosen career"""
        try:
            # Load historical data
            historical_data = self.load_career_success_data()
            
            # Prepare training data
            X = self.prepare_career_features(historical_data)
            y = historical_data['success_metrics']
            
            # Train model
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            model = RandomForestClassifier()
            model.fit(X_train, y_train)
            
            # Generate predictions
            student_features = self.get_student_career_features(student_id, career_path)
            prediction = model.predict_proba([student_features])[0]
            
            return {
                'success_probability': prediction[1],
                'key_factors': self.identify_key_success_factors(model, student_features),
                'areas_for_improvement': self.identify_improvement_areas(model, student_features),
                'recommended_actions': self.generate_action_recommendations(prediction[1])
            }
            
        except Exception as e:
            log_system_event(f"Error predicting career success: {str(e)}")
            return None

    def analyze_institution_performance(self, institution_id: int, institution_type: str) -> Dict:
        """Analyze performance metrics for different institution types"""
        try:
            if institution_type == "coaching":
                return self.analyze_coaching_center(institution_id)
            elif institution_type == "college":
                return self.analyze_college(institution_id)
            elif institution_type == "university":
                return self.analyze_university(institution_id)
            else:
                return self.analyze_school(institution_id)
        except Exception as e:
            log_system_event(f"Error analyzing institution performance: {str(e)}")
            return None

    def analyze_coaching_center(self, center_id: int) -> Dict:
        """Analyze coaching center performance"""
        data = self.load_coaching_data(center_id)
        return {
            'batch_performance': self.analyze_batch_metrics(data),
            'teacher_effectiveness': self.analyze_teacher_impact(data),
            'resource_utilization': self.analyze_resource_usage(data),
            'student_progress': self.analyze_student_improvement(data),
            'cost_efficiency': self.analyze_operational_efficiency(data),
            'recommendations': self.generate_coaching_recommendations(data)
        }

    def analyze_college(self, college_id: int) -> Dict:
        """Analyze college performance"""
        data = self.load_college_data(college_id)
        return {
            'academic_metrics': self.analyze_academic_performance(data),
            'research_output': self.analyze_research_metrics(data),
            'placement_stats': self.analyze_placement_data(data),
            'faculty_performance': self.analyze_faculty_metrics(data),
            'department_analysis': self.analyze_department_performance(data),
            'recommendations': self.generate_college_recommendations(data)
        }

    def analyze_university(self, university_id: int) -> Dict:
        """Analyze university performance"""
        data = self.load_university_data(university_id)
        return {
            'academic_standing': self.analyze_academic_rankings(data),
            'research_impact': self.analyze_research_impact(data),
            'student_outcomes': self.analyze_student_success(data),
            'faculty_achievements': self.analyze_faculty_contributions(data),
            'global_presence': self.analyze_international_metrics(data),
            'recommendations': self.generate_university_recommendations(data)
        }

    def load_attendance_data(self, course_id: int) -> pd.DataFrame:
        """Load attendance data from database/file"""
        try:
            attendance_file = os.path.join(self.data_dir, f'attendance_{course_id}.json')
            if os.path.exists(attendance_file):
                with open(attendance_file, 'r') as f:
                    data = json.load(f)
                return pd.DataFrame(data)
            return pd.DataFrame()
        except Exception as e:
            log_system_event(f"Error loading attendance data: {str(e)}")
            return pd.DataFrame()

    def load_coaching_data(self, center_id: int) -> Dict:
        """Load coaching center data"""
        try:
            data_file = os.path.join(self.data_dir, f'coaching_{center_id}.json')
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            log_system_event(f"Error loading coaching data: {str(e)}")
            return {}

    def load_college_data(self, college_id: int) -> Dict:
        """Load college data"""
        try:
            data_file = os.path.join(self.data_dir, f'college_{college_id}.json')
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            log_system_event(f"Error loading college data: {str(e)}")
            return {}

    def load_university_data(self, university_id: int) -> Dict:
        """Load university data"""
        try:
            data_file = os.path.join(self.data_dir, f'university_{university_id}.json')
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            log_system_event(f"Error loading university data: {str(e)}")
            return {}
