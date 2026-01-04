#!/usr/bin/env python3
"""
Test script to fetch model cards for a small batch
Outputs SQL for manual execution via MCP
"""

import hashlib
import json
import sys
import time
from typing import Dict, List

import tiktoken
from huggingface_hub import hf_hub_download
from huggingface_hub.utils import RepositoryNotFoundError, EntryNotFoundError

# Initialize tiktoken
encoder = tiktoken.get_encoding("cl100k_base")
tokenizer_name = "tiktoken:cl100k_base"

def fetch_model_card(model_id: str) -> str:
    """Fetch model card text"""
    try:
        print(f"Fetching: {model_id}", file=sys.stderr)
        readme_path = hf_hub_download(
            repo_id=model_id,
            filename="README.md",
            repo_type="model"
        )
        
        with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
            card_text = f.read()
        
        if not card_text or len(card_text.strip()) == 0:
            return "No model card found."
        
        return card_text
        
    except (EntryNotFoundError, RepositoryNotFoundError):
        return "No model card found."
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return "No model card found."

def compute_hash(text: str) -> str:
    """Compute SHA256 hash"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def count_tokens(text: str) -> int:
    """Count tokens"""
    try:
        tokens = encoder.encode(text)
        return len(tokens)
    except:
        return len(text.split())

def escape_sql_string(s: str) -> str:
    """Escape string for SQL"""
    return s.replace("'", "''").replace("\\", "\\\\")

def main():
    # Get first 50 models from our database
    models = [
        'google/gemma-3-27b-it',
        'google/gemma-3-12b-it',
        'google/gemma-3-4b-it',
        'microsoft/Florence-2-large',
        'OpenGVLab/InternVL3_5-GPT-OSS-20B-A4B-Preview-HF',
        'microsoft/Florence-2-base',
        'google/medgemma-4b-it',
        'dengcao/GLM-4.1V-9B-Thinking-AWQ',
        'Qwen/Qwen2.5-Omni-3B',
        'meta-llama/Llama-4-Scout-17B-16E-Instruct',
        'Qwen/Qwen3-Omni-30B-A3B-Instruct',
        'zai-org/GLM-4.1V-9B-Thinking',
        'google/gemma-3n-E2B-it',
        'abhishekchohan/gemma-3-12b-it-quantized-W4A16',
        'zai-org/GLM-4.6V-Flash',
        'HuggingFaceTB/SmolVLM2-256M-Video-Instruct',
        'lmstudio-community/GLM-4.6V-Flash-MLX-4bit',
        'lmstudio-community/GLM-4.6V-Flash-MLX-8bit',
        'Qwen/Qwen2.5-Omni-7B',
        'lmstudio-community/GLM-4.6V-Flash-MLX-6bit',
        'cyankiwi/GLM-4.6V-AWQ-4bit',
        'HuggingFaceTB/SmolVLM2-500M-Video-Instruct',
        'gaunernst/gemma-3-27b-it-int4-awq',
        'HuggingFaceTB/SmolVLM2-2.2B-Instruct',
        'zai-org/GLM-4.6V',
        'lmstudio-community/gemma-3n-E4B-it-MLX-4bit',
        'unsloth/gemma-3-12b-it-unsloth-bnb-4bit',
        'meta-llama/Llama-4-Maverick-17B-128E-Instruct',
        'lmstudio-community/gemma-3n-E4B-it-MLX-bf16',
        'openbmb/MiniCPM-o-2_6',
        'lmstudio-community/gemma-3n-E4B-it-MLX-8bit',
        'lmstudio-community/gemma-3n-E4B-it-MLX-6bit',
        'OpenGVLab/InternVL3-1B-hf',
        'unsloth/gemma-3-4b-it',
        'google/gemma-3n-E4B-it',
        'mlx-community/gemma-3-12b-it-qat-4bit',
        'zai-org/AutoGLM-Phone-9B',
        'unsloth/gemma-3-27b-it-bnb-4bit',
        'mlx-community/gemma-3-27b-it-qat-4bit',
        'meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8',
        'meta-llama/Llama-Guard-4-12B',
        'deepseek-ai/Janus-Pro-7B',
        'RioJune/AG-KD',
        'trl-internal-testing/tiny-Gemma3ForConditionalGeneration',
        'unsloth/gemma-3-27b-it-GGUF',
        'unsloth/gemma-3-4b-it-GGUF',
        'florence-community/Florence-2-large-ft',
        'CohereLabs/aya-vision-8b',
        'google/gemma-3-4b-pt',
        'Qwen/Qwen3-Omni-30B-A3B-Thinking'
    ]
    
    results = []
    failures = []
    
    for idx, model_id in enumerate(models, 1):
        print(f"\nProcessing {idx}/{len(models)}: {model_id}", file=sys.stderr)
        
        try:
            card_text = fetch_model_card(model_id)
            card_hash = compute_hash(card_text)
            token_count = count_tokens(card_text)
            
            results.append({
                'model_id': model_id,
                'card_text': card_text,
                'card_hash': card_hash,
                'token_count': token_count,
                'success': True
            })
            
            print(f"  ✓ {token_count} tokens", file=sys.stderr)
            
        except Exception as e:
            print(f"  ✗ Error: {e}", file=sys.stderr)
            failures.append({
                'model_id': model_id,
                'reason': str(e)
            })
        
        time.sleep(0.5)  # Rate limiting
    
    # Save results to JSON
    with open('model_cards_test_results.json', 'w') as f:
        json.dump({
            'results': results,
            'failures': failures,
            'stats': {
                'total': len(models),
                'successful': len(results),
                'failed': len(failures)
            }
        }, f, indent=2)
    
    print(f"\n✓ Processed {len(results)} models", file=sys.stderr)
    print(f"✓ Results saved to model_cards_test_results.json", file=sys.stderr)
    
    # Generate SQL for first 10 (to keep it manageable)
    print("\n-- SQL INSERT statements for first 10 models:")
    for result in results[:10]:
        model_id = escape_sql_string(result['model_id'])
        card_text = escape_sql_string(result['card_text'][:1000])  # Truncate for display
        card_hash = result['card_hash']
        token_count = result['token_count']
        
        print(f"-- {result['model_id']} ({token_count} tokens)")

if __name__ == '__main__':
    main()

