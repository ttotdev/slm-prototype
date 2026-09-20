import json
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field
from sklearn.metrics import cohen_kappa_score, confusion_matrix
from mlx_lm import load, generate

class AuditVerdict(BaseModel):
    verdict: Literal["PASS", "FAIL"] = Field(description="PASS if faithful, FAIL if violating rules")
    rationale: str

benchmark_path = Path(__file__).parent / "data" / "golden_eval.json"
with benchmark_path.open() as f:
    eval_benchmark = json.load(f)

print("Loading fully fused fine-tuned model from ./fused_model...")
model, tokenizer = load("./fused_model")

print("Running Evaluated Benchmark on 15 Corporate Test Cases...\n")
print(f"{'ID':<8} | {'Expected':<8} | {'Trained SLM':<8} | {'Status':<8} | {'Rationale'}")
print("-" * 75)

y_true, y_pred = [], []

for case in eval_benchmark:
    messages = [
        {"role": "system", "content": "You are a deterministic compliance judge. Output strict JSON with 'verdict' (PASS/FAIL) and 'rationale'."},
        {"role": "user", "content": f"Context: {case['policy']}\nAnswer: {case['test_answer']}\n"}
    ]
    
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    response_str = generate(model, tokenizer, prompt=prompt, verbose=False, max_tokens=200)

    try:
        verdict_obj = AuditVerdict.model_validate_json(response_str)
        pred_verdict = verdict_obj.verdict
        rationale = verdict_obj.rationale
    except Exception:
        pred_verdict = "FAIL"
        rationale = f"Parsing error: {response_str[:50]}"

    y_true.append(case["ground_truth"])
    y_pred.append(pred_verdict)

    status = "✅ PASS" if pred_verdict == case["ground_truth"] else "❌ MISS"
    print(f"{case['id']:<8} | {case['ground_truth']:<8} | {pred_verdict:<8} | {status:<8} | {rationale}")

labels = ["PASS", "FAIL"]
kappa = cohen_kappa_score(y_true, y_pred, labels=labels)
cm = confusion_matrix(y_true, y_pred, labels=labels)

print("\n" + "=" * 50)
print(f"Trained Cohen's Kappa (κ_trained): {kappa:.3f}")
print("=" * 50)
print("Confusion Matrix:")
print(f"             Pred PASS   Pred FAIL")
print(f"Actual PASS:     {cm[0][0]:<10} {cm[0][1]}")
print(f"Actual FAIL:     {cm[1][0]:<10} {cm[1][1]}")

results = {
    "model": "llama3.2:1b-fused-lora",
    "sample_size": len(eval_benchmark),
    "cohen_kappa": round(float(kappa), 3),
    "predictions": y_pred,
    "ground_truth": y_true,
    "confusion_matrix": cm.tolist()
}

with open("trained_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSaved 15-case trained metrics to trained_results.json")