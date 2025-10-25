#!/usr/bin/env python3
"""
Log Viewer for WorldWise Agent System
Simple tool to view and analyze agent logs
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class LogViewer:
    """Simple log viewer for agent logs"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
    
    def view_agent_reasoning(self, limit: int = 10, agent_filter: str = None):
        """View recent agent reasoning logs"""
        log_file = self.log_dir / "agent_reasoning.log"
        
        if not log_file.exists():
            print("No agent reasoning logs found.")
            return
        
        print(f"\n🔍 Agent Reasoning Logs (Last {limit} entries)")
        print("=" * 60)
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Filter and limit
        filtered_lines = []
        for line in lines:
            if agent_filter and agent_filter.lower() not in line.lower():
                continue
            filtered_lines.append(line)
        
        recent_lines = filtered_lines[-limit:] if limit > 0 else filtered_lines
        
        for line in recent_lines:
            print(line.strip())
    
    def view_api_calls(self, limit: int = 10, service_filter: str = None):
        """View recent API call logs"""
        log_file = self.log_dir / "api_calls.log"
        
        if not log_file.exists():
            print("No API call logs found.")
            return
        
        print(f"\n🌐 API Call Logs (Last {limit} entries)")
        print("=" * 60)
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Parse JSON logs
        api_calls = []
        for line in lines:
            try:
                log_entry = json.loads(line.strip())
                if service_filter and service_filter.lower() not in log_entry.get('service', '').lower():
                    continue
                api_calls.append(log_entry)
            except json.JSONDecodeError:
                continue
        
        recent_calls = api_calls[-limit:] if limit > 0 else api_calls
        
        for call in recent_calls:
            timestamp = call.get('timestamp', 'Unknown')
            service = call.get('service', 'Unknown')
            endpoint = call.get('endpoint', 'Unknown')
            status = call.get('status_code', 'Unknown')
            duration = call.get('execution_time_ms', 0)
            
            print(f"[{timestamp}] {service} {endpoint} | Status: {status} | Time: {duration:.1f}ms")
    
    def view_system_events(self, limit: int = 10):
        """View recent system events"""
        log_file = self.log_dir / "system_events.log"
        
        if not log_file.exists():
            print("No system event logs found.")
            return
        
        print(f"\n⚙️ System Events (Last {limit} entries)")
        print("=" * 60)
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        recent_lines = lines[-limit:] if limit > 0 else lines
        
        for line in recent_lines:
            print(line.strip())
    
    def view_performance(self, limit: int = 10):
        """View performance metrics"""
        log_file = self.log_dir / "performance.log"
        
        if not log_file.exists():
            print("No performance logs found.")
            return
        
        print(f"\n⚡ Performance Metrics (Last {limit} entries)")
        print("=" * 60)
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Parse JSON logs
        perf_metrics = []
        for line in lines:
            try:
                log_entry = json.loads(line.strip())
                perf_metrics.append(log_entry)
            except json.JSONDecodeError:
                continue
        
        recent_metrics = perf_metrics[-limit:] if limit > 0 else perf_metrics
        
        for metric in recent_metrics:
            timestamp = metric.get('timestamp', 'Unknown')
            operation = metric.get('operation', 'Unknown')
            duration = metric.get('duration_ms', 0)
            metadata = metric.get('metadata', {})
            
            print(f"[{timestamp}] {operation} | Duration: {duration:.1f}ms")
            if metadata:
                print(f"  Metadata: {metadata}")
    
    def search_logs(self, search_term: str, log_type: str = "all"):
        """Search across all logs for a term"""
        print(f"\n🔎 Searching for '{search_term}' in {log_type} logs")
        print("=" * 60)
        
        log_files = []
        if log_type == "all":
            log_files = [
                "agent_reasoning.log",
                "api_calls.log", 
                "system_events.log",
                "performance.log"
            ]
        else:
            log_files = [f"{log_type}.log"]
        
        found_results = []
        
        for log_file in log_files:
            file_path = self.log_dir / log_file
            if not file_path.exists():
                continue
            
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if search_term.lower() in line.lower():
                    found_results.append({
                        'file': log_file,
                        'line_number': i + 1,
                        'content': line.strip()
                    })
        
        if found_results:
            for result in found_results:
                print(f"[{result['file']}:{result['line_number']}] {result['content']}")
        else:
            print(f"No results found for '{search_term}'")
    
    def show_summary(self):
        """Show a summary of all logs"""
        print("\n📊 Log Summary")
        print("=" * 60)
        
        log_files = [
            "agent_reasoning.log",
            "api_calls.log",
            "system_events.log", 
            "performance.log"
        ]
        
        for log_file in log_files:
            file_path = self.log_dir / log_file
            if file_path.exists():
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                print(f"{log_file}: {len(lines)} entries")
            else:
                print(f"{log_file}: Not found")


def main():
    parser = argparse.ArgumentParser(description="WorldWise Agent Log Viewer")
    parser.add_argument("--log-dir", default="logs", help="Log directory path")
    parser.add_argument("--limit", type=int, default=10, help="Number of entries to show")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Agent reasoning
    agent_parser = subparsers.add_parser("agents", help="View agent reasoning logs")
    agent_parser.add_argument("--filter", help="Filter by agent name")
    
    # API calls
    api_parser = subparsers.add_parser("api", help="View API call logs")
    api_parser.add_argument("--service", help="Filter by service name")
    
    # System events
    subparsers.add_parser("system", help="View system event logs")
    
    # Performance
    subparsers.add_parser("performance", help="View performance metrics")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search logs")
    search_parser.add_argument("term", help="Search term")
    search_parser.add_argument("--type", choices=["all", "agents", "api", "system", "performance"], 
                              default="all", help="Log type to search")
    
    # Summary
    subparsers.add_parser("summary", help="Show log summary")
    
    args = parser.parse_args()
    
    viewer = LogViewer(args.log_dir)
    
    if args.command == "agents":
        viewer.view_agent_reasoning(args.limit, args.filter)
    elif args.command == "api":
        viewer.view_api_calls(args.limit, args.service)
    elif args.command == "system":
        viewer.view_system_events(args.limit)
    elif args.command == "performance":
        viewer.view_performance(args.limit)
    elif args.command == "search":
        viewer.search_logs(args.term, args.type)
    elif args.command == "summary":
        viewer.show_summary()
    else:
        # Default: show summary
        viewer.show_summary()


if __name__ == "__main__":
    main()
