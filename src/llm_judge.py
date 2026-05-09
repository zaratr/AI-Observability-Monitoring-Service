import json

def gemma_judge_eval(prompt, response, context):
    # Simulates an LLM-as-a-judge grading system
    print(f"Grading response based on context...")
    return {"score": 9, "reasoning": "Accurate to context, no hallucination detected.", "pass": True}

if __name__ == '__main__':
    result = gemma_judge_eval("What is the refund policy?", "Refunds within 30 days.", "Context: 30 day refunds allowed.")
    print(f"Eval Output: {json.dumps(result, indent=2)}")
