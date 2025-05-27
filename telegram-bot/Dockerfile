FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY telegram-bot/Pipfile ./
RUN pip install pipenv && \
    pipenv requirements > requirements.txt && \
    pip install -r requirements.txt

# Copy application code
COPY telegram-bot/ ./

# Create directories for generated files
RUN mkdir -p /app/generated_apps /app/research /app/apps

# Run the application
CMD ["python", "mvp.py"]