import json
import os
import random
from typing import List, Dict, Any
import logging
from datetime import datetime
from .logger import log_system_event

class QuizManager:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.quizzes_file = os.path.join(data_dir, 'quizzes.json')
        self.quiz_attempts_file = os.path.join(data_dir, 'quiz_attempts.json')
        self._ensure_data_files()

    def _ensure_data_files(self):
        """Ensure quiz data files exist and are properly initialized."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if not os.path.exists(self.quizzes_file):
            with open(self.quizzes_file, 'w') as f:
                json.dump(self._generate_sample_quizzes(), f, indent=4)
                
        if not os.path.exists(self.quiz_attempts_file):
            with open(self.quiz_attempts_file, 'w') as f:
                json.dump([], f, indent=4)

    def _generate_sample_quizzes(self) -> List[Dict[str, Any]]:
        """Generate a set of sample quizzes across different subjects."""
        return [
            # Computer Science Quiz
            {
                "id": 1,
                "title": "Fundamentals of Programming",
                "description": "Test your knowledge of programming basics",
                "subject": "Computer Science",
                "time_limit_minutes": 20,
                "passing_score": 70,
                "difficulty": "Beginner",
                "questions": [
                    {
                        "id": 1,
                        "text": "Which of the following is NOT a programming paradigm?",
                        "type": "multiple_choice",
                        "options": [
                            "Procedural Programming",
                            "Object-Oriented Programming",
                            "Functional Programming",
                            "Descriptive Programming"
                        ],
                        "correct_answer": "Descriptive Programming",
                        "explanation": "Descriptive Programming is not a standard programming paradigm. The main paradigms include Procedural, Object-Oriented, Functional, and Logic Programming."
                    },
                    {
                        "id": 2,
                        "text": "What does the acronym 'API' stand for?",
                        "type": "multiple_choice",
                        "options": [
                            "Application Programming Interface",
                            "Application Process Integration",
                            "Automated Programming Interface",
                            "Application Protocol Interface"
                        ],
                        "correct_answer": "Application Programming Interface",
                        "explanation": "API stands for Application Programming Interface. It defines the ways different software components should interact."
                    },
                    {
                        "id": 3,
                        "text": "Which data structure operates on a Last-In-First-Out (LIFO) principle?",
                        "type": "multiple_choice",
                        "options": [
                            "Queue",
                            "Stack",
                            "Linked List",
                            "Tree"
                        ],
                        "correct_answer": "Stack",
                        "explanation": "A Stack follows the Last-In-First-Out (LIFO) principle, where the last element added is the first one to be removed."
                    },
                    {
                        "id": 4,
                        "text": "What is the time complexity of binary search on a sorted array?",
                        "type": "multiple_choice",
                        "options": [
                            "O(1)",
                            "O(n)",
                            "O(log n)",
                            "O(n²)"
                        ],
                        "correct_answer": "O(log n)",
                        "explanation": "Binary search has a time complexity of O(log n) because it divides the search interval in half with each step."
                    },
                    {
                        "id": 5,
                        "text": "Which of the following is an example of a high-level programming language?",
                        "type": "multiple_choice",
                        "options": [
                            "Assembly",
                            "Machine Code",
                            "Python",
                            "Microcode"
                        ],
                        "correct_answer": "Python",
                        "explanation": "Python is a high-level programming language. Assembly and Machine Code are low-level languages, and Microcode is even lower level, directly controlling processor operations."
                    }
                ]
            },
            # Mathematics Quiz
            {
                "id": 2,
                "title": "Calculus Concepts",
                "description": "Test your understanding of basic calculus principles",
                "subject": "Mathematics",
                "time_limit_minutes": 30,
                "passing_score": 75,
                "difficulty": "Intermediate",
                "questions": [
                    {
                        "id": 1,
                        "text": "What is the derivative of e^x?",
                        "type": "multiple_choice",
                        "options": [
                            "e^x",
                            "x·e^x",
                            "e^(x-1)",
                            "ln(x)"
                        ],
                        "correct_answer": "e^x",
                        "explanation": "The function e^x is its own derivative, making it a unique and important function in calculus."
                    },
                    {
                        "id": 2,
                        "text": "What is the integral of 1/x?",
                        "type": "multiple_choice",
                        "options": [
                            "x",
                            "ln|x| + C",
                            "1/(x+1) + C",
                            "e^x + C"
                        ],
                        "correct_answer": "ln|x| + C",
                        "explanation": "The integral of 1/x is ln|x| + C, where C is the constant of integration."
                    },
                    {
                        "id": 3,
                        "text": "Which of the following represents the chain rule for differentiation?",
                        "type": "multiple_choice",
                        "options": [
                            "d/dx[f(g(x))] = f'(g(x)) × g'(x)",
                            "d/dx[f(g(x))] = f'(x) × g'(x)",
                            "d/dx[f(g(x))] = f(x) × g(x)",
                            "d/dx[f(g(x))] = f'(x)/g'(x)"
                        ],
                        "correct_answer": "d/dx[f(g(x))] = f'(g(x)) × g'(x)",
                        "explanation": "The chain rule states that the derivative of a composite function is the derivative of the outer function evaluated at the inner function, multiplied by the derivative of the inner function."
                    },
                    {
                        "id": 4,
                        "text": "What is the limit of sin(x)/x as x approaches 0?",
                        "type": "multiple_choice",
                        "options": [
                            "0",
                            "1",
                            "∞",
                            "Does not exist"
                        ],
                        "correct_answer": "1",
                        "explanation": "The limit of sin(x)/x as x approaches 0 is 1. This is a fundamental limit in calculus and can be proven using the squeeze theorem."
                    },
                    {
                        "id": 5,
                        "text": "What is the second derivative of position with respect to time?",
                        "type": "multiple_choice",
                        "options": [
                            "Velocity",
                            "Acceleration",
                            "Jerk",
                            "Momentum"
                        ],
                        "correct_answer": "Acceleration",
                        "explanation": "The second derivative of position with respect to time is acceleration. The first derivative gives velocity."
                    }
                ]
            },
            # Physics Quiz
            {
                "id": 3,
                "title": "Classical Mechanics",
                "description": "Test your knowledge of Newton's laws and applications",
                "subject": "Physics",
                "time_limit_minutes": 25,
                "passing_score": 70,
                "difficulty": "Intermediate",
                "questions": [
                    {
                        "id": 1,
                        "text": "What is Newton's First Law of Motion?",
                        "type": "multiple_choice",
                        "options": [
                            "F = ma",
                            "For every action, there is an equal and opposite reaction",
                            "An object at rest stays at rest, and an object in motion stays in motion unless acted upon by a net force",
                            "Energy cannot be created or destroyed, only transformed"
                        ],
                        "correct_answer": "An object at rest stays at rest, and an object in motion stays in motion unless acted upon by a net force",
                        "explanation": "Newton's First Law, also known as the Law of Inertia, states that an object will maintain its state of rest or uniform motion in a straight line unless acted upon by an external force."
                    },
                    {
                        "id": 2,
                        "text": "What is the SI unit of force?",
                        "type": "multiple_choice",
                        "options": [
                            "Watt",
                            "Joule",
                            "Newton",
                            "Pascal"
                        ],
                        "correct_answer": "Newton",
                        "explanation": "The SI unit of force is the Newton (N), which is defined as the force needed to accelerate a 1kg mass at 1 m/s²."
                    },
                    {
                        "id": 3,
                        "text": "Which of the following is a vector quantity?",
                        "type": "multiple_choice",
                        "options": [
                            "Time",
                            "Mass",
                            "Energy",
                            "Velocity"
                        ],
                        "correct_answer": "Velocity",
                        "explanation": "Velocity is a vector quantity because it has both magnitude (speed) and direction. Time, mass, and energy are scalar quantities."
                    },
                    {
                        "id": 4,
                        "text": "What is the law of conservation of momentum?",
                        "type": "multiple_choice",
                        "options": [
                            "The total momentum of an isolated system remains constant",
                            "The total energy of an isolated system remains constant",
                            "The total force in an isolated system remains constant",
                            "The total mass in an isolated system remains constant"
                        ],
                        "correct_answer": "The total momentum of an isolated system remains constant",
                        "explanation": "The law of conservation of momentum states that the total momentum of an isolated system (where no external forces act) remains constant over time."
                    },
                    {
                        "id": 5,
                        "text": "What happens to the gravitational force between two objects when the distance between them is doubled?",
                        "type": "multiple_choice",
                        "options": [
                            "It doubles",
                            "It halves",
                            "It becomes one-fourth",
                            "It remains the same"
                        ],
                        "correct_answer": "It becomes one-fourth",
                        "explanation": "According to Newton's Law of Universal Gravitation, the gravitational force is inversely proportional to the square of the distance. So if the distance doubles, the force becomes (1/2)² = 1/4 of its original value."
                    }
                ]
            },
            # Biology Quiz
            {
                "id": 4,
                "title": "Cell Biology Essentials",
                "description": "Test your knowledge of cellular structures and functions",
                "subject": "Biology",
                "time_limit_minutes": 20,
                "passing_score": 70,
                "difficulty": "Beginner",
                "questions": [
                    {
                        "id": 1,
                        "text": "Which organelle is known as the 'powerhouse of the cell'?",
                        "type": "multiple_choice",
                        "options": [
                            "Nucleus",
                            "Mitochondria",
                            "Endoplasmic Reticulum",
                            "Golgi Apparatus"
                        ],
                        "correct_answer": "Mitochondria",
                        "explanation": "Mitochondria are known as the 'powerhouse of the cell' because they generate most of the cell's supply of adenosine triphosphate (ATP), the energy currency of the cell."
                    },
                    {
                        "id": 2,
                        "text": "What is the primary function of chloroplasts in plant cells?",
                        "type": "multiple_choice",
                        "options": [
                            "Cellular respiration",
                            "Protein synthesis",
                            "Photosynthesis",
                            "Waste removal"
                        ],
                        "correct_answer": "Photosynthesis",
                        "explanation": "Chloroplasts contain chlorophyll and are responsible for photosynthesis, the process by which plants convert light energy into chemical energy."
                    },
                    {
                        "id": 3,
                        "text": "Which of the following is NOT a component of the cell membrane?",
                        "type": "multiple_choice",
                        "options": [
                            "Phospholipids",
                            "Cholesterol",
                            "Proteins",
                            "DNA"
                        ],
                        "correct_answer": "DNA",
                        "explanation": "The cell membrane is composed mainly of a phospholipid bilayer with embedded proteins and cholesterol. DNA is primarily found in the nucleus and mitochondria."
                    },
                    {
                        "id": 4,
                        "text": "What is the process by which cells engulf particles or fluids?",
                        "type": "multiple_choice",
                        "options": [
                            "Exocytosis",
                            "Osmosis",
                            "Diffusion",
                            "Endocytosis"
                        ],
                        "correct_answer": "Endocytosis",
                        "explanation": "Endocytosis is the process by which cells engulf external particles or fluids by forming vesicles from the cell membrane. Exocytosis is the opposite process."
                    },
                    {
                        "id": 5,
                        "text": "Which cell organelle is responsible for protein synthesis?",
                        "type": "multiple_choice",
                        "options": [
                            "Ribosome",
                            "Lysosome",
                            "Vacuole",
                            "Peroxisome"
                        ],
                        "correct_answer": "Ribosome",
                        "explanation": "Ribosomes are responsible for protein synthesis. They can be found free in the cytoplasm or attached to the endoplasmic reticulum."
                    }
                ]
            },
            # Chemistry Quiz
            {
                "id": 5,
                "title": "Chemical Reactions and Equations",
                "description": "Test your understanding of chemical reaction types and balancing equations",
                "subject": "Chemistry",
                "time_limit_minutes": 25,
                "passing_score": 75,
                "difficulty": "Intermediate",
                "questions": [
                    {
                        "id": 1,
                        "text": "What type of reaction is: 2H₂ + O₂ → 2H₂O?",
                        "type": "multiple_choice",
                        "options": [
                            "Decomposition",
                            "Single displacement",
                            "Double displacement",
                            "Synthesis (Combination)"
                        ],
                        "correct_answer": "Synthesis (Combination)",
                        "explanation": "This is a synthesis or combination reaction where two or more substances combine to form a single product."
                    },
                    {
                        "id": 2,
                        "text": "In the reaction: C₃H₈ + 5O₂ → 3CO₂ + 4H₂O, what is being oxidized?",
                        "type": "multiple_choice",
                        "options": [
                            "Oxygen",
                            "Carbon",
                            "Hydrogen",
                            "Both Carbon and Hydrogen"
                        ],
                        "correct_answer": "Both Carbon and Hydrogen",
                        "explanation": "In this combustion reaction, the carbon in C₃H₈ is oxidized from -8/3 to +4, and hydrogen is oxidized from +1 to +1 (in H₂O). Both elements in propane are being oxidized."
                    },
                    {
                        "id": 3,
                        "text": "What is the balanced equation for the reaction between aluminum and copper(II) sulfate?",
                        "type": "multiple_choice",
                        "options": [
                            "Al + CuSO₄ → AlSO₄ + Cu",
                            "2Al + 3CuSO₄ → Al₂(SO₄)₃ + 3Cu",
                            "Al + Cu₂SO₄ → Al₂SO₄ + Cu",
                            "2Al + Cu₂SO₄ → 2AlSO₄ + Cu"
                        ],
                        "correct_answer": "2Al + 3CuSO₄ → Al₂(SO₄)₃ + 3Cu",
                        "explanation": "This is a single displacement reaction where aluminum replaces copper in copper(II) sulfate. The balanced equation accounts for the charges of Al³⁺ and Cu²⁺."
                    },
                    {
                        "id": 4,
                        "text": "Which of the following is an endothermic reaction?",
                        "type": "multiple_choice",
                        "options": [
                            "Combustion of methane",
                            "Rusting of iron",
                            "Photosynthesis",
                            "Neutralization of an acid with a base"
                        ],
                        "correct_answer": "Photosynthesis",
                        "explanation": "Photosynthesis is an endothermic reaction because it absorbs energy from sunlight. The other reactions listed are exothermic, releasing energy."
                    },
                    {
                        "id": 5,
                        "text": "What is the pH of a 0.01 M HCl solution?",
                        "type": "multiple_choice",
                        "options": [
                            "1",
                            "2",
                            "12",
                            "14"
                        ],
                        "correct_answer": "2",
                        "explanation": "The pH of an acidic solution is calculated as -log[H⁺]. For a 0.01 M HCl solution, pH = -log(0.01) = -log(10⁻²) = 2."
                    }
                ]
            }
        ]
    
    def get_all_quizzes(self) -> List[Dict[str, Any]]:
        """Get all available quizzes."""
        try:
            with open(self.quizzes_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            log_system_event(f"Error loading quizzes: {str(e)}")
            return []
    
    def get_quiz_by_id(self, quiz_id: int) -> Dict[str, Any]:
        """Get a specific quiz by ID."""
        quizzes = self.get_all_quizzes()
        for quiz in quizzes:
            if quiz['id'] == quiz_id:
                return quiz
        return None
    
    def get_quizzes_by_subject(self, subject: str) -> List[Dict[str, Any]]:
        """Get all quizzes for a specific subject."""
        quizzes = self.get_all_quizzes()
        return [quiz for quiz in quizzes if quiz['subject'] == subject]
    
    def get_quizzes_by_course(self, course_id: int) -> List[Dict[str, Any]]:
        """Get all quizzes for a specific course."""
        all_quizzes = self.get_all_quizzes()
        return [quiz for quiz in all_quizzes if quiz.get('course_id') == course_id]
    
    def add_quiz(self, quiz_data: Dict[str, Any]) -> bool:
        """Add a new quiz."""
        try:
            all_quizzes = self.get_all_quizzes()
            
            # Generate a new ID
            new_id = 1
            if all_quizzes:
                new_id = max(quiz["id"] for quiz in all_quizzes) + 1
            
            # Update the quiz data with the ID
            quiz_data["id"] = new_id
            
            # Add created timestamp if not present
            if "created_at" not in quiz_data:
                quiz_data["created_at"] = datetime.now().isoformat()
            
            # Add the quiz
            all_quizzes.append(quiz_data)
            
            # Save to file
            with open(self.quizzes_file, 'w') as f:
                json.dump(all_quizzes, f, indent=4)
            
            log_system_event(f"Added new quiz: {quiz_data['title']}")
            return True
        except Exception as e:
            logging.error(f"Error adding quiz: {str(e)}")
            return False
    
    def update_quiz(self, quiz_id: int, quiz_data: Dict[str, Any]) -> bool:
        """Update an existing quiz."""
        try:
            quizzes = self.get_all_quizzes()
            
            for i, quiz in enumerate(quizzes):
                if quiz['id'] == quiz_id:
                    # Preserve the ID
                    quiz_data['id'] = quiz_id
                    quizzes[i] = quiz_data
                    
                    with open(self.quizzes_file, 'w') as f:
                        json.dump(quizzes, f, indent=4)
                    
                    return True
            
            return False
        except Exception as e:
            log_system_event(f"Error updating quiz: {str(e)}")
            return False
    
    def delete_quiz(self, quiz_id: int) -> bool:
        """Delete a quiz."""
        try:
            quizzes = self.get_all_quizzes()
            
            for i, quiz in enumerate(quizzes):
                if quiz['id'] == quiz_id:
                    del quizzes[i]
                    
                    with open(self.quizzes_file, 'w') as f:
                        json.dump(quizzes, f, indent=4)
                    
                    return True
            
            return False
        except Exception as e:
            log_system_event(f"Error deleting quiz: {str(e)}")
            return False
    
    def record_quiz_attempt(self, student_id: int, quiz_id: int, score: float, answers: List[Dict[str, Any]]) -> bool:
        """Record a student's quiz attempt."""
        try:
            attempts = self._load_quiz_attempts()
            
            attempt = {
                'id': len(attempts) + 1,
                'student_id': student_id,
                'quiz_id': quiz_id,
                'score': score,
                'answers': answers,
                'timestamp': os.path.basename(__file__)
            }
            
            attempts.append(attempt)
            
            with open(self.quiz_attempts_file, 'w') as f:
                json.dump(attempts, f, indent=4)
            
            return True
        except Exception as e:
            log_system_event(f"Error recording quiz attempt: {str(e)}")
            return False
    
    def get_student_quiz_attempts(self, student_id: int) -> List[Dict[str, Any]]:
        """Get all quiz attempts for a specific student."""
        attempts = self._load_quiz_attempts()
        return [attempt for attempt in attempts if attempt['student_id'] == student_id]
    
    def get_quiz_statistics(self, quiz_id: int) -> Dict[str, Any]:
        """Get statistics for a specific quiz."""
        attempts = self._load_quiz_attempts()
        quiz_attempts = [attempt for attempt in attempts if attempt['quiz_id'] == quiz_id]
        
        if not quiz_attempts:
            return {
                'attempts': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0,
                'passing_rate': 0
            }
        
        scores = [attempt['score'] for attempt in quiz_attempts]
        quiz = self.get_quiz_by_id(quiz_id)
        passing_score = quiz.get('passing_score', 60) if quiz else 60
        passing_attempts = sum(1 for score in scores if score >= passing_score)
        
        return {
            'attempts': len(quiz_attempts),
            'average_score': sum(scores) / len(scores) if scores else 0,
            'highest_score': max(scores) if scores else 0,
            'lowest_score': min(scores) if scores else 0,
            'passing_rate': (passing_attempts / len(quiz_attempts)) * 100 if quiz_attempts else 0
        }
    
    def _load_quiz_attempts(self) -> List[Dict[str, Any]]:
        """Load all quiz attempts."""
        try:
            with open(self.quiz_attempts_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            log_system_event(f"Error loading quiz attempts: {str(e)}")
            return []
