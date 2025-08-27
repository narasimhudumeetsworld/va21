import os
from poml import Prompt

class PromptManager:
    def __init__(self):
        pass

    def render_prompt(self, prompt_name, variables={}):
        """
        Renders a prompt programmatically using the poml library.

        :param prompt_name: The name of the prompt to build.
        :param variables: A dictionary of variables to pass to the template.
        :return: The rendered prompt as a string.
        """
        p = Prompt()

        if prompt_name == 'system_prompt.poml':
            with p:
                p.role("You are a helpful assistant.")
                p.task("""You have access to the following tools:
- Web Search: To search the web for information. To use, output: {"tool": "web_search", "query": "your search query"}
- Create Backup: To save the current conversation history and long-term memory to your configured backup location. To use, output: {"tool": "create_backup"}
- Remember: To save a key-value pair to your long-term memory. To use, output: {"tool": "remember", "key": "the key", "value": "the value"}
- Recall: To recall a value from your long-term memory. To use, output: {"tool": "recall", "key": "the key"}
- Log Message: A simple tool that logs a message to the console. To use, output: {"tool": "log_message", "message": "your message"}
- Check Email: To search for emails in your Gmail account. To use, output: {"tool": "check_email", "query": "your gmail search query"}
- List GitHub Repos: To list your GitHub repositories. To use, output: {"tool": "list_github_repos"}
- Create GitHub Issue: To create an issue in a GitHub repository. To use, output: {"tool": "create_github_issue", "repo_full_name": "user/repo", "title": "Issue Title", "body": "Issue body text"}
- Summarize Text: To summarize a long piece of text. To use, output: {"tool": "summarize", "text": "the text to summarize"}
When you have the answer, reply to the user.""")
            return p.render(chat=False)

        elif prompt_name == 'workflow_planner.poml':
            description = variables.get('description', '')
            with p:
                p.role("You are a workflow planning assistant.")
                p.task("""Convert a natural language description of a workflow into a structured JSON plan.
The plan must have a 'name', a 'trigger', and a list of 'steps'.
The 'trigger' must be a schedule in cron format (e.g., "cron: 0 9 * * *").
Each 'step' in the plan must be a call to one of the available tools.""")
                with p.captioned_paragraph(caption="Available tools"):
                    with p.list():
                        with p.list_item():
                            p.text("log_message(message: str)")
                        with p.list_item():
                            p.text("check_email(query: str)")
                        with p.list_item():
                            p.text("list_github_repos()")
                        with p.list_item():
                            p.text("create_github_issue(repo_full_name: str, title: str, body: str)")
                        with p.list_item():
                            p.text("summarize(text: str)")
                        with p.list_item():
                            p.text("create_backup()")
                        with p.list_item():
                            p.text("remember(key: str, value: str)")
                        with p.list_item():
                            p.text("recall(key: str)")

                with p.example():
                    with p.example_input():
                        p.text("Description: \"Every morning at 9, check my email for messages from 'boss@example.com' and create a summary.\"")
                    with p.example_output(caption="JSON"):
                        # Escape the template variables by wrapping them in a string literal within the expression.
                        p.code("""```json
{
  "name": "Daily Boss Email Summary",
  "trigger": "cron: 0 9 * * *",
  "steps": [
    {
      "tool": "check_email",
      "params": {
        "query": "from:boss@example.com"
      }
    },
    {
      "tool": "summarize",
      "params": {
        "text": "{{ '{{steps[0].output}}' }}"
      }
    },
    {
      "tool": "log_message",
      "params": {
        "message": "Summary of boss's emails: {{ '{{steps[1].output}}' }}"
      }
    }
  ]
}
```""")
                p.hint("Note the use of {{steps[0].output}} to use the output of a previous step as input to the next.")
                p.task(f"Natural language description: \"{description}\"\n\nJSON plan:")

            return p.render(chat=False)

        else:
            raise ValueError(f"Unknown prompt name: {prompt_name}")

# Example Usage (for testing purposes)
if __name__ == '__main__':
    manager = PromptManager()
    print("--- Testing System Prompt ---")
    system_prompt = manager.render_prompt('system_prompt.poml')
    print(system_prompt)
    print("\n--- Testing Workflow Planner Prompt ---")
    workflow_prompt = manager.render_prompt('workflow_planner.poml', {'description': 'Create a daily summary of my emails.'})
    print(workflow_prompt)
