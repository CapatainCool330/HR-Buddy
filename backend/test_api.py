import requests
import sys

def test_chat(message):
    url = "http://127.0.0.1:8000/chat"
    try:
        response = requests.post(url, json={"message": message})
        print(f"Input: {message}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
        print("-" * 30)
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    print("Testing API...")
    test_chat("What is the leave policy?")     # Expect FAQ answer
    test_chat("I want to apply for sick leave") # Expect Action prompt
    test_chat("Hello")                         # Expect Fallback
