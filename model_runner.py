from abc import ABC, abstractmethod
from mlx_lm import load, generate

class BaseComplianceModel(ABC):
    @abstractmethod
    def evaluate(self, prompt: str) -> str:
        pass

class MLXModelRunner(BaseComplianceModel):
    def __init__(self, model_path: str):
        print(f"Loading model from {model_path}...")
        self.model, self.tokenizer = load(model_path)

    def evaluate(self, prompt: str, max_tokens: int = 200) -> str:
        response_str = generate(self.model, self.tokenizer, prompt=prompt, verbose=False, max_tokens=max_tokens)
        return response_str

class ModelRegistry:
    _registry = {
        "llama-3.2-1b": "./fused_model",
        "mistral-7b": "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
    }

    @classmethod
    def get_runner(cls, model_key: str) -> BaseComplianceModel:
        path = cls._registry.get(model_key, model_key)
        return MLXModelRunner(path)