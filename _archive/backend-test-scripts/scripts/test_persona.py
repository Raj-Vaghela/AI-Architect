
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.requirements_agent import extract_workload_spec, format_clarification_for_user
from app.schemas import ClarificationResponse, ClarificationQuestion, WorkloadSpec

@patch('app.agents.requirements_agent.openai_client')
def test_persona_greeting(mock_openai):
    print("\nTesting persona greeting...")
    
    # Mock response with specific conversational opening
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "response_type": "clarification",
        "conversational_opening": "Hi there! I'd be happy to help you deploy a chatbot.",
        "questions": [
            {
                "question": "Do you need GPU support?",
                "field": "gpu_needed",
                "why_needed": "Choice of instance"
            }
        ],
        "current_understanding": {}
    })
    mock_openai.chat.completions.create.return_value = mock_response

    # Run extraction
    result = extract_workload_spec([{"role": "user", "content": "hi"}])
    
    # Verify extraction
    assert isinstance(result, ClarificationResponse)
    assert result.conversational_opening == "Hi there! I'd be happy to help you deploy a chatbot."
    print("✅ Conversational opening extracted correctly.")
    
    # Run formatting
    formatted_msg = format_clarification_for_user(result)
    print("\nFormatted Message:\n" + "-"*40 + "\n" + formatted_msg + "\n" + "-"*40)
    
    # Verify formatting
    assert "Hi there! I'd be happy to help you deploy a chatbot." in formatted_msg
    assert "Take your time" not in formatted_msg
    assert "no wrong answers" not in formatted_msg
    print("✅ Formatted message uses dynamic greeting and lacks robotic footer.")

if __name__ == "__main__":
    test_persona_greeting()
