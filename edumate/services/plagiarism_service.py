"""Plagiarism service for detecting plagiarism in student submissions."""
from edumate.services.gemini_service import GeminiService
from edumate.utils.text_utils import extract_text_from_file, similarity_score


class PlagiarismService:
    """Service for detecting plagiarism in student submissions."""
    
    def __init__(self):
        """Initialize the plagiarism service."""
        self.gemini_service = GeminiService()
    
    def check_plagiarism(self, submission, reference_submissions=None):
        """Check a submission for plagiarism against reference submissions."""
        if not submission:
            return {
                'plagiarism_score': 0,
                'analysis': 'No submission provided.',
                'suspicious_passages': []
            }
        
        # Get content from submission
        content = submission.content or ""
        if submission.file_path:
            file_content = extract_text_from_file(submission.file_path)
            if file_content:
                content = file_content
        
        if not content.strip():
            return {
                'plagiarism_score': 0,
                'analysis': 'No content to check for plagiarism.',
                'suspicious_passages': []
            }
        
        # Get reference submissions if not provided
        if reference_submissions is None:
            reference_submissions = self._get_reference_submissions(submission)
        
        if not reference_submissions:
            return {
                'plagiarism_score': 0,
                'analysis': 'No reference submissions available for comparison.',
                'suspicious_passages': []
            }
        
        # Extract content from reference submissions
        reference_texts = []
        for ref in reference_submissions:
            ref_content = ref.content or ""
            if ref.file_path:
                ref_file_content = extract_text_from_file(ref.file_path)
                if ref_file_content:
                    ref_content = ref_file_content
            
            if ref_content.strip():
                reference_texts.append(ref_content)
        
        if not reference_texts:
            return {
                'plagiarism_score': 0,
                'analysis': 'No content in reference submissions for comparison.',
                'suspicious_passages': []
            }
        
        # Use Gemini to check for plagiarism
        plagiarism_result = self.gemini_service.check_plagiarism(content, reference_texts)
        
        # Parse the result
        result = self._parse_plagiarism_result(plagiarism_result)
        
        # Update submission with plagiarism score
        submission.plagiarism_score = result['plagiarism_score']
        
        return result
    
    def check_internet_plagiarism(self, submission):
        """Check a submission for plagiarism against internet sources."""
        # This would typically use an external API or service
        # For now, we'll use a placeholder implementation
        
        if not submission:
            return {
                'plagiarism_score': 0,
                'analysis': 'No submission provided.',
                'suspicious_passages': []
            }
        
        # Get content from submission
        content = submission.content or ""
        if submission.file_path:
            file_content = extract_text_from_file(submission.file_path)
            if file_content:
                content = file_content
        
        if not content.strip():
            return {
                'plagiarism_score': 0,
                'analysis': 'No content to check for plagiarism.',
                'suspicious_passages': []
            }
        
        # Use Gemini to simulate internet plagiarism check
        prompt = f"""
        Analyze the following text and determine if it appears to be plagiarized from common internet sources.
        
        Text to check:
        {content[:2000]}  # Limit length
        
        Provide an analysis that includes:
        1. An estimated plagiarism percentage
        2. Whether the text appears to be original or copied
        3. Any suspicious passages that might be plagiarized
        4. Potential sources if identifiable
        
        Format your response as:
        
        PLAGIARISM SCORE: [estimated percentage]
        
        ANALYSIS:
        [detailed analysis of potential plagiarism]
        
        SUSPICIOUS PASSAGES:
        [list of potentially plagiarized passages]
        
        POTENTIAL SOURCES:
        [list of potential sources if identifiable]
        """
        
        plagiarism_result = self.gemini_service.generate_text(prompt)
        
        # Parse the result
        result = self._parse_plagiarism_result(plagiarism_result)
        
        return result
    
    def calculate_similarity(self, submission1, submission2):
        """Calculate similarity score between two submissions."""
        if not submission1 or not submission2:
            return 0
        
        # Get content from submissions
        content1 = submission1.content or ""
        if submission1.file_path:
            file_content = extract_text_from_file(submission1.file_path)
            if file_content:
                content1 = file_content
        
        content2 = submission2.content or ""
        if submission2.file_path:
            file_content = extract_text_from_file(submission2.file_path)
            if file_content:
                content2 = file_content
        
        if not content1.strip() or not content2.strip():
            return 0
        
        # Calculate similarity score
        return similarity_score(content1, content2)
    
    def _get_reference_submissions(self, submission):
        """Get reference submissions for plagiarism checking."""
        if not submission or not submission.assignment:
            return []
        
        # Get all submissions for the same assignment except the current one
        return [s for s in submission.assignment.submissions if s.id != submission.id]
    
    def _parse_plagiarism_result(self, plagiarism_result):
        """Parse plagiarism result from Gemini."""
        if not plagiarism_result:
            return {
                'plagiarism_score': 0,
                'analysis': 'No plagiarism analysis available.',
                'suspicious_passages': []
            }
        
        # Extract plagiarism score
        plagiarism_score = 0
        analysis = ""
        suspicious_passages = []
        
        # Parse the result
        lines = plagiarism_result.split('\n')
        section = None
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            if line.lower().startswith('plagiarism score:'):
                # Extract score
                try:
                    score_text = line.split(':', 1)[1].strip()
                    if '%' in score_text:
                        score_text = score_text.replace('%', '').strip()
                    plagiarism_score = float(score_text) / 100
                except:
                    pass
                continue
            
            if line.lower().startswith('analysis:'):
                section = 'analysis'
                continue
            
            if line.lower().startswith('suspicious passages:'):
                section = 'suspicious'
                continue
            
            if section == 'analysis':
                analysis += line + "\n"
            
            if section == 'suspicious' and line.startswith('-'):
                suspicious_passages.append(line[1:].strip())
        
        return {
            'plagiarism_score': plagiarism_score,
            'analysis': analysis.strip(),
            'suspicious_passages': suspicious_passages
        } 