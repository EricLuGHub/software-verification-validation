import subprocess
import time
import os
import requests
from behave import given

# TODO: add guardrail for if service is already running on 4567
@given('the API service is running')
def step_api_service_running(context):
    """Start the Todo Manager REST API service."""
    time.sleep(0.5)
    
    if not hasattr(context, 'api_process') or context.api_process is None:
        partb_dir = os.path.join(os.path.dirname(__file__), '..')
        jar_path = os.path.join(partb_dir, 'runTodoManagerRestAPI-1.5.5.jar')
        
        context.api_process = subprocess.Popen(
            ['java', '-jar', jar_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        max_retries = 10
        for attempt in range(max_retries):
            time.sleep(1)
            
            if context.api_process.poll() is not None:
                _, stderr = context.api_process.communicate()
                raise RuntimeError(f"API service crashed. Error: {stderr}")
            
            try:
                response = requests.get('http://localhost:4567/todos', timeout=1)
                if response.status_code == 200:
                    return
            except Exception:
                pass
        
        raise RuntimeError("API service failed to start after waiting 10 seconds")
