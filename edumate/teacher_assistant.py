class TeacherAssistant:
    def grade_assignment(self, assignment_text: str) -> dict:
        # ...existing code...
        # Simulated grading logic:
        if not assignment_text.strip():
            grade = 0
            feedback = ["Assignment is empty."]
        else:
            word_count = len(assignment_text.split())
            # Simple grading: word count contributes to grade (max 100)
            grade = min(100, word_count)
            feedback = []
            if word_count < 50:
                feedback.append("Assignment is too short; please elaborate.")
            else:
                feedback.append("Well done! Some sections may be enhanced for clarity.")
            if "improve" in assignment_text.lower():
                feedback.append("Tip: Consider improving structure and organization.")
        return {"grade": grade, "feedback": feedback}
