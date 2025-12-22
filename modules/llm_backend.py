# llm_backend.py
import requests
import json
from typing import Optional, Dict, Any

class LLMBackend:
    """
    Abstraction layer for LLM backends (cloud or local)
    """
    
    def __init__(self, backend_type: str = "local", model: str = "qwen:0.5b"):
        """
        Args:
            backend_type: "local" for Ollama, "cloud" for Claude/GPT
            model: Model name (e.g., "qwen:0.5b", "tinyllama", "claude-sonnet-4", "gpt-4")
        """
        self.backend_type = backend_type
        self.model = model
        self.ollama_endpoint = "http://localhost:11434/api/generate"
    
    def analyze(self, prompt: str, data: str) -> str:
        """
        Send prompt + data to LLM and get response
        
        Args:
            prompt: Analysis instructions
            data: Structured data from MOSAIC extractors
            
        Returns:
            LLM response as string
        """
        if self.backend_type == "local":
            return self._call_ollama(prompt, data)
        elif self.backend_type == "cloud":
            raise NotImplementedError("Cloud backend not yet implemented")
        else:
            raise ValueError(f"Unknown backend type: {self.backend_type}")
    
    def _call_ollama(self, prompt: str, data: str) -> str:
        """
        Call local Ollama server (optimized for lightweight models)
        """
        full_prompt = f"{prompt}\n\n{data}" if data else prompt
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,      # Déterministe
                "num_predict": 50,       # Max 50 tokens
                "top_k": 10,             # Réduit les options
                "top_p": 0.5,            # Focus
                "num_thread": 6          # Utilise tes 6 CPU
            }
        }
        
        try:
            response = requests.post(
                self.ollama_endpoint,
                json=payload,
                timeout=120  # 2 minutes max
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.ConnectionError:
            return "ERROR: Cannot connect to Ollama. Is it running? (ollama serve)"
        except requests.exceptions.Timeout:
            return "ERROR: Ollama request timed out (>120s)"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def check_availability(self) -> bool:
        """
        Check if the backend is available
        """
        if self.backend_type == "local":
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                return response.status_code == 200
            except:
                return False
        return True  # Assume cloud is available if API keys are set
