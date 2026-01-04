"""View full chat conversation from logs.

Usage:
    python scripts/view_chat.py CONVERSATION_ID
"""
import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def view_conversation(conversation_id):
    """View full conversation history."""
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    try:
        response = requests.get(f"{BASE_URL}/chat/{conversation_id}")
        if response.status_code == 200:
            data = response.json()
            
            print("\n" + "=" * 80)
            print(f"  CONVERSATION: {conversation_id}")
            print("=" * 80 + "\n")
            
            for i, msg in enumerate(data['messages'], 1):
                role = msg['role'].upper()
                content = msg['content']
                timestamp = msg['created_at']
                
                print(f"[{i}] {role} ({timestamp}):")
                print("-" * 80)
                print(content)
                print("\n")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/view_chat.py CONVERSATION_ID")
        print("\nExample:")
        print("  python scripts/view_chat.py 05ad1bb5-ea3e-43a2-a408-7931cae6d3f0")
        sys.exit(1)
    
    conversation_id = sys.argv[1]
    view_conversation(conversation_id)

