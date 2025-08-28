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

        print("[LocalLLM] Initializing real ONNX model via onnxruntime-genai...")

        try:
            # The model files were downloaded by huggingface-cli into the current dir.
            # We assume this script is run from the `backend` directory.
            model_path = "."
            if not os.path.exists(os.path.join(model_path, "genai_config.json")):
                 raise FileNotFoundError("Could not find genai_config.json in the model path. Make sure the model was downloaded correctly.")

            self.model = og.Model(model_path)
            self.tokenizer = og.Tokenizer(self.model)
            print("[LocalLLM] Real ONNX model and tokenizer loaded successfully.")

        except Exception as e:
            print(f"[LocalLLM] Error loading ONNX model: {e}")
            self.model = None
            self.tokenizer = None

        self.initialized = True

    def generate(self, prompt: str, max_length=150):
        """
        Generates a response from the local ONNX model.
        """
        if not self.model or not self.tokenizer:
            return "Error: Local LLM is not initialized."

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
