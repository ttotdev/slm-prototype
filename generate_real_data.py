import json

training_cases = [
    # --- Category 1: Financial & Transaction Limits ---
    ("Policy FIN-10: Single wire transfers over $10,000 require two-manager approval.",
     "The system automatically approved a $15,000 international wire transfer.",
     {"verdict": "FAIL", "rationale": "Violates two-manager approval mandate for transfers over $10,000."}),
    
    ("Policy FIN-10: Single wire transfers over $10,000 require two-manager approval.",
     "A $4,500 wire transfer was processed under standard automated routing.",
     {"verdict": "PASS", "rationale": "Transfer amount is below the $10,000 threshold."}),

    ("Policy TRD-02: Retail equity day-trading margin accounts require a minimum equity balance of $25,000.",
     "Account opened with $18,000 was flagged and restricted from day-trading margin privileges.",
     {"verdict": "PASS", "rationale": "Account restricted in compliance with minimum $25,000 balance."}),

    ("Policy TRD-02: Retail equity day-trading margin accounts require a minimum equity balance of $25,000.",
     "Allowed day-trading margin execution for a new customer with a $12,000 deposit.",
     {"verdict": "FAIL", "rationale": "Approved day trading below the mandatory $25,000 equity limit."}),

    # --- Category 2: Data Privacy & Retention ---
    ("Policy SEC-01: Customer audit trails must be retained in immutable cold storage for exactly 7 years.",
     "Audit logs older than 3 years were permanently purged to save cloud bucket space.",
     {"verdict": "FAIL", "rationale": "Prematurely purged records before the required 7-year retention period."}),

    ("Policy SEC-01: Customer audit trails must be retained in immutable cold storage for exactly 7 years.",
     "Transferred 5-year-old customer audit logs to immutable Glacier storage.",
     {"verdict": "PASS", "rationale": "Complies with retaining audit records in immutable storage."}),

    ("Policy PRIV-04: Customer email lists must never be shared with external vendors without explicit opt-in.",
     "Provided email marketing partners with full customer list for quarterly newsletter blast.",
     {"verdict": "FAIL", "rationale": "Shared email list without verifying customer opt-in consent."}),

    ("Policy PRIV-04: Customer email lists must never be shared with external vendors without explicit opt-in.",
     "Exported only the verified opt-in customer subset to the third-party marketing vendor.",
     {"verdict": "PASS", "rationale": "Adheres to opt-in requirement prior to sharing data."}),

    # --- Category 3: Access Control & Identity ---
    ("Policy IAM-05: Production database direct access requires MFA and an active JIRA change ticket.",
     "Developer logged into prod database via standard SSH key without ticket reference.",
     {"verdict": "FAIL", "rationale": "Bypassed mandatory MFA and change ticket requirements."}),

    ("Policy IAM-05: Production database direct access requires MFA and an active JIRA change ticket.",
     "DBA accessed production replica using hardware token MFA and active ticket CHG-8821.",
     {"verdict": "PASS", "rationale": "Satisfied both MFA and approved change ticket conditions."}),

    ("Policy IAM-08: Third-party contractors must be assigned role-based access with maximum 90-day expiry.",
     "Contractor provisioned with permanent unrestricted read-only analyst credentials.",
     {"verdict": "FAIL", "rationale": "Permanent access provisioned; violates 90-day expiration mandate."}),

    ("Policy IAM-08: Third-party contractors must be assigned role-based access with maximum 90-day expiry.",
     "Contractor account created with role 'Contractor-Analyst' expiring automatically in 60 days.",
     {"verdict": "PASS", "rationale": "Role-based assignment within the 90-day expiration limit."}),

    # --- Category 4: AML & Compliance Reporting ---
    ("Policy AML-03: Cash deposits exceeding $10,000 must trigger a Currency Transaction Report (CTR) within 24 hours.",
     "Customer deposited $14,000 cash; automated CTR filing initiated immediately.",
     {"verdict": "PASS", "rationale": "CTR initiated within required timeframe for >$10k deposit."}),

    ("Policy AML-03: Cash deposits exceeding $10,000 must trigger a Currency Transaction Report (CTR) within 24 hours.",
     "Customer deposited $12,500 cash; teller bypassed CTR logging citing long-term customer status.",
     {"verdict": "FAIL", "rationale": "CTR requirement cannot be waived based on customer relationship."}),

    # --- Category 5: Credit & Underwriting ---
    ("Policy UND-09: Commercial real estate loans cannot exceed 75% Loan-to-Value (LTV).",
     "Approved commercial warehouse loan at 82% LTV based on projected rental revenues.",
     {"verdict": "FAIL", "rationale": "Exceeds maximum allowable 75% LTV ceiling."}),

    ("Policy UND-09: Commercial real estate loans cannot exceed 75% Loan-to-Value (LTV).",
     "Approved commercial mortgage at 70% LTV following appraisal verification.",
     {"verdict": "PASS", "rationale": "LTV is strictly within the 75% policy threshold."}),

    ("Policy UND-12: Unsecured personal lines of credit require a minimum FICO score of 680.",
     "Extended $15,000 unsecured line of credit to applicant with 640 FICO score.",
     {"verdict": "FAIL", "rationale": "Approved applicant below mandatory 680 credit score cutoff."}),

    ("Policy UND-12: Unsecured personal lines of credit require a minimum FICO score of 680.",
     "Approved credit line for borrower with verified 720 FICO score.",
     {"verdict": "PASS", "rationale": "Applicant satisfies the minimum 680 credit score requirement."}),

    # --- Category 6: Information Security & Devices ---
    ("Policy DEV-02: Corporate code repositories must never be cloned onto non-MDM personal hardware.",
     "Developer cloned backend repository to personal MacBook to troubleshoot during weekend.",
     {"verdict": "FAIL", "rationale": "Prohibited transfer of corporate code to unmanaged device."}),

    ("Policy DEV-02: Corporate code repositories must never be cloned onto non-MDM personal hardware.",
     "Engineer cloned repo onto enterprise-managed laptop with full-disk encryption active.",
     {"verdict": "PASS", "rationale": "Compliant development work on managed enterprise hardware."})
]

validation_cases = [
    ("Policy FIN-10: Single wire transfers over $10,000 require two-manager approval.",
     "Manager approved a $20,000 transfer alone while second manager was away.",
     {"verdict": "FAIL", "rationale": "Single-manager sign-off violates two-manager requirement."}),

    ("Policy SEC-01: Customer audit trails must be retained in immutable cold storage for exactly 7 years.",
     "Retained all 2019-2026 transaction records in write-once-read-many (WORM) storage.",
     {"verdict": "PASS", "rationale": "Full 7-year audit retention maintained in WORM format."}),

    ("Policy UND-09: Commercial real estate loans cannot exceed 75% Loan-to-Value (LTV).",
     "Underwriter countered client request by capping loan offer at exactly 75% LTV.",
     {"verdict": "PASS", "rationale": "Loan strictly capped at policy maximum."}),

    ("Policy DEV-02: Corporate code repositories must never be cloned onto non-MDM personal hardware.",
     "Pushed production keys to a personal public GitHub repository for quick testing.",
     {"verdict": "FAIL", "rationale": "Severe breach of security and code storage guidelines."})
]

def format_row(policy, answer, label_dict):
    return {
        "messages": [
            {"role": "system", "content": "You are a deterministic compliance judge. Output strict JSON with 'verdict' (PASS/FAIL) and 'rationale'."},
            {"role": "user", "content": f"Context: {policy}\nAnswer: {answer}"},
            {"role": "assistant", "content": json.dumps(label_dict)}
        ]
    }

with open("data/train.jsonl", "w") as f:
    for p, a, l in training_cases:
        f.write(json.dumps(format_row(p, a, l)) + "\n")

with open("data/valid.jsonl", "w") as f:
    for p, a, l in validation_cases:
        f.write(json.dumps(format_row(p, a, l)) + "\n")

print(f"Generated data/train.jsonl with {len(training_cases)} UNIQUE records.")
print(f"Generated data/valid.jsonl with {len(validation_cases)} UNIQUE validation records.")
