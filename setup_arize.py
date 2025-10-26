#!/usr/bin/env python3
"""
Arize Setup Script for Lingua-Cal Agent Evaluations
This script helps set up Arize AI observability for all agents
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "arize",
        "opentelemetry-api",
        "opentelemetry-sdk",
        "opentelemetry-instrumentation",
        "opentelemetry-instrumentation-aiohttp-client",
        "opentelemetry-instrumentation-requests",
        "opentelemetry-exporter-otlp"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            return False
    
    return True

def setup_environment():
    """Set up environment variables for Arize"""
    print("\n🔧 Setting up environment variables...")
    
    env_file = Path("backend/.env")
    env_template = Path("backend/env.template")
    
    if not env_template.exists():
        print("❌ Environment template not found!")
        return False
    
    if env_file.exists():
        print("⚠️  .env file already exists. Backing up...")
        backup_file = Path("backend/.env.backup")
        env_file.rename(backup_file)
        print(f"✅ Backed up to {backup_file}")
    
    # Copy template to .env
    with open(env_template, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template")
    print("\n📝 Please update the following variables in backend/.env:")
    print("   - ARIZE_SPACE_ID: Your Arize Space ID")
    print("   - ARIZE_API_KEY: Your Arize API Key")
    print("   - ARIZE_PROJECT_NAME: lingua-cal-agents (or your preferred name)")
    print("   - ARIZE_ENVIRONMENT: development (or production)")
    
    return True

def create_arize_config():
    """Create Arize configuration file"""
    print("\n⚙️  Creating Arize configuration...")
    
    config = {
        "project_name": "lingua-cal-agents",
        "environment": "development",
        "agents": [
            "Evaluation",
            "ProgressAnalytics", 
            "VocabularyBuilder",
            "PronunciationCoach",
            "CulturalEtiquette",
            "MotivationCoach",
            "LanguageCorrection",
            "CulturalContext",
            "Translation",
            "Conversation",
            "Personalization",
            "DataRetrieval"
        ],
        "evaluation_metrics": [
            "confidence_score",
            "execution_time_ms",
            "success_rate",
            "response_quality_score",
            "user_satisfaction_score",
            "error_rate",
            "retry_count"
        ],
        "monitoring": {
            "trace_agent_executions": True,
            "log_evaluation_results": True,
            "log_user_interactions": True,
            "performance_monitoring": True,
            "error_tracking": True
        }
    }
    
    config_file = Path("backend/arize_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created Arize configuration: {config_file}")
    return True

def create_evaluation_tasks():
    """Create evaluation task definitions"""
    print("\n📊 Creating evaluation task definitions...")
    
    evaluation_tasks = {
        "learning_progress_evaluation": {
            "description": "Evaluate learning progress across all agents",
            "agent": "Evaluation",
            "criteria": {
                "language_improvement": "excellent/good/needs_work",
                "cultural_understanding": "excellent/good/needs_work", 
                "engagement_level": "high/medium/low"
            },
            "schedule": "continuous",
            "thresholds": {
                "excellent": 0.8,
                "good": 0.6,
                "needs_work": 0.4
            }
        },
        "agent_performance_evaluation": {
            "description": "Monitor agent performance metrics",
            "agents": ["all"],
            "criteria": {
                "confidence_score": "float 0.0-1.0",
                "execution_time_ms": "int",
                "success_rate": "float 0.0-1.0",
                "error_rate": "float 0.0-1.0"
            },
            "schedule": "continuous",
            "alerts": {
                "low_confidence": 0.5,
                "high_execution_time": 5000,
                "high_error_rate": 0.1
            }
        },
        "user_satisfaction_evaluation": {
            "description": "Track user satisfaction and engagement",
            "agent": "all",
            "criteria": {
                "session_completion_rate": "float 0.0-1.0",
                "interaction_quality": "float 0.0-1.0",
                "learning_progress_rate": "float 0.0-1.0"
            },
            "schedule": "daily",
            "thresholds": {
                "high_satisfaction": 0.8,
                "medium_satisfaction": 0.6,
                "low_satisfaction": 0.4
            }
        }
    }
    
    tasks_file = Path("backend/evaluation_tasks.json")
    with open(tasks_file, 'w') as f:
        json.dump(evaluation_tasks, f, indent=2)
    
    print(f"✅ Created evaluation tasks: {tasks_file}")
    return True

def create_dashboard_config():
    """Create dashboard configuration for Arize"""
    print("\n📈 Creating dashboard configuration...")
    
    dashboard_config = {
        "dashboards": [
            {
                "name": "Agent Performance Overview",
                "description": "High-level view of all agent performance",
                "widgets": [
                    {
                        "type": "metric",
                        "title": "Overall Success Rate",
                        "metric": "success_rate",
                        "aggregation": "average"
                    },
                    {
                        "type": "metric", 
                        "title": "Average Execution Time",
                        "metric": "execution_time_ms",
                        "aggregation": "average"
                    },
                    {
                        "type": "chart",
                        "title": "Confidence Scores Over Time",
                        "metric": "confidence_score",
                        "chart_type": "line"
                    }
                ]
            },
            {
                "name": "Learning Progress Analytics",
                "description": "Detailed learning progress and evaluation metrics",
                "widgets": [
                    {
                        "type": "metric",
                        "title": "Learning Progress Score",
                        "metric": "learning_progress_score",
                        "aggregation": "average"
                    },
                    {
                        "type": "chart",
                        "title": "User Engagement Trends",
                        "metric": "engagement_level",
                        "chart_type": "bar"
                    },
                    {
                        "type": "table",
                        "title": "Top Improvement Areas",
                        "metric": "improvement_areas",
                        "aggregation": "count"
                    }
                ]
            },
            {
                "name": "Error Monitoring",
                "description": "Agent error tracking and debugging",
                "widgets": [
                    {
                        "type": "metric",
                        "title": "Error Rate",
                        "metric": "error_rate",
                        "aggregation": "average"
                    },
                    {
                        "type": "chart",
                        "title": "Errors by Agent",
                        "metric": "error_count",
                        "chart_type": "pie"
                    },
                    {
                        "type": "table",
                        "title": "Recent Errors",
                        "metric": "error_logs",
                        "aggregation": "latest"
                    }
                ]
            }
        ],
        "alerts": [
            {
                "name": "High Error Rate Alert",
                "condition": "error_rate > 0.1",
                "severity": "warning",
                "notification": "email"
            },
            {
                "name": "Low Confidence Alert", 
                "condition": "confidence_score < 0.5",
                "severity": "info",
                "notification": "slack"
            },
            {
                "name": "Performance Degradation Alert",
                "condition": "execution_time_ms > 10000",
                "severity": "critical",
                "notification": "email"
            }
        ]
    }
    
    dashboard_file = Path("backend/arize_dashboard_config.json")
    with open(dashboard_file, 'w') as f:
        json.dump(dashboard_config, f, indent=2)
    
    print(f"✅ Created dashboard configuration: {dashboard_file}")
    return True

def create_test_script():
    """Create test script to verify Arize integration"""
    print("\n🧪 Creating test script...")
    
    test_script = '''#!/usr/bin/env python3
"""
Test script for Arize integration
Run this to verify that Arize is properly configured
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

async def test_arize_integration():
    """Test Arize integration"""
    print("🧪 Testing Arize integration...")
    
    try:
        from integrations.arize import arize_integration
        
        if not arize_integration.enabled:
            print("❌ Arize integration is disabled")
            print("   Check your environment variables:")
            print("   - ARIZE_SPACE_ID")
            print("   - ARIZE_API_KEY")
            return False
        
        print("✅ Arize integration is enabled")
        
        # Test logging a sample agent execution
        test_data = {
            "agent_name": "TestAgent",
            "user_id": "test_user_123",
            "session_id": "test_session_456",
            "input_data": {"test": "input"},
            "output_data": {"test": "output", "confidence": 0.8},
            "execution_time": 1.5,
            "confidence": 0.8,
            "status": "success"
        }
        
        arize_integration.log_agent_execution(**test_data)
        print("✅ Successfully logged test agent execution")
        
        # Test logging evaluation result
        arize_integration.log_evaluation_result(
            agent_name="TestAgent",
            user_id="test_user_123",
            evaluation_type="test_evaluation",
            evaluation_data={"score": 0.85},
            score=0.85
        )
        print("✅ Successfully logged test evaluation result")
        
        # Test logging user interaction
        arize_integration.log_user_interaction(
            user_id="test_user_123",
            interaction_type="test_interaction",
            interaction_data={"satisfaction": 0.9},
            satisfaction_score=0.9
        )
        print("✅ Successfully logged test user interaction")
        
        print("\\n🎉 All tests passed! Arize integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_arize_integration())
    sys.exit(0 if success else 1)
'''
    
    test_file = Path("test_arize_integration.py")
    with open(test_file, 'w') as f:
        f.write(test_script)
    
    # Make executable
    test_file.chmod(0o755)
    
    print(f"✅ Created test script: {test_file}")
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 Arize Setup Complete!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Get your Arize credentials:")
    print("   - Sign up at https://arize.com")
    print("   - Create a new space")
    print("   - Get your Space ID and API Key")
    print("\n2. Update your environment variables:")
    print("   - Edit backend/.env")
    print("   - Set ARIZE_SPACE_ID and ARIZE_API_KEY")
    print("\n3. Test the integration:")
    print("   - Run: python test_arize_integration.py")
    print("\n4. Start your agents:")
    print("   - All agents will now automatically log to Arize")
    print("   - View traces and metrics in your Arize dashboard")
    print("\n5. Set up evaluation tasks:")
    print("   - Use backend/evaluation_tasks.json as reference")
    print("   - Create tasks in your Arize dashboard")
    print("\n6. Configure dashboards:")
    print("   - Use backend/arize_dashboard_config.json as reference")
    print("   - Set up monitoring dashboards in Arize")
    print("\n📚 Documentation:")
    print("   - Arize Docs: https://docs.arize.com")
    print("   - Agent Evaluation Guide: https://docs.arize.com/agent-evaluation")
    print("\n🔧 Configuration Files Created:")
    print("   - backend/arize_config.json")
    print("   - backend/evaluation_tasks.json") 
    print("   - backend/arize_dashboard_config.json")
    print("   - test_arize_integration.py")

def main():
    """Main setup function"""
    print("🚀 Setting up Arize AI for Lingua-Cal Agent Evaluations")
    print("="*60)
    
    steps = [
        ("Checking dependencies", check_dependencies),
        ("Setting up environment", setup_environment),
        ("Creating Arize configuration", create_arize_config),
        ("Creating evaluation tasks", create_evaluation_tasks),
        ("Creating dashboard configuration", create_dashboard_config),
        ("Creating test script", create_test_script)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Failed: {step_name}")
            return False
        print(f"✅ Completed: {step_name}")
    
    print_next_steps()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
