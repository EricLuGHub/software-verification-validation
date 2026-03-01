import subprocess
import time
import requests


def before_scenario(context, scenario):
    """Initialize context before each scenario."""
    context.api_process = None
    context.http = requests.Session()
    context.base_url = "http://localhost:4567"


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    if hasattr(context, 'api_process') and context.api_process is not None:
        try:
            # Attempt graceful shutdown via endpoint
            requests.post('http://localhost:4567/shutdown', timeout=2)
        except Exception:
            # If endpoint fails, terminate the process
            pass
        
        # Wait for process to exit, then force terminate if needed
        try:
            context.api_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            context.api_process.terminate()
            context.api_process.wait(timeout=2)
