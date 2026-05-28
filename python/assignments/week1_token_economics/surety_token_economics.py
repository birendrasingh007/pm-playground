#!/usr/bin/env python3
"""Surety Platform token economics: cost estimation at scale"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Pricing per 1M tokens
PRICING = {
    "haiku": {"input": 0.80, "output": 4.00, "name": "Haiku 4.5"},
    "sonnet": {"input": 3.00, "output": 15.00, "name": "Sonnet 4.6"},
    "opus": {"input": 15.00, "output": 75.00, "name": "Opus 4.6"}
}

# Surety Platform constants
INPUT_TOKENS_PER_CATEGORY = 124500  # 2MB compressed files (8MB raw / 4x compression)
OUTPUT_TOKENS_PER_CATEGORY = 336    # Risk assessment output
FREQUENCY_PER_YEAR = 52             # Weekly runs

def calculate_costs(input_tokens, output_tokens):
    """Calculate cost for each model"""
    results = {}
    
    for model_key, pricing in PRICING.items():
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        results[model_key] = {
            "name": pricing["name"],
            "input_cost": round(input_cost, 2),
            "output_cost": round(output_cost, 2),
            "total_cost": round(total_cost, 2),
        }
    
    return results

def display_results(num_categories, costs):
    """Display cost breakdown for Surety scenario"""
    total_input_tokens = INPUT_TOKENS_PER_CATEGORY * num_categories
    total_output_tokens = OUTPUT_TOKENS_PER_CATEGORY * num_categories
    
    print("\n" + "="*70)
    print("SURETY PLATFORM: TOKEN ECONOMICS AT SCALE")
    print("="*70)
    
    print(f"\nScenario:")
    print(f"  Number of categories: {num_categories:,}")
    print(f"  Input tokens/category: {INPUT_TOKENS_PER_CATEGORY:,} (2MB compressed files)")
    print(f"  Output tokens/category: {OUTPUT_TOKENS_PER_CATEGORY:,} (risk assessment)")
    print(f"  Frequency: Weekly (52 runs/year)")
    
    print(f"\nTotal tokens per run:")
    print(f"  Input: {total_input_tokens:,}")
    print(f"  Output: {total_output_tokens:,}")
    
    print("\n" + "="*70)
    print("COST BREAKDOWN (Per Run)\n")
    
    for model_key, data in costs.items():
        print(f"{data['name']}:")
        print(f"  Input cost:  ${data['input_cost']:,.2f}")
        print(f"  Output cost: ${data['output_cost']:,.2f}")
        print(f"  Total cost:  ${data['total_cost']:,.2f}")
    
    print("\n" + "="*70)
    print("ANNUALIZED COST (52 weekly runs/year)\n")
    
    annual_costs = {}
    for model_key, data in costs.items():
        annual_cost = data['total_cost'] * FREQUENCY_PER_YEAR
        annual_costs[model_key] = annual_cost
        print(f"{data['name']}: ${annual_cost:,.2f}/year")
    
    print("\n" + "="*70)
    print("COST DIFFERENCE\n")
    
    # Calculate savings vs Opus
    opus_annual = annual_costs['opus']
    for model_key in ['haiku', 'sonnet']:
        savings = opus_annual - annual_costs[model_key]
        print(f"{PRICING[model_key]['name']} vs Opus: Save ${savings:,.2f}/year")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 surety_token_economics.py <num_categories>")
        print("Example: python3 surety_token_economics.py 1200")
        sys.exit(1)
    
    try:
        num_categories = int(sys.argv[1])
    except ValueError:
        print("Error: num_categories must be an integer")
        sys.exit(1)
    
    total_input_tokens = INPUT_TOKENS_PER_CATEGORY * num_categories
    total_output_tokens = OUTPUT_TOKENS_PER_CATEGORY * num_categories
    
    costs = calculate_costs(total_input_tokens, total_output_tokens)
    display_results(num_categories, costs)