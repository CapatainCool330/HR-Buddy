import requests
import uuid

def test_flow():
    session_id = str(uuid.uuid4())
    url = "http://127.0.0.1:8000/chat"
    
    print(f"Testing Session: {session_id}")
    
    # Step 1: Initialize Action
    msg1 = "I want to apply for day off"
    res1 = requests.post(url, json={"message": msg1, "session_id": session_id}).json()
    print(f"User: {msg1}")
    print(f"Bot: {res1['response']}")
    
    # Step 2: Provide details (Contextual)
    msg2 = "2 days"
    res2 = requests.post(url, json={"message": msg2, "session_id": session_id}).json()
    print(f"User: {msg2}")
    print(f"Bot: {res2['response']}")
    
    # Step 3: Verify State Cleared
    msg3 = "Hello"
    res3 = requests.post(url, json={"message": msg3, "session_id": session_id}).json()
    print(f"User: {msg3}")
    print(f"Bot: {res3['response']}")

if __name__ == "__main__":
    test_flow()
