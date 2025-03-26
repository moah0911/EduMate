"""AI grading service for EduMate application."""

import logging
from typing import Dict, Any, List, Optional
import json
import re

from edumate.services.ai_service import AIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIGradingService:
    """Service for AI-powered grading of assignments."""

    @staticmethod
    def is_available() -> bool:
        """Check if AI grading is available."""
        return AIService.is_available()
    
    @classmethod
    def grade_essay(cls, content: str, rubric: Dict[str, Any], max_points: int = 100) -> Dict[str, Any]:
        """Grade an essay assignment."""
        logger.info("Grading essay assignment")
        
        # Prepare rubric for AI
        formatted_rubric = {}
        for criterion, points in rubric.items():
            if isinstance(points, (int, float)):
                formatted_rubric[criterion] = points
            elif isinstance(points, dict) and 'points' in points:
                formatted_rubric[criterion] = points['points']
            else:
                formatted_rubric[criterion] = 10  # Default points
        
        # Grade the essay
        result = AIService.grade_assignment(
            content=content,
            assignment_type="essay",
            rubric=formatted_rubric,
            max_points=max_points
        )
        
        # Ensure the grade is within bounds
        if result.get('grade', 0) > max_points:
            result['grade'] = max_points
        
        return result
    
    @classmethod
    def grade_code(cls, code: str, rubric: Dict[str, Any], language: str = 'python', max_points: int = 100) -> Dict[str, Any]:
        """Grade a code assignment."""
        logger.info(f"Grading {language} code assignment")
        
        # Prepare rubric for AI
        formatted_rubric = {}
        for criterion, points in rubric.items():
            if isinstance(points, (int, float)):
                formatted_rubric[criterion] = points
            elif isinstance(points, dict) and 'points' in points:
                formatted_rubric[criterion] = points['points']
            else:
                formatted_rubric[criterion] = 10  # Default points
        
        # Add code-specific criteria if not present
        if "Correctness" not in formatted_rubric:
            formatted_rubric["Correctness"] = max_points * 0.4
        if "Code Quality" not in formatted_rubric:
            formatted_rubric["Code Quality"] = max_points * 0.3
        if "Documentation" not in formatted_rubric:
            formatted_rubric["Documentation"] = max_points * 0.2
        if "Efficiency" not in formatted_rubric:
            formatted_rubric["Efficiency"] = max_points * 0.1
        
        # Grade the code
        result = AIService.grade_assignment(
            content=code,
            assignment_type=f"code ({language})",
            rubric=formatted_rubric,
            max_points=max_points
        )
        
        # Ensure the grade is within bounds
        if result.get('grade', 0) > max_points:
            result['grade'] = max_points
        
        return result
    
    @classmethod
    def grade_quiz(cls, student_answers: Dict[str, Any], correct_answers: Dict[str, Any], max_points: int = 100) -> Dict[str, Any]:
        """Grade a quiz assignment."""
        logger.info("Grading quiz assignment")
        
        # Calculate score based on correct answers
        total_questions = len(correct_answers)
        correct_count = 0
        
        results = {
            "grade": 0,
            "rubric_scores": {},
            "strengths": [],
            "improvements": [],
            "feedback": "",
            "question_results": []
        }
        
        for question_id, correct_answer in correct_answers.items():
            student_answer = student_answers.get(question_id, "")
            is_correct = False
            
            # Compare answers
            if isinstance(correct_answer, list):
                # Multiple choice with multiple correct answers
                if isinstance(student_answer, list):
                    is_correct = set(student_answer) == set(correct_answer)
                else:
                    is_correct = False
            elif isinstance(student_answer, str) and isinstance(correct_answer, str):
                # Text answer - use AI to evaluate
                if AIService.is_available():
                    prompt = f"""
                    Question: {question_id}
                    Correct answer: {correct_answer}
                    Student answer: {student_answer}
                    
                    Is the student's answer correct? Consider semantic equivalence, not just exact matching.
                    Respond with only "yes" or "no".
        """
        try:
                        response = AIService.generate_text(prompt, max_tokens=10)
                        is_correct = "yes" in response.lower()
                    except Exception:
                        # Fall back to exact matching
                        is_correct = student_answer.strip().lower() == correct_answer.strip().lower()
                else:
                    # No AI available, use exact matching
                    is_correct = student_answer.strip().lower() == correct_answer.strip().lower()
            else:
                # Simple equality check
                is_correct = student_answer == correct_answer
            
            # Record result
            if is_correct:
                correct_count += 1
            
            results["question_results"].append({
                "question_id": question_id,
                "correct": is_correct,
                "student_answer": student_answer,
                "correct_answer": correct_answer
            })
        
        # Calculate grade
        if total_questions > 0:
            results["grade"] = (correct_count / total_questions) * max_points
        
        # Generate feedback
        if correct_count == total_questions:
            results["strengths"].append("Perfect score! You answered all questions correctly.")
            results["feedback"] = "Excellent work! You've demonstrated a thorough understanding of the material."
        elif correct_count >= total_questions * 0.8:
            results["strengths"].append("Strong performance! You answered most questions correctly.")
            results["improvements"].append("Review the few questions you missed to solidify your understanding.")
            results["feedback"] = "Great job! You've shown a good grasp of the material with just a few areas to review."
        elif correct_count >= total_questions * 0.6:
            results["strengths"].append("Good effort! You answered the majority of questions correctly.")
            results["improvements"].append("Focus on reviewing the concepts related to the questions you missed.")
            results["feedback"] = "Good work! You're on the right track, but there are some concepts that need more attention."
        else:
            results["strengths"].append("You've made an attempt at all questions.")
            results["improvements"].append("Consider revisiting the course material and seeking additional help.")
            results["feedback"] = "Thank you for your submission. It looks like you might need to review the material more thoroughly."
        
        return results
    
    @classmethod
    def generate_personalized_feedback(cls, student_name: str, assignment_title: str, grading_result: Dict[str, Any]) -> str:
        """Generate personalized feedback for a student based on grading results."""
        logger.info(f"Generating personalized feedback for {student_name}")
        
        grade = grading_result.get('grade', 0)
        max_points = grading_result.get('max_points', 100)
        strengths = grading_result.get('strengths', [])
        improvements = grading_result.get('improvements', [])
        
        return AIService.generate_personalized_feedback(
            student_name=student_name,
            assignment_title=assignment_title,
            grade=grade,
            max_points=max_points,
            strengths=strengths,
            improvements=improvements
        )
    
    @classmethod
    def check_plagiarism(cls, content: str) -> Dict[str, Any]:
        """Check for plagiarism in student submission."""
        logger.info("Checking for plagiarism")
        
        return AIService.check_plagiarism(content)
    
    @classmethod
    def analyze_submission_pattern(cls, submissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze submission patterns for a student."""
        logger.info("Analyzing submission patterns")
        
        if not submissions:
            return {
                "pattern": "insufficient_data",
                "insights": ["Not enough submissions to analyze patterns"],
                "recommendations": ["Continue submitting assignments to receive pattern analysis"]
            }
        
        # Extract grades and timestamps
        grades = [sub.get('grade', 0) for sub in submissions if 'grade' in sub]
        timestamps = [sub.get('submitted_at', '') for sub in submissions if 'submitted_at' in sub]
        
        # Calculate statistics
        avg_grade = sum(grades) / len(grades) if grades else 0
        grade_trend = "improving" if len(grades) > 1 and grades[-1] > grades[0] else "steady"
        
        # Generate insights
        insights = []
        recommendations = []
        
        if avg_grade > 90:
            insights.append("Consistently high performance across assignments")
            recommendations.append("Consider taking on more challenging work or helping peers")
        elif avg_grade > 75:
            insights.append("Good overall performance with room for improvement")
            recommendations.append("Focus on specific areas mentioned in assignment feedback")
        else:
            insights.append("Performance indicates need for additional support")
            recommendations.append("Schedule time with instructor for personalized guidance")
        
        if grade_trend == "improving":
            insights.append("Grades show an improving trend over time")
            recommendations.append("Continue applying feedback from previous assignments")
        
        # Check submission timing patterns
        last_minute = any("23:" in ts for ts in timestamps)
        if last_minute:
            insights.append("Some assignments submitted close to deadlines")
            recommendations.append("Try to start assignments earlier to allow more time for review")
            
            return {
            "pattern": grade_trend,
            "average_grade": avg_grade,
            "insights": insights,
            "recommendations": recommendations
            } 