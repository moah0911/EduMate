"""
Plagiarism Detection module for EduMate.

This module provides functionality to detect plagiarism in student submissions
using advanced NLP techniques.
"""

import os
import json
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize
import difflib
import requests

class PlagiarismDetector:
    """Class to detect plagiarism in student submissions."""
    
    def __init__(self, data_dir="data/plagiarism"):
        """Initialize the PlagiarismDetector class.
        
        Args:
            data_dir (str): Directory to store plagiarism detection data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Create subdirectories
        self.reports_dir = os.path.join(data_dir, "reports")
        self.database_dir = os.path.join(data_dir, "database")
        
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.database_dir, exist_ok=True)
        
        # Download NLTK data if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    def check_plagiarism(self, submission_text, student_id, assignment_id, check_web=True, threshold=0.8):
        """Check a submission for plagiarism against previous submissions and optionally the web.
        
        Args:
            submission_text (str): The text content to check for plagiarism
            student_id (str): ID of the student who made the submission
            assignment_id (str): ID of the assignment
            check_web (bool): Whether to check for plagiarism against web sources
            threshold (float): Similarity threshold above which to flag plagiarism (0.0-1.0)
            
        Returns:
            dict: Plagiarism detection results
        """
        results = {
            "student_id": student_id,
            "assignment_id": assignment_id,
            "timestamp": datetime.now().isoformat(),
            "plagiarism_detected": False,
            "similarity_score": 0.0,
            "matched_sources": [],
            "web_matches": []
        }
        
        # Check against previous submissions
        database_matches = self._check_against_database(submission_text, threshold)
        if database_matches:
            results["plagiarism_detected"] = True
            results["matched_sources"] = database_matches
            
            # Get the highest similarity score
            max_score = max(match.get("similarity_score", 0) for match in database_matches)
            results["similarity_score"] = max_score
        
        # Check against web sources if requested
        if check_web:
            web_matches = self._check_against_web(submission_text, threshold)
            if web_matches:
                results["plagiarism_detected"] = True
                results["web_matches"] = web_matches
                
                # Update the similarity score if a higher match is found
                web_max_score = max(match.get("similarity_score", 0) for match in web_matches)
                if web_max_score > results["similarity_score"]:
                    results["similarity_score"] = web_max_score
        
        # Add the submission to the database
        self._add_to_database(submission_text, student_id, assignment_id)
        
        # Generate a detailed report
        report_path = self._generate_report(results, submission_text)
        results["report_path"] = report_path
        
        return results
    
    def _check_against_database(self, submission_text, threshold):
        """Check submission against the database of previous submissions.
        
        Args:
            submission_text (str): The text to check
            threshold (float): Similarity threshold
            
        Returns:
            list: List of matched sources
        """
        matches = []
        
        # Get all submissions from the database
        submissions = self._get_all_submissions()
        
        if not submissions:
            return matches
        
        # Prepare the texts for comparison
        texts = [sub["text"] for sub in submissions]
        texts.append(submission_text)
        
        # Calculate TF-IDF vectors
        vectorizer = TfidfVectorizer().fit_transform(texts)
        vectors = vectorizer.toarray()
        
        # Calculate similarity between the submission and all previous submissions
        submission_vector = vectors[-1]
        for i, sub in enumerate(submissions):
            similarity = cosine_similarity([vectors[i]], [submission_vector])[0][0]
            
            if similarity >= threshold:
                # Find matching sentences
                matching_sentences = self._find_matching_sentences(
                    submission_text, 
                    sub["text"],
                    threshold
                )
                
                matches.append({
                    "student_id": sub["student_id"],
                    "assignment_id": sub["assignment_id"],
                    "similarity_score": float(similarity),
                    "matching_sentences": matching_sentences
                })
        
        return matches
    
    def _check_against_web(self, submission_text, threshold):
        """Check submission against web sources.
        
        Args:
            submission_text (str): The text to check
            threshold (float): Similarity threshold
            
        Returns:
            list: List of matched web sources
        """
        matches = []
        
        # Split the submission into sentences
        sentences = sent_tokenize(submission_text)
        
        # Check each sentence (or group of sentences) against web sources
        # In a real implementation, this would use a search API or specialized service
        
        # Simulate web checking with a mock implementation
        # In a production environment, you would integrate with a real service
        for i in range(0, len(sentences), 3):
            # Take groups of 3 sentences to check
            sentence_group = " ".join(sentences[i:i+3])
            if len(sentence_group.split()) < 10:
                continue  # Skip very short groups
                
            # Simulate a web search result
            # In reality, this would call a search API
            web_match = self._simulate_web_search(sentence_group)
            
            if web_match and web_match["similarity_score"] >= threshold:
                matches.append(web_match)
        
        return matches
    
    def _simulate_web_search(self, text):
        """Simulate a web search for plagiarism detection.
        
        In a real implementation, this would call a search API or specialized service.
        
        Args:
            text (str): The text to search for
            
        Returns:
            dict: Simulated web match result, or None if no match
        """
        # This is a mock implementation
        # In a real system, you would integrate with a search API
        
        # Randomly determine if this text has a web match (for demonstration)
        if len(text) > 100 and np.random.random() < 0.1:
            return {
                "source_url": f"https://example.com/article{np.random.randint(1000)}",
                "source_title": f"Example Article {np.random.randint(100)}",
                "similarity_score": np.random.uniform(0.8, 0.95),
                "matched_text": text
            }
        
        return None
    
    def _find_matching_sentences(self, text1, text2, threshold):
        """Find matching sentences between two texts.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            threshold (float): Similarity threshold
            
        Returns:
            list: List of matching sentence pairs
        """
        # Split texts into sentences
        sentences1 = sent_tokenize(text1)
        sentences2 = sent_tokenize(text2)
        
        matches = []
        
        # Compare each sentence from text1 with each sentence from text2
        for i, s1 in enumerate(sentences1):
            for j, s2 in enumerate(sentences2):
                # Calculate similarity ratio using difflib
                similarity = difflib.SequenceMatcher(None, s1, s2).ratio()
                
                if similarity >= threshold:
                    matches.append({
                        "text1_sentence": s1,
                        "text2_sentence": s2,
                        "similarity": float(similarity)
                    })
        
        return matches
    
    def _add_to_database(self, submission_text, student_id, assignment_id):
        """Add a submission to the database for future plagiarism checks.
        
        Args:
            submission_text (str): The text content
            student_id (str): ID of the student
            assignment_id (str): ID of the assignment
        """
        # Create a unique ID for the submission
        submission_id = f"{student_id}_{assignment_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Prepare submission data
        submission_data = {
            "id": submission_id,
            "student_id": student_id,
            "assignment_id": assignment_id,
            "timestamp": datetime.now().isoformat(),
            "text": submission_text
        }
        
        # Save to database
        file_path = os.path.join(self.database_dir, f"{submission_id}.json")
        with open(file_path, 'w') as f:
            json.dump(submission_data, f, indent=4)
    
    def _get_all_submissions(self):
        """Get all submissions from the database.
        
        Returns:
            list: List of submission data
        """
        submissions = []
        
        # List all files in the database directory
        for filename in os.listdir(self.database_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.database_dir, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        submission_data = json.load(f)
                        submissions.append(submission_data)
                except Exception as e:
                    print(f"Error loading submission file {filename}: {e}")
        
        return submissions
    
    def _generate_report(self, results, submission_text):
        """Generate a detailed plagiarism report.
        
        Args:
            results (dict): Plagiarism detection results
            submission_text (str): The original submission text
            
        Returns:
            str: Path to the generated report file
        """
        # Create a unique report ID
        report_id = f"{results['student_id']}_{results['assignment_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Prepare report data
        report_data = {
            "id": report_id,
            "student_id": results["student_id"],
            "assignment_id": results["assignment_id"],
            "timestamp": datetime.now().isoformat(),
            "plagiarism_detected": results["plagiarism_detected"],
            "similarity_score": results["similarity_score"],
            "submission_text": submission_text,
            "matched_sources": results["matched_sources"],
            "web_matches": results["web_matches"],
            "summary": self._generate_summary(results)
        }
        
        # Save report to file
        report_path = os.path.join(self.reports_dir, f"{report_id}.json")
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=4)
        
        return report_path
    
    def _generate_summary(self, results):
        """Generate a human-readable summary of plagiarism detection results.
        
        Args:
            results (dict): Plagiarism detection results
            
        Returns:
            str: Summary text
        """
        if not results["plagiarism_detected"]:
            return "No plagiarism detected in this submission."
        
        summary = []
        summary.append(f"Plagiarism detected with a similarity score of {results['similarity_score']:.2f}.")
        
        if results["matched_sources"]:
            summary.append(f"Found {len(results['matched_sources'])} matches with other student submissions:")
            for i, match in enumerate(results["matched_sources"]):
                summary.append(f"  {i+1}. Submission by student {match['student_id']} for assignment {match['assignment_id']}")
                summary.append(f"     Similarity: {match['similarity_score']:.2f}")
                if match.get("matching_sentences"):
                    summary.append(f"     {len(match['matching_sentences'])} matching sentences found")
        
        if results["web_matches"]:
            summary.append(f"Found {len(results['web_matches'])} matches with web sources:")
            for i, match in enumerate(results["web_matches"]):
                summary.append(f"  {i+1}. {match['source_title']}")
                summary.append(f"     URL: {match['source_url']}")
                summary.append(f"     Similarity: {match['similarity_score']:.2f}")
        
        return "\n".join(summary)
    
    def get_report(self, report_id):
        """Retrieve a plagiarism report by ID.
        
        Args:
            report_id (str): ID of the report to retrieve
            
        Returns:
            dict: Report data if found, otherwise None
        """
        report_path = os.path.join(self.reports_dir, f"{report_id}.json")
        
        if os.path.exists(report_path):
            try:
                with open(report_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading report {report_id}: {e}")
        
        return None
    
    def get_reports_by_student(self, student_id):
        """Get all plagiarism reports for a specific student.
        
        Args:
            student_id (str): ID of the student
            
        Returns:
            list: List of report data
        """
        reports = []
        
        # List all files in the reports directory
        for filename in os.listdir(self.reports_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.reports_dir, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        report_data = json.load(f)
                        if report_data.get("student_id") == student_id:
                            reports.append(report_data)
                except Exception as e:
                    print(f"Error loading report file {filename}: {e}")
        
        return reports
    
    def get_reports_by_assignment(self, assignment_id):
        """Get all plagiarism reports for a specific assignment.
        
        Args:
            assignment_id (str): ID of the assignment
            
        Returns:
            list: List of report data
        """
        reports = []
        
        # List all files in the reports directory
        for filename in os.listdir(self.reports_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.reports_dir, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        report_data = json.load(f)
                        if report_data.get("assignment_id") == assignment_id:
                            reports.append(report_data)
                except Exception as e:
                    print(f"Error loading report file {filename}: {e}")
        
        return reports
