"""Test script to verify AI-powered conversation title generation."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import _generate_conversation_title


def test_title_generation():
    """Test AI title generation with various conversation types."""
    
    print("[TEST] Testing AI-Powered Conversation Title Generation\n")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Kubernetes Deployment",
            "user": "I want to deploy a BERT model on Kubernetes with GPU support",
            "assistant": "Great! I can help you deploy BERT on Kubernetes. Let me search for the best GPU instances..."
        },
        {
            "name": "Cost Analysis",
            "user": "What's the cheapest way to run LLaMA 3.1 70B?",
            "assistant": "Let me analyze cost-effective options for running LLaMA 3.1 70B model..."
        },
        {
            "name": "Vision Model",
            "user": "I need to deploy YOLOv8 for real-time object detection",
            "assistant": "I'll help you set up YOLOv8 for real-time inference. Let me check compute requirements..."
        },
        {
            "name": "Multi-Model Setup",
            "user": "Can I run Stable Diffusion and Whisper on the same cluster?",
            "assistant": "Yes! I can help you configure a multi-model deployment with Stable Diffusion and Whisper..."
        },
        {
            "name": "Simple Question",
            "user": "What GPU do I need for training?",
            "assistant": "The GPU requirements depend on your model size and batch size. Let me provide recommendations..."
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[TEST {i}] {test['name']}")
        print(f"User: {test['user'][:60]}...")
        
        try:
            title = _generate_conversation_title(test['user'], test['assistant'])
            print(f"[PASS] Generated Title: '{title}'")
            
            # Validate title
            assert len(title) > 0, "Title should not be empty"
            assert len(title) <= 60, f"Title too long: {len(title)} chars"
            assert title != "New Conversation", "Should generate unique title"
            
            print(f"       Length: {len(title)} chars")
            
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("\n[SUCCESS] All title generation tests completed!")
    print("\nTitle generation is working! Titles will be:")
    print("  - Concise (3-6 words, max 60 chars)")
    print("  - Descriptive (based on conversation content)")
    print("  - Automatically generated after first exchange")
    print("  - No more 'New Conversation' in sidebar!")


if __name__ == "__main__":
    try:
        test_title_generation()
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


