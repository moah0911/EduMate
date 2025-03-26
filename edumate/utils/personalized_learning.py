"""
Personalized Learning Path module for EduMate.

This module provides functionality to create and manage personalized learning paths
based on student performance and learning style.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os
import json
from datetime import datetime

class PersonalizedLearningPath:
    """Class to manage personalized learning paths for students."""
    
    def __init__(self, data_dir="data/learning_paths"):
        """Initialize the PersonalizedLearningPath class.
        
        Args:
            data_dir (str): Directory to store learning path data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Create subdirectories
        self.models_dir = os.path.join(data_dir, "models")
        self.paths_dir = os.path.join(data_dir, "paths")
        self.analytics_dir = os.path.join(data_dir, "analytics")
        
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.paths_dir, exist_ok=True)
        os.makedirs(self.analytics_dir, exist_ok=True)
        
        # Initialize default learning styles
        self.learning_styles = {
            "visual": "Learns best through images, diagrams, and visual aids",
            "auditory": "Learns best through listening and verbal instructions",
            "reading/writing": "Learns best through reading and writing text",
            "kinesthetic": "Learns best through hands-on activities and practice"
        }
        
        # Initialize default difficulty levels
        self.difficulty_levels = ["beginner", "intermediate", "advanced", "expert"]
    
    def analyze_student_performance(self, student_id, course_data):
        """Analyze student performance to identify strengths and weaknesses.
        
        Args:
            student_id (str): Unique identifier for the student
            course_data (dict): Dictionary containing course performance data
            
        Returns:
            dict: Analysis results with strengths, weaknesses, and recommendations
        """
        # Extract performance metrics
        assignments = course_data.get("assignments", [])
        quizzes = course_data.get("quizzes", [])
        participation = course_data.get("participation", [])
        
        # Calculate average scores
        avg_assignment_score = np.mean([a.get("score", 0) for a in assignments]) if assignments else 0
        avg_quiz_score = np.mean([q.get("score", 0) for q in quizzes]) if quizzes else 0
        avg_participation = np.mean([p.get("score", 0) for p in participation]) if participation else 0
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if avg_assignment_score >= 80:
            strengths.append("Strong performance on assignments")
        elif avg_assignment_score < 60:
            weaknesses.append("Needs improvement on assignments")
            
        if avg_quiz_score >= 80:
            strengths.append("Strong quiz performance")
        elif avg_quiz_score < 60:
            weaknesses.append("Needs improvement on quizzes")
            
        if avg_participation >= 80:
            strengths.append("Active class participation")
        elif avg_participation < 60:
            weaknesses.append("Low class participation")
        
        # Analyze topic-specific performance
        topic_performance = {}
        for assignment in assignments:
            topics = assignment.get("topics", [])
            score = assignment.get("score", 0)
            for topic in topics:
                if topic not in topic_performance:
                    topic_performance[topic] = []
                topic_performance[topic].append(score)
        
        for quiz in quizzes:
            topics = quiz.get("topics", [])
            score = quiz.get("score", 0)
            for topic in topics:
                if topic not in topic_performance:
                    topic_performance[topic] = []
                topic_performance[topic].append(score)
        
        # Calculate average score per topic
        topic_averages = {topic: np.mean(scores) for topic, scores in topic_performance.items()}
        
        # Identify strong and weak topics
        strong_topics = [topic for topic, avg in topic_averages.items() if avg >= 80]
        weak_topics = [topic for topic, avg in topic_averages.items() if avg < 60]
        
        # Add topic-specific strengths and weaknesses
        if strong_topics:
            strengths.append(f"Strong understanding of: {', '.join(strong_topics)}")
        if weak_topics:
            weaknesses.append(f"Needs improvement on: {', '.join(weak_topics)}")
        
        # Generate recommendations
        recommendations = []
        if weak_topics:
            for topic in weak_topics:
                recommendations.append(f"Focus on improving {topic} through additional practice")
        
        if avg_participation < 60:
            recommendations.append("Increase class participation and engagement")
        
        # Save analysis results
        analysis_results = {
            "student_id": student_id,
            "timestamp": datetime.now().isoformat(),
            "average_scores": {
                "assignments": avg_assignment_score,
                "quizzes": avg_quiz_score,
                "participation": avg_participation
            },
            "topic_performance": topic_averages,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations
        }
        
        # Save analysis to file
        analysis_file = os.path.join(self.analytics_dir, f"{student_id}_analysis.json")
        with open(analysis_file, 'w') as f:
            json.dump(analysis_results, f, indent=4)
        
        return analysis_results
    
    def create_learning_path(self, student_id, course_id, analysis_results=None):
        """Create a personalized learning path based on student performance analysis.
        
        Args:
            student_id (str): Unique identifier for the student
            course_id (str): Unique identifier for the course
            analysis_results (dict, optional): Results from performance analysis
            
        Returns:
            dict: Personalized learning path
        """
        # If analysis results not provided, try to load from file
        if analysis_results is None:
            analysis_file = os.path.join(self.analytics_dir, f"{student_id}_analysis.json")
            if os.path.exists(analysis_file):
                with open(analysis_file, 'r') as f:
                    analysis_results = json.load(f)
            else:
                return {"error": "No analysis results available for this student"}
        
        # Get student's learning style (this would come from a questionnaire or previous data)
        # For now, we'll randomly assign one
        learning_style = np.random.choice(list(self.learning_styles.keys()))
        
        # Create personalized path
        learning_path = {
            "student_id": student_id,
            "course_id": course_id,
            "created_at": datetime.now().isoformat(),
            "learning_style": learning_style,
            "path_modules": []
        }
        
        # Add modules based on weaknesses
        if "weaknesses" in analysis_results:
            for weakness in analysis_results["weaknesses"]:
                if "Needs improvement on:" in weakness:
                    topics = weakness.replace("Needs improvement on:", "").strip().split(", ")
                    for topic in topics:
                        # Add remedial module for this topic
                        learning_path["path_modules"].append({
                            "type": "remedial",
                            "topic": topic,
                            "difficulty": "beginner",
                            "resources": self._get_resources_for_topic(topic, "beginner", learning_style),
                            "estimated_time": "2 hours",
                            "priority": "high"
                        })
        
        # Add standard course modules
        # This would typically come from the course structure
        # For demonstration, we'll add some example modules
        standard_modules = [
            {"topic": "Introduction", "difficulty": "beginner"},
            {"topic": "Core Concepts", "difficulty": "intermediate"},
            {"topic": "Advanced Applications", "difficulty": "advanced"},
            {"topic": "Case Studies", "difficulty": "intermediate"},
            {"topic": "Final Project", "difficulty": "expert"}
        ]
        
        for module in standard_modules:
            # Check if this is a weak topic that we've already added
            if any(m.get("topic") == module["topic"] and m.get("type") == "remedial" 
                  for m in learning_path["path_modules"]):
                continue
                
            learning_path["path_modules"].append({
                "type": "standard",
                "topic": module["topic"],
                "difficulty": module["difficulty"],
                "resources": self._get_resources_for_topic(
                    module["topic"], 
                    module["difficulty"], 
                    learning_style
                ),
                "estimated_time": "3 hours",
                "priority": "medium"
            })
        
        # Add enrichment modules for strong topics
        if "strengths" in analysis_results:
            for strength in analysis_results["strengths"]:
                if "Strong understanding of:" in strength:
                    topics = strength.replace("Strong understanding of:", "").strip().split(", ")
                    for topic in topics:
                        # Add advanced module for this topic
                        learning_path["path_modules"].append({
                            "type": "enrichment",
                            "topic": topic,
                            "difficulty": "expert",
                            "resources": self._get_resources_for_topic(topic, "expert", learning_style),
                            "estimated_time": "4 hours",
                            "priority": "low"
                        })
        
        # Sort modules by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        learning_path["path_modules"].sort(key=lambda x: priority_order.get(x.get("priority"), 99))
        
        # Save learning path to file
        path_file = os.path.join(self.paths_dir, f"{student_id}_{course_id}_path.json")
        with open(path_file, 'w') as f:
            json.dump(learning_path, f, indent=4)
        
        return learning_path
    
    def update_learning_path(self, student_id, course_id, new_performance_data):
        """Update an existing learning path based on new performance data.
        
        Args:
            student_id (str): Unique identifier for the student
            course_id (str): Unique identifier for the course
            new_performance_data (dict): New performance data to incorporate
            
        Returns:
            dict: Updated learning path
        """
        # Analyze new performance data
        analysis_results = self.analyze_student_performance(student_id, new_performance_data)
        
        # Create new learning path based on updated analysis
        updated_path = self.create_learning_path(student_id, course_id, analysis_results)
        
        return updated_path
    
    def get_learning_path(self, student_id, course_id):
        """Retrieve an existing learning path.
        
        Args:
            student_id (str): Unique identifier for the student
            course_id (str): Unique identifier for the course
            
        Returns:
            dict: Learning path if it exists, otherwise None
        """
        path_file = os.path.join(self.paths_dir, f"{student_id}_{course_id}_path.json")
        if os.path.exists(path_file):
            with open(path_file, 'r') as f:
                return json.load(f)
        return None
    
    def cluster_students(self, performance_data):
        """Group students into clusters based on performance patterns.
        
        Args:
            performance_data (list): List of dictionaries with student performance data
            
        Returns:
            dict: Clustering results with student groups
        """
        # Extract features for clustering
        features = []
        student_ids = []
        
        for student in performance_data:
            student_id = student.get("student_id")
            avg_scores = student.get("average_scores", {})
            
            # Extract feature values
            feature_vector = [
                avg_scores.get("assignments", 0),
                avg_scores.get("quizzes", 0),
                avg_scores.get("participation", 0)
            ]
            
            features.append(feature_vector)
            student_ids.append(student_id)
        
        # Convert to numpy array
        X = np.array(features)
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Determine optimal number of clusters (simplified)
        n_clusters = min(4, len(X))  # Maximum of 4 clusters or number of students
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Save model
        model_file = os.path.join(self.models_dir, "student_clusters.joblib")
        joblib.dump(kmeans, model_file)
        
        # Organize results by cluster
        cluster_groups = {}
        for i, cluster_id in enumerate(clusters):
            cluster_name = f"Group {cluster_id + 1}"
            if cluster_name not in cluster_groups:
                cluster_groups[cluster_name] = []
            
            cluster_groups[cluster_name].append({
                "student_id": student_ids[i],
                "features": features[i]
            })
        
        # Analyze cluster characteristics
        cluster_profiles = {}
        for cluster_name, students in cluster_groups.items():
            # Calculate average scores for this cluster
            cluster_features = np.array([student["features"] for student in students])
            avg_cluster_features = np.mean(cluster_features, axis=0)
            
            # Determine cluster profile based on average scores
            profile = {
                "avg_assignment_score": avg_cluster_features[0],
                "avg_quiz_score": avg_cluster_features[1],
                "avg_participation": avg_cluster_features[2],
                "student_count": len(students)
            }
            
            # Categorize cluster
            if all(score >= 80 for score in avg_cluster_features):
                profile["category"] = "High Performers"
            elif all(score < 60 for score in avg_cluster_features):
                profile["category"] = "Needs Support"
            elif avg_cluster_features[0] >= 80 and avg_cluster_features[1] < 60:
                profile["category"] = "Strong on Assignments, Weak on Quizzes"
            elif avg_cluster_features[0] < 60 and avg_cluster_features[1] >= 80:
                profile["category"] = "Strong on Quizzes, Weak on Assignments"
            elif avg_cluster_features[2] < 60:
                profile["category"] = "Low Participation"
            else:
                profile["category"] = "Mixed Performance"
            
            cluster_profiles[cluster_name] = profile
        
        # Prepare final results
        clustering_results = {
            "timestamp": datetime.now().isoformat(),
            "n_clusters": n_clusters,
            "cluster_groups": cluster_groups,
            "cluster_profiles": cluster_profiles
        }
        
        # Save results
        results_file = os.path.join(self.analytics_dir, "clustering_results.json")
        with open(results_file, 'w') as f:
            json.dump(clustering_results, f, indent=4)
        
        return clustering_results
    
    def _get_resources_for_topic(self, topic, difficulty, learning_style):
        """Get appropriate learning resources based on topic, difficulty, and learning style.
        
        Args:
            topic (str): The topic to find resources for
            difficulty (str): Difficulty level (beginner, intermediate, advanced, expert)
            learning_style (str): Student's learning style
            
        Returns:
            list: List of appropriate learning resources
        """
        # This would typically come from a database of learning resources
        # For demonstration, we'll generate some example resources
        
        resources = []
        
        # Add resources based on learning style
        if learning_style == "visual":
            resources.append({
                "type": "video",
                "title": f"{topic} Visualization",
                "description": f"Visual explanation of {topic} concepts",
                "url": f"https://example.com/videos/{topic.lower().replace(' ', '_')}"
            })
            resources.append({
                "type": "infographic",
                "title": f"{topic} Infographic",
                "description": f"Visual summary of key {topic} concepts",
                "url": f"https://example.com/infographics/{topic.lower().replace(' ', '_')}"
            })
            
        elif learning_style == "auditory":
            resources.append({
                "type": "podcast",
                "title": f"{topic} Explained",
                "description": f"Audio explanation of {topic} concepts",
                "url": f"https://example.com/podcasts/{topic.lower().replace(' ', '_')}"
            })
            resources.append({
                "type": "lecture",
                "title": f"{topic} Lecture",
                "description": f"Recorded lecture on {topic}",
                "url": f"https://example.com/lectures/{topic.lower().replace(' ', '_')}"
            })
            
        elif learning_style == "reading/writing":
            resources.append({
                "type": "article",
                "title": f"{topic} Explained",
                "description": f"Comprehensive article on {topic}",
                "url": f"https://example.com/articles/{topic.lower().replace(' ', '_')}"
            })
            resources.append({
                "type": "worksheet",
                "title": f"{topic} Worksheet",
                "description": f"Practice worksheet for {topic}",
                "url": f"https://example.com/worksheets/{topic.lower().replace(' ', '_')}"
            })
            
        elif learning_style == "kinesthetic":
            resources.append({
                "type": "interactive",
                "title": f"{topic} Interactive Exercise",
                "description": f"Hands-on practice with {topic}",
                "url": f"https://example.com/interactive/{topic.lower().replace(' ', '_')}"
            })
            resources.append({
                "type": "project",
                "title": f"{topic} Mini-Project",
                "description": f"Applied project on {topic}",
                "url": f"https://example.com/projects/{topic.lower().replace(' ', '_')}"
            })
        
        # Add general resources based on difficulty
        if difficulty == "beginner":
            resources.append({
                "type": "tutorial",
                "title": f"{topic} for Beginners",
                "description": f"Introduction to {topic}",
                "url": f"https://example.com/tutorials/beginner_{topic.lower().replace(' ', '_')}"
            })
        elif difficulty == "intermediate":
            resources.append({
                "type": "case_study",
                "title": f"{topic} in Practice",
                "description": f"Practical applications of {topic}",
                "url": f"https://example.com/case_studies/{topic.lower().replace(' ', '_')}"
            })
        elif difficulty == "advanced":
            resources.append({
                "type": "research_paper",
                "title": f"Advanced {topic}",
                "description": f"In-depth exploration of {topic}",
                "url": f"https://example.com/papers/advanced_{topic.lower().replace(' ', '_')}"
            })
        elif difficulty == "expert":
            resources.append({
                "type": "seminar",
                "title": f"{topic} Mastery",
                "description": f"Expert-level content on {topic}",
                "url": f"https://example.com/seminars/expert_{topic.lower().replace(' ', '_')}"
            })
        
        return resources
