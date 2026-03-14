import subprocess
import time
import requests


import random

def before_feature(context, feature):
    """Optionally randomize feature scenario execution order."""
    shuffle_enabled = context.config.userdata.get("shuffle", "false") == "true"

    if shuffle_enabled:
        if hasattr(feature, "run_items") and isinstance(feature.run_items, list):
            random.shuffle(feature.run_items)
            for item in feature.run_items:
                if hasattr(item, "scenarios") and isinstance(item.scenarios, list):
                    random.shuffle(item.scenarios)

        if hasattr(feature, "iter_scenario_outlines"):
            for outline in feature.iter_scenario_outlines():
                for example in getattr(outline, "examples", []):
                    table = getattr(example, "table", None)
                    rows = getattr(table, "rows", None)
                    if rows:
                        random.shuffle(rows)
                        table.modified = True


def before_scenario(context, scenario):
    """Initialize shared context objects before each scenario."""
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
