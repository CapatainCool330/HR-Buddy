import json
import re
import os
from thefuzz import process

class ChatEngine:
    def __init__(self, faq_path="data/faqs.json", leaves_path="data/leaves.json"):
        self.data_dir = os.path.dirname(faq_path)
        self.faq_path = os.path.join(os.path.dirname(__file__), faq_path)
        self.leaves_path = os.path.join(os.path.dirname(__file__), leaves_path)
        
        self.faqs = self._load_json(self.faq_path, [])
        self.faq_questions = [f["question"] for f in self.faqs]
        self.leave_applications = self._load_json(self.leaves_path, {})
        self.sessions = {}

    def _load_json(self, path, default):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    def _save_json(self, path, data):
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving to {path}: {e}")

    def process_message(self, message: str, session_id: str = "default") -> dict:
        """
        Process the user message and return a structured response.
        """
        original_message = message # Keep case for learning
        message = message.lower().strip()

        # 0. Check Session State (Context)
        current_state = self.sessions.get(session_id, {}).get("state")
        
        if current_state == "WAITING_FOR_LEAVE_DAYS":
            return self._handle_leave_days(message, session_id)

        # 1. Learning Command (e.g., "Learn: Question -> Answer")
        if message.startswith("learn:"):
            return self._handle_learning(original_message)

        # 2. Check for Intents (Structured Actions)
        intent_response = self._check_intents(message, session_id)
        if intent_response:
            return intent_response

        # 3. Check Knowledge Base (FAQs)
        faq_response = self._check_knowledge_base(message)
        if faq_response:
            return faq_response

        # 4. Fallback
        return {
            "type": "text",
            "content": "I'm sorry, I didn't quite catch that. Could you please rephrase? You can ask me about leave policies, holidays, or apply for leave. (You can also teach me! Type 'Learn: Question -> Answer')"
        }

    def _handle_learning(self, message: str):
        # Format: "Learn: What is wifi? -> 12345"
        try:
            content = message.split(":", 1)[1].strip()
            question, answer = content.split("->")
            question = question.strip()
            answer = answer.strip()
            
            new_faq = {
                "question": question,
                "answer": answer,
                "keywords": question.lower().split()
            }
            
            self.faqs.append(new_faq)
            self.faq_questions.append(question)
            self._save_json(self.faq_path, self.faqs)
            
            return {
                "type": "text",
                "content": f"Thanks! I've learned a new fact: '{question}'."
            }
        except ValueError:
             return {
                "type": "text",
                "content": "To teach me, use the format: 'Learn: [Question] -> [Answer]'"
            }
    
    def _handle_leave_days(self, message: str, session_id: str):
        # Try to extract a number
        numbers = re.findall(r'\d+', message)
        
        if numbers:
            days = numbers[0]
            # Save to Persistent DB
            self.leave_applications[session_id] = {
                "days": days,
                "status": "Pending Approval",
                "timestamp": str(os.path.getmtime(self.faq_path)) # Mock timestamp
            }
            self._save_json(self.leaves_path, self.leave_applications)
            
            # Clear state
            if session_id in self.sessions:
                del self.sessions[session_id]
                
            return {
                "type": "text",
                "content": f"Leave applied for {days} days. Status: Pending Approval. (Saved to database)"
            }
        else:
            return {
                "type": "text",
                "content": "Please specify the number of days (e.g., '2 days')."
            }

    def _check_intents(self, message: str, session_id: str):
        # Intent: Apply for leave
        # Pattern match: "apply" + "leave" or "request" + "leave" or "take off" or "day off"
        if ("apply" in message or "request" in message or "want" in message) and ("leave" in message or "off" in message):
            # Set state
            self.sessions[session_id] = {"state": "WAITING_FOR_LEAVE_DAYS"}
            return {
                "type": "action",
                "action": "apply_leave",
                "content": "Sure, I can help with that. How many days of leave do you want to apply for?"
            }
        
        # Intent: Check Status
        if ("status" in message or "check" in message or "approve" in message) and ("application" in message or "leave" in message):
             app = self.leave_applications.get(session_id)
             if app:
                 return {
                    "type": "text",
                    "content": f"You have a pending leave application for {app['days']} days. Current Status: {app['status']}."
                }
             else:
                 return {
                    "type": "text",
                    "content": "You currently have no pending leave applications."
                }
            
        return None

    def _check_knowledge_base(self, message: str):
        if not self.faq_questions:
            return None
        
        # Find best match
        # process.extractOne returns (match, score)
        match, score = process.extractOne(message, self.faq_questions)
        
        if score > 60:  # Threshold for acceptance
            # Find the full FAQ object
            for faq in self.faqs:
                if faq["question"] == match:
                    return {
                        "type": "text",
                        "content": faq["answer"]
                    }
        
        return None
