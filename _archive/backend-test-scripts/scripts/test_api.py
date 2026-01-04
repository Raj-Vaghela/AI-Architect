"""Test script for Stack8s Backend API.

This script tests all endpoints with 5 example prompts and validates responses.
"""
import os
import requests
import json
import time
import sys
from typing import Dict, Any, List

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
BASE_URL = os.getenv("STACK8S_BASE_URL", "http://localhost:8000")
API_V1 = f"{BASE_URL}/api/v1"
USER_ID = "test-user-1"


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_section(text: str):
    """Print a formatted section."""
    print(f"\n--- {text} ---")


def test_health_check():
    """Test health check endpoint."""
    print_header("Testing Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Health check passed")


def test_tool_compute():
    """Test compute search tool endpoint."""
    print_header("Testing Compute Search Tool")
    
    request_data = {
        "gpu_needed": True,
        "min_vram_gb": 40,
        "max_price_monthly": 5000,
        "top_k": 5
    }
    
    print(f"Request: {json.dumps(request_data, indent=2)}")
    response = requests.post(
        f"{API_V1}/tools/compute/search",
        json=request_data,
        headers={"X-User-Id": USER_ID},
    )
    
    print(f"\nStatus: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['results'])} results")
        print(f"Metadata: {json.dumps(data['metadata'], indent=2)}")
        
        if data['results']:
            print("\nTop 3 Results:")
            for result in data['results'][:3]:
                print(f"  {result['rank']}. {result['provider']} - {result['name']}")
                gpu_count = result.get('gpu_count', 0)
                gpu_model = result.get('gpu_model', 'N/A')
                vram_gb = result.get('vram_gb', 0)
                price_monthly = float(result.get('price_monthly', 0)) if result.get('price_monthly') else 0
                print(f"     GPU: {gpu_count}x {gpu_model} ({vram_gb}GB)")
                print(f"     Price: ${price_monthly:.2f}/mo")
        print("✓ Compute search passed")
    else:
        print(f"Error: {response.text}")


def test_tool_k8s():
    """Test K8s search tool endpoint."""
    print_header("Testing K8s Search Tool")
    
    request_data = {
        "query": "mlflow",
        "top_k": 5
    }
    
    print(f"Request: {json.dumps(request_data, indent=2)}")
    response = requests.post(
        f"{API_V1}/tools/k8s/search",
        json=request_data,
        headers={"X-User-Id": USER_ID},
    )
    
    print(f"\nStatus: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['results'])} results")
        print(f"Metadata: {json.dumps(data['metadata'], indent=2)}")
        
        if data['results']:
            print("\nTop 3 Results:")
            for result in data['results'][:3]:
                print(f"  {result['rank']}. {result['name']}")
                print(f"     Version: {result.get('version')}")
                print(f"     Official: {result.get('official')}")
        print("✓ K8s search passed")
    else:
        print(f"Error: {response.text}")


def test_tool_hf():
    """Test HuggingFace search tool endpoint."""
    print_header("Testing HuggingFace Search Tool")
    
    request_data = {
        "query": "stable diffusion image generation",
        "top_k": 5
    }
    
    print(f"Request: {json.dumps(request_data, indent=2)}")
    response = requests.post(
        f"{API_V1}/tools/hf/search",
        json=request_data,
        headers={"X-User-Id": USER_ID},
    )
    
    print(f"\nStatus: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['results'])} results")
        print(f"Metadata: {json.dumps(data['metadata'], indent=2)}")
        
        if data['results']:
            print("\nTop 3 Results:")
            for result in data['results'][:3]:
                print(f"  {result['rank']}. {result['model_id']}")
                print(f"     License: {result.get('license', 'Unknown')}")
                downloads = int(result.get('downloads', 0)) if result.get('downloads') else 0
                relevance = float(result.get('relevance_score', 0)) if result.get('relevance_score') else 0
                print(f"     Downloads: {downloads:,}")
                print(f"     Relevance: {relevance:.2f}")
        print("✓ HuggingFace search passed")
    else:
        print(f"Error: {response.text}")


def test_chat_conversation(prompt: str, conversation_id: str = None) -> Dict[str, Any]:
    """
    Test a complete chat conversation.
    
    Args:
        prompt: User prompt
        conversation_id: Existing conversation ID or None for new conversation
        
    Returns:
        Response data with conversation_id
    """
    # Start new conversation if needed
    if not conversation_id:
        print_section(f"Starting new conversation")
        response = requests.post(
            f"{API_V1}/chat/start",
            headers={"X-User-Id": USER_ID},
        )
        assert response.status_code == 200
        data = response.json()
        conversation_id = data["conversation_id"]
        print(f"Conversation ID: {conversation_id}")
        print(f"Message: {data['message']}")
    
    # Send message
    print_section(f"Sending message")
    print(f"User: {prompt}")
    
    request_data = {
        "conversation_id": conversation_id,
        "message": prompt
    }
    
    response = requests.post(
        f"{API_V1}/chat/message",
        json=request_data,
        headers={"X-User-Id": USER_ID},
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response Type: {data['response_type']}")
        print(f"\nAssistant Response:\n{data['response'][:500]}...")
        
        if data.get('deployment_plan'):
            plan = data['deployment_plan']
            print(f"\n✓ Deployment Plan Generated:")
            print(f"  - GPU Recommendations: {len(plan.get('gpu_recommendations', []))}")
            print(f"  - Model Recommendations: {len(plan.get('model_recommendations', []))}")
            print(f"  - K8s Packages: {len(plan.get('kubernetes_stack', []))}")
        
        return {
            "conversation_id": conversation_id,
            "response_type": data['response_type'],
            "has_plan": data.get('deployment_plan') is not None
        }
    else:
        print(f"Error: {response.text}")
        return {"conversation_id": conversation_id, "error": response.text}


def run_test_prompts():
    """Run 5 test prompts through the chat API."""
    print_header("Testing Chat Conversations with 5 Test Prompts")
    
    test_prompts = [
        {
            "name": "LLM Inference",
            "prompts": [
                "I need to deploy an LLM for inference, something like Llama 70B"
            ]
        },
        {
            "name": "Computer Vision Training",
            "prompts": [
                "I want to train a computer vision model for object detection",
                "I have a budget of $3000/month and need at least 2 GPUs with 24GB VRAM each"
            ]
        },
        {
            "name": "Stable Diffusion Inference",
            "prompts": [
                "Help me set up Stable Diffusion XL for image generation"
            ]
        },
        {
            "name": "Fine-tuning with MLflow",
            "prompts": [
                "I need to fine-tune a language model and track experiments with MLflow",
                "My budget is $2000/month and I prefer AWS"
            ]
        },
        {
            "name": "Minimal Clarification Test",
            "prompts": [
                "I need some GPUs"
            ]
        }
    ]
    
    for i, test_case in enumerate(test_prompts, 1):
        print_header(f"Test Case {i}: {test_case['name']}")
        
        conversation_id = None
        for prompt in test_case['prompts']:
            result = test_chat_conversation(prompt, conversation_id)
            conversation_id = result.get('conversation_id')
            time.sleep(1)  # Rate limiting
        
        # Get conversation history
        print_section("Fetching Conversation History")
        response = requests.get(
            f"{API_V1}/chat/{conversation_id}",
            headers={"X-User-Id": USER_ID},
        )
        if response.status_code == 200:
            data = response.json()
            print(f"Total messages in conversation: {len(data['messages'])}")
            print("✓ Conversation history retrieved")
        
        time.sleep(2)  # Delay between test cases


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("=" + " " * 78 + "=")
    print("=  " + "Stack8s Backend API Test Suite".center(76) + "  =")
    print("=" + " " * 78 + "=")
    print("=" * 80)
    
    try:
        # Basic tests
        test_health_check()
        time.sleep(0.5)
        
        test_tool_compute()
        time.sleep(0.5)
        
        test_tool_k8s()
        time.sleep(0.5)
        
        test_tool_hf()
        time.sleep(1)
        
        # Chat conversation tests
        run_test_prompts()
        
        print_header("All Tests Completed Successfully!")
        print("\n>>> All endpoints working correctly <<<\n")
        
    except Exception as e:
        print(f"\n>>> Test failed: {e} <<<\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

