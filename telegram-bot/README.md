# CogniCraft AI Telegram Bot 🧠✨

AI-powered Telegram bot for research, analysis, and interactive web app creation.

## Features

- 🔍 **Deep Research** - Comprehensive AI-powered research on any topic
- 🧐 **Content Analysis** - Analyze text and audio for themes, sentiment, and insights
- 🎨 **App Creation** - Transform content into beautiful interactive web showcases
- 🔗 **Command Chaining** - Seamlessly flow between commands

## Quick Start (MVP)

The MVP focuses on the `/createapp` command for rapid testing.

### 1. Setup Environment

```bash
# Clone the repository
cd telegram-bot

# Install dependencies with pipenv
pipenv install

# Copy environment variables
cp .env.example .env
```

### 2. Configure .env

```env
TELEGRAM_BOT_TOKEN=your-bot-token
GEMINI_API_KEY=your-gemini-api-key
APPS_DIR=./generated_apps
```

### 3. Run MVP Bot

```bash
# Activate virtual environment
pipenv shell

# Run the MVP bot
python mvp.py
```

### 4. Test in Telegram

1. Start chat with your bot
2. Send `/createapp`
3. Provide content
4. Select visual style
5. Receive generated HTML app

## Full Installation

### Prerequisites

- Python 3.11+
- PostgreSQL (for Supabase)
- Telegram Bot Token
- Google Gemini API Key

### Setup

```bash
# Install all dependencies
pipenv install --dev

# Set up database tables in Supabase
# Run the SQL from PROJECT_REQUIREMENTS.md

# Configure all environment variables
# Edit .env with your values
```

### Run Full Bot

```bash
# Development mode
pipenv run uvicorn app.main:app --reload

# Production mode
pipenv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Project Structure

```
telegram-bot/
├── app/
│   ├── core/          # Configuration, database
│   ├── handlers/      # Command, callback, message handlers
│   ├── services/      # Gemini AI service
│   ├── utils/         # File management
│   └── main.py        # FastAPI application
├── mvp.py             # Minimal MVP implementation
├── Pipfile            # Dependencies
└── README.md          # This file
```

## Commands

### `/start`
Welcome message and command overview

### `/research` [topic]
Deep AI research on any topic
- AI-suggested refinements
- Structured output with key concepts
- Hosted research page

### `/analyze`
Analyze text or audio content
- Extract themes and sentiment
- Identify key points
- Support for voice messages

### `/createapp`
Create interactive web showcases
- Multiple visual styles
- Interactive features (quizzes, charts)
- Single-file HTML output

## Development

### Running Tests

```bash
pipenv run pytest
```

### Code Formatting

```bash
pipenv run black app/
pipenv run flake8 app/
```

### Test UI

Access the test UI at `http://localhost:8000/test-ui` when running in debug mode.

## Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system --deploy

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Webhook Setup

For production, configure webhook URL in `.env`:

```env
WEBHOOK_URL=https://your-domain.com
```

## Architecture

- **Backend**: Python FastAPI
- **Bot Framework**: python-telegram-bot
- **AI**: Google Gemini API
- **Database**: Supabase (PostgreSQL)
- **File Storage**: Local filesystem (configurable)

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License - see LICENSE file

## Support

For issues and questions:
- Create an issue in the repository
- Contact: @your_telegram_username