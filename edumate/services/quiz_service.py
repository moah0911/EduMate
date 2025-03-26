"""
Quiz Service - Handles quiz generation, management, and grading
"""
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1/models"

class QuizService:
    """Service for managing quiz operations including AI-generated quizzes"""
    
    def __init__(self, data_path: str = "data/quizzes"):
        """Initialize the quiz service"""
        self.data_path = data_path
        # Create data directory if it doesn't exist
        if not os.path.exists(data_path):
            os.makedirs(data_path)
    
    def get_quizzes_by_course(self, course_id: str) -> List[Dict[str, Any]]:
        """Get all quizzes for a specific course"""
        quizzes_file = os.path.join(self.data_path, f"course_{course_id}_quizzes.json")
        
        if not os.path.exists(quizzes_file):
            return []
        
        with open(quizzes_file, 'r') as f:
            return json.load(f)
    
    def get_quiz_by_id(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """Get a quiz by its ID, searches across all courses"""
        # List all quiz files
        quiz_files = [f for f in os.listdir(self.data_path) if f.endswith("_quizzes.json")]
        
        for file in quiz_files:
            file_path = os.path.join(self.data_path, file)
            with open(file_path, 'r') as f:
                quizzes = json.load(f)
                for quiz in quizzes:
                    if quiz.get('id') == quiz_id:
                        return quiz
        
        return None
    
    def create_quiz(self, course_id: str, quiz_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Create a new quiz for a course"""
        quizzes_file = os.path.join(self.data_path, f"course_{course_id}_quizzes.json")
        
        # Load existing quizzes or create empty list
        if os.path.exists(quizzes_file):
            with open(quizzes_file, 'r') as f:
                quizzes = json.load(f)
        else:
            quizzes = []
        
        # Add unique ID and timestamps
        quiz_data['id'] = str(uuid.uuid4())
        quiz_data['created_at'] = datetime.now().isoformat()
        quiz_data['updated_at'] = datetime.now().isoformat()
        quiz_data['course_id'] = course_id
        
        # Add the quiz to the list
        quizzes.append(quiz_data)
        
        # Save to file
        with open(quizzes_file, 'w') as f:
            json.dump(quizzes, f, indent=4)
        
        return True, "Quiz created successfully!"
    
    def update_quiz(self, quiz_id: str, updated_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Update an existing quiz"""
        # Find which file contains the quiz
        quiz_files = [f for f in os.listdir(self.data_path) if f.endswith("_quizzes.json")]
        
        for file in quiz_files:
            file_path = os.path.join(self.data_path, file)
            with open(file_path, 'r') as f:
                quizzes = json.load(f)
                
                # Find the quiz to update
                for i, quiz in enumerate(quizzes):
                    if quiz.get('id') == quiz_id:
                        # Update fields but keep ID and creation date
                        quiz_id = quiz['id']
                        created_at = quiz['created_at']
                        course_id = quiz['course_id']
                        
                        # Update with new data
                        updated_data['id'] = quiz_id
                        updated_data['created_at'] = created_at
                        updated_data['updated_at'] = datetime.now().isoformat()
                        updated_data['course_id'] = course_id
                        
                        # Replace the quiz
                        quizzes[i] = updated_data
                        
                        # Save updated list
                        with open(file_path, 'w') as f_write:
                            json.dump(quizzes, f_write, indent=4)
                        
                        return True, "Quiz updated successfully!"
        
        return False, "Quiz not found!"
    
    def delete_quiz(self, quiz_id: str) -> Tuple[bool, str]:
        """Delete a quiz"""
        # Find which file contains the quiz
        quiz_files = [f for f in os.listdir(self.data_path) if f.endswith("_quizzes.json")]
        
        for file in quiz_files:
            file_path = os.path.join(self.data_path, file)
            with open(file_path, 'r') as f:
                quizzes = json.load(f)
                
                # Find the quiz to delete
                for i, quiz in enumerate(quizzes):
                    if quiz.get('id') == quiz_id:
                        # Remove the quiz
                        quizzes.pop(i)
                        
                        # Save updated list
                        with open(file_path, 'w') as f_write:
                            json.dump(quizzes, f_write, indent=4)
                        
                        return True, "Quiz deleted successfully!"
        
        return False, "Quiz not found!"
    
    def generate_quiz_with_ai(self, subject: str, topic: str, difficulty: str, num_questions: int = 10) -> Dict[str, Any]:
        """Generate a quiz using Gemini AI"""
        # Create the prompt for Gemini
        prompt = f"""Create a detailed quiz on {subject} focusing on {topic}. 
        Difficulty level: {difficulty}.
        Total questions: {num_questions}.
        
        Please structure the quiz as a JSON object with the following format:
        {{
            "title": "[Quiz Title]",
            "subject": "{subject}",
            "topic": "{topic}",
            "difficulty": "{difficulty}",
            "total_questions": {num_questions},
            "questions": [
                {{
                    "question": "[Question text]",
                    "type": "[multiple_choice/true_false/short_answer/fill_blank]",
                    "options": ["Option A", "Option B", "Option C", "Option D"], (for multiple choice only)
                    "correct_answer": "[Correct answer]",
                    "explanation": "[Explanation of the answer]"
                }},
                ...
            ]
        }}
        
        Ensure the questions are appropriate for the {difficulty} difficulty level and cover key concepts in {topic}.
        For multiple choice questions, provide 4 options.
        For true/false questions, set options as ["True", "False"].
        Don't include the options field for short answer or fill in the blank questions.
        Each question should have a detailed explanation of the correct answer.
        """
        
        # Call Gemini API
        try:
            headers = {
                'Authorization': f'Bearer {GEMINI_API_KEY}',
                'Content-Type': 'application/json'
            }
            data = {
                'prompt': prompt,
                'maxTokens': 2048,
                'temperature': 0.7,
                'topP': 1,
                'frequencyPenalty': 0,
                'presencePenalty': 0
            }
            response = requests.post(f'{GEMINI_API_BASE_URL}/generate', headers=headers, json=data)
            
            # Extract the JSON response
            response_text = response.json().get('text', '')
            
            # Clean the response if it contains markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse the JSON
            quiz_data = json.loads(response_text)
            
            # Add basic metadata
            quiz_data["created_by"] = "AI"
            quiz_data["created_at"] = datetime.now().isoformat()
            
            return quiz_data
            
        except Exception as e:
            # If AI generation fails, create a basic template
            fallback_quiz = {
                "title": f"{topic} Quiz",
                "subject": subject,
                "topic": topic,
                "difficulty": difficulty,
                "total_questions": num_questions,
                "questions": [],
                "error": str(e),
                "note": "AI generation failed, using template instead"
            }
            
            # Add some template questions based on the type
            question_types = ["multiple_choice", "true_false", "short_answer", "fill_blank"]
            
            for i in range(num_questions):
                q_type = question_types[i % len(question_types)]
                
                if q_type == "multiple_choice":
                    question = {
                        "question": f"Sample question {i+1} about {topic}?",
                        "type": "multiple_choice",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "explanation": f"This is an explanation of the correct answer for question {i+1}."
                    }
                elif q_type == "true_false":
                    question = {
                        "question": f"Sample true/false statement {i+1} about {topic}.",
                        "type": "true_false",
                        "options": ["True", "False"],
                        "correct_answer": "True",
                        "explanation": f"This is an explanation of why the statement {i+1} is true."
                    }
                elif q_type == "short_answer":
                    question = {
                        "question": f"Explain briefly the concept of {topic} related to question {i+1}.",
                        "type": "short_answer",
                        "correct_answer": f"A brief explanation of {topic} for question {i+1}.",
                        "explanation": f"This is a more detailed explanation for short answer question {i+1}."
                    }
                else:  # fill_blank
                    question = {
                        "question": f"The process of _____ is essential to understanding {topic}.",
                        "type": "fill_blank",
                        "correct_answer": topic,
                        "explanation": f"This is an explanation of why {topic} fills the blank correctly."
                    }
                
                fallback_quiz["questions"].append(question)
            
            return fallback_quiz
    
    def grade_quiz_submission(self, quiz_id: str, submission: Dict[str, Any]) -> Dict[str, Any]:
        """Grade a quiz submission and provide feedback"""
        # Get the quiz
        quiz = self.get_quiz_by_id(quiz_id)
        
        if not quiz:
            return {
                "error": "Quiz not found",
                "score": 0,
                "total": 0,
                "percentage": 0,
                "feedback": "Error: Quiz not found"
            }
        
        # Initialize results
        total_questions = len(quiz.get("questions", []))
        correct_answers = 0
        question_results = []
        
        # Grade each question
        for i, question in enumerate(quiz.get("questions", [])):
            q_id = str(i)
            student_answer = submission.get("answers", {}).get(q_id, "")
            
            # Check if answer is correct
            is_correct = False
            
            if question.get("type") == "multiple_choice" or question.get("type") == "true_false":
                is_correct = student_answer.lower() == question.get("correct_answer", "").lower()
            elif question.get("type") == "fill_blank":
                is_correct = student_answer.lower() == question.get("correct_answer", "").lower()
            elif question.get("type") == "short_answer":
                # For short answers, use AI to evaluate
                try:
                    is_correct = self._evaluate_short_answer(
                        student_answer, 
                        question.get("correct_answer", ""),
                        question.get("question", "")
                    )
                except:
                    # If AI evaluation fails, more lenient scoring
                    is_correct = any(word.lower() in student_answer.lower() 
                                     for word in question.get("correct_answer", "").split() 
                                     if len(word) > 3)
            
            # Add to results
            if is_correct:
                correct_answers += 1
            
            question_results.append({
                "question_id": q_id,
                "is_correct": is_correct,
                "student_answer": student_answer,
                "correct_answer": question.get("correct_answer", ""),
                "explanation": question.get("explanation", "")
            })
        
        # Calculate score
        percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Generate feedback using AI
        feedback = self._generate_feedback(quiz, question_results, percentage)
        
        # Return results
        return {
            "score": correct_answers,
            "total": total_questions,
            "percentage": percentage,
            "question_results": question_results,
            "feedback": feedback
        }
    
    def _evaluate_short_answer(self, student_answer: str, correct_answer: str, question: str) -> bool:
        """Use Gemini AI to evaluate a short answer response"""
        if not student_answer:
            return False
            
        prompt = f"""Evaluate if the student's answer correctly addresses the question.
        
        Question: {question}
        Expected answer key points: {correct_answer}
        Student answer: {student_answer}
        
        Determine if the student's answer adequately addresses the key points expected in the answer. 
        The student doesn't need to use the exact same words, but should demonstrate understanding of the core concepts.
        
        Respond with either "CORRECT" or "INCORRECT" followed by a brief explanation.
        """
        
        try:
            headers = {
                'Authorization': f'Bearer {GEMINI_API_KEY}',
                'Content-Type': 'application/json'
            }
            data = {
                'prompt': prompt,
                'maxTokens': 2048,
                'temperature': 0.7,
                'topP': 1,
                'frequencyPenalty': 0,
                'presencePenalty': 0
            }
            response = requests.post(f'{GEMINI_API_BASE_URL}/generate', headers=headers, json=data)
            
            # Check if the response indicates the answer is correct
            response_text = response.json().get('text', '').strip().upper()
            return response_text.startswith("CORRECT")
        except:
            # If AI evaluation fails, fall back to keyword matching
            return any(word.lower() in student_answer.lower() 
                      for word in correct_answer.split() 
                      if len(word) > 3)
    
    def _generate_feedback(self, quiz: Dict[str, Any], results: List[Dict[str, Any]], score: float) -> str:
        """Generate personalized feedback for a quiz attempt using Gemini AI"""
        # Prepare data for the AI prompt
        quiz_title = quiz.get("title", "")
        quiz_topic = quiz.get("topic", "")
        correct_count = sum(1 for r in results if r.get("is_correct"))
        total_count = len(results)
        
        # Build the question details
        question_details = []
        for i, result in enumerate(results):
            q_text = quiz.get("questions", [])[i].get("question", "")
            q_detail = f"Q{i+1}: '{q_text}' - {'Correct' if result.get('is_correct') else 'Incorrect'}"
            if not result.get("is_correct"):
                q_detail += f" (You answered: '{result.get('student_answer')}', Correct answer: '{result.get('correct_answer')}')"
            
            question_details.append(q_detail)
        
        # Create prompt for Gemini
        prompt = f"""Generate personalized feedback for a student's quiz performance.
        
        Quiz: {quiz_title} on {quiz_topic}
        Score: {correct_count}/{total_count} ({score:.1f}%)
        
        Question performance:
        {chr(10).join(question_details)}
        
        Please provide:
        1. A encouraging opening statement about their performance
        2. Identify 2-3 areas they did well in
        3. Identify 2-3 areas for improvement, focusing on questions they got wrong
        4. Suggest specific ways they can improve their understanding of {quiz_topic}
        5. End with an encouraging statement
        
        Keep the tone positive and constructive. Format the response in markdown.
        """
        
        try:
            headers = {
                'Authorization': f'Bearer {GEMINI_API_KEY}',
                'Content-Type': 'application/json'
            }
            data = {
                'prompt': prompt,
                'maxTokens': 2048,
                'temperature': 0.7,
                'topP': 1,
                'frequencyPenalty': 0,
                'presencePenalty': 0
            }
            response = requests.post(f'{GEMINI_API_BASE_URL}/generate', headers=headers, json=data)
            return response.json().get('text', '')
        except Exception as e:
            # Fallback feedback if AI fails
            if score >= 80:
                return f"Great job! You scored {score:.1f}% on the quiz. Keep up the good work!"
            elif score >= 60:
                return f"Good effort! You scored {score:.1f}% on the quiz. Review the questions you missed to improve."
            else:
                return f"You scored {score:.1f}% on the quiz. Consider revisiting the material and trying again."

# Create a singleton instance
quiz_service = QuizService()
