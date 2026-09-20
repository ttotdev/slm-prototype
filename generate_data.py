import json

# Format: Chat conversation pairs matching Llama 3 prompt structure
samples = [
    {
        "messages": [
            {"role": "system", "content": "You are a deterministic compliance judge. Output strict JSON."},
            {"role": "user", "content": "Context: Policy CM-10: Commercial mortgage LTV cap is 75%.\nAnswer: We approve commercial loans up to 85% LTV."},
            {"role": "assistant", "content": json.dumps({"verdict": "FAIL", "rationale": "Exceeds 75% LTV ceiling."})}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are a deterministic compliance judge. Output strict JSON."},
            {"role": "user", "content": "Context: Policy SEC-4: Audit logs must be retained for 7 years.\nAnswer: All transaction audit records are retained for seven years in cold archive."},
            {"role": "assistant", "content": json.dumps({"verdict": "PASS", "rationale": "Directly matches 7-year retention mandate."})}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are a deterministic compliance judge. Output strict JSON."},
            {"role": "user", "content": "Context: Policy OPS-2: Third-party contractors require 2FA authentication.\nAnswer: Contractors can login using basic user and password credentials."},
            {"role": "assistant", "content": json.dumps({"verdict": "FAIL", "rationale": "Violates required 2FA authentication rule."})}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are a deterministic compliance judge. Output strict JSON."},
            {"role": "user", "content": "Context: Policy AML-01: Wires exceeding $10,000 require senior officer sign-off.\nAnswer: Wire of $12,500 routed to Senior Compliance Officer for mandatory approval."},
            {"role": "assistant", "content": json.dumps({"verdict": "PASS", "rationale": "Properly routed for senior sign-off based on threshold."})}
        ]
    }
]

# Write train and validation splits
with open("data/train.jsonl", "w") as f:
    for item in samples * 10:  # Expand to 40 samples for local epoch run
        f.write(json.dumps(item) + "\n")

with open("data/valid.jsonl", "w") as f:
    for item in samples:
        f.write(json.dumps(item) + "\n")

print("Generated data/train.jsonl and data/valid.jsonl")
