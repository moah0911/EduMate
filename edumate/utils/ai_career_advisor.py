import os
import json
import requests
from typing import List, Dict, Any
import logging
from .logger import log_system_event, log_error
import base64

class AICareerAdvisor:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.api_url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
    
    def analyze_skills(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze student skills using Gemini API
        
        Args:
            student_data: Student profile data including skills, interests, and goals
            
        Returns:
            Dictionary with analysis, recommended careers, and skill gaps
        """
        if not self.api_key:
            log_error("Gemini API key not configured")
            return {"error": "API key not configured"}
            
        try:
            # Construct the prompt for Gemini
            prompt = self._construct_skill_analysis_prompt(student_data)
            
            # Make the API request
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            # Process the response
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                response_text = result['candidates'][0]['content']['parts'][0]['text']
                return self._parse_response(response_text)
            else:
                return {"error": "No response from API"}
                
        except Exception as e:
            log_error(f"Error analyzing skills with Gemini: {str(e)}")
            return {"error": str(e)}
    
    def get_career_advice(self, query: str, student_data: Dict[str, Any]) -> str:
        """
        Get career advice for a specific query
        
        Args:
            query: The career question asked by the student
            student_data: Student profile data
            
        Returns:
            Career advice response from Gemini
        """
        if not self.api_key:
            log_error("Gemini API key not configured")
            return "I'm unable to provide career advice at this moment due to a configuration issue."
            
        try:
            # Construct the prompt
            prompt = f"""
            As an AI career advisor, please provide detailed and personalized career advice for a student with the following profile:
            
            Interests: {', '.join(student_data.get('interests', []))}
            Skills:
            - Technical: {student_data.get('skills', {}).get('technical', 0)}/10
            - Creative: {student_data.get('skills', {}).get('creative', 0)}/10
            - Communication: {student_data.get('skills', {}).get('communication', 0)}/10
            - Leadership: {student_data.get('skills', {}).get('leadership', 0)}/10
            
            Education Level: {student_data.get('education', {}).get('level', 'Not specified')}
            Career Goals: {student_data.get('goals', 'Not specified')}
            
            The student is asking: "{query}"
            
            Please provide a helpful, informative, and actionable response that addresses their question.
            """
            
            # Make the API request
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            # Process the response
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                response_text = result['candidates'][0]['content']['parts'][0]['text']
                return response_text
            else:
                return "I'm unable to provide specific advice at this moment. Please try again later."
                
        except Exception as e:
            log_error(f"Error getting career advice from Gemini: {str(e)}")
            return "I encountered an error while processing your question. Please try again later."
    
    def _construct_skill_analysis_prompt(self, student_data: Dict[str, Any]) -> str:
        """Construct a prompt for skill analysis"""
        interests = ', '.join(student_data.get('interests', []))
        skills = student_data.get('skills', {})
        goals = student_data.get('goals', 'Not specified')
        
        return f"""
        Please analyze the following student profile and provide career recommendations and skill gaps analysis.
        
        Student Profile:
        - Interests: {interests}
        - Technical Skills: {skills.get('technical', 0)}/10
        - Creative Skills: {skills.get('creative', 0)}/10
        - Communication Skills: {skills.get('communication', 0)}/10
        - Leadership Skills: {skills.get('leadership', 0)}/10
        - Career Goals: {goals}
        
        Please provide your analysis in the following JSON format:
        {{
            "analysis": "A paragraph summarizing your analysis of the student's profile",
            "recommended_careers": [
                {{
                    "title": "Career Title",
                    "match": match_percentage_as_integer,
                    "description": "Brief description of the career",
                    "outlook": "Job market outlook",
                    "salary_range": "Typical salary range",
                    "education": "Required education",
                    "skills_needed": ["Skill 1", "Skill 2", "Skill 3", "Skill 4"]
                }}
            ],
            "skill_gaps": ["Skill Gap 1", "Skill Gap 2", "Skill Gap 3"],
            "next_steps": ["Recommended Step 1", "Recommended Step 2", "Recommended Step 3"]
        }}
        
        Provide 3-5 career recommendations sorted by match percentage (highest first).
        """
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the response from Gemini"""
        try:
            # Extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # If no JSON is found, return the text as analysis
                return {
                    "analysis": response_text,
                    "recommended_careers": [],
                    "skill_gaps": [],
                    "next_steps": []
                }
        except json.JSONDecodeError:
            # If JSON parsing fails, return the text as analysis
            return {
                "analysis": response_text,
                "recommended_careers": [],
                "skill_gaps": [],
                "next_steps": []
            }
