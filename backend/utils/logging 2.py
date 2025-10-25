"""
Structured Logging System for WorldWise Agents
Provides detailed logging for agent reasoning, API calls, and system events
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class AgentLogger:
    """
    Structured logger for agent operations
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create different loggers for different purposes
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Setup different loggers for different types of events"""
        
        # Main agent logger
        self.agent_logger = logging.getLogger('agent')
        self.agent_logger.setLevel(logging.INFO)
        
        # API call logger
        self.api_logger = logging.getLogger('api')
        self.api_logger.setLevel(logging.INFO)
        
        # System events logger
        self.system_logger = logging.getLogger('system')
        self.system_logger.setLevel(logging.INFO)
        
        # Performance logger
        self.perf_logger = logging.getLogger('performance')
        self.perf_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        for logger in [self.agent_logger, self.api_logger, self.system_logger, self.perf_logger]:
            logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        json_formatter = JSONFormatter()
        
        # Agent reasoning logs (detailed)
        agent_handler = logging.FileHandler(self.log_dir / 'agent_reasoning.log')
        agent_handler.setFormatter(detailed_formatter)
        self.agent_logger.addHandler(agent_handler)
        
        # API calls (JSON for easy parsing)
        api_handler = logging.FileHandler(self.log_dir / 'api_calls.log')
        api_handler.setFormatter(json_formatter)
        self.api_logger.addHandler(api_handler)
        
        # System events
        system_handler = logging.FileHandler(self.log_dir / 'system_events.log')
        system_handler.setFormatter(detailed_formatter)
        self.system_logger.addHandler(system_handler)
        
        # Performance metrics
        perf_handler = logging.FileHandler(self.log_dir / 'performance.log')
        perf_handler.setFormatter(json_formatter)
        self.perf_logger.addHandler(perf_handler)
        
        # Console output for development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(detailed_formatter)
        console_handler.setLevel(logging.WARNING)  # Only show warnings/errors in console
        
        for logger in [self.agent_logger, self.api_logger, self.system_logger, self.perf_logger]:
            logger.addHandler(console_handler)
    
    def log_agent_reasoning(self, agent_name: str, operation: str, input_data: Dict, 
                           output_data: Dict, reasoning: str, confidence: float, 
                           execution_time: Optional[float] = None):
        """Log detailed agent reasoning and decision making"""
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "operation": operation,
            "input_data": input_data,
            "output_data": output_data,
            "reasoning": reasoning,
            "confidence": confidence,
            "execution_time_ms": execution_time * 1000 if execution_time else None
        }
        
        self.agent_logger.info(f"[{agent_name}] {operation} | Confidence: {confidence:.2f} | Time: {execution_time:.3f}s")
        self.agent_logger.debug(json.dumps(log_data, indent=2))
    
    def log_api_call(self, service: str, endpoint: str, method: str, 
                    request_data: Dict, response_data: Dict, 
                    status_code: int, execution_time: float):
        """Log API calls with request/response data"""
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "request_data": request_data,
            "response_data": response_data,
            "status_code": status_code,
            "execution_time_ms": execution_time * 1000
        }
        
        self.api_logger.info(json.dumps(log_data))
    
    def log_system_event(self, event_type: str, message: str, data: Optional[Dict] = None):
        """Log system events like startup, errors, etc."""
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "data": data or {}
        }
        
        self.system_logger.info(f"[{event_type}] {message}")
        if data:
            self.system_logger.debug(json.dumps(log_data, indent=2))
    
    def log_performance(self, operation: str, duration: float, 
                       metadata: Optional[Dict] = None):
        """Log performance metrics"""
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "duration_ms": duration * 1000,
            "metadata": metadata or {}
        }
        
        self.perf_logger.info(json.dumps(log_data))
    
    def log_orchestrator_decision(self, user_query: str, execution_plan: Dict, 
                                 agents_activated: list, total_time: float):
        """Log orchestrator decision making process"""
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "execution_plan": execution_plan,
            "agents_activated": agents_activated,
            "total_execution_time_ms": total_time * 1000
        }
        
        self.agent_logger.info(f"[Orchestrator] Query: '{user_query}' | Agents: {agents_activated} | Time: {total_time:.3f}s")
        self.agent_logger.debug(json.dumps(log_data, indent=2))


class JSONFormatter(logging.Formatter):
    """Custom formatter for JSON logs"""
    
    def format(self, record):
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            try:
                # If it's already JSON, return as is
                json.loads(record.msg)
                return record.msg
            except (json.JSONDecodeError, TypeError):
                # If not JSON, create a JSON structure
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.msg,
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }
                return json.dumps(log_entry)
        return super().format(record)


# Global logger instance
agent_logger = AgentLogger()

# Convenience functions
def log_agent_reasoning(agent_name: str, operation: str, input_data: Dict, 
                       output_data: Dict, reasoning: str, confidence: float, 
                       execution_time: Optional[float] = None):
    """Convenience function for logging agent reasoning"""
    agent_logger.log_agent_reasoning(agent_name, operation, input_data, 
                                   output_data, reasoning, confidence, execution_time)

def log_api_call(service: str, endpoint: str, method: str, 
                request_data: Dict, response_data: Dict, 
                status_code: int, execution_time: float):
    """Convenience function for logging API calls"""
    agent_logger.log_api_call(service, endpoint, method, request_data, 
                            response_data, status_code, execution_time)

def log_system_event(event_type: str, message: str, data: Optional[Dict] = None):
    """Convenience function for logging system events"""
    agent_logger.log_system_event(event_type, message, data)

def log_performance(operation: str, duration: float, metadata: Optional[Dict] = None):
    """Convenience function for logging performance metrics"""
    agent_logger.log_performance(operation, duration, metadata)

def log_orchestrator_decision(user_query: str, execution_plan: Dict, 
                            agents_activated: list, total_time: float):
    """Convenience function for logging orchestrator decisions"""
    agent_logger.log_orchestrator_decision(user_query, execution_plan, 
                                         agents_activated, total_time)
