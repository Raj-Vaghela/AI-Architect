"""Simple interactive chat script for Stack8s AI Architect.

Usage:
    python scripts/chat.py
"""
import requests
import json
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"
USER_ID = "demo-user-1"


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 80 + "\n")


def print_ai_response(response_data):
    """Format and print AI response."""
    response_type = response_data.get('response_type')
    response_text = response_data.get('response', '')
    
    print(f"AI Architect [{response_type}]:")
    print_separator()
    print(response_text)
    
    # If there's a deployment plan, show summary
    if response_data.get('deployment_plan'):
        plan = response_data['deployment_plan']
        print("\n" + "-" * 80)
        print("DEPLOYMENT PLAN SUMMARY:")
        print(f"  - GPU Options: {len(plan.get('gpu_recommendations', []))}")
        print(f"  - Model Recommendations: {len(plan.get('model_recommendations', []))}")
        print(f"  - Kubernetes Packages: {len(plan.get('kubernetes_stack', []))}")
        print("-" * 80)


def start_conversation():
    """Start a new conversation."""
    try:
        response = requests.post(
            f"{API_V1}/chat/start",
            headers={"X-User-Id": USER_ID},
        )
        if response.status_code == 200:
            data = response.json()
            return data['conversation_id']
        else:
            print(f"Error starting conversation: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("Make sure the server is running:")
        print("  cd backend")
        print("  python -m app.main")
        return None


def send_message(conversation_id, message):
    """Send a message and get response."""
    try:
        response = requests.post(
            f"{API_V1}/chat/message",
            json={
                "conversation_id": conversation_id,
                "message": message
            },
            headers={"X-User-Id": USER_ID},
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error sending message: {e}")
        return None


def main():
    """Run interactive chat session."""
    print("\n" + "=" * 80)
    print("  Stack8s AI Architect - Interactive Chat")
    print("=" * 80)
    print("\nStarting new conversation...")
    
    conversation_id = start_conversation()
    if not conversation_id:
        return
    
    print(f"✓ Conversation started (ID: {conversation_id[:8]}...)")
    print("\nType your messages below. Commands:")
    print("  - 'exit' or 'quit' to end chat")
    print("  - 'new' to start a new conversation")
    print("  - 'history' to see all messages")
    print_separator()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye! 👋")
                break
            
            if user_input.lower() == 'new':
                print("\nStarting new conversation...")
                conversation_id = start_conversation()
                if conversation_id:
                    print(f"✓ New conversation started (ID: {conversation_id[:8]}...)")
                print_separator()
                continue
            
            if user_input.lower() == 'history':
                try:
                    response = requests.get(
                        f"{API_V1}/chat/{conversation_id}",
                        headers={"X-User-Id": USER_ID},
                    )
                    if response.status_code == 200:
                        data = response.json()
                        print("\nCONVERSATION HISTORY:")
                        print_separator()
                        for msg in data['messages']:
                            role = msg['role'].upper()
                            content = msg['content']
                            if len(content) > 200:
                                content = content[:200] + "..."
                            print(f"{role}: {content}\n")
                        print_separator()
                except Exception as e:
                    print(f"Error fetching history: {e}")
                continue

            if user_input.lower() == 'list':
                try:
                    response = requests.get(
                        f"{API_V1}/chat",
                        headers={"X-User-Id": USER_ID},
                    )
                    if response.status_code == 200:
                        data = response.json()
                        print("\nYOUR CONVERSATIONS:")
                        print_separator()
                        for c in data.get("conversations", []):
                            print(f"- {c['id']} | {c.get('title')} | {c.get('updated_at')}")
                        print_separator()
                except Exception as e:
                    print(f"Error listing conversations: {e}")
                continue
            
            # Send message to AI
            print("\nThinking...")
            response_data = send_message(conversation_id, user_input)
            
            if response_data:
                print_ai_response(response_data)
                print_separator()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\nError: {e}")
            continue


if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("⚠️  Server is running but not healthy")
    except:
        print("\n" + "=" * 80)
        print("  ❌ ERROR: Server is not running!")
        print("=" * 80)
        print("\nPlease start the server first:")
        print("  1. Open a terminal")
        print("  2. cd E:\\Stack8s\\backend")
        print("  3. .\\venv\\Scripts\\Activate.ps1")
        print("  4. python -m app.main")
        print("\nThen run this script again:")
        print("  python scripts\\chat.py")
        print("=" * 80 + "\n")
        sys.exit(1)
    
    main()

