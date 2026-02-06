# HR Buddy 🤖

**HR Buddy** is an intelligent, full-stack HR chatbot designed to assist employees with common queries and leave management. It uses a **Hybrid AI Engine** combining Regex (for strict actions) and Fuzzy Matching (for flexible FAQs) to ensure 100% reliability for critical tasks while maintaining a conversational feel.

## ✨ Features

-   **🧠 Hybrid AI Engine**: Uses `TheFuzz` for similarity matching and Regex for intent parsing.
-   **📝 structured Actions**: Detects intents like "Apply for leave" and triggers multi-turn workflows.
-   **💾 Persistent Memory**: Stores leave applications and learned facts in local JSON files (`leaves.json`, `faqs.json`).
-   **🎓 Dynamic Learning**: You can teach the bot new facts directly in the chat command `Learn: Q -> A`.
-   **⏰ Auto-Wake**: Automatically "pings" the backend on page load to wake up free-tier servers (like Render) instantly.
-   **💬 Modern UI**: Built with React, Tailwind CSS, and Lucide Icons.

## 🛠️ Tech Stack

-   **Frontend**: React (Vite), Tailwind CSS, Native WebSockets (Real-time)
-   **Backend**: Python, FastAPI, Uvicorn, WebSockets
-   **NLP Tools**: `thefuzz`, `regex`
-   **Data Storage**: JSON (Persistence with `data/employees.json`)

## 🚀 Getting Started

### Prerequisites
-   Node.js & npm
-   Python 3.x

### 1. Backend Setup
The backend runs on port `8000`.

```bash
cd backend
pip install -r requirements.txt
# Runs with Trust Proxy Config
uvicorn main:app --reload --proxy-headers
```

### 2. Frontend Setup
The frontend runs on port `5173`.

```bash
cd frontend
npm install
npm run dev
```

## 📖 How to Use

1.  **Login**: The bot will ask for your Employee ID. Enter a valid ID (e.g., `EMP001`, `EMP042`).
2.  **Ask Questions**: "What is the leave policy?", "Do we have health insurance?"
3.  **Apply for Leave**: "I want to apply for sick leave" -> Bot asks "How many days?" -> "2 days".
4.  **My Data**:
    -   "What is my leave balance?" -> Returns *your* specific balance.
    -   "Check my application status" -> Returns *your* recent requests.
5.  **Check Status**: "what is the status of my leave application?"
6.  **Teach the Bot**: "Learn: Who is the CEO? -> Ayush is the CEO."
7.  **Admin Lookup**: "Check details for EMP005" -> Returns full employee profile (Role, Manager, Rating).

> **Note**: All data (Leaves, New FAQs) is saved instantly to the `data/` folder. It persists even if you restart the server! 💾

## 🎲 Mock Data Setup
To populate the database with 50+ fake employees for testing:

```bash
# Verify you have 'faker' installed
pip install faker
# Run the seed script
python backend/seed_db.py
```
*This will reset the database and create users with IDs EMP001 to EMP050.*

## 📂 Project Structure

```
├── backend/
│   ├── data/           # Stores faqs.json and leaves.json
│   ├── engine.py       # Core NLP Logic (Intents + Fuzzy Match)
│   ├── main.py         # FastAPI Endpoints
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/ # ChatWindow, MessageBubble
    │   └── App.jsx
    └── tailwind.config.js
```

## 🛡️ Design Decisions
Check out `design_decisions.md` (if available) for a deep dive into why we chose a Hybrid AI approach over a pure LLM.

---
*Built for Assignment 3 - Internal Chatbots & Automations*
