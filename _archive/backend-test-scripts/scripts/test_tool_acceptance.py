"""
Test Tool Acceptance Criteria
Tests the AI Architect bot's tool usage, accuracy, and conversational quality.
"""
import sys
import json
import requests
from typing import Dict, Any, List
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
API_ENDPOINT = f"{BACKEND_URL}/api/v1/chat/message"

# Test scenarios
TEST_CASES = [
    # CPU/GPU Bias Tests (Priority 1)
    {
        "id": "COMPUTE-001a",
        "category": "CPU/GPU Balance",
        "query": "I need to deploy a REST API for my scikit-learn model",
        "expected_tool": "search_compute_instances",
        "expected_params": {"gpu_needed": False},
        "description": "Should recommend CPU instances for traditional ML API"
    },
    {
        "id": "COMPUTE-001b",
        "category": "CPU/GPU Balance",
        "query": "I want to train a YOLOv8 computer vision model",
        "expected_tool": "search_compute_instances",
        "expected_params": {"gpu_needed": True},
        "description": "Should recommend GPU instances for deep learning training"
    },
    {
        "id": "COMPUTE-001d",
        "category": "CPU/GPU Balance",
        "query": "I need to run a PostgreSQL database for my application",
        "expected_tool": "search_compute_instances",
        "expected_params": {"gpu_needed": False},
        "description": "Should recommend CPU instances for databases"
    },
    
    # Kubernetes Tool Tests
    {
        "id": "K8S-001a",
        "category": "Kubernetes Tool",
        "query": "I need a monitoring solution for my Kubernetes cluster",
        "expected_tool": "search_k8s_packages",
        "expected_in_query": "monitoring",
        "description": "Should search K8s packages for monitoring tools"
    },
    {
        "id": "K8S-001b",
        "category": "Kubernetes Tool",
        "query": "Help me set up a database in Kubernetes",
        "expected_tool": "search_k8s_packages",
        "expected_in_query": "database",
        "description": "Should search K8s packages for database solutions"
    },
    {
        "id": "K8S-002a",
        "category": "Kubernetes Tool",
        "query": "I need an ingress controller for my cluster",
        "expected_tool": "search_k8s_packages",
        "expected_in_query": "ingress",
        "description": "Should search for ingress controllers"
    },
    
    # HuggingFace Tool Tests
    {
        "id": "HF-001a",
        "category": "HuggingFace Tool",
        "query": "Find me a good text generation model",
        "expected_tool": "search_hf_models",
        "expected_params": {"pipeline_tag": "text-generation"},
        "description": "Should search HF with text-generation pipeline tag"
    },
    {
        "id": "HF-001b",
        "category": "HuggingFace Tool",
        "query": "I need an image classification model",
        "expected_tool": "search_hf_models",
        "expected_in_query": "image",
        "description": "Should search HF for image classification models"
    },
    
    # Multi-tool Tests
    {
        "id": "MULTI-001a",
        "category": "Multi-Tool Orchestration",
        "query": "I want to deploy Llama 2 70B for inference on GCP",
        "expected_tools": ["search_hf_models", "search_compute_instances"],
        "description": "Should call both HF and compute tools"
    },
    
    # No-tool Tests (informational queries)
    {
        "id": "MULTI-002a",
        "category": "Tool Selection",
        "query": "What is Kubernetes?",
        "expected_tool": None,
        "description": "Should NOT call any tool for informational query"
    },
    
    # Price filtering
    {
        "id": "COMPUTE-002a",
        "category": "Budget Constraints",
        "query": "I need a GPU for inference under $200 per month",
        "expected_tool": "search_compute_instances",
        "expected_params": {"gpu_needed": True, "max_price_monthly": 200},
        "description": "Should apply price filter"
    },
]


class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.total = 0
        
    def add_pass(self, test_id: str, message: str):
        self.passed.append({"id": test_id, "message": message})
        self.total += 1
        
    def add_fail(self, test_id: str, message: str):
        self.failed.append({"id": test_id, "message": message})
        self.total += 1
        
    def add_warning(self, test_id: str, message: str):
        self.warnings.append({"id": test_id, "message": message})
        
    def print_summary(self):
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"\n✅ PASSED: {len(self.passed)}/{self.total}")
        for test in self.passed:
            print(f"   {test['id']}: {test['message']}")
            
        if self.failed:
            print(f"\n❌ FAILED: {len(self.failed)}/{self.total}")
            for test in self.failed:
                print(f"   {test['id']}: {test['message']}")
                
        if self.warnings:
            print(f"\n⚠️  WARNINGS: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   {warning['id']}: {warning['message']}")
                
        pass_rate = (len(self.passed) / self.total * 100) if self.total > 0 else 0
        print(f"\n📊 Pass Rate: {pass_rate:.1f}%")
        print("="*80 + "\n")


def send_test_message(conversation_id: str, message: str, auth_token: str = None) -> Dict[str, Any]:
    """Send a test message to the chatbot."""
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
        
    payload = {
        "conversation_id": conversation_id,
        "message": message
    }
    
    try:
        response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def extract_tool_calls_from_response(response_text: str) -> List[Dict[str, Any]]:
    """
    Parse tool calls from the response text.
    Looks for patterns in the logged output.
    """
    tool_calls = []
    lines = response_text.split('\n')
    
    current_tool = None
    current_args = {}
    
    for line in lines:
        # Look for tool call markers
        if '[TOOL CALL]' in line:
            tool_name = line.split('[TOOL CALL]')[-1].strip()
            current_tool = tool_name
            current_args = {}
        elif current_tool and '•' in line and ':' in line:
            # Parse arguments
            parts = line.split(':', 1)
            if len(parts) == 2:
                arg_name = parts[0].strip().replace('•', '').strip()
                arg_value = parts[1].strip()
                current_args[arg_name] = arg_value
        elif current_tool and '[SUCCESS]' in line:
            tool_calls.append({
                "name": current_tool,
                "args": current_args
            })
            current_tool = None
            current_args = {}
            
    return tool_calls


def run_test_case(test_case: Dict[str, Any], conversation_id: str, results: TestResults):
    """Run a single test case."""
    test_id = test_case["id"]
    print(f"\n{'='*80}")
    print(f"Running Test: {test_id}")
    print(f"Category: {test_case['category']}")
    print(f"Query: {test_case['query']}")
    print(f"Expected: {test_case['description']}")
    print(f"{'='*80}")
    
    # Send the message
    response = send_test_message(conversation_id, test_case["query"])
    
    if not response:
        results.add_fail(test_id, "Failed to get response from backend")
        return
    
    response_text = response.get("response", "")
    print(f"\n📝 Response Preview: {response_text[:200]}...")
    
    # Extract tool calls (this is a simplified version - in real implementation,
    # you'd need to capture the actual tool calls from logs or add instrumentation)
    # For now, we'll do basic text analysis
    
    # Check if expected tool was called (basic heuristic)
    expected_tool = test_case.get("expected_tool")
    expected_tools = test_case.get("expected_tools", [])
    
    if expected_tool:
        # Simple check: look for tool mentions or related keywords
        tool_name_lower = expected_tool.lower()
        
        if expected_tool == "search_compute_instances":
            # Check for compute-related responses
            has_compute_keywords = any(kw in response_text.lower() for kw in 
                ['instance', 'gpu', 'cpu', 'vcpu', 'ram', 'price', 'provider'])
            
            if has_compute_keywords:
                results.add_pass(test_id, "Appears to use compute tool (keywords found)")
                
                # Check specific parameters if expected
                expected_params = test_case.get("expected_params", {})
                if "gpu_needed" in expected_params:
                    if expected_params["gpu_needed"] == True:
                        if any(kw in response_text.lower() for kw in ['a100', 'h100', 't4', 'l4', 'gpu', 'vram']):
                            print("   ✅ GPU-related content found")
                        else:
                            results.add_warning(test_id, "Expected GPU content, but not clearly present")
                    elif expected_params["gpu_needed"] == False:
                        if 'cpu' in response_text.lower() and not any(kw in response_text.lower() for kw in ['a100', 'h100', 'need.*gpu']):
                            print("   ✅ CPU-focused content (GPU not emphasized)")
                        else:
                            results.add_warning(test_id, "Expected CPU focus, but response may mention GPUs")
            else:
                results.add_fail(test_id, "No compute-related keywords found in response")
                
        elif expected_tool == "search_k8s_packages":
            # Check for K8s-related responses
            has_k8s_keywords = any(kw in response_text.lower() for kw in 
                ['helm', 'chart', 'package', 'kubernetes', 'k8s', 'bitnami', 'prometheus', 'grafana', 'ingress'])
            
            if has_k8s_keywords:
                results.add_pass(test_id, "Appears to use K8s tool (keywords found)")
            else:
                results.add_fail(test_id, "No K8s-related keywords found in response")
                
        elif expected_tool == "search_hf_models":
            # Check for HF-related responses
            has_hf_keywords = any(kw in response_text.lower() for kw in 
                ['model', 'hugging', 'llama', 'mistral', 'downloads', 'likes', 'license'])
            
            if has_hf_keywords:
                results.add_pass(test_id, "Appears to use HF tool (keywords found)")
            else:
                results.add_fail(test_id, "No HuggingFace-related keywords found in response")
                
    elif expected_tool is None:
        # Should NOT call tools
        tool_keywords = ['found', 'results', 'instances', 'packages', 'models']
        has_tool_language = sum(1 for kw in tool_keywords if kw in response_text.lower()) >= 2
        
        if not has_tool_language:
            results.add_pass(test_id, "Correctly did not call tools (informational response)")
        else:
            results.add_warning(test_id, "May have called tools unnecessarily")
            
    elif expected_tools:
        # Multi-tool test
        tools_found = []
        if any(kw in response_text.lower() for kw in ['model', 'hugging', 'llama']):
            tools_found.append("search_hf_models")
        if any(kw in response_text.lower() for kw in ['instance', 'gpu', 'price']):
            tools_found.append("search_compute_instances")
            
        if len(tools_found) >= len(expected_tools):
            results.add_pass(test_id, f"Multiple tools appear to be used: {tools_found}")
        else:
            results.add_fail(test_id, f"Expected {len(expected_tools)} tools, found evidence of {len(tools_found)}")
    
    print(f"\n{'='*80}\n")


def main():
    """Run all test cases."""
    print("\n" + "🧪"*40)
    print("Stack8s AI Architect - Tool Acceptance Testing")
    print("🧪"*40 + "\n")
    
    # Check backend health
    try:
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        health_response.raise_for_status()
        print("✅ Backend is healthy\n")
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend health check failed: {e}")
        print("   Make sure the backend is running on http://localhost:8000")
        sys.exit(1)
    
    # Create a test conversation
    conversation_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    results = TestResults()
    
    # Run each test case
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\nProgress: {i}/{len(TEST_CASES)}")
        run_test_case(test_case, conversation_id, results)
    
    # Print summary
    results.print_summary()
    
    # Return exit code based on results
    if len(results.failed) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

