# Trae Slack Platform Documentation

## Project Overview

The Trae Slack Platform is a powerful Slack integration platform built with Python and FastAPI, designed to provide AI-powered agents and memory management for Slack conversations.

## Architecture

### Core Components
- **src/app.py**: Main application entry point
- **src/agents/**: Contains various AI agent implementations
- **src/core/**: Core functionality including memory management
- **src/integrations/slack/**: Slack integration handlers
- **src/llm/**: Language model integrations

### Data Flow
1. Slack events are received through webhooks
2. Events are routed to appropriate handlers
3. AI agents process messages using language models
4. Responses are sent back to Slack

## Setup Instructions

1. Install dependencies:
```
pip install -r requirements.txt
```
2. Configure environment variables:
```
cp .env.template .env
```
3. Run the development server:
```
uvicorn src.app:app --reload
```

## Usage Examples

### Starting a Conversation
```
@trae hello
```

### Asking Questions
```
@trae What's the weather in New York?
```

### Managing Memory
```
@trae Remember that we have a meeting at 3pm
```

## Advanced Configuration

### Environment Variables
- `SLACK_BOT_TOKEN`: Your Slack bot token
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI models)

### Customizing Agents
New agents can be added in the `src/agents/` directory by extending the BaseAgent class.

## Troubleshooting

### Common Issues
1. **Invalid Slack token**: Verify SLACK_BOT_TOKEN in .env
2. **API connection errors**: Check internet connection and API keys
3. **Memory issues**: Verify thread_memory.py configuration

## Development Guidelines

### Testing
Run unit tests:
```
python -m pytest tests/
```

### Code Style
Follow PEP 8 guidelines and use Black for formatting.

### Documentation Updates
Edit this file to update project documentation.