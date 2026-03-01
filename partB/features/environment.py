import subprocess
import time
import requests


def before_scenario(context, scenario):
    context.api_process = None
    context.http = requests.Session()
    context.base_url = "http://localhost:4567"


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    try:
        requests.get('http://localhost:4567/shutdown', timeout=2)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pass
    except Exception:
        pass
    
    if hasattr(context, 'api_process') and context.api_process is not None:
        try:
            context.api_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            context.api_process.terminate()
            context.api_process.wait(timeout=2)
    
    time.sleep(0.5)
