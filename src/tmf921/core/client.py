"""
Ollama LLM client for TMF921 intent translation.

Provides unified interface to local Ollama models.
"""

import json
import requests
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import yaml
import time


class OllamaClient:
    """Client for interacting with local Ollama LLMs."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama API endpoint
            model: Model name (e.g., "llama3.1:8b", "phi3:mini", "gemma2:9b")
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.total_tokens = 0
        self.total_time = 0.0  # seconds
        
    def _check_connection(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate(
        self, 
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        top_p: float = 0.9,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate completion from Ollama model.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens to generate
            top_p: Nuclear sampling parameter
            stream: Whether to stream response
            
        Returns:
            {
                'response': str,
                'tokens': int,
                'time_seconds': float,
                'model': str
            }
        """
        if not self._check_connection():
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Please ensure Ollama is running: 'ollama serve'"
            )
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": top_p,
            }
        }
        
        # Time the request
        start_time = time.time()
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120
        )
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")
        
        result = response.json()
        
        # Extract response text
        response_text = result.get('message', {}).get('content', '')
        
        # Token counting (approximate - Ollama doesn't always provide exact counts)
        prompt_tokens = result.get('prompt_eval_count', len(prompt) // 4)
        completion_tokens = result.get('eval_count', len(response_text) // 4)
        total_tokens = prompt_tokens + completion_tokens
        
        # Update totals
        self.total_tokens += total_tokens
        self.total_time += elapsed
        
        return {
            'response': response_text,
            'tokens': total_tokens,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'time_seconds': elapsed,
            'model': self.model
        }
    
    def extract_json(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from LLM response.
        
        Handles cases where LLM wraps JSON in markdown code blocks.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Parsed JSON dict or None if extraction fails
        """
        # Try direct JSON parse first
        try:
            return json.loads(response_text)
        except:
            pass
        
        # Try extracting from ```json ... ``` blocks
        if "```json" in response_text:
            try:
                start_idx = response_text.find("```json") + 7
                end_idx = response_text.find("```", start_idx)
                json_str = response_text[start_idx:end_idx].strip()
                return json.loads(json_str)
            except:
                pass
        
        # Try extracting from ``` ... ``` blocks (no language specified)
        if "```" in response_text:
            try:
                start_idx = response_text.find("```") + 3
                end_idx = response_text.find("```", start_idx)
                json_str = response_text[start_idx:end_idx].strip()
                # Remove potential language identifier on first line
                lines = json_str.split('\\n')
                if lines[0].strip().lower() in ['json', 'javascript', 'js']:
                    json_str = '\\n'.join(lines[1:])
                return json.loads(json_str)
            except:
                pass
        
        # Try finding JSON object boundaries
        try:
            start_idx = response_text.find('{')
            if start_idx != -1:
                # Find matching closing brace
                brace_count = 0
                for i in range(start_idx, len(response_text)):
                    if response_text[i] == '{':
                        brace_count += 1
                    elif response_text[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_str = response_text[start_idx:i+1]
                            return json.loads(json_str)
        except:
            pass
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cumulative statistics."""
        return {
            'total_tokens': self.total_tokens,
            'total_time_seconds': self.total_time,
            'avg_tokens_per_second': self.total_tokens / self.total_time if self.total_time > 0 else 0,
            'model': self.model
        }
    
    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [m.get('name') for m in models]
            return []
        except:
            return []


def load_llm_client(config_path: str = "config.yaml", model_alias: Optional[str] = None) -> OllamaClient:
    """
    Load LLM client from configuration.
    
    Args:
        config_path: Path to config.yaml
        model_alias: Optional model alias (e.g., "llama-3.1-8b")  
        
    Returns:
        Configured OllamaClient
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    ollama_config = config['models']['ollama']
    base_url = ollama_config['base_url']
    
    # Use gemma:2b as default for low RAM systems
    if model_alias is None:
        model_name = "gemma:2b"
    else:
        # Find model by alias
        model_name = None
        for model_spec in ollama_config['models']:
            if model_spec['alias'] == model_alias:
                model_name = model_spec['name']
                break
        
        if not model_name:
            # Fallback to gemma:2b
            model_name = "gemma:2b"
    
    return OllamaClient(base_url=base_url, model=model_name)


if __name__ == "__main__":
    # Test Ollama connection
    print("Testing Ollama Connection...")
    print("=" * 60)
    
    try:
        client = load_llm_client()
        
        # Check connection
        if not client._check_connection():
            print("[ERROR] Cannot connect to Ollama.")
            print("Please ensure Ollama is running: 'ollama serve'")
            print(f"And that models are pulled: 'ollama pull {client.model}'")
            exit(1)
        
        print(f"[OK] Connected to Ollama at {client.base_url}")
        print(f"[OK] Using model: {client.model}")
        
        # List available models
        models = client.list_models()
        print(f"\\nAvailable models: {', '.join(models)}")
        
        # Test generation
        print("\\n" + "=" * 60)
        print("Testing Generation...")
        print("=" * 60)
        
        test_prompt = "Translate this to JSON: Create a network slice with 100 Mbps bandwidth and 10ms latency."
        
        result = client.generate(
            prompt=test_prompt,
            system_prompt="You are a network configuration expert. Translate requests to JSON.",
            temperature=0.1,
            max_tokens=500
        )
        
        print(f"\\nPrompt: {test_prompt}")
        print(f"\\nResponse ({result['time_seconds']:.2f}s, {result['tokens']} tokens):")
        print("-" * 60)
        print(result['response'][:500])
        
        # Test JSON extraction
        print("\\n" + "=" * 60)
        print("Testing JSON Extraction...")
        print("=" * 60)
        
        extracted = client.extract_json(result['response'])
        if extracted:
            print("[OK] Successfully extracted JSON:")
            print(json.dumps(extracted, indent=2)[:300])
        else:
            print("[WARNING] Could not extract valid JSON from response")
        
        # Print stats
        print("\\n" + "=" * 60)
        stats = client.get_stats()
        print("Client Statistics:")
        print(f"  Total tokens: {stats['total_tokens']}")
        print(f"  Total time: {stats['total_time_seconds']:.2f}s")
        print(f"  Avg speed: {stats['avg_tokens_per_second']:.1f} tokens/sec")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
