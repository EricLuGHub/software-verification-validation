#!/usr/bin/env python3

import subprocess
import time
import requests
import psutil
import csv
import socket
import os
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

## NOTE: CUD = Create, Update, Delete (operations)

HOST = "http://localhost:4567"
PROJECTS_ENDPOINT = "/projects"
TODOS_ENDPOINT = "/todos"
JAR_PATH = Path(__file__).resolve().parents[1] / "partC" / "runTodoManagerRestAPI-1.5.5.jar"
NUM_OPERATIONS = 1
SAMPLING_RATE = 10
BATCH_CONCURRENCY = 500

class MetricsCollector:
    """Collects CPU and memory metrics during operations."""
    
    def __init__(self):
        self.process = psutil.Process()
        
    def get_metrics(self) -> Dict:
        """Get current CPU and memory metrics."""
        return {
            "cpu_percent": self.process.cpu_percent(interval=0.1),
            "memory_mb": self.process.memory_info().rss / (1024 * 1024),
        }

class CUDMetricsGenerator:
    """Main class for generating CUD metrics."""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.server_proc = None
        self.project_ids = []
        self.todo_ids = []
        
    def is_port_open(self, host="localhost", port=4567) -> bool:
        """Check if port is open."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((host, port)) == 0
    
    def wait_until_ready(self, timeout_seconds=15, endpoint=TODOS_ENDPOINT):
        """Wait for server to be ready."""
        deadline = time.time() + timeout_seconds
        url = f"{HOST}{endpoint}"
        
        print("Waiting for server to be ready...")
        while time.time() < deadline:
            try:
                r = requests.get(url, timeout=0.5)
                if r.status_code in (200, 404):
                    print("Server is ready!")
                    return
            except requests.RequestException:
                pass
            time.sleep(0.1)
        
        raise RuntimeError("Server did not become ready in time")
    
    def start_server(self):
        """Start the TODO server."""
        if self.is_port_open():
            print("Server is already running on port 4567")
            return
        
        if not JAR_PATH.exists():
            raise FileNotFoundError(f"JAR file not found at {JAR_PATH}")
        
        print(f"Starting server from {JAR_PATH}...")
        self.server_proc = subprocess.Popen(
            ["java", "-jar", str(JAR_PATH)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        
        # Give it a moment to start
        time.sleep(2)
        self.wait_until_ready()
    
    def stop_server(self):
        """Stop the TODO server."""
        print("Shutting down server...")
        requests.get(f"{HOST}/shutdown", timeout=3)
        time.sleep(1)
      
        
    
    def measure_create_project(self) -> Tuple[float, Dict, str]:
        """Create a project and measure performance."""
        start_time = time.time()
        start_metrics = self.metrics_collector.get_metrics()
        
        payload = {
            "title": f"Project-{int(time.time() * 1000)}",
            "description": "Test project for metrics"
        }
        
        start_request = time.time()
        response = requests.post(f"{HOST}{PROJECTS_ENDPOINT}", json=payload, timeout=10)
        transaction_time = time.time() - start_request
        
        end_metrics = self.metrics_collector.get_metrics()
        
        if response.status_code == 201:
            project_id = str(response.json().get("id"))
            return transaction_time, end_metrics, project_id
        else:
            raise Exception(f"Failed to create project: {response.status_code}")
    
    def measure_update_project(self, project_id: str) -> Tuple[float, Dict]:
        """Update a project and measure performance."""
        start_metrics = self.metrics_collector.get_metrics()
        
        payload = {
            "title": f"Updated-Project-{int(time.time() * 1000)}",
            "description": "Updated test project"
        }
        
        start_request = time.time()
        response = requests.put(f"{HOST}{PROJECTS_ENDPOINT}/{project_id}", json=payload, timeout=10)
        transaction_time = time.time() - start_request
        
        end_metrics = self.metrics_collector.get_metrics()
        
        if response.status_code != 200:
            raise Exception(f"Failed to update project: {response.status_code}")
        
        return transaction_time, end_metrics
    
    def measure_delete_project(self, project_id: str) -> Tuple[float, Dict]:
        """Delete a project and measure performance."""
        start_metrics = self.metrics_collector.get_metrics()
        
        start_request = time.time()
        response = requests.delete(f"{HOST}{PROJECTS_ENDPOINT}/{project_id}", timeout=10)
        transaction_time = time.time() - start_request
        
        end_metrics = self.metrics_collector.get_metrics()
        
        if response.status_code != 200:
            raise Exception(f"Failed to delete project: {response.status_code}")
        
        return transaction_time, end_metrics
    
    def measure_create_todo(self) -> Tuple[float, Dict, str]:
        """Create a todo and measure performance."""
        start_time = time.time()
        start_metrics = self.metrics_collector.get_metrics()
        
        payload = {
            "title": f"Todo-{int(time.time() * 1000)}",
            "doneStatus": False,
            "description": "Test todo for metrics"
        }
        
        start_request = time.time()
        response = requests.post(f"{HOST}{TODOS_ENDPOINT}", json=payload, timeout=10)
        transaction_time = time.time() - start_request
        
        end_metrics = self.metrics_collector.get_metrics()
        
        if response.status_code == 201:
            todo_id = str(response.json().get("id"))
            return transaction_time, end_metrics, todo_id
        else:
            raise Exception(f"Failed to create todo: {response.status_code}")
    
    def measure_update_todo(self, todo_id: str) -> Tuple[float, Dict]:
        """Update a todo and measure performance."""
        start_metrics = self.metrics_collector.get_metrics()
        
        payload = {
            "title": f"Updated-Todo-{int(time.time() * 1000)}",
            "doneStatus": True,
            "description": "Updated test todo"
        }
        
        start_request = time.time()
        response = requests.put(f"{HOST}{TODOS_ENDPOINT}/{todo_id}", json=payload, timeout=10)
        transaction_time = time.time() - start_request
        
        end_metrics = self.metrics_collector.get_metrics()
        
        if response.status_code != 200:
            raise Exception(f"Failed to update todo: {response.status_code}")
        
        return transaction_time, end_metrics
    
    def measure_delete_todo(self, todo_id: str) -> Tuple[float, Dict]:
        """Delete a todo and measure performance."""
        start_metrics = self.metrics_collector.get_metrics()
        
        start_request = time.time()
        response = requests.delete(f"{HOST}{TODOS_ENDPOINT}/{todo_id}", timeout=10)
        transaction_time = time.time() - start_request
        
        end_metrics = self.metrics_collector.get_metrics()
        
        if response.status_code != 200:
            raise Exception(f"Failed to delete todo: {response.status_code}")
        
        return transaction_time, end_metrics

    def _sampled_row(self, operation: str, end_metrics: Dict, transaction_time: float, item_id: str, count: int) -> Dict:
        """Build a sampled CSV row with numeric metrics rounded to 2 decimals."""
        return {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "cpu_percent": round(end_metrics["cpu_percent"], 2),
            "memory_mb": round(end_metrics["memory_mb"], 2),
            "transaction_time_ms": round(transaction_time * 1000, 2),
            "item_id": item_id,
            "count": count,
        }
    
    def collect_project_metrics(self) -> List[Dict]:
        """Collect metrics for project CUD operations."""
        print("\n Collecting PROJECT metrics...")
        metrics = []
        
        # Calculate splits: C, U, D
        create_count = NUM_OPERATIONS 
        update_count = NUM_OPERATIONS 
        delete_count = NUM_OPERATIONS 
        
        operation_count = 0
        errors = 0
        
        # CREATE operations
        print(f"  Creating {create_count} projects...")
        for batch_start in range(0, create_count, BATCH_CONCURRENCY):
            batch_end = min(batch_start + BATCH_CONCURRENCY, create_count)
            with ThreadPoolExecutor(max_workers=BATCH_CONCURRENCY) as executor:
                futures = [executor.submit(self.measure_create_project) for _ in range(batch_end - batch_start)]
                for future in as_completed(futures):
                    try:
                        transaction_time, end_metrics, project_id = future.result()
                        self.project_ids.append(project_id)
                        operation_count += 1
                        if operation_count % SAMPLING_RATE == 0:
                            metrics.append(self._sampled_row("CREATE", end_metrics, transaction_time, project_id, operation_count))
                    except Exception as e:
                        errors += 1
                        print(f"Error: {e}")
            if batch_end % 100 == 0 or batch_end == create_count:
                print(f"{batch_end}/{create_count} creates")
        
        # UPDATE operations
        print(f"  Updating {update_count} projects...")
        if not self.project_ids:
            print("    No projects available for update")
        else:
            for batch_start in range(0, update_count, BATCH_CONCURRENCY):
                batch_end = min(batch_start + BATCH_CONCURRENCY, update_count)
                future_to_id = {}
                with ThreadPoolExecutor(max_workers=BATCH_CONCURRENCY) as executor:
                    for i in range(batch_start, batch_end):
                        project_id = self.project_ids[i % len(self.project_ids)]
                        future = executor.submit(self.measure_update_project, project_id)
                        future_to_id[future] = project_id
                    for future in as_completed(future_to_id):
                        project_id = future_to_id[future]
                        try:
                            transaction_time, end_metrics = future.result()
                            operation_count += 1
                            if operation_count % SAMPLING_RATE == 0:
                                metrics.append(self._sampled_row("UPDATE", end_metrics, transaction_time, project_id, operation_count))
                        except Exception as e:
                            errors += 1
                            print(f"Error: {e}")
                if batch_end % 100 == 0 or batch_end == update_count:
                    print(f"{batch_end}/{update_count} updates")
        
        # DELETE operations
        print(f"  Deleting {delete_count} projects...")
        projects_to_delete = self.project_ids[:delete_count]
        for batch_start in range(0, len(projects_to_delete), BATCH_CONCURRENCY):
            batch_ids = projects_to_delete[batch_start: batch_start + BATCH_CONCURRENCY]
            future_to_id = {}
            with ThreadPoolExecutor(max_workers=BATCH_CONCURRENCY) as executor:
                for project_id in batch_ids:
                    future = executor.submit(self.measure_delete_project, project_id)
                    future_to_id[future] = project_id
                for future in as_completed(future_to_id):
                    project_id = future_to_id[future]
                    try:
                        transaction_time, end_metrics = future.result()
                        operation_count += 1
                        if operation_count % SAMPLING_RATE == 0:
                            metrics.append(self._sampled_row("DELETE", end_metrics, transaction_time, project_id, operation_count))
                    except Exception as e:
                        errors += 1
                        print(f"Error: {e}")
            done = min(batch_start + BATCH_CONCURRENCY, len(projects_to_delete))
            if done % 100 == 0 or done == len(projects_to_delete):
                print(f"{done}/{delete_count} deletes")
        
        print(f"Collected {operation_count} project operations with {errors} errors")
        return metrics
    
    def collect_todo_metrics(self) -> List[Dict]:
        """Collect metrics for todo CUD operations."""
        print("\nCollecting TODO metrics...")
        metrics = []
        
        # Calculate splits: C, U, D
        create_count = NUM_OPERATIONS 
        update_count = NUM_OPERATIONS 
        delete_count = NUM_OPERATIONS 
        
        operation_count = 0
        errors = 0
        
        # CREATE operations
        print(f"  Creating {create_count} todos...")
        for batch_start in range(0, create_count, BATCH_CONCURRENCY):
            batch_end = min(batch_start + BATCH_CONCURRENCY, create_count)
            with ThreadPoolExecutor(max_workers=BATCH_CONCURRENCY) as executor:
                futures = [executor.submit(self.measure_create_todo) for _ in range(batch_end - batch_start)]
                for future in as_completed(futures):
                    try:
                        transaction_time, end_metrics, todo_id = future.result()
                        self.todo_ids.append(todo_id)
                        operation_count += 1
                        if operation_count % SAMPLING_RATE == 0:
                            metrics.append(self._sampled_row("CREATE", end_metrics, transaction_time, todo_id, operation_count))
                    except Exception as e:
                        errors += 1
                        print(f"Error: {e}")
            if batch_end % 100 == 0 or batch_end == create_count:
                print(f"{batch_end}/{create_count} creates")
        
        # UPDATE operations
        print(f"  Updating {update_count} todos...")
        if not self.todo_ids:
            print("No todos available for update")
        else:
            for batch_start in range(0, update_count, BATCH_CONCURRENCY):
                batch_end = min(batch_start + BATCH_CONCURRENCY, update_count)
                future_to_id = {}
                with ThreadPoolExecutor(max_workers=BATCH_CONCURRENCY) as executor:
                    for i in range(batch_start, batch_end):
                        todo_id = self.todo_ids[i % len(self.todo_ids)]
                        future = executor.submit(self.measure_update_todo, todo_id)
                        future_to_id[future] = todo_id
                    for future in as_completed(future_to_id):
                        todo_id = future_to_id[future]
                        try:
                            transaction_time, end_metrics = future.result()
                            operation_count += 1
                            if operation_count % SAMPLING_RATE == 0:
                                metrics.append(self._sampled_row("UPDATE", end_metrics, transaction_time, todo_id, operation_count))
                        except Exception as e:
                            errors += 1
                            print(f"Error: {e}")
                if batch_end % 100 == 0 or batch_end == update_count:
                    print(f"{batch_end}/{update_count} updates")
        
        # DELETE operations
        print(f"  Deleting {delete_count} todos...")
        todos_to_delete = self.todo_ids[:delete_count]
        for batch_start in range(0, len(todos_to_delete), BATCH_CONCURRENCY):
            batch_ids = todos_to_delete[batch_start: batch_start + BATCH_CONCURRENCY]
            future_to_id = {}
            with ThreadPoolExecutor(max_workers=BATCH_CONCURRENCY) as executor:
                for todo_id in batch_ids:
                    future = executor.submit(self.measure_delete_todo, todo_id)
                    future_to_id[future] = todo_id
                for future in as_completed(future_to_id):
                    todo_id = future_to_id[future]
                    try:
                        transaction_time, end_metrics = future.result()
                        operation_count += 1
                        if operation_count % SAMPLING_RATE == 0:
                            metrics.append(self._sampled_row("DELETE", end_metrics, transaction_time, todo_id, operation_count))
                    except Exception as e:
                        errors += 1
                        print(f"Error: {e}")
            done = min(batch_start + BATCH_CONCURRENCY, len(todos_to_delete))
            if done % 100 == 0 or done == len(todos_to_delete):
                print(f"{done}/{delete_count} deletes")
        
        print(f"Collected {operation_count} todo operations with {errors} errors")
        return metrics
    
    def save_metrics_to_csv(self, metrics: List[Dict], filename: str):
        """Save collected metrics to CSV file."""
        if not metrics:
            print(f"No metrics to save for {filename}")
            return
        
        filepath = Path(__file__).resolve().parent / filename
        
        fieldnames = ["timestamp", "operation", "cpu_percent", "memory_mb", "transaction_time_ms", "item_id", "count"]
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(metrics)
        
        print(f"Saved {len(metrics)} metrics to {filename}")
    
    def run(self):
        """Run the complete metrics collection pipeline."""
        try:
            print("CUD Performance Metrics Generator")
            
            # Start server
            self.start_server()
            
            # Collect metrics
            project_metrics = self.collect_project_metrics()
            todo_metrics = self.collect_todo_metrics()
            
            # Save to CSV
            self.save_metrics_to_csv(project_metrics, "cud_metrics_projects.csv")
            self.save_metrics_to_csv(todo_metrics, "cud_metrics_todos.csv")
            
            print("\n" + "=" * 60)
            print("Metrics collection complete!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\nError: {e}")
            raise
        finally:
            # Stop server
            self.stop_server()

if __name__ == "__main__":
    generator = CUDMetricsGenerator()
    generator.run()
