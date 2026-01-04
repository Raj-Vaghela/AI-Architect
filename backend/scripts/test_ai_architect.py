"""
Automated test suite for Stack8s AI Architect
Tests the bot's ability to understand requirements and provide recommendations
per the Project Requirements Document.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test cases configuration
TEST_CASES = [
    {
        "id": "1.1",
        "category": "Intent Understanding",
        "name": "Medical Imaging (PRD Example)",
        "prompt": "I have 2TB of MRI images and want to detect lung cancer. What GPUs should I choose? What architecture do I need?",
        "pass_criteria": [
            "Identifies medical imaging domain",
            "Asks clarifying questions (2-3)",
            "Recommends appropriate GPU (A100/H100)",
            "Suggests medical-specific models (ViT, BioMedCLIP, MONAI)"
        ]
    },
    {
        "id": "1.2",
        "category": "Intent Understanding",
        "name": "LLM Fine-tuning",
        "prompt": "I want to fine-tune a large language model on my company's documentation (50GB text). What do I need?",
        "pass_criteria": [
            "Recognizes LLM fine-tuning task",
            "Suggests appropriate GPU memory (40GB+)",
            "Recommends relevant base models (Llama, Mistral, Qwen)",
            "Mentions LoRA/QLoRA as option"
        ]
    },
    {
        "id": "1.3",
        "category": "Intent Understanding",
        "name": "Computer Vision - Object Detection",
        "prompt": "I need to build a real-time object detection system for autonomous vehicles. We have 10TB of dashcam footage.",
        "pass_criteria": [
            "Differentiates training vs inference needs",
            "Recommends real-time capable models (YOLO)",
            "Suggests inference optimization (Triton/TensorRT)",
            "Mentions latency considerations"
        ]
    },
    {
        "id": "3.1",
        "category": "GPU Recommendations",
        "name": "LLM Inference at Scale",
        "prompt": "I need to serve LLaMA 3.1 70B with 100 concurrent users, each with 4K context length.",
        "pass_criteria": [
            "Recommends 80GB+ VRAM GPUs",
            "Mentions quantization options",
            "Suggests vLLM for inference optimization",
            "Addresses concurrency requirements"
        ]
    },
    {
        "id": "3.2",
        "category": "GPU Recommendations",
        "name": "Multi-GPU Training",
        "prompt": "I want to train a 13B parameter model from scratch. What multi-GPU setup do I need?",
        "pass_criteria": [
            "Recommends multi-GPU setup",
            "Mentions GPU interconnect importance (NVLink)",
            "Suggests distributed training frameworks (DeepSpeed, FSDP)",
            "Provides multiple provider options"
        ]
    },
    {
        "id": "4.1",
        "category": "Model Recommendations",
        "name": "NLP Task",
        "prompt": "I need to build a customer support chatbot that understands technical questions.",
        "pass_criteria": [
            "Suggests appropriate size models (7-8B)",
            "Mentions fine-tuning approach",
            "Considers RAG architecture",
            "Notes license compatibility"
        ]
    },
    {
        "id": "5.1",
        "category": "Kubernetes Stack",
        "name": "Complete ML Pipeline",
        "prompt": "I need a full ML training pipeline from data prep to model deployment.",
        "pass_criteria": [
            "Covers data, training, serving, monitoring",
            "All components are Kubernetes-native",
            "Suggests integration patterns",
            "Mentions observability (Prometheus, Grafana)"
        ]
    },
    {
        "id": "6.1",
        "category": "Deployment Plans",
        "name": "End-to-End Architecture",
        "prompt": "Give me a complete architecture for training and serving a text classification model.",
        "pass_criteria": [
            "Complete architecture summary",
            "Separates training and inference",
            "Provides cost breakdown",
            "Includes deployment steps"
        ]
    },
]


def print_header():
    """Print test suite header"""
    print("=" * 80)
    print("STACK8S AI ARCHITECT - AUTOMATED TEST SUITE")
    print("=" * 80)
    print(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Tests: {len(TEST_CASES)}")
    print("=" * 80)
    print()


def print_test_case(test):
    """Print individual test case"""
    print(f"\n[TEST {test['id']}] {test['name']}")
    print(f"Category: {test['category']}")
    print(f"\nPrompt: {test['prompt']}")
    print("\nPass Criteria:")
    for i, criteria in enumerate(test['pass_criteria'], 1):
        print(f"  {i}. {criteria}")
    print("\n" + "-" * 80)


def manual_evaluation():
    """
    Manual test evaluation guide
    This script helps you systematically test the bot
    """
    print_header()
    
    results = []
    
    print("\nINSTRUCTIONS:")
    print("1. For each test case, copy the prompt and send it to the bot")
    print("2. Review the bot's response")
    print("3. Check if the response meets each pass criteria")
    print("4. Score the test case (0-5) based on how many criteria are met")
    print("5. Record your observations")
    print("\n" + "=" * 80)
    
    for test in TEST_CASES:
        print_test_case(test)
        
        print("\nTO TEST:")
        print("1. Go to your Stack8s chat interface")
        print("2. Start a new conversation")
        print("3. Send the prompt above")
        print("4. Evaluate the response")
        print()
        
        # Manual scoring
        print("SCORING (press Enter after each):")
        score_str = input(f"  Score for Test {test['id']} (0-5): ").strip()
        try:
            score = int(score_str) if score_str else 0
        except:
            score = 0
        
        notes = input(f"  Notes (optional): ").strip()
        
        results.append({
            "id": test["id"],
            "name": test["name"],
            "category": test["category"],
            "score": score,
            "notes": notes
        })
        
        print(f"\n✓ Test {test['id']} recorded: {score}/5")
        print("=" * 80)
    
    # Print summary
    print_summary(results)
    
    # Save results
    save_results(results)


def print_summary(results):
    """Print test results summary"""
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    total_score = sum(r['score'] for r in results)
    max_score = len(results) * 5
    average = total_score / len(results) if results else 0
    
    print(f"\nOverall Score: {total_score}/{max_score} ({average:.2f}/5.00)")
    print(f"Pass Threshold: 4.0/5.0")
    print(f"Status: {'✅ PASS' if average >= 4.0 else '❌ FAIL'}")
    
    # Category breakdown
    categories = {}
    for result in results:
        cat = result['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result['score'])
    
    print("\n" + "-" * 80)
    print("CATEGORY BREAKDOWN:")
    print("-" * 80)
    for cat, scores in sorted(categories.items()):
        avg = sum(scores) / len(scores)
        print(f"{cat:30} {avg:.2f}/5.00 ({sum(scores)}/{len(scores)*5})")
    
    print("\n" + "-" * 80)
    print("INDIVIDUAL TESTS:")
    print("-" * 80)
    for result in results:
        status = "✅" if result['score'] >= 4 else "⚠️" if result['score'] >= 3 else "❌"
        print(f"{status} Test {result['id']:5} {result['name']:40} {result['score']}/5")
        if result['notes']:
            print(f"         Notes: {result['notes']}")
    
    print("\n" + "=" * 80)


def save_results(results):
    """Save test results to file"""
    filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(filename, 'w') as f:
        f.write("STACK8S AI ARCHITECT - TEST RESULTS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for result in results:
            f.write(f"Test {result['id']}: {result['name']}\n")
            f.write(f"Category: {result['category']}\n")
            f.write(f"Score: {result['score']}/5\n")
            if result['notes']:
                f.write(f"Notes: {result['notes']}\n")
            f.write("\n")
        
        total_score = sum(r['score'] for r in results)
        max_score = len(results) * 5
        average = total_score / len(results) if results else 0
        
        f.write("=" * 80 + "\n")
        f.write(f"Overall Score: {total_score}/{max_score} ({average:.2f}/5.00)\n")
        f.write(f"Status: {'PASS' if average >= 4.0 else 'FAIL'}\n")
    
    print(f"\n✓ Results saved to: {filename}")


def print_quick_reference():
    """Print quick reference of all test prompts"""
    print("\n" + "=" * 80)
    print("QUICK REFERENCE - TEST PROMPTS")
    print("=" * 80)
    
    for test in TEST_CASES:
        print(f"\n[Test {test['id']}] {test['name']}")
        print(f"Prompt: {test['prompt']}")
        print()


if __name__ == "__main__":
    print("\nStack8s AI Architect Test Suite")
    print("================================\n")
    print("Choose mode:")
    print("1. Manual Evaluation (interactive)")
    print("2. Quick Reference (print all prompts)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        manual_evaluation()
    elif choice == "2":
        print_quick_reference()
    else:
        print("Exiting...")
        sys.exit(0)


