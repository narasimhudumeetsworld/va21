import os
import json
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
                # Unpack the cron string into arguments for the scheduler
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
        for step in steps:
            self.execute_step(step)

    def execute_step(self, step):
        """Executes a single step of a workflow."""
        tool_name = step.get("tool")
        params = step.get("params", {})

        if tool_name in self.tools:
            try:
                print(f"Executing tool: {tool_name} with params: {params}")
                self.tools[tool_name](**params)
            except Exception as e:
                print(f"Error executing tool {tool_name}: {e}")
        else:
            print(f"Unknown tool: {tool_name}")

    def start(self):
        """Starts the workflow engine."""
        self.load_and_schedule_workflows()
        self.scheduler.start()
        print("Workflow engine started.")
