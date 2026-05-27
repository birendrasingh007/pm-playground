#!/usr/bin/env python3
"""Token counter + cost estimator for Claude models"""
import sys
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Pricing per 1M tokens
PRICING = {
    "haiku": {"input": 0.80, "output": 4.00, "name": "Haiku 4.5"},
    "sonnet": {"input": 3.00, "output": 15.00, "name": "Sonnet 4.6"},
    "opus": {"input": 15.00, "output": 75.00, "name": "Opus 4.6"}
}

def estimate_tokens(text):
    """Rough token estimate: ~1 token per 4 chars"""
    return len(text) // 4

def get_summary(text, model, max_words=100):
    """Generate summary using specified model"""
    client = Anthropic()
    
    prompt = f"""Summarize this text in {max_words} words or less:

{text}

Summary:"""
    
    response = client.messages.create(
        model=model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    summary = response.content[0].text
    output_tokens = response.usage.output_tokens
    
    return summary, output_tokens

def calculate_costs(input_tokens, output_tokens=500):
    """Calculate cost for each model"""
    results = {}
    
    for model_key, pricing in PRICING.items():
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        results[model_key] = {
            "name": pricing["name"],
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "cost_per_1k_calls": round(total_cost * 1000, 2)
        }
    
    return results

def display_results(text, input_tokens, summaries_data):
    """Display original text, all summaries, and cost comparison"""
    print("\n" + "="*60)
    print("TOKEN COUNTER + COST ESTIMATOR")
    print("="*60)
    
    print(f"\nOriginal text ({input_tokens} tokens):")
    print(f"  {text[:200]}...\n")
    
    print("="*60)
    print("SUMMARIES & COSTS\n")
    
    for model_key, data in summaries_data.items():
        print(f"{data['name']}:")
        print(f"  Summary: {data['summary']}")
        print(f"  Output tokens: {data['output_tokens']}")
        print(f"  Input cost:  ${data['input_cost']:.6f}")
        print(f"  Output cost: ${data['output_cost']:.6f}")
        print(f"  Total cost:  ${data['total_cost']:.6f}")
        print(f"  Per 1K calls: ${data['cost_per_1k_calls']:.2f}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 token_counter.py 'your text here' [max_words]")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    
    # Check if it's a file
    if os.path.isfile(input_arg):
        with open(input_arg, 'r') as f:
            text = f.read()
        print(f"Reading from file: {input_arg}\n")
    else:
        text = input_arg
    max_words = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    
    models = {
        "haiku": "claude-haiku-4-5-20251001",
        "sonnet": "claude-sonnet-4-6",
        "opus": "claude-opus-4-6"
    }
    
    input_tokens = estimate_tokens(text)
    summaries_data = {}
    
    for model_key, model_id in models.items():
        print(f"Generating {PRICING[model_key]['name']} summary...")
        summary, output_tokens = get_summary(text, model_id, max_words)
        costs = calculate_costs(input_tokens, output_tokens)
        
        summaries_data[model_key] = {
            "name": PRICING[model_key]['name'],
            "summary": summary,
            "output_tokens": output_tokens,
            "input_cost": costs[model_key]['input_cost'],
            "output_cost": costs[model_key]['output_cost'],
            "total_cost": costs[model_key]['total_cost'],
            "cost_per_1k_calls": costs[model_key]['cost_per_1k_calls']
        }
    
    display_results(text, input_tokens, summaries_data)