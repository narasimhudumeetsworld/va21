import onnxruntime_genai as og
import os

class LocalLLM:
    """
    A wrapper class for a local ONNX model using the onnxruntime-genai library.
    This class is implemented as a singleton to ensure the model is only loaded once.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalLLM, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return

        print("[LocalLLM] Initializing Guardian AI Security Core...")

        # Check if all required model files exist
        model_path = "."
        required_files = ["genai_config.json", "model.onnx", "model.onnx.data"]
        missing_files = [f for f in required_files if not os.path.exists(os.path.join(model_path, f))]
        
        if missing_files:
            print(f"[LocalLLM] Missing model files: {missing_files}")
            print("[LocalLLM] Running in simulation mode for security analysis")
            self.model = None
            self.tokenizer = None
            self.simulation_mode = True
        else:
            try:
                self.model = og.Model(model_path)
                self.tokenizer = og.Tokenizer(self.model)
                self.simulation_mode = False
                print("[LocalLLM] Guardian AI model loaded successfully - SECURITY ACTIVE")
            except Exception as e:
                print(f"[LocalLLM] Error loading ONNX model: {e}")
                print("[LocalLLM] Falling back to simulation mode")
                self.model = None
                self.tokenizer = None
                self.simulation_mode = True

        self.initialized = True

    def generate(self, prompt: str, max_length=150):
        """
        Generates a response from the local ONNX model or simulation.
        """
        if self.simulation_mode or not self.model or not self.tokenizer:
            # Guardian AI simulation mode - provides basic security analysis
            return self._simulate_security_analysis(prompt)

        try:
            search_options = {'max_length': max_length}

            prompt_tokens = self.tokenizer.encode(prompt)

            params = og.GeneratorParams(self.model)
            params.set_search_options(**search_options)
            params.input_ids = prompt_tokens

            generator = og.Generator(self.model, params)

            response_tokens = []
            while not generator.is_done():
                generator.compute_logits()
                generator.generate_next_token()
                response_tokens.append(generator.get_next_tokens()[0])

            response = self.tokenizer.decode(response_tokens)
            # The response might include the prompt, so we find where the prompt ends
            # and return the text after it. This is a common pattern.
            prompt_end_index = response.find(prompt) + len(prompt)
            return response[prompt_end_index:].strip()

        except Exception as e:
            return f"Error during local LLM generation: {e}"
    
    def _simulate_security_analysis(self, prompt: str):
        """
        Simulation mode for security analysis when full model isn't available
        """
        prompt_lower = prompt.lower()
        
        # Basic security pattern detection
        dangerous_patterns = [
            'eval(', 'exec(', '__import__', 'subprocess', 'os.system',
            'shell=true', 'rm -rf', 'delete from', 'drop table',
            'script>', '<iframe', 'javascript:', 'data:text/html',
            'base64', 'xss', 'sql injection', 'malicious'
        ]
        
        suspicious_patterns = [
            'password', 'secret', 'api_key', 'token', 'auth',
            'http://', 'ftp://', 'file://', 'network request'
        ]
        
        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if pattern in prompt_lower:
                return "UNSAFE - Potentially malicious code or command detected"
        
        # Check for suspicious patterns 
        for pattern in suspicious_patterns:
            if pattern in prompt_lower:
                return "SUSPICIOUS - Contains sensitive or potentially risky content"
        
        # If no issues found
        return "SAFE - No security threats detected"

# Example Usage (for testing purposes)
if __name__ == '__main__':
    print("--- Testing Local LLM Initialization (onnxruntime-genai) ---")
    local_llm = LocalLLM()

    if local_llm.model:
        print("\n--- Testing Local LLM Generation ---")
        # The prompt format for Phi-3 needs to be specific.
        test_prompt = "<|user|>\nWhat is the capital of France?<|end|>\n<|assistant|>"
        print(f"Prompt: {test_prompt}")
        response = local_llm.generate(test_prompt)
        print(f"Response: {response}")
    else:
        print("\nSkipping generation test because model failed to initialize.")
