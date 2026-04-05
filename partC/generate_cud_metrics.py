#!/usr/bin/env python3

import subprocess
import time
import requests
import psutil
import csv
import socket
import os
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

## NOTE: CUD = Create, Update, Delete (operations)

HOST = "http://localhost:4567"
PROJECTS_ENDPOINT = "/projects"
TODOS_ENDPOINT = "/todos"
JAR_PATH = Path(__file__).resolve().parents[1] / "partC" / "runTodoManagerRestAPI-1.5.5.jar"
NUM_OPERATIONS = 2000
SAMPLING_RATE = 10

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
        try:
            print("Shutting down server...")
            requests.get(f"{HOST}/shutdown", timeout=3)
            time.sleep(1)
        except requests.RequestException as e:
            print(f"Error calling shutdown endpoint: {e}")
        
        if self.server_proc is not None:
            try:
                self.server_proc.terminate()
                self.server_proc.wait(timeout=5)
                print("Server stopped")
            except subprocess.TimeoutExpired:
                self.server_proc.kill()
                self.server_proc.wait()
                print("Server killed")
    
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
            self.project_ids.append(project_id)
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
            self.todo_ids.append(todo_id)
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
        
        # CREATE operations
        print(f"  Creating {create_count} projects...")
        for i in range(create_count):
            try:
                transaction_time, end_metrics, project_id = self.measure_create_project()
                operation_count += 1
                # Only sample every SAMPLING_RATE operations
                if operation_count % SAMPLING_RATE == 0:
                    metrics.append(self._sampled_row("CREATE", end_metrics, transaction_time, project_id, operation_count))
                if (i + 1) % 100 == 0:
                    print(f"{i + 1}/{create_count} creates")
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        # UPDATE operations
        print(f"  Updating {update_count} projects...")
        for i in range(update_count):
            if not self.project_ids:
                print("    No projects available for update")
                break
            try:
                project_id = self.project_ids[i % len(self.project_ids)]
                transaction_time, end_metrics = self.measure_update_project(project_id)
                operation_count += 1
                # Only sample every SAMPLING_RATE operations
                if operation_count % SAMPLING_RATE == 0:
                    metrics.append(self._sampled_row("UPDATE", end_metrics, transaction_time, project_id, operation_count))
                if (i + 1) % 100 == 0:
                    print(f"{i + 1}/{update_count} updates")
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        # DELETE operations
        print(f"  Deleting {delete_count} projects...")
        projects_to_delete = self.project_ids[:delete_count]
        for i, project_id in enumerate(projects_to_delete):
            try:
                transaction_time, end_metrics = self.measure_delete_project(project_id)
                operation_count += 1
                # Only sample every SAMPLING_RATE operations
                if operation_count % SAMPLING_RATE == 0:
                    metrics.append(self._sampled_row("DELETE", end_metrics, transaction_time, project_id, operation_count))
                if (i + 1) % 100 == 0:
                    print(f"{i + 1}/{delete_count} deletes")
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        print(f"Collected {operation_count} project metrics")
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
        
        # CREATE operations
        print(f"  Creating {create_count} todos...")
        for i in range(create_count):
            try:
                transaction_time, end_metrics, todo_id = self.measure_create_todo()
                operation_count += 1
                # Only sample every SAMPLING_RATE operations
                if operation_count % SAMPLING_RATE == 0:
                    metrics.append(self._sampled_row("CREATE", end_metrics, transaction_time, todo_id, operation_count))
                if (i + 1) % 100 == 0:
                    print(f" {i + 1}/{create_count} creates")
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        # UPDATE operations
        print(f"  Updating {update_count} todos...")
        for i in range(update_count):
            if not self.todo_ids:
                print("No todos available for update")
                break
            try:
                todo_id = self.todo_ids[i % len(self.todo_ids)]
                transaction_time, end_metrics = self.measure_update_todo(todo_id)
                operation_count += 1
                # Only sample every SAMPLING_RATE operations
                if operation_count % SAMPLING_RATE == 0:
                    metrics.append(self._sampled_row("UPDATE", end_metrics, transaction_time, todo_id, operation_count))
                if (i + 1) % 100 == 0:
                    print(f"{i + 1}/{update_count} updates")
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        # DELETE operations
        print(f"  Deleting {delete_count} todos...")
        todos_to_delete = self.todo_ids[:delete_count]
        for i, todo_id in enumerate(todos_to_delete):
            try:
                transaction_time, end_metrics = self.measure_delete_todo(todo_id)
                operation_count += 1
                # Only sample every SAMPLING_RATE operations
                if operation_count % SAMPLING_RATE == 0:
                    metrics.append(self._sampled_row("DELETE", end_metrics, transaction_time, todo_id, operation_count))
                if (i + 1) % 100 == 0:
                    print(f" {i + 1}/{delete_count} deletes")
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        print(f"Collected {operation_count} todo metrics")
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
