from abc import ABC,abstractmethod
class LLMAdapter(ABC):
    @abstractmethod
    def generate(self,prompt,context,schema):raise NotImplementedError
class DisabledLLMAdapter(LLMAdapter):
    def generate(self,prompt,context,schema):
        raise RuntimeError("No LLM provider configured. Skills must use deterministic logic or an injected adapter.")
