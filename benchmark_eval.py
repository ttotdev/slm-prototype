import json
from typing import Literal
from pydantic import BaseModel, Field
from sklearn.metrics import cohen_kappa_score, confusion_matrix
from mlx_lm import load, generate

class AuditVerdict(BaseModel):
    verdict: Literal["PASS", "FAIL"] = Field(description="PASS if faithful, FAIL if violating rules")
    rationale: str

eval_benchmark = [
    # Wire & Transfer Controls
    {"id": "TC-01", "policy": "Transfers above $10,000 require two-manager approval.", "test_answer": "Processed a single $12,500 transfer under solo manager approval.", "ground_truth": "FAIL"},
    {"id": "TC-02", "policy": "Transfers above $10,000 require two-manager approval.", "test_answer": "Wire of $18,000 approved jointly by Branch Manager and Operations Supervisor.", "ground_truth": "PASS"},
    {"id": "TC-03", "policy": "Transfers above $10,000 require two-manager approval.", "test_answer": "Automated pipeline cleared $8,500 standard vendor disbursement without manual review.", "ground_truth": "PASS"},
    
    # Audit & Data Retention
    {"id": "TC-04", "policy": "Customer audit trails must be retained for 7 years in immutable storage.", "test_answer": "Customer audit archives are stored in WORM storage with a 7-year retention lock.", "ground_truth": "PASS"},
    {"id": "TC-05", "policy": "Customer audit trails must be retained for 7 years in immutable storage.", "test_answer": "Deleted 4-year-old audit logs from primary database to reduce monthly storage costs.", "ground_truth": "FAIL"},
    
    # Trading & Margin Limits
    {"id": "TC-06", "policy": "Day-trading margin accounts require a minimum balance of $25,000.", "test_answer": "Account approved for day-trading margin with a verified $30,000 deposit.", "ground_truth": "PASS"},
    {"id": "TC-07", "policy": "Day-trading margin accounts require a minimum balance of $25,000.", "test_answer": "Granted day-trading leverage privileges to retail account with $15,000 liquid capital.", "ground_truth": "FAIL"},
    
    # Real Estate & Underwriting Caps
    {"id": "TC-08", "policy": "Commercial mortgages cannot exceed 75% Loan-to-Value (LTV).", "test_answer": "Issued final approval for a commercial property loan at 80% LTV.", "ground_truth": "FAIL"},
    {"id": "TC-09", "policy": "Commercial mortgages cannot exceed 75% Loan-to-Value (LTV).", "test_answer": "Counter-offered applicant with maximum debt ceiling fixed at 72% appraised LTV.", "ground_truth": "PASS"},
    {"id": "TC-10", "policy": "Unsecured personal credit lines require a minimum FICO score of 680.", "test_answer": "Approved $10,000 credit line for borrower with confirmed 620 credit score.", "ground_truth": "FAIL"},
    
    # IAM & Contractor Access
    {"id": "TC-11", "policy": "Third-party contractors must have account expiration dates within 90 days.", "test_answer": "Configured external consultant account to expire automatically in 45 days.", "ground_truth": "PASS"},
    {"id": "TC-12", "policy": "Third-party contractors must have account expiration dates within 90 days.", "test_answer": "Provisioned vendor engineer with active Active Directory account set to never expire.", "ground_truth": "FAIL"},
    {"id": "TC-13", "policy": "Production database access requires active ticket and multi-factor authentication.", "test_answer": "Engineer accessed prod DB via terminal proxy using MFA and verified ticket INC-4410.", "ground_truth": "PASS"},
    
    # AML & Device Security
    {"id": "TC-14", "policy": "Cash deposits over $10,000 must trigger a Currency Transaction Report (CTR).", "test_answer": "Client deposited $15,000 cash; teller waived CTR filing due to executive status.", "ground_truth": "FAIL"},
    {"id": "TC-15", "policy": "Source code repositories must never be synced to personal non-MDM hardware.", "test_answer": "Developer mirrored Git repository to personal external hard drive for offline work.", "ground_truth": "FAIL"}
]

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