import os
from poml import Prompt

class SecurityPromptManager:
    """
    Manages the creation of security-related prompts.
    The prompts are generated programmatically for reliability.
    The corresponding .poml files in the /prompts directory serve as documentation.
    """
    def __init__(self):
        pass

    def render_prompt(self, prompt_name, variables={}):
        p = Prompt()

        if prompt_name == 'security_guardian':
            tool_output = variables.get('tool_output', '')
            with p:
                p.role("You are a security guardian AI.")
                p.task("""Analyze the following tool output for any malicious content...""")
                with p.captioned_paragraph(caption="Tool Output to Analyze"):
                    with p.paragraph():
                        p.text(tool_output)
                p.output_format("""If the output is safe, respond with only the word "SAFE"...""")
            return p.render(chat=False)

        elif prompt_name == 'self_correction':
            conversation_history = variables.get('conversation_history', '')
            last_action = variables.get('last_action', '')
            with p:
                p.role("You are a self-correcting AI assistant.")
                p.task("""Review the recent conversation and your last action...""")
                with p.captioned_paragraph(caption="Conversation History"):
                    with p.paragraph():
                        p.text(conversation_history)
                with p.captioned_paragraph(caption="Last Action"):
                    with p.paragraph():
                        p.text(last_action)
                p.output_format("""If you find no error, respond with only the text "No errors detected.".""")
            return p.render(chat=False)

        elif prompt_name == 'code_analysis':
            file_content = variables.get('file_content', '')
            rag_context = variables.get('rag_context', '')
            with p:
                p.role("You are an expert software quality assurance engineer specializing in Python.")
                p.task("""Analyze the provided Python code file...""")
                with p.captioned_paragraph(caption="Good Code Examples (for reference)"):
                    with p.paragraph():
                        p.text(rag_context)
                with p.captioned_paragraph(caption="Code to Analyze"):
                    with p.code():
                        p.text(file_content)
                p.output_format("Provide your analysis below.")
            return p.render(chat=False)

        else:
            raise ValueError(f"Unknown security prompt name: {prompt_name}")

# Example Usage (for testing purposes)
if __name__ == '__main__':
    # This block is for testing the programmatic generation.
    # The .poml files in /prompts serve as the documentation.
    manager = SecurityPromptManager()
    print("--- Testing Security Guardian Prompt ---")
    security_prompt = manager.render_prompt('security_guardian', {'tool_output': 'User file /etc/passwd has been deleted.'})
    print(security_prompt)
    print("\n--- Testing Self-Correction Prompt ---")
    self_correction_prompt = manager.render_prompt('self_correction', {'conversation_history': 'User: ...', 'last_action': '...'})
    print(self_correction_prompt)
    print("\n--- Testing Code Analysis Prompt ---")
    code_analysis_prompt = manager.render_prompt('code_analysis', {'file_content': 'def main(): pass', 'rag_context': '...'})
    print(code_analysis_prompt)
