# WorldWise Agent Logging System

A comprehensive logging system for tracking agent reasoning, API calls, and system performance.

## Features

- **Agent Reasoning Logs**: Detailed logs of each agent's decision-making process
- **API Call Logs**: Structured JSON logs of all API calls with timing
- **System Events**: Logs of system startup, errors, and important events
- **Performance Metrics**: Timing and performance data for all operations
- **Log Viewer**: Command-line tool for analyzing logs

## Log Files

All logs are stored in the `logs/` directory:

- `agent_reasoning.log` - Detailed agent decision logs
- `api_calls.log` - JSON logs of API calls
- `system_events.log` - System events and errors
- `performance.log` - Performance metrics

## Using the Log Viewer

### View Recent Agent Reasoning
```bash
python3 log_viewer.py agents --limit 20
```

### View API Calls
```bash
python3 log_viewer.py api --limit 10
```

### Search Logs
```bash
python3 log_viewer.py search "error" --type agents
python3 log_viewer.py search "anthropic" --type api
```

### View Performance Metrics
```bash
python3 log_viewer.py performance --limit 15
```

### Show Summary
```bash
python3 log_viewer.py summary
```

## Log Structure

### Agent Reasoning Logs
```
2024-01-15 10:30:45 | agent | INFO | [Orchestrator] process | Confidence: 0.85 | Time: 0.234s
```

### API Call Logs (JSON)
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "service": "anthropic",
  "endpoint": "/v1/messages",
  "method": "POST",
  "status_code": 200,
  "execution_time_ms": 234.5
}
```

### Performance Logs (JSON)
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "operation": "Orchestrator_process",
  "duration_ms": 234.5,
  "metadata": {
    "agent_name": "Orchestrator",
    "status": "success",
    "confidence": 0.85
  }
}
```

## Integration

The logging system is automatically integrated into all agents through the `BaseAgent` class. Each agent's `process` method is automatically wrapped with logging functionality.

### Manual Logging

You can also manually log events:

```python
from logging_system import log_system_event, log_performance

# Log system events
log_system_event("startup", "Agent system initialized", {"version": "1.0.0"})

# Log performance
log_performance("custom_operation", 0.123, {"custom_data": "value"})
```

## Troubleshooting

### Log Files Not Created
- Ensure the `logs/` directory exists and is writable
- Check that the logging system is properly imported

### Missing Logs
- Verify that agents are using the `BaseAgent` class
- Check that the logging system is initialized

### Performance Impact
- Logging adds minimal overhead (~1-2ms per operation)
- JSON parsing for API logs is optimized
- Log files are rotated automatically

## Example Usage

```bash
# View recent orchestrator decisions
python3 log_viewer.py agents --filter orchestrator --limit 5

# Check API performance
python3 log_viewer.py api --service anthropic --limit 10

# Search for errors
python3 log_viewer.py search "error" --type all

# Monitor performance
python3 log_viewer.py performance --limit 20
```
