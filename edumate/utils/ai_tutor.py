"""
AI Tutor module for EduMate.

This module provides an AI-powered tutor that can answer student questions
about course content, provide explanations, and assist with learning.
"""

import os
import json
import numpy as np
from datetime import datetime
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class AITutor:
    """Class to provide AI tutoring capabilities."""
    
    def __init__(self, data_dir="data/ai_tutor"):
        """Initialize the AITutor class.
        
        Args:
            data_dir (str): Directory to store AI tutor data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Create subdirectories
        self.knowledge_dir = os.path.join(data_dir, "knowledge_base")
        self.sessions_dir = os.path.join(data_dir, "sessions")
        self.feedback_dir = os.path.join(data_dir, "feedback")
        
        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.feedback_dir, exist_ok=True)
        
        # Download NLTK data if needed
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        # Initialize stop words
        self.stop_words = set(stopwords.words('english'))
        
        # Initialize knowledge base
        self.knowledge_base = self._load_knowledge_base()
        
        # Initialize tutoring strategies
        self.tutoring_strategies = {
            "socratic": "Ask leading questions to guide the student to the answer",
            "direct": "Provide clear, direct explanations",
            "example_based": "Use examples to illustrate concepts",
            "analogy": "Use analogies to explain complex concepts",
            "visual": "Use visual descriptions and diagrams"
        }
        
        # Initialize learning styles
        self.learning_styles = {
            "visual": "Learns best through images, diagrams, and visual aids",
            "auditory": "Learns best through listening and verbal instructions",
            "reading/writing": "Learns best through reading and writing text",
            "kinesthetic": "Learns best through hands-on activities and practice"
        }
    
    def answer_question(self, question, student_id, course_id, context=None, preferred_style=None):
        """Answer a student's question about course content.
        
        Args:
            question (str): The student's question
            student_id (str): ID of the student asking the question
            course_id (str): ID of the course the question is about
            context (dict, optional): Additional context about the student and course
            preferred_style (str, optional): Preferred tutoring style
            
        Returns:
            dict: Response containing the answer and related information
        """
        # Clean and preprocess the question
        cleaned_question = self._preprocess_text(question)
        
        # Get the student's learning style if available
        learning_style = None
        if context and "learning_style" in context:
            learning_style = context["learning_style"]
        
        # Default to direct style if not specified
        if not preferred_style:
            preferred_style = "direct"
        
        # Find relevant knowledge base entries
        relevant_entries = self._find_relevant_knowledge(cleaned_question, course_id)
        
        if not relevant_entries:
            # If no relevant entries found, provide a generic response
            answer = self._generate_generic_response(question)
            confidence = 0.2
        else:
            # Generate an answer based on relevant knowledge
            answer, confidence = self._generate_answer(
                question, 
                relevant_entries, 
                preferred_style,
                learning_style
            )
        
        # Create response object
        response = {
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "student_id": student_id,
            "course_id": course_id,
            "tutoring_style": preferred_style,
            "sources": [entry["id"] for entry in relevant_entries] if relevant_entries else []
        }
        
        # Save the interaction to the session history
        self._save_interaction(student_id, course_id, question, answer, confidence)
        
        return response
    
    def add_to_knowledge_base(self, content, metadata):
        """Add new content to the knowledge base.
        
        Args:
            content (str): The content to add (e.g., lecture notes, textbook excerpt)
            metadata (dict): Metadata about the content (course, topic, etc.)
            
        Returns:
            str: ID of the new knowledge base entry
        """
        # Generate a unique ID for the entry
        entry_id = f"{metadata.get('course_id', 'general')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Preprocess the content
        processed_content = self._preprocess_text(content)
        
        # Create the knowledge base entry
        entry = {
            "id": entry_id,
            "content": content,
            "processed_content": processed_content,
            "metadata": metadata,
            "added_at": datetime.now().isoformat()
        }
        
        # Save to file
        file_path = os.path.join(self.knowledge_dir, f"{entry_id}.json")
        with open(file_path, 'w') as f:
            json.dump(entry, f, indent=4)
        
        # Add to in-memory knowledge base
        self.knowledge_base.append(entry)
        
        return entry_id
    
    def get_session_history(self, student_id, course_id=None, limit=10):
        """Get the history of tutoring sessions for a student.
        
        Args:
            student_id (str): ID of the student
            course_id (str, optional): Filter by course ID
            limit (int): Maximum number of interactions to return
            
        Returns:
            list: List of tutoring interactions
        """
        history = []
        
        # Get all session files for the student
        session_pattern = f"{student_id}_*.json"
        session_files = [f for f in os.listdir(self.sessions_dir) if re.match(session_pattern, f)]
        
        # Sort by timestamp (newest first)
        session_files.sort(reverse=True)
        
        # Load sessions
        for filename in session_files[:limit]:
            file_path = os.path.join(self.sessions_dir, filename)
            
            try:
                with open(file_path, 'r') as f:
                    session_data = json.load(f)
                    
                    # Filter by course if specified
                    if course_id and session_data.get("course_id") != course_id:
                        continue
                    
                    history.append(session_data)
            except Exception as e:
                print(f"Error loading session file {filename}: {e}")
        
        return history
    
    def provide_feedback(self, student_id, question_id, feedback_type, feedback_text):
        """Record student feedback on a tutoring interaction.
        
        Args:
            student_id (str): ID of the student providing feedback
            question_id (str): ID of the question being rated
            feedback_type (str): Type of feedback (helpful, confusing, incorrect)
            feedback_text (str): Additional feedback text
            
        Returns:
            bool: True if feedback was successfully recorded
        """
        # Create feedback entry
        feedback = {
            "id": f"feedback_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "student_id": student_id,
            "question_id": question_id,
            "feedback_type": feedback_type,
            "feedback_text": feedback_text,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        file_path = os.path.join(self.feedback_dir, f"{feedback['id']}.json")
        with open(file_path, 'w') as f:
            json.dump(feedback, f, indent=4)
        
        return True
    
    def _load_knowledge_base(self):
        """Load the knowledge base from files.
        
        Returns:
            list: List of knowledge base entries
        """
        knowledge_base = []
        
        # List all files in the knowledge directory
        for filename in os.listdir(self.knowledge_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.knowledge_dir, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        entry = json.load(f)
                        knowledge_base.append(entry)
                except Exception as e:
                    print(f"Error loading knowledge base file {filename}: {e}")
        
        return knowledge_base
    
    def _preprocess_text(self, text):
        """Preprocess text for better matching.
        
        Args:
            text (str): Text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        words = word_tokenize(text)
        
        # Remove stop words and punctuation
        words = [word for word in words if word.isalnum() and word not in self.stop_words]
        
        # Join back into a string
        return " ".join(words)
    
    def _find_relevant_knowledge(self, question, course_id, top_n=3, threshold=0.3):
        """Find knowledge base entries relevant to the question.
        
        Args:
            question (str): The preprocessed question
            course_id (str): ID of the course
            top_n (int): Number of top matches to return
            threshold (float): Minimum similarity score
            
        Returns:
            list: List of relevant knowledge base entries
        """
        if not self.knowledge_base:
            return []
        
        # Filter knowledge base by course if possible
        course_entries = [
            entry for entry in self.knowledge_base 
            if entry.get("metadata", {}).get("course_id") == course_id
        ]
        
        # If no course-specific entries, use the entire knowledge base
        if not course_entries:
            course_entries = self.knowledge_base
        
        # Extract processed content from entries
        texts = [entry.get("processed_content", "") for entry in course_entries]
        
        # Add the question to the texts
        texts.append(question)
        
        # Calculate TF-IDF vectors
        vectorizer = TfidfVectorizer().fit_transform(texts)
        vectors = vectorizer.toarray()
        
        # Calculate similarity between the question and all knowledge base entries
        question_vector = vectors[-1]
        similarities = []
        
        for i, entry in enumerate(course_entries):
            similarity = cosine_similarity([vectors[i]], [question_vector])[0][0]
            similarities.append((entry, similarity))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Filter by threshold and get top matches
        relevant_entries = [
            entry for entry, score in similarities 
            if score >= threshold
        ][:top_n]
        
        return relevant_entries
    
    def _generate_answer(self, question, relevant_entries, tutoring_style, learning_style=None):
        """Generate an answer based on relevant knowledge base entries.
        
        Args:
            question (str): The original question
            relevant_entries (list): List of relevant knowledge base entries
            tutoring_style (str): Preferred tutoring style
            learning_style (str, optional): Student's learning style
            
        Returns:
            tuple: (answer, confidence)
        """
        # Extract content from relevant entries
        contents = [entry.get("content", "") for entry in relevant_entries]
        
        # Combine contents
        combined_content = " ".join(contents)
        
        # Extract sentences from the combined content
        sentences = sent_tokenize(combined_content)
        
        # Find sentences most relevant to the question
        question_words = set(self._preprocess_text(question).split())
        
        # Score sentences based on word overlap with the question
        scored_sentences = []
        for sentence in sentences:
            sentence_words = set(self._preprocess_text(sentence).split())
            overlap = len(question_words.intersection(sentence_words))
            score = overlap / max(len(question_words), 1)
            scored_sentences.append((sentence, score))
        
        # Sort by score (highest first)
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Select top sentences
        top_sentences = [sentence for sentence, score in scored_sentences[:3]]
        
        # Calculate confidence based on the scores of top sentences
        confidence = min(0.9, sum(score for _, score in scored_sentences[:3]) / 3)
        
        # Generate answer based on tutoring style
        answer = self._format_answer(question, top_sentences, tutoring_style, learning_style)
        
        return answer, confidence
    
    def _format_answer(self, question, sentences, tutoring_style, learning_style=None):
        """Format the answer based on tutoring style and learning style.
        
        Args:
            question (str): The original question
            sentences (list): Relevant sentences to include in the answer
            tutoring_style (str): Preferred tutoring style
            learning_style (str, optional): Student's learning style
            
        Returns:
            str: Formatted answer
        """
        # Base answer from the sentences
        base_answer = " ".join(sentences)
        
        # Format based on tutoring style
        if tutoring_style == "socratic":
            # Turn the answer into leading questions
            answer_parts = []
            for sentence in sentences:
                # Convert statements to questions when possible
                if "is" in sentence:
                    parts = sentence.split("is", 1)
                    question = f"Have you considered that {parts[0].strip()} might be {parts[1].strip()}?"
                    answer_parts.append(question)
                else:
                    answer_parts.append(f"What do you think about this: {sentence}")
            
            answer = " ".join(answer_parts)
            answer += f" What are your thoughts on these ideas related to your question: '{question}'?"
            
        elif tutoring_style == "example_based":
            # Add an introduction requesting examples
            answer = f"Let me explain with examples: {base_answer}"
            answer += " Does this help you understand the concept? Can you think of another example that applies this idea?"
            
        elif tutoring_style == "analogy":
            # Add an analogy framework
            answer = f"Think of it this way: {base_answer}"
            answer += " It's similar to how [relevant analogy would be here]. Does that comparison help clarify the concept?"
            
        elif tutoring_style == "visual":
            # Emphasize visual elements
            answer = f"Visualize this: {base_answer}"
            answer += " Imagine you could see this concept as a diagram or picture. What elements would it contain?"
            
        else:  # Default to direct style
            answer = f"Here's what you need to know: {base_answer}"
            answer += " Does this answer your question? Let me know if you need any clarification."
        
        # Adapt to learning style if available
        if learning_style:
            if learning_style == "visual" and tutoring_style != "visual":
                answer += " It might help to draw this out or find a diagram that illustrates these concepts."
            elif learning_style == "auditory":
                answer += " Try explaining this concept out loud to reinforce your understanding."
            elif learning_style == "reading/writing":
                answer += " Consider writing a summary of these key points in your own words."
            elif learning_style == "kinesthetic":
                answer += " Can you think of a hands-on activity that would demonstrate this concept?"
        
        return answer
    
    def _generate_generic_response(self, question):
        """Generate a generic response when no relevant knowledge is found.
        
        Args:
            question (str): The original question
            
        Returns:
            str: Generic response
        """
        # List of generic responses
        generic_responses = [
            f"I don't have specific information to answer your question about '{question}'. Could you provide more context or rephrase your question?",
            f"That's an interesting question about '{question}', but I don't have enough information in my knowledge base yet. Could you ask your instructor for more details?",
            f"I'm still learning about this topic. Your question about '{question}' goes beyond what I currently know. Would you like to explore a related topic instead?",
            f"I don't have a complete answer about '{question}' in my database. Would you like me to notify your instructor that you're interested in this topic?"
        ]
        
        # Randomly select a response
        return np.random.choice(generic_responses)
    
    def _save_interaction(self, student_id, course_id, question, answer, confidence):
        """Save a tutoring interaction to the session history.
        
        Args:
            student_id (str): ID of the student
            course_id (str): ID of the course
            question (str): The student's question
            answer (str): The tutor's answer
            confidence (float): Confidence in the answer
        """
        # Create a unique ID for the interaction
        interaction_id = f"{student_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create interaction data
        interaction = {
            "id": interaction_id,
            "student_id": student_id,
            "course_id": course_id,
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        file_path = os.path.join(self.sessions_dir, f"{interaction_id}.json")
        with open(file_path, 'w') as f:
            json.dump(interaction, f, indent=4)
    
    def analyze_question_patterns(self, student_id=None, course_id=None):
        """Analyze patterns in student questions.
        
        Args:
            student_id (str, optional): Filter by student ID
            course_id (str, optional): Filter by course ID
            
        Returns:
            dict: Analysis results
        """
        # Get all session files
        session_files = [f for f in os.listdir(self.sessions_dir) if f.endswith('.json')]
        
        questions = []
        
        # Load sessions
        for filename in session_files:
            file_path = os.path.join(self.sessions_dir, filename)
            
            try:
                with open(file_path, 'r') as f:
                    session_data = json.load(f)
                    
                    # Apply filters
                    if student_id and session_data.get("student_id") != student_id:
                        continue
                    if course_id and session_data.get("course_id") != course_id:
                        continue
                    
                    questions.append({
                        "text": session_data.get("question", ""),
                        "student_id": session_data.get("student_id"),
                        "course_id": session_data.get("course_id"),
                        "timestamp": session_data.get("timestamp"),
                        "confidence": session_data.get("confidence", 0)
                    })
            except Exception as e:
                print(f"Error loading session file {filename}: {e}")
        
        if not questions:
            return {"error": "No questions found matching the filters"}
        
        # Extract common words and phrases
        all_question_text = " ".join([q["text"] for q in questions])
        words = word_tokenize(all_question_text.lower())
        words = [word for word in words if word.isalnum() and word not in self.stop_words]
        
        # Count word frequencies
        word_counts = {}
        for word in words:
            if word not in word_counts:
                word_counts[word] = 0
            word_counts[word] += 1
        
        # Sort by frequency
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        top_words = sorted_words[:20]
        
        # Analyze confidence scores
        confidence_scores = [q["confidence"] for q in questions]
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
        
        # Analyze question frequency over time
        timestamps = [datetime.fromisoformat(q["timestamp"]) for q in questions if "timestamp" in q]
        timestamps.sort()
        
        # Group by day
        days = {}
        for ts in timestamps:
            day_key = ts.strftime('%Y-%m-%d')
            if day_key not in days:
                days[day_key] = 0
            days[day_key] += 1
        
        # Prepare results
        results = {
            "total_questions": len(questions),
            "top_words": top_words,
            "average_confidence": avg_confidence,
            "questions_by_day": days,
            "student_count": len(set(q["student_id"] for q in questions)),
            "course_count": len(set(q["course_id"] for q in questions if "course_id" in q))
        }
        
        return results
