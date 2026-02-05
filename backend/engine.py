import json
import re
import os
from thefuzz import process
import database # Import the new DB module

class ChatEngine:
    def __init__(self, faq_path="data/faqs.json"):
        self.data_dir = os.path.dirname(faq_path)
        self.faq_path = os.path.join(os.path.dirname(__file__), faq_path)
        
        self.faqs = self._load_json(self.faq_path, [])
        self.faq_questions = [f["question"] for f in self.faqs]
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

    async def process_message(self, message: str, user_id: str = "default") -> dict:
        """
        Process the user message and return a structured response.
        """
        original_message = message # Keep case for learning
        message = message.lower().strip()

        # Get Session Data
        session = self.sessions.get(user_id, {})
        current_state = session.get("state")
        authenticated_user = session.get("authenticated_user_id")

        print(f"DEBUG: User={user_id}, State={current_state}, AuthUser={authenticated_user}, Msg={message}")

        # 0. Handle Authentication State
        if current_state == "WAITING_FOR_AUTH":
            print("DEBUG: Handling Auth...")
            return await self._handle_auth(message, user_id)

        # 1. Gating: If not authenticated, force login
        if not authenticated_user:
            self.sessions[user_id] = {
                "state": "WAITING_FOR_AUTH",
                "pending_query": original_message # Save intent
            }
            return {
                "type": "text",
                "content": "👋 Hi! I am HR Buddy. Before we start, **what is your Employee ID?** (e.g., EMP001)"
            }

        # 2. Check Session State (Context)
        if current_state == "WAITING_FOR_LEAVE_DAYS":
            return await self._handle_leave_days(message, user_id)

        # 3. Learning Command (e.g., "Learn: Question -> Answer")
        if message.startswith("learn:"):
            return self._handle_learning(original_message)

        # 4. Check for Intents (Structured Actions)
        # Pass authenticated_user_id instead of session_id for logic
        intent_response = await self._check_intents(message, user_id, authenticated_user)
        if intent_response:
            return intent_response

        # 5. Check Knowledge Base (FAQs)
        faq_response = self._check_knowledge_base(message)
        if faq_response:
            return faq_response

        # 6. Fallback
        print(f"DEBUG: Fallback triggered. User={user_id}, Auth={authenticated_user}, Msg={message}")
        return {
            "type": "text",
            "content": "I'm sorry, I didn't quite catch that. Could you please rephrase? You can ask me about leave policies, holidays, or apply for leave."
        }
    
    async def _handle_auth(self, message: str, session_id: str):
        # Extract ID
        emp_match = re.search(r'\b(EMP\d{3})\b', message.upper())
        if not emp_match:
             return {
                "type": "text",
                "content": "⚠️ Invalid format. Please enter a valid Employee ID like **EMP001**."
            }
        
        target_id = emp_match.group(1)
        
        # Verify in DB
        emp = await database.get_employee_full_details(target_id)
        if not emp:
             return {
                "type": "text",
                "content": f"❌ Employee **{target_id}** not found. Please try again."
            }
        
        # Success: Save Auth State
        pending_query = self.sessions[session_id].get("pending_query")
        
        self.sessions[session_id] = {
            "authenticated_user_id": target_id,
            "user_name": emp['name'],
            "state": "AUTHENTICATED"
        }
        
        welcome_msg = f"✅ Welcome back, **{emp['name']}**! ({emp['role']})\n"
        
        # If there was a pending query, process it immediately
        if pending_query:
            # Recursive call with authenticated state
            response = await self.process_message(pending_query, session_id)
            welcome_msg += f"\nRe: *'{pending_query}'*\n" + response["content"]
            return {
                "type": response["type"],
                "content": welcome_msg
            }
            
        return {
            "type": "text",
            "content": welcome_msg + "How can I help you today?"
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
    
    async def _handle_leave_days(self, message: str, session_id: str):
        # Extract Auth User
        user_id = self.sessions.get(session_id, {}).get("authenticated_user_id")
        if not user_id:
             return {"type": "text", "content": "Session expired. Please re-login."}

        # Try to extract a number
        numbers = re.findall(r'\d+', message)
        
        if numbers:
            days = int(numbers[0])
            # Save to MongoDB
            app_id = await database.create_leave_application(user_id, days)
            
            # Reset state but keep auth
            self.sessions[session_id]["state"] = "AUTHENTICATED"
                
            return {
                "type": "text",
                "content": f"Leave applied for {days} days. Application ID: {app_id}. Status: Pending Approval."
            }
        else:
            return {
                "type": "text",
                "content": "Please specify the number of days (e.g., '2 days')."
            }

    async def _check_intents(self, message: str, session_id: str, user_id: str):
        # Intent: Apply for leave
        if ("apply" in message or "request" in message or "want" in message) and ("leave" in message or "off" in message):
            self.sessions[session_id]["state"] = "WAITING_FOR_LEAVE_DAYS"
            return {
                "type": "action",
                "action": "apply_leave",
                "content": "Sure, I can help with that. How many days of leave do you want to apply for?"
            }
        
        # Intent: Check Status (My Status)
        if ("status" in message or "check" in message or "approve" in message) and ("application" in message or "leave" in message or "my" in message):
             applications = await database.get_user_applications(user_id)
             if applications:
                 latest_app = applications[0]
                 return {
                    "type": "text",
                    "content": f"You have a pending leave application for {latest_app['days']} days. Current Status: {latest_app['status']}."
                }
             else:
                 return {
                    "type": "text",
                    "content": "You currently have no pending leave applications."
                }

        # Intent: Check Leave Balance (My Balance)
        if ("how many" in message or "remaining" in message or "balance" in message) and ("leave" in message or "days" in message):
            user_data = await database.get_user_balance(user_id)
            return {
                "type": "text",
                "content": f"You have {user_data['annual_leave']} days of Annual Leave and {user_data['sick_leave']} days of Sick Leave remaining."
            }

        # Intent: Admin Lookup (Employee ID)
        emp_match = re.search(r'\b(EMP\d{3})\b', message.upper())
        if emp_match:
            target_id = emp_match.group(1)
            emp = await database.get_employee_full_details(target_id)
            
            if emp:
                # Format Response
                response = f"📋 **Employee Details: {target_id}**\n"
                response += f"**Name:** {emp['name']}\n"
                response += f"**Role:** {emp['role']} ({emp['department']})\n"
                response += f"**Manager:** {emp['manager']}\n"
                response += f"**Performance:** {'⭐' * emp['performance_rating']}\n"
                response += f"**Leave Balance:** {emp['annual_leave']} Annual, {emp['sick_leave']} Sick\n"
                
                if emp.get("recent_leaves"):
                    response += "\n**Recent Leaves:**\n"
                    for leave in emp["recent_leaves"][:3]:
                        response += f"- {leave['days']} days ({leave['status']})\n"
                
                return {
                    "type": "text",
                    "content": response
                }
            else:
                 return {
                    "type": "text",
                    "content": f"❌ Employee {target_id} not found in the database."
                }
            
        return None

    def _check_knowledge_base(self, message: str):
        if not self.faq_questions:
            return None
        
        match, score = process.extractOne(message, self.faq_questions)
        
        if score > 60:
            for faq in self.faqs:
                if faq["question"] == match:
                    return {
                        "type": "text",
                        "content": faq["answer"]
                    }
        
        return None
