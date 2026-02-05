import requests
import uuid
import time

def test_features():
    session_id = str(uuid.uuid4())
    url = "http://127.0.0.1:8000/chat"
    
    print("--- 1. Testing Persistence ---")
    # Apply for leave
    requests.post(url, json={"message": "Apply for leave", "session_id": session_id})
    res = requests.post(url, json={"message": "5 days", "session_id": session_id}).json()
    print(f"Application Response: {res['response']}")
    
    # Check if leaves.json exists (by indirect verification via status check)
    res_status = requests.post(url, json={"message": "check status", "session_id": session_id}).json()
    print(f"Status Response: {res_status['response']}")
    
    print("\n--- 2. Testing Learning ---")
    # Ask unknown question
    q_unknown = "What is the secret code?"
    res_unknown = requests.post(url, json={"message": q_unknown, "session_id": session_id}).json()
    print(f"Unknown Q: {res_unknown['response']}")
    
    # Teach it
    teach_msg = "Learn: What is the secret code? -> AlphaBravo123"
    res_teach = requests.post(url, json={"message": teach_msg, "session_id": session_id}).json()
    print(f"Teaching: {res_teach['response']}")
    
    # Ask again
    res_known = requests.post(url, json={"message": q_unknown, "session_id": session_id}).json()
    print(f"Known Q: {res_known['response']}")

if __name__ == "__main__":
    test_features()
