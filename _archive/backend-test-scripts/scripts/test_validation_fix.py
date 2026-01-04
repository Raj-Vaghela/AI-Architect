
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.requirements_agent import extract_workload_spec, normalize_task_type
from app.schemas import WorkloadSpec, ClarificationResponse

def test_normalization_logic():
    print("Testing normalization logic directly...")
    assert normalize_task_type("train a chatbot") == "training"
    assert normalize_task_type("training") == "training"
    assert normalize_task_type("run inference") == "inference"
    assert normalize_task_type("deploy model") == "inference"
    assert normalize_task_type("fine-tuning") == "fine-tuning"
    assert normalize_task_type("tuning") == "fine-tuning"
    assert normalize_task_type(None) is None
    print("✅ Normalization logic passed.")

@patch('app.agents.requirements_agent.openai_client')
def test_extract_workload_spec_fix(mock_openai):
    print("\nTesting extract_workload_spec with mocked LLM response...")
    
    # Mock response with invalid task_type that previously caused crash
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "response_type": "workload_spec",
        "spec": {
            "task_type": "train a chatbot",
            "domain": "NLP",
            "gpu_needed": True
        }
    })
    mock_openai.chat.completions.create.return_value = mock_response

    # Run extraction
    result = extract_workload_spec([{"role": "user", "content": "I want to train a chatbot"}])
    
    # Verify type
    if isinstance(result, WorkloadSpec):
        print(f"✅ User Intent: 'train a chatbot' -> Normalized: '{result.task_type}'")
        assert result.task_type == 'training'
    else:
        print("❌ Expected WorkloadSpec but got ClarificationResponse")
        exit(1)

    # Test Fallback Mechanism
    print("\nTesting fallback mechanism for bad JSON...")
    mock_response.choices[0].message.content = "{invalid_json}"
    
    result = extract_workload_spec([{"role": "user", "content": "crash me"}])
    
    if isinstance(result, ClarificationResponse):
        print("✅ Gracefully handled invalid JSON by returning ClarificationResponse")
        print(f"   Question: {result.questions[0].question}")
    else:
        print("❌ Expected ClarificationResponse for invalid JSON")
        exit(1)

if __name__ == "__main__":
    test_normalization_logic()
    test_extract_workload_spec_fix()
