# Arize AI Integration for Lingua-Cal Agent Evaluations

This guide will help you set up comprehensive agent evaluation and monitoring using Arize AI's observability platform.

## 🚀 Quick Setup

Run the automated setup script:

```bash
python setup_arize.py
```

This will:
- Install all required dependencies
- Set up environment configuration
- Create evaluation task definitions
- Generate dashboard configurations
- Create test scripts

## 📋 Manual Setup Steps

### 1. Install Dependencies

```bash
pip install arize==7.0.0
pip install opentelemetry-api==1.21.0
pip install opentelemetry-sdk==1.21.0
pip install opentelemetry-instrumentation==0.42b0
pip install opentelemetry-instrumentation-aiohttp-client==0.42b0
pip install opentelemetry-instrumentation-requests==0.42b0
pip install opentelemetry-exporter-otlp==1.21.0
```

### 2. Get Arize Credentials

1. Sign up at [Arize AI](https://arize.com)
2. Create a new space
3. Get your Space ID and API Key from the dashboard

### 3. Configure Environment Variables

Update `backend/.env` with your Arize credentials:

```bash
# Arize AI Observability Configuration
ARIZE_SPACE_ID=your_arize_space_id
ARIZE_API_KEY=your_arize_api_key
ARIZE_PROJECT_NAME=lingua-cal-agents
ARIZE_ENVIRONMENT=development
```

### 4. Test Integration

```bash
python test_arize_integration.py
```

## 🔧 What's Included

### Agent Monitoring

All agents automatically log:
- **Execution metrics**: Confidence scores, execution time, success rates
- **Performance data**: Token usage, response quality, error rates
- **User interactions**: Engagement levels, satisfaction scores
- **Evaluation results**: Learning progress, improvement areas

### Evaluation Metrics

The system tracks:
- `confidence_score`: Agent confidence in responses (0.0-1.0)
- `execution_time_ms`: Time taken to process requests
- `success_rate`: Percentage of successful executions
- `response_quality_score`: Quality assessment of outputs
- `user_satisfaction_score`: User feedback scores
- `error_rate`: Frequency of errors
- `retry_count`: Number of retry attempts

### Traced Agents

- **EvaluationAgent**: Learning progress assessment
- **ProgressAnalyticsAgent**: Deep learning analytics
- **VocabularyBuilderAgent**: Vocabulary learning metrics
- **PronunciationCoachAgent**: Pronunciation improvement tracking
- **CulturalEtiquetteAgent**: Cultural learning progress
- **MotivationCoachAgent**: Motivation and engagement metrics
- **LanguageCorrectionAgent**: Language accuracy improvements
- **CulturalContextAgent**: Cultural understanding metrics
- **TranslationAgent**: Translation quality assessment
- **ConversationAgent**: Conversation fluency tracking
- **PersonalizationAgent**: Personalization effectiveness
- **DataRetrievalAgent**: Data retrieval performance

## 📊 Dashboard Configuration

### Agent Performance Overview
- Overall success rates across all agents
- Average execution times
- Confidence score trends over time
- Error rate monitoring

### Learning Progress Analytics
- Learning progress scores
- User engagement trends
- Top improvement areas
- Cultural understanding metrics

### Error Monitoring
- Error rates by agent
- Recent error logs
- Performance degradation alerts
- Debugging information

## 🎯 Evaluation Tasks

### Learning Progress Evaluation
- **Criteria**: Language improvement, cultural understanding, engagement
- **Schedule**: Continuous monitoring
- **Thresholds**: Excellent (0.8+), Good (0.6+), Needs Work (0.4+)

### Agent Performance Evaluation
- **Criteria**: Confidence, execution time, success rate, error rate
- **Schedule**: Continuous monitoring
- **Alerts**: Low confidence, high execution time, high error rate

### User Satisfaction Evaluation
- **Criteria**: Session completion, interaction quality, learning progress
- **Schedule**: Daily aggregation
- **Thresholds**: High (0.8+), Medium (0.6+), Low (0.4+)

## 🔍 Monitoring Features

### Real-time Tracing
- Complete execution traces for all agents
- Performance bottleneck identification
- Error debugging and root cause analysis
- User journey tracking

### Evaluation Analytics
- Learning progress trends
- Agent performance comparisons
- User satisfaction metrics
- Improvement area identification

### Alerting
- High error rate alerts
- Low confidence warnings
- Performance degradation notifications
- Custom threshold monitoring

## 📈 Usage Examples

### Logging Agent Execution
```python
from integrations.arize import log_agent_execution

log_agent_execution(
    agent_name="VocabularyBuilder",
    user_id="user_123",
    session_id="session_456",
    input_data={"word": "hello", "context": "greeting"},
    output_data={"translation": "hola", "confidence": 0.9},
    execution_time=1.2,
    confidence=0.9,
    status="success"
)
```

### Logging Evaluation Results
```python
from integrations.arize import log_evaluation_result

log_evaluation_result(
    agent_name="Evaluation",
    user_id="user_123",
    evaluation_type="learning_progress",
    evaluation_data={
        "language_improvement": "good",
        "cultural_understanding": "excellent",
        "engagement_level": "high"
    },
    score=0.8,
    feedback="Strong progress in cultural understanding"
)
```

### Logging User Interactions
```python
from integrations.arize import log_user_interaction

log_user_interaction(
    user_id="user_123",
    interaction_type="vocabulary_practice",
    interaction_data={
        "words_practiced": 15,
        "accuracy": 0.85,
        "session_duration": 300
    },
    satisfaction_score=0.9
)
```

## 🛠️ Configuration Files

- `backend/arize_config.json`: Main configuration
- `backend/evaluation_tasks.json`: Evaluation task definitions
- `backend/arize_dashboard_config.json`: Dashboard setup
- `backend/integrations/arize.py`: Core integration module

## 🔧 Troubleshooting

### Common Issues

1. **"Arize integration disabled"**
   - Check environment variables are set correctly
   - Verify Space ID and API Key are valid

2. **Import errors**
   - Run: `pip install -r backend/requirements.txt`
   - Ensure all dependencies are installed

3. **No data in dashboard**
   - Check network connectivity
   - Verify credentials are correct
   - Run test script to verify integration

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger("integrations.arize").setLevel(logging.DEBUG)
```

## 📚 Additional Resources

- [Arize Documentation](https://docs.arize.com)
- [Agent Evaluation Guide](https://docs.arize.com/agent-evaluation)
- [OpenTelemetry Integration](https://docs.arize.com/otel)
- [Dashboard Configuration](https://docs.arize.com/dashboards)

## 🆘 Support

For issues with:
- **Arize Platform**: Contact Arize support
- **Integration Code**: Check the logs and run test script
- **Configuration**: Review environment variables and config files

---

**Note**: This integration provides comprehensive monitoring and evaluation for all your language learning agents. The system automatically tracks performance, learning progress, and user satisfaction to help you continuously improve your AI agents.
