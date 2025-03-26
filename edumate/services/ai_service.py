"""AI service for EduMate application."""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check which AI services are available
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Import AI libraries based on available API keys
gemini_available = False
openai_available = False

if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_available = True
        logger.info("Gemini AI service initialized successfully")
    except ImportError:
        logger.warning("google-generativeai package not installed. Gemini AI service will not be available.")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini AI service: {str(e)}")

if OPENAI_API_KEY:
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        openai_available = True
        logger.info("OpenAI service initialized successfully")
    except ImportError:
        logger.warning("openai package not installed. OpenAI service will not be available.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI service: {str(e)}")

if not gemini_available and not openai_available:
    logger.warning("No AI services available. AI features will not work.")


def parse_json_response(response_text: str) -> Dict[str, Any]:
    """Parse JSON from AI response text."""
    try:
        # Find JSON content between triple backticks
        if "```json" in response_text and "```" in response_text.split("```json")[1]:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
            return json.loads(json_str)
        
        # Try to find any JSON object in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)
        
        # If no JSON found, return the raw text
        return {"error": "No JSON found in response", "raw_text": response_text}
    
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON from response: {response_text}")
        return {"error": "Invalid JSON in response", "raw_text": response_text}
    except Exception as e:
        logger.error(f"Error parsing response: {str(e)}")
        return {"error": str(e), "raw_text": response_text}


class AIService:
    """AI service for EduMate application."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if any AI service is available."""
        return gemini_available or openai_available
    
    @staticmethod
    def get_available_models() -> List[str]:
        """Get list of available AI models."""
        models = []
        
        if gemini_available:
            models.append("gemini-pro")
        
        if openai_available:
            models.extend(["gpt-3.5-turbo", "gpt-4"])
        
        return models
    
    @classmethod
    def generate_text(cls, 
                     prompt: str, 
                     model: Optional[str] = None,
                     max_tokens: int = 1024,
                     temperature: float = 0.7) -> str:
        """Generate text using available AI service."""
        # Try to use specified model or fall back to available service
        if model:
            if "gemini" in model and gemini_available:
                return cls._generate_with_gemini(prompt, model, max_tokens, temperature)
            elif ("gpt" in model or "text-davinci" in model) and openai_available:
                return cls._generate_with_openai(prompt, model, max_tokens, temperature)
        
        # No specific model requested, try available services in order
        if gemini_available:
            try:
                return cls._generate_with_gemini(prompt, "gemini-pro", max_tokens, temperature)
            except Exception as e:
                logger.error(f"Gemini generation failed: {str(e)}")
                if openai_available:
                    logger.info("Falling back to OpenAI")
                    return cls._generate_with_openai(prompt, "gpt-3.5-turbo", max_tokens, temperature)
                raise
        
        if openai_available:
            return cls._generate_with_openai(prompt, "gpt-3.5-turbo", max_tokens, temperature)
        
        raise ValueError("No AI service available")
    
    @staticmethod
    def _generate_with_gemini(prompt: str, 
                             model: str = "gemini-pro", 
                             max_tokens: int = 1024,
                             temperature: float = 0.7) -> str:
        """Generate text using Gemini."""
        if not gemini_available:
            raise ValueError("Gemini AI service not available")
        
        try:
            # Configure the model
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "top_p": 0.95,
                "top_k": 40,
            }
            
            # Get the model
            model = genai.GenerativeModel(model_name=model)
            
            # Generate content
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {str(e)}")
            raise
    
    @staticmethod
    def _generate_with_openai(prompt: str, 
                             model: str = "gpt-3.5-turbo", 
                             max_tokens: int = 1024,
                             temperature: float = 0.7) -> str:
        """Generate text using OpenAI."""
        if not openai_available:
            raise ValueError("OpenAI service not available")
        
        try:
            # Create the completion
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant for an educational platform."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {str(e)}")
            raise
    
    @classmethod
    def grade_assignment(cls, 
                        content: str, 
                        assignment_type: str,
                        rubric: Dict[str, Any],
                        max_points: int = 100) -> Dict[str, Any]:
        """Grade an assignment using AI."""
        prompt = f"""
        You are an AI grading assistant for an educational platform. Please grade the following {assignment_type} assignment.
        
        RUBRIC:
        {json.dumps(rubric, indent=2)}
        
        MAXIMUM POINTS: {max_points}
        
        STUDENT SUBMISSION:
        {content}
        
        Please provide a comprehensive evaluation including:
        1. Overall grade (out of {max_points} points)
        2. Breakdown of points for each rubric criterion
        3. Strengths of the submission
        4. Areas for improvement
        5. Specific feedback comments
        
        Format your response as a JSON object with the following structure:
        ```json
        {{
            "grade": <numeric_grade>,
            "rubric_scores": {{
                "criterion1": <score>,
                "criterion2": <score>,
                ...
            }},
            "strengths": [
                "strength1",
                "strength2",
                ...
            ],
            "improvements": [
                "improvement1",
                "improvement2",
                ...
            ],
            "feedback": "detailed feedback text"
        }}
        ```
        """
        
        try:
            response_text = cls.generate_text(prompt)
            result = parse_json_response(response_text)
            
            # Validate the result
            if "grade" not in result:
                logger.warning(f"Invalid grading result: {result}")
                result["grade"] = 0
            
            return result
        except Exception as e:
            logger.error(f"Error grading assignment: {str(e)}")
            return {
                "grade": 0,
                "rubric_scores": {},
                "strengths": ["Unable to evaluate due to an error"],
                "improvements": ["Please try again or contact your instructor"],
                "feedback": f"The AI grading system encountered an error: {str(e)}"
            }
    
    @classmethod
    def generate_personalized_feedback(cls,
                                      student_name: str,
                                      assignment_title: str,
                                      assignment_type: str,
                                      grade: float,
                                      max_points: int,
                                      strengths: List[str],
                                      improvements: List[str]) -> str:
        """Generate detailed personalized feedback for a student."""
        # Determine performance level
        if grade >= 90:
            performance_level = "excellent"
        elif grade >= 80:
            performance_level = "very good"
        elif grade >= 70:
            performance_level = "good"
        elif grade >= 60:
            performance_level = "satisfactory"
        else:
            performance_level = "needs improvement"
        
        # Create type-specific feedback
        type_specific_tips = ""
        if assignment_type == "essay":
            type_specific_tips = """
            For future essays, remember to:
            - Start with a clear thesis statement
            - Support your arguments with evidence
            - Ensure smooth transitions between paragraphs
            - Conclude by restating your main points
            """
        elif assignment_type == "code":
            type_specific_tips = """
            For future coding assignments, remember to:
            - Test your code with different inputs
            - Add comments to explain complex logic
            - Use meaningful variable names
            - Consider edge cases in your solution
            """
        
        prompt = f"""
        You are an AI teaching assistant providing feedback to a student named {student_name} on their {assignment_title} assignment.
        
        The student received a grade of {grade} out of {max_points} points, which is considered {performance_level}.
        
        Strengths of the submission:
        {json.dumps(strengths, indent=2)}
        
        Areas for improvement:
        {json.dumps(improvements, indent=2)}
        
        Please write a personalized, encouraging feedback message that:
        1. Addresses the student by name
        2. Acknowledges specific strengths from the list provided
        3. Offers constructive guidance on how to improve based on the areas for improvement
        4. Includes these type-specific tips: {type_specific_tips}
        5. Ends with an encouraging note about their potential for growth
        
        The tone should be supportive, specific, and motivating.
        Keep the feedback concise but detailed (about 200-250 words).
        """
        
        try:
            return cls.generate_text(prompt, max_tokens=400, temperature=0.7)
        except Exception as e:
            logger.error(f"Error generating personalized feedback: {str(e)}")
            # Fallback feedback template
            strengths_text = "\n".join([f"- {s}" for s in strengths]) if strengths else "- Your submission was received successfully."
            improvements_text = "\n".join([f"- {i}" for i in improvements]) if improvements else "- Continue practicing to improve your skills."
            
            return f"""
            Dear {student_name},
            
            Thank you for submitting your {assignment_title} assignment. You received a grade of {grade} out of {max_points}.
            
            Strengths:
            {strengths_text}
            
            Areas for improvement:
            {improvements_text}
            
            I encourage you to review these points and continue working on improving your skills. Remember that learning is a journey, and each assignment is an opportunity to grow.
            
            Best regards,
            EduMate AI Assistant
            """
    
    @classmethod
    def check_plagiarism(cls, content: str) -> Dict[str, Any]:
        """Check for plagiarism in student submission."""
        prompt = f"""
        You are an AI plagiarism detection system. Please analyze the following text for potential plagiarism.
        
        TEXT TO ANALYZE:
        {content}
        
        Provide an analysis of the originality of this text. Look for:
        1. Common phrases or patterns that might indicate copied content
        2. Writing style inconsistencies
        3. Unusual vocabulary or phrasing that might be copied
        
        Format your response as a JSON object with the following structure:
        ```json
        {{
            "originality_score": <score_between_0_and_100>,
            "potential_issues": [
                "issue1",
                "issue2",
                ...
            ],
            "recommendation": "your recommendation"
        }}
        ```
        
        The originality score should be higher for more original content and lower for potentially plagiarized content.
        """
        
        try:
            response_text = cls.generate_text(prompt)
            result = parse_json_response(response_text)
            
            # Validate the result
            if "originality_score" not in result:
                logger.warning(f"Invalid plagiarism check result: {result}")
                result["originality_score"] = 50
            
            return result
        except Exception as e:
            logger.error(f"Error checking plagiarism: {str(e)}")
            return {
                "originality_score": 50,
                "potential_issues": ["Unable to analyze due to an error"],
                "recommendation": "Manual review recommended"
            }