# CogniCraft AI - Project Requirements Document

## 1. Executive Summary

**Product Name:** CogniCraft AI 🧠✨  
**Type:** Telegram Bot with Web Integration  
**Purpose:** AI-powered knowledge synthesis and interactive content creation platform

CogniCraft AI is a versatile Telegram bot that empowers users to:
- Conduct deep research on any topic using AI
- Analyze various data inputs (text, audio)
- Transform insights into beautiful, interactive web showcases
- Chain commands for seamless workflow

## 2. Core Features

### 2.1 Command Architecture

The bot provides three chainable commands:

#### `/research` 🔍 - Deep Topic Exploration
- AI-powered comprehensive research on any topic
- Smart refinement suggestions
- Structured output with summaries, key findings, and sources
- Results saved to `aiSatisfy.me/with-research/[id]`

#### `/analyze` 🧐 - Content Analysis
- Supports text and audio inputs (MVP)
- Extracts themes, sentiment, and key insights
- Future support for images, videos, URLs, documents
- Can chain output to other commands

#### `/createapp` 🎨 - Interactive Showcase Generator
- Transforms research/analysis into beautiful HTML apps
- Multiple visual personas and interaction styles
- Customizable display options (quizzes, charts, tables)
- Apps hosted at `aiSatisfy.me/with-app/[id]`

### 2.2 Command Chaining
Users can seamlessly flow between commands:
- Research → Create App
- Analyze → Research → Create App
- Any combination based on user needs

## 3. Technical Architecture

### 3.1 Backend Stack
- **Framework:** Python FastAPI
- **Bot Library:** python-telegram-bot
- **Database:** Supabase (PostgreSQL)
- **AI Provider:** Google Gemini API
- **Optional:** LangChain for prompt management

### 3.2 Infrastructure
- **Hosting:** Server with domain aiSatisfy.me
- **File Storage:** Local directories for HTML files
  - `/var/www/aisatisfy.me/research/`
  - `/var/www/aisatisfy.me/apps/`
- **Web Server:** Nginx as reverse proxy

### 3.3 Environment Variables
```env
GEMINI_API_KEY=your-api-key
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
TELEGRAM_BOT_TOKEN=your-bot-token
DOMAIN_URL=https://aisatisfy.me
```

## 4. User Experience Design

### 4.1 Conversation Flow

#### Research Flow
1. User: `/research quantum computing`
2. Bot: Confirms topic, offers AI refinements
3. User: Selects refinements or adds custom focus
4. Bot: Shows progress with engaging messages
5. Bot: Presents summary + link to full research
6. Bot: Suggests next actions (create app, analyze further)

#### Analyze Flow
1. User: `/analyze` + sends audio/text
2. Bot: Processes content
3. Bot: Shows analysis (themes, sentiment, summary)
4. Bot: Suggests chaining to research or app creation

#### Create App Flow
1. User: `/createapp` (standalone or chained)
2. Bot: Asks for visual style (Crimson Codex, Quantum Void, etc.)
3. Bot: Offers interaction options (quizzes, charts, etc.)
4. Bot: Generates and hosts app
5. Bot: Provides link and downloadable HTML

### 4.2 UI Elements
- **Inline Keyboards:** For selections and navigation
- **Progress Messages:** Animated updates during processing
- **Rich Formatting:** Bold, italic, code blocks for results
- **Emojis:** Extensive use for visual appeal
- **File Attachments:** HTML files for offline access

## 5. AI Prompt Engineering

### 5.1 Research Prompt
Generates comprehensive, structured research with:
- Executive summary
- Key concepts with explanations
- Current developments
- Practical applications
- Future trends
- Formatted as JSON schema

### 5.2 Analysis Prompt
Processes content to extract:
- Concise summary (100 words)
- 3-5 key themes
- Sentiment analysis
- Tone identification

### 5.3 App Generation Prompt
Creates single-file HTML apps with:
- Tailwind CSS styling
- Vanilla JavaScript interactivity
- Responsive design
- Selected visual persona
- User-chosen interaction patterns

## 6. MVP Implementation Plan

### Phase 1: Basic Infrastructure (Week 1)
- [ ] Set up FastAPI project structure
- [ ] Configure Telegram webhook
- [ ] Implement basic command handlers
- [ ] Set up Supabase connection
- [ ] Configure environment variables

### Phase 2: CreateApp Command (Week 2)
- [ ] Implement `/createapp` flow
- [ ] Basic text input handling
- [ ] Two visual style options
- [ ] Gemini API integration for HTML generation
- [ ] File saving and serving logic
- [ ] URL generation system

### Phase 3: Testing & Polish (Week 3)
- [ ] Simple web UI for testing
- [ ] Error handling
- [ ] Progress messages
- [ ] Basic logging
- [ ] Deploy to server

### Phase 4: Full Feature Set (Weeks 4-6)
- [ ] Implement `/research` command
- [ ] Implement `/analyze` with audio support
- [ ] Command chaining logic
- [ ] Advanced app customization
- [ ] Performance optimization

## 7. Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP
);
```

### Commands Table
```sql
CREATE TABLE commands (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    command_type VARCHAR(50),
    input_data JSONB,
    output_data JSONB,
    file_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### User State Table
```sql
CREATE TABLE user_states (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    current_command VARCHAR(50),
    last_command_id INTEGER REFERENCES commands(id),
    state_data JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 8. Security Considerations

- API keys stored as environment variables
- Input validation for all user data
- Rate limiting for API calls
- Secure file storage with unique IDs
- HTTPS for all web content
- No user data in URLs

## 9. Future Enhancements

- Support for more input types (images, PDFs, URLs)
- Multi-language support
- User accounts with history
- Collaborative features
- API access for developers
- Custom branding options

## 10. Success Metrics

- Command completion rate
- Average generation time
- User retention (daily/weekly active)
- Generated content engagement
- Error rate < 1%
- Response time < 3s for simple commands