import subprocess
import time
import os
import requests
from behave import given, before, after


@given('the API service is running')
def step_api_service_running(context):
    """Start the Todo Manager REST API service."""
    if not hasattr(context, 'api_process') or context.api_process is None:
        partb_dir = os.path.join(os.path.dirname(__file__), '..')
        jar_path = os.path.join(partb_dir, 'runTodoManagerRestAPI-1.5.5.jar')
        
        context.api_process = subprocess.Popen(
            ['java', '-jar', jar_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(3)
        
        if context.api_process.poll() is not None:
            raise RuntimeError("Failed to start API service")


@before.each_scenario
def before_scenario(context):
    """Initialize context before each scenario."""
    context.api_process = None


@after.each_scenario
def after_scenario(context):
    """Clean up after each scenario."""
    if hasattr(context, 'api_process') and context.api_process is not None:
        try:
            requests.post('http://localhost:4567/shutdown', timeout=2)
        except Exception:
            pass
        try:
            context.api_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            context.api_process.terminate()
            context.api_process.wait(timeout=2)
