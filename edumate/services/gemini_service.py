"""Gemini service for AI-powered grading and feedback."""
import os
import google.generativeai as genai
from flask import current_app
import openai


class GeminiService:
    """Service for interacting with the Gemini API."""
    
    def __init__(self, api_key=None):
        """Initialize the Gemini service."""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or current_app.config.get('GEMINI_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY') or current_app.config.get('OPENAI_API_KEY')
        self.use_fallback = False
        
        # Configure Gemini
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            self.use_fallback = True
            print("Warning: Gemini API key not found. Using OpenAI fallback if available.")
    
    def generate_text(self, prompt, temperature=0.7, max_tokens=1024):
        """Generate text using Gemini or fallback to OpenAI."""
        if not self.use_fallback and self.api_key:
            try:
                # Use Gemini
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )
                return response.text
            except Exception as e:
                print(f"Error using Gemini API: {e}")
                if self.openai_api_key:
                    self.use_fallback = True
                    print("Falling back to OpenAI.")
                else:
                    return f"Error: {str(e)}"
        
        if self.use_fallback and self.openai_api_key:
            try:
                # Use OpenAI as fallback
                openai.api_key = self.openai_api_key
                response = openai.Completion.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].text.strip()
            except Exception as e:
                return f"Error: {str(e)}"
        
        return "Error: No API keys available for text generation."
    
    def analyze_text(self, text, prompt=None):
        """Analyze text using Gemini or fallback to OpenAI."""
        if not prompt:
            prompt = f"Analyze the following text and provide insights:\n\n{text}"
        else:
            prompt = f"{prompt}\n\n{text}"
        
        return self.generate_text(prompt)
    
    def grade_essay(self, essay_text, rubric, max_score=100):
        """Grade an essay based on a rubric."""
        prompt = f"""
        Grade the following essay based on this rubric:
        
        {rubric}
        
        Essay:
        {essay_text}
        
        Provide a score out of {max_score} and detailed feedback for each criterion in the rubric.
        Format your response as:
        
        SCORE: [numerical score]
        
        FEEDBACK:
        [detailed feedback organized by rubric criteria]
        
        STRENGTHS:
        [bullet points of strengths]
        
        AREAS FOR IMPROVEMENT:
        [bullet points of areas to improve]
        """
        
        return self.generate_text(prompt)
    
    def grade_code(self, code, language, requirements, test_cases=None, max_score=100):
        """Grade code based on requirements and test cases."""
        test_cases_text = ""
        if test_cases:
            test_cases_text = "Test Cases:\n" + "\n".join([f"- {tc}" for tc in test_cases])
        
        prompt = f"""
        Grade the following {language} code based on these requirements:
        
        {requirements}
        
        {test_cases_text}
        
        Code:
        ```{language}
        {code}
        ```
        
        Provide a score out of {max_score} and detailed feedback.
        Format your response as:
        
        SCORE: [numerical score]
        
        CORRECTNESS: [evaluation of whether the code meets the requirements]
        
        CODE QUALITY: [evaluation of code style, efficiency, and best practices]
        
        FEEDBACK:
        [detailed feedback]
        
        STRENGTHS:
        [bullet points of strengths]
        
        AREAS FOR IMPROVEMENT:
        [bullet points of areas to improve]
        """
        
        return self.generate_text(prompt)
    
    def generate_feedback(self, submission, tone="constructive"):
        """Generate personalized feedback for a submission."""
        # Get the submission details
        assignment_type = submission.assignment.assignment_type
        content = submission.content or ""
        score = submission.score or 0
        max_score = submission.assignment.points or 100
        
        # Determine the tone of the feedback
        tone_instruction = ""
        if tone == "encouraging":
            tone_instruction = "Be very encouraging and positive, focusing on strengths while gently suggesting improvements."
        elif tone == "critical":
            tone_instruction = "Be critical and direct, clearly pointing out areas that need improvement."
        elif tone == "neutral":
            tone_instruction = "Be neutral and objective, balancing positive feedback with constructive criticism."
        else:  # constructive
            tone_instruction = "Be constructive, offering specific suggestions for improvement while acknowledging strengths."
        
        prompt = f"""
        Generate personalized feedback for a student submission. {tone_instruction}
        
        Assignment Type: {assignment_type}
        Student Score: {score} out of {max_score}
        
        Submission:
        {content[:1000]}  # Limit content length
        
        Provide detailed, actionable feedback that helps the student understand their strengths and areas for improvement.
        Include specific examples from their work when possible.
        Suggest resources or strategies that could help them improve.
        
        Format your response as:
        
        FEEDBACK:
        [personalized feedback paragraphs]
        
        STRENGTHS:
        [bullet points of specific strengths]
        
        AREAS FOR IMPROVEMENT:
        [bullet points with specific, actionable suggestions]
        
        RESOURCES:
        [2-3 relevant resources that could help the student improve]
        """
        
        return self.generate_text(prompt)
    
    def check_plagiarism(self, text, reference_texts):
        """Check for potential plagiarism using AI analysis."""
        references = "\n\n".join([f"Reference {i+1}:\n{ref[:500]}" for i, ref in enumerate(reference_texts)])
        
        prompt = f"""
        Analyze the following text for potential plagiarism by comparing it with the reference texts.
        
        Text to check:
        {text[:1000]}
        
        Reference texts:
        {references}
        
        Provide an analysis of potential plagiarism, including:
        1. An estimated plagiarism percentage
        2. Specific passages that appear to be plagiarized
        3. Which reference text(s) the plagiarized content appears to come from
        
        Format your response as:
        
        PLAGIARISM SCORE: [estimated percentage]
        
        ANALYSIS:
        [detailed analysis of potential plagiarism]
        
        SUSPICIOUS PASSAGES:
        [list of potentially plagiarized passages with corresponding reference sources]
        """
        
        return self.generate_text(prompt)
    
    def generate_quiz_questions(self, topic, num_questions=5, difficulty="medium"):
        """Generate quiz questions on a specific topic."""
        prompt = f"""
        Generate {num_questions} {difficulty}-difficulty quiz questions about {topic}.
        
        For each question, provide:
        1. A clear question
        2. Multiple choice options (A, B, C, D)
        3. The correct answer
        4. A brief explanation of why that answer is correct
        
        Format each question as:
        
        Question #: [question text]
        A. [option A]
        B. [option B]
        C. [option C]
        D. [option D]
        Correct Answer: [letter]
        Explanation: [explanation]
        """
        
        return self.generate_text(prompt)
    
    def suggest_resources(self, topic, student_level="intermediate", resource_types=None):
        """Suggest learning resources for a specific topic."""
        if not resource_types:
            resource_types = "articles, videos, tutorials, books"
        
        prompt = f"""
        Suggest learning resources about {topic} for a {student_level} level student.
        
        Include a variety of resource types: {resource_types}
        
        For each resource, provide:
        1. Title
        2. Type (article, video, etc.)
        3. Brief description
        4. Why it's helpful for this topic
        5. Where to find it (website, platform, etc.)
        
        Format your response as a list of 5-7 resources, each with the information above.
        """
        
        return self.generate_text(prompt) 