"""Feedback service for personalized student feedback."""
from edumate.services.gemini_service import GeminiService


class FeedbackService:
    """Service for generating personalized feedback for students."""
    
    def __init__(self):
        """Initialize the feedback service."""
        self.gemini_service = GeminiService()
    
    def generate_feedback(self, submission, tone="constructive"):
        """Generate personalized feedback for a submission."""
        if not submission or not submission.assignment:
            return "Unable to generate feedback for this submission."
        
        # Use Gemini to generate personalized feedback
        feedback = self.gemini_service.generate_feedback(submission, tone)
        
        return feedback
    
    def generate_improvement_plan(self, student, course):
        """Generate an improvement plan for a student in a course."""
        if not student or not course:
            return "Unable to generate improvement plan."
        
        # Get all graded submissions for the student in the course
        submissions = self._get_student_submissions(student, course)
        
        if not submissions:
            return "No graded submissions available to generate an improvement plan."
        
        # Analyze submissions to identify patterns
        strengths, weaknesses = self._analyze_submissions(submissions)
        
        # Generate improvement plan
        prompt = f"""
        Generate a personalized improvement plan for {student.get_full_name()} in the course {course.name}.
        
        Student's strengths:
        {self._format_list(strengths)}
        
        Areas needing improvement:
        {self._format_list(weaknesses)}
        
        Create a detailed, actionable improvement plan that:
        1. Acknowledges and builds on the student's strengths
        2. Addresses each area needing improvement with specific strategies
        3. Includes recommended resources for each area
        4. Provides a timeline with milestones
        5. Suggests ways to measure progress
        
        Format the plan in a clear, encouraging way that motivates the student to take action.
        """
        
        improvement_plan = self.gemini_service.generate_text(prompt)
        
        return improvement_plan
    
    def generate_resource_recommendations(self, student, topic, level="intermediate"):
        """Generate personalized resource recommendations for a student on a topic."""
        if not student or not topic:
            return "Unable to generate resource recommendations."
        
        # Get student's learning style and preferences if available
        learning_style = self._get_student_learning_style(student)
        
        # Generate resource recommendations
        resources = self.gemini_service.suggest_resources(
            topic, 
            student_level=level,
            resource_types=learning_style
        )
        
        return resources
    
    def generate_comparative_feedback(self, submission, previous_submissions):
        """Generate feedback comparing current submission to previous ones."""
        if not submission or not previous_submissions:
            return "Unable to generate comparative feedback."
        
        # Extract relevant information
        current_score = submission.score or 0
        previous_scores = [s.score or 0 for s in previous_submissions]
        avg_previous_score = sum(previous_scores) / len(previous_scores) if previous_scores else 0
        
        # Determine if student is improving
        improving = current_score > avg_previous_score
        
        # Generate comparative feedback
        prompt = f"""
        Generate feedback comparing a student's current submission to their previous ones.
        
        Current submission score: {current_score}
        Average score on previous submissions: {avg_previous_score}
        
        The student is {'improving' if improving else 'not showing improvement'} based on scores.
        
        Provide encouraging, constructive feedback that:
        1. Acknowledges progress or identifies regression
        2. Highlights specific improvements or persistent issues
        3. Offers targeted advice for continued growth
        4. Motivates the student to keep working hard
        
        Keep the tone positive and supportive, even when addressing areas needing improvement.
        """
        
        comparative_feedback = self.gemini_service.generate_text(prompt)
        
        return comparative_feedback
    
    def _get_student_submissions(self, student, course):
        """Get all graded submissions for a student in a course."""
        from edumate.models.submission import Submission
        
        # Get all assignments for the course
        assignments = course.assignments
        
        # Get all graded submissions for these assignments
        submissions = []
        for assignment in assignments:
            submission = assignment.get_submission_for_student(student.id)
            if submission and submission.is_graded:
                submissions.append(submission)
        
        return submissions
    
    def _analyze_submissions(self, submissions):
        """Analyze submissions to identify strengths and weaknesses."""
        if not submissions:
            return [], []
        
        # Extract feedback from submissions
        all_feedback = "\n\n".join([s.feedback or "" for s in submissions if s.feedback])
        
        # Use Gemini to analyze feedback and identify patterns
        prompt = f"""
        Analyze the following feedback from multiple student submissions to identify patterns of strengths and weaknesses.
        
        Feedback:
        {all_feedback[:2000]}  # Limit length
        
        Identify:
        1. 3-5 consistent strengths demonstrated across submissions
        2. 3-5 consistent areas needing improvement across submissions
        
        Format your response as:
        
        STRENGTHS:
        - [strength 1]
        - [strength 2]
        ...
        
        WEAKNESSES:
        - [weakness 1]
        - [weakness 2]
        ...
        """
        
        analysis = self.gemini_service.generate_text(prompt)
        
        # Extract strengths and weaknesses
        strengths = []
        weaknesses = []
        
        strengths_section = False
        weaknesses_section = False
        
        for line in analysis.split('\n'):
            line = line.strip()
            
            if line.lower().startswith('strengths:'):
                strengths_section = True
                weaknesses_section = False
                continue
            
            if line.lower().startswith('weaknesses:'):
                strengths_section = False
                weaknesses_section = True
                continue
            
            if line.startswith('-') and strengths_section:
                strengths.append(line[1:].strip())
            
            if line.startswith('-') and weaknesses_section:
                weaknesses.append(line[1:].strip())
        
        return strengths, weaknesses
    
    def _get_student_learning_style(self, student):
        """Get a student's learning style and preferences."""
        # This would typically come from a student profile or preferences
        # For now, return a default set of resource types
        return "articles, videos, interactive tutorials, books"
    
    def _format_list(self, items):
        """Format a list of items as a bulleted list."""
        if not items:
            return "None identified."
        
        return "\n".join([f"- {item}" for item in items]) 