"""Grading service for automated assignment grading."""
import re
from edumate.services.gemini_service import GeminiService
from edumate.utils.text_utils import extract_text_from_file, similarity_score
from edumate.utils.code_utils import run_code, check_code_style


class GradingService:
    """Service for automated grading of assignments."""
    
    def __init__(self):
        """Initialize the grading service."""
        self.gemini_service = GeminiService()
    
    def grade_submission(self, submission):
        """Grade a submission based on its assignment type."""
        if not submission or not submission.assignment:
            return None
        
        assignment = submission.assignment
        assignment_type = assignment.assignment_type
        
        # Get content from file if needed
        content = submission.content or ""
        if submission.file_path:
            file_content = extract_text_from_file(submission.file_path)
            if file_content:
                content = file_content
        
        # Grade based on assignment type
        if assignment_type == 'essay':
            return self.grade_essay(submission, content)
        elif assignment_type == 'code':
            return self.grade_code(submission, content)
        elif assignment_type == 'quiz':
            return self.grade_quiz(submission, content)
        elif assignment_type == 'short_answer':
            return self.grade_short_answer(submission, content)
        elif assignment_type == 'project':
            return self.grade_project(submission, content)
        else:
            return None
    
    def grade_essay(self, submission, content):
        """Grade an essay submission."""
        assignment = submission.assignment
        rubric_text = self._get_rubric_text(assignment)
        
        # Check for plagiarism if there are other submissions
        plagiarism_score = 0
        other_submissions = [s.content for s in assignment.submissions 
                            if s.id != submission.id and s.content]
        if other_submissions:
            plagiarism_result = self.gemini_service.check_plagiarism(content, other_submissions)
            plagiarism_score = self._extract_plagiarism_score(plagiarism_result)
        
        # Grade the essay
        grading_result = self.gemini_service.grade_essay(content, rubric_text, assignment.points)
        
        # Extract score and feedback
        score = self._extract_score(grading_result, assignment.points)
        
        # Apply plagiarism penalty if needed
        if plagiarism_score > 0.3:  # More than 30% plagiarism
            penalty = min(score * 0.5, score * plagiarism_score)  # Up to 50% penalty
            score = max(0, score - penalty)
        
        # Update submission
        submission.score = score
        submission.feedback = grading_result
        submission.plagiarism_score = plagiarism_score
        submission.is_graded = True
        
        # Add criterion scores if rubric exists
        if assignment.rubric and assignment.rubric.criteria:
            self._add_criterion_scores(submission, grading_result)
        
        return submission
    
    def grade_code(self, submission, content):
        """Grade a code submission."""
        assignment = submission.assignment
        rubric_text = self._get_rubric_text(assignment)
        
        # Determine language from file extension or assignment instructions
        language = self._determine_code_language(submission)
        
        # Run the code if possible
        run_result = None
        if language:
            run_result = run_code(content, language)
        
        # Check code style
        style_result = None
        if language:
            style_result = check_code_style(content, language)
        
        # Prepare requirements and test cases
        requirements = assignment.instructions or "No specific requirements provided."
        test_cases = self._extract_test_cases(assignment.instructions)
        
        # Grade the code
        grading_result = self.gemini_service.grade_code(
            content, language, requirements, test_cases, assignment.points
        )
        
        # Extract score and feedback
        score = self._extract_score(grading_result, assignment.points)
        
        # Add execution results to feedback
        feedback = grading_result
        if run_result:
            feedback += f"\n\nCODE EXECUTION RESULTS:\n"
            feedback += f"Success: {run_result.get('success', False)}\n"
            feedback += f"Output: {run_result.get('output', '')}\n"
            feedback += f"Errors: {run_result.get('error', '')}\n"
        
        if style_result:
            feedback += f"\n\nCODE STYLE ANALYSIS:\n"
            feedback += f"Style Issues: {', '.join(style_result.get('issues', []))}\n"
        
        # Update submission
        submission.score = score
        submission.feedback = feedback
        submission.is_graded = True
        
        # Add criterion scores if rubric exists
        if assignment.rubric and assignment.rubric.criteria:
            self._add_criterion_scores(submission, grading_result)
        
        return submission
    
    def grade_quiz(self, submission, content):
        """Grade a quiz submission."""
        assignment = submission.assignment
        
        # Parse quiz answers from content
        student_answers = self._parse_quiz_answers(content)
        
        # Get correct answers from assignment instructions
        correct_answers = self._parse_quiz_answers(assignment.instructions)
        
        if not student_answers or not correct_answers:
            # If we can't parse answers, use AI to grade
            grading_result = self.gemini_service.analyze_text(
                content,
                f"Grade this quiz submission against the correct answers:\n{assignment.instructions}"
            )
            score = self._extract_score(grading_result, assignment.points)
            
            # Update submission
            submission.score = score
            submission.feedback = grading_result
            submission.is_graded = True
            return submission
        
        # Calculate score based on correct answers
        total_questions = len(correct_answers)
        correct_count = 0
        
        feedback = "QUIZ GRADING RESULTS:\n\n"
        
        for question_num, correct_answer in correct_answers.items():
            student_answer = student_answers.get(question_num)
            
            if student_answer and student_answer.lower() == correct_answer.lower():
                correct_count += 1
                feedback += f"Question {question_num}: Correct ✓\n"
            else:
                feedback += f"Question {question_num}: Incorrect ✗\n"
                feedback += f"Your answer: {student_answer}\n"
                feedback += f"Correct answer: {correct_answer}\n\n"
        
        # Calculate score
        score = (correct_count / total_questions) * assignment.points if total_questions > 0 else 0
        
        feedback += f"\nFinal Score: {score}/{assignment.points} ({correct_count}/{total_questions} correct)"
        
        # Update submission
        submission.score = score
        submission.feedback = feedback
        submission.is_graded = True
        
        return submission
    
    def grade_short_answer(self, submission, content):
        """Grade a short answer submission."""
        assignment = submission.assignment
        rubric_text = self._get_rubric_text(assignment)
        
        # Use AI to grade short answer
        grading_result = self.gemini_service.analyze_text(
            content,
            f"Grade this short answer response based on the following rubric:\n{rubric_text}\n\n"
            f"Provide a score out of {assignment.points} and detailed feedback."
        )
        
        # Extract score and feedback
        score = self._extract_score(grading_result, assignment.points)
        
        # Update submission
        submission.score = score
        submission.feedback = grading_result
        submission.is_graded = True
        
        # Add criterion scores if rubric exists
        if assignment.rubric and assignment.rubric.criteria:
            self._add_criterion_scores(submission, grading_result)
        
        return submission
    
    def grade_project(self, submission, content):
        """Grade a project submission."""
        assignment = submission.assignment
        rubric_text = self._get_rubric_text(assignment)
        
        # Use AI to grade project
        grading_result = self.gemini_service.analyze_text(
            content,
            f"Grade this project submission based on the following rubric:\n{rubric_text}\n\n"
            f"Provide a score out of {assignment.points} and detailed feedback for each criterion."
        )
        
        # Extract score and feedback
        score = self._extract_score(grading_result, assignment.points)
        
        # Update submission
        submission.score = score
        submission.feedback = grading_result
        submission.is_graded = True
        
        # Add criterion scores if rubric exists
        if assignment.rubric and assignment.rubric.criteria:
            self._add_criterion_scores(submission, grading_result)
        
        return submission
    
    def _get_rubric_text(self, assignment):
        """Get rubric text from an assignment."""
        if not assignment.rubric:
            return "No rubric provided."
        
        rubric_text = f"Rubric: {assignment.rubric.name}\n\n"
        
        for criterion in assignment.rubric.criteria:
            rubric_text += f"- {criterion.name} ({criterion.max_score} points): {criterion.description}\n"
        
        return rubric_text
    
    def _extract_score(self, grading_result, max_score):
        """Extract numerical score from grading result text."""
        if not grading_result:
            return 0
        
        # Look for score in format "SCORE: X" or "Score: X/Y"
        score_match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?)', grading_result, re.IGNORECASE)
        if score_match:
            try:
                return min(float(score_match.group(1)), max_score)
            except ValueError:
                pass
        
        # Look for score in format "X/Y"
        score_match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)', grading_result)
        if score_match:
            try:
                score = float(score_match.group(1))
                out_of = float(score_match.group(2))
                return (score / out_of) * max_score if out_of > 0 else 0
            except ValueError:
                pass
        
        # If no score found, use AI to extract it
        score_prompt = f"Extract only the numerical score from this grading result. Respond with just the number:\n\n{grading_result}"
        score_text = self.gemini_service.generate_text(score_prompt)
        
        try:
            score = float(score_text.strip())
            return min(score, max_score)
        except ValueError:
            # Default to 70% if we can't extract a score
            return max_score * 0.7
    
    def _extract_plagiarism_score(self, plagiarism_result):
        """Extract plagiarism score from plagiarism check result."""
        if not plagiarism_result:
            return 0
        
        # Look for percentage in format "PLAGIARISM SCORE: X%" or "X% plagiarism"
        score_match = re.search(r'PLAGIARISM SCORE:\s*(\d+(?:\.\d+)?)', plagiarism_result, re.IGNORECASE)
        if score_match:
            try:
                return min(float(score_match.group(1)) / 100, 1.0)
            except ValueError:
                pass
        
        score_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*plagiarism', plagiarism_result, re.IGNORECASE)
        if score_match:
            try:
                return min(float(score_match.group(1)) / 100, 1.0)
            except ValueError:
                pass
        
        # If no score found, use AI to extract it
        score_prompt = f"Extract only the plagiarism percentage from this result. Respond with just the number (0-100):\n\n{plagiarism_result}"
        score_text = self.gemini_service.generate_text(score_prompt)
        
        try:
            score = float(score_text.strip())
            return min(score / 100, 1.0)
        except ValueError:
            return 0
    
    def _add_criterion_scores(self, submission, grading_result):
        """Add criterion scores based on grading result."""
        from edumate.models.submission import CriterionScore
        
        assignment = submission.assignment
        if not assignment.rubric or not assignment.rubric.criteria:
            return
        
        # Clear existing criterion scores
        for cs in submission.criterion_scores:
            cs.delete()
        
        # For each criterion, try to extract a score from the grading result
        for criterion in assignment.rubric.criteria:
            # Look for the criterion name in the grading result
            pattern = rf'{re.escape(criterion.name)}.*?(\d+(?:\.\d+)?)\s*/\s*{criterion.max_score}'
            score_match = re.search(pattern, grading_result, re.IGNORECASE | re.DOTALL)
            
            if score_match:
                try:
                    score = min(float(score_match.group(1)), criterion.max_score)
                except ValueError:
                    score = criterion.max_score * 0.7  # Default to 70%
            else:
                # If no specific score found, allocate proportionally to overall score
                score = (submission.score / assignment.points) * criterion.max_score
            
            # Create criterion score
            criterion_score = CriterionScore(
                submission_id=submission.id,
                criterion_id=criterion.id,
                score=score
            )
            criterion_score.save()
    
    def _determine_code_language(self, submission):
        """Determine the programming language of a code submission."""
        if submission.file_path:
            ext = submission.file_path.split('.')[-1].lower()
            language_map = {
                'py': 'python',
                'java': 'java',
                'cpp': 'cpp',
                'c': 'c',
                'js': 'javascript',
                'html': 'html',
                'css': 'css',
                'php': 'php'
            }
            return language_map.get(ext)
        
        # Try to determine from assignment instructions
        if submission.assignment.instructions:
            instructions = submission.assignment.instructions.lower()
            for lang in ['python', 'java', 'cpp', 'c', 'javascript', 'html', 'css', 'php']:
                if lang in instructions:
                    return lang
        
        # Default to Python
        return 'python'
    
    def _extract_test_cases(self, instructions):
        """Extract test cases from assignment instructions."""
        if not instructions:
            return []
        
        test_cases = []
        
        # Look for test cases section
        test_section_match = re.search(r'test cases?:(.*?)(?:\n\n|$)', instructions, re.IGNORECASE | re.DOTALL)
        if test_section_match:
            test_section = test_section_match.group(1)
            # Extract individual test cases (lines starting with - or * or number)
            case_matches = re.findall(r'(?:^|\n)\s*(?:-|\*|\d+\.)\s*(.*?)(?:\n|$)', test_section)
            test_cases.extend(case_matches)
        
        return test_cases
    
    def _parse_quiz_answers(self, content):
        """Parse quiz answers from content."""
        if not content:
            return {}
        
        answers = {}
        
        # Look for answers in format "1. A" or "Question 1: A"
        answer_matches = re.findall(r'(?:Question\s*)?(\d+)[\.:]\s*([A-D])', content, re.IGNORECASE)
        for question_num, answer in answer_matches:
            answers[question_num] = answer
        
        return answers 