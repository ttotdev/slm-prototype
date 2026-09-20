import json

with open("baseline_results.json") as f:
    base = json.load(f)

try:
    with open("trained_results.json") as f:
        trained = json.load(f)
    
    print("=" * 50)
    print("COMPLIANCE GUARDRAIL: BEFORE vs. AFTER TRAINING")
    print("=" * 50)
    print(f"Baseline Kappa (κ):  {base['cohen_kappa']:.3f}")
    print(f"Trained Kappa (κ):   {trained['cohen_kappa']:.3f}")
    delta = trained['cohen_kappa'] - base['cohen_kappa']
    print(f"Improvement (Δκ):    +{delta:.3f}")
    print("=" * 50)
except FileNotFoundError:
    print("Make sure your post-training results are saved to trained_results.json!")
