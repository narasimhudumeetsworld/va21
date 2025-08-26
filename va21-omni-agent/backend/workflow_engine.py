import os
import json
import re
from apscheduler.schedulers.background import BackgroundScheduler

class WorkflowEngine:
    def __init__(self, tools):
        self.scheduler = BackgroundScheduler()
        self.tools = tools
        self.workflows_dir = "workflows"

    def load_and_schedule_workflows(self):
        """Loads all workflow plans from the workflows directory and schedules them."""
        if not os.path.exists(self.workflows_dir):
            return

        for filename in os.listdir(self.workflows_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.workflows_dir, filename)
                with open(file_path, 'r') as f:
                    try:
                        plan = json.load(f)
                        self.schedule_workflow(plan)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from {filename}")

    def schedule_workflow(self, plan):
        """Schedules a single workflow based on its plan."""
        trigger = plan.get("trigger")
        steps = plan.get("steps")

        if not trigger or not steps:
            print(f"Invalid workflow plan: {plan.get('name')}")
            return

        if trigger.startswith("cron:"):
            cron_str = trigger.split("cron:")[1].strip()
            try:
                cron_parts = cron_str.split()
                if len(cron_parts) != 5:
                    raise ValueError("Invalid cron string format")

                self.scheduler.add_job(
                    self.execute_workflow,
                    'cron',
                    minute=cron_parts[0],
                    hour=cron_parts[1],
                    day=cron_parts[2],
                    month=cron_parts[3],
                    day_of_week=cron_parts[4],
                    args=[steps]
                )
                print(f"Scheduled workflow: {plan.get('name')}")
            except Exception as e:
                print(f"Error scheduling workflow {plan.get('name')}: {e}")

    def execute_workflow(self, steps):
        """Executes the steps of a workflow."""
        print(f"Executing workflow with {len(steps)} steps...")
        step_outputs = []
        for step in steps:
            output = self.execute_step(step, step_outputs)
            step_outputs.append(output)

    def execute_step(self, step, step_outputs):
        """Executes a single step of a workflow."""
        tool_name = step.get("tool")
        params = step.get("params", {})

        # Resolve templates in params
        resolved_params = {}
        for key, value in params.items():
            if isinstance(value, str):
                # Use regex to find all template strings
                matches = re.findall(r"{{steps\[(\d+)\]\.output}}", value)
                for match in matches:
                    step_index = int(match)
                    if step_index < len(step_outputs):
                        # Replace the template with the actual output
                        value = value.replace(f"{{{{steps[{step_index}].output}}}}", str(step_outputs[step_index]))
            resolved_params[key] = value

        if tool_name in self.tools:
            try:
                print(f"Executing tool: {tool_name} with params: {resolved_params}")
                output = self.tools[tool_name](**resolved_params)
                print(f"Tool {tool_name} output: {output}")
                return output
            except Exception as e:
                print(f"Error executing tool {tool_name}: {e}")
                return f"Error: {e}"
        else:
            print(f"Unknown tool: {tool_name}")
            return f"Error: Unknown tool {tool_name}"

    def start(self):
        """Starts the workflow engine."""
        self.load_and_schedule_workflows()
        self.scheduler.start()
        print("Workflow engine started.")
