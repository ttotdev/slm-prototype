# SLM Prototype

A local learning project for fine-tuning a small Llama model for structured
compliance judgments, plus a separate Streamlit demo for structured incident
log extraction.

The repository intentionally does not contain model weights. Model files are
downloaded or generated locally and are ignored by Git.

## Architectural Scope & Use Case

This repository implements a zero-cloud, deterministic compliance and legal rule-checking harness running locally on Apple Silicon.

* **The Use Case:** The system evaluates complex, composite legal and operational scenarios against strict statutory constraints. Because this is a high-stakes governance domain, continuous training loss metrics are insufficient; success is defined entirely by discrete classification accuracy—specifically minimizing Type II errors (false negatives where severe violations slip through).
* **Source Grounding & Truthfulness:** To prevent hallucinations in a legal domain, the model’s outputs (`PASS`/`FAIL` and `rationale`) are strictly constrained via Pydantic schemas and trained via LoRA to anchor reasoning solely to the provided policy text.
* **Evaluation Governance:** The pipeline decouples low-level optimization from release governance, utilizing a multi-layered evaluation gate:
  1. **Tuning Layer:** Measured via training loss and adapter convergence.
  2. **Release Layer:** Governed by our 15+ case golden benchmark, tracking a Confusion Matrix and Cohen’s Kappa ($\kappa$) to measure true inter-rater agreement against human baselines while correcting for random chance.

## Requirements

- macOS with Apple Silicon recommended for MLX
- Python 3.10 or newer
- Ollama for the incident analyzer
- A Hugging Face account/token if the selected base model requires access

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install mlx mlx-lm pydantic scikit-learn streamlit ollama
```

Generate the local training and validation files:

```bash
python generate_real_data.py
```

## Download and regenerate weights

The MLX commands below download the base model from Hugging Face on first use.
The base model used by the existing adapter configuration is
`mlx-community/Llama-3.2-1B-Instruct-4bit`.

Train a LoRA adapter locally:

```bash
python -m mlx_lm.lora \
	--model mlx-community/Llama-3.2-1B-Instruct-4bit \
	--data ./data \
	--train \
	--iters 200 \
	--batch-size 2 \
	--learning-rate 1e-4 \
	--num-layers 16 \
	--adapter-path ./adapters
```

Fuse the adapter into a local model used by the benchmark:

```bash
python -m mlx_lm.fuse \
	--model mlx-community/Llama-3.2-1B-Instruct-4bit \
	--adapter-path ./adapters \
	--save-path ./fused_model
```

These commands create `.safetensors` files under `adapters/` and
`fused_model/`. They remain local and are excluded from commits.

## Evaluate the fine-tuned model

The benchmark expects `fused_model/` to exist locally:

```bash
python benchmark_eval.py
python compare_results.py
```

`benchmark_eval.py` writes `trained_results.json`. The checked-in
`baseline_results.json` and `trained_results.json` are small experiment
records, not model files.

## Run the incident analyzer

Start Ollama and download the small runtime model:

```bash
ollama pull llama3.2:1b
streamlit run app.py
```

This app uses Ollama's model directly and does not use the compliance adapter.
The standalone smoke test is:

```bash
python test.py
```

## License note

The base model is Llama 3.2 and remains subject to Meta's Llama 3.2 Community
License and Acceptable Use Policy. This project is for local learning and does
not redistribute model weights. Review the model license before publishing
weights, derivatives, or a hosted service.
