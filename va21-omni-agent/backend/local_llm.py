import time

class LocalLLM:
    """
    A DUMMY/MOCK implementation of the LocalLLM class.
    This is used for testing the integration pipeline because the environment
    is preventing a real model from being downloaded and used reliably.
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

        print("[LocalLLM] Initializing DUMMY local model.")
        self.initialized = True
        print("[LocalLLM] Dummy model initialized.")

    def generate(self, prompt: str, max_tokens=150):
        """
        Generates a predefined, hardcoded response based on the prompt content.
        """
        print(f"[LocalLLM] Generating dummy response for prompt containing: '{prompt[:50]}...'")
        time.sleep(0.1) # Simulate a very short processing time

        if 'security_guardian' in prompt:
            print("[LocalLLM] Dummy response: SAFE")
            return "SAFE"

        elif 'code_analysis' in prompt:
            print("[LocalLLM] Dummy response: No issues found.")
            return "No issues found."

        else:
            print("[LocalLLM] Dummy response: Default fallback.")
            return "This is a default response from the dummy local LLM."

# Example Usage (for testing purposes)
if __name__ == '__main__':
    print("--- Testing Local LLM Initialization (DUMMY) ---")
    local_llm = LocalLLM()

    print("\n--- Testing Local LLM Generation (Security) ---")
    security_prompt = "security_guardian prompt"
    print(f"Prompt: {security_prompt}")
    response = local_llm.generate(security_prompt)
    print(f"Response: {response}")

    print("\n--- Testing Local LLM Generation (Code Analysis) ---")
    code_prompt = "code_analysis prompt"
    print(f"Prompt: {code_prompt}")
    response = local_llm.generate(code_prompt)
    print(f"Response: {response}")
