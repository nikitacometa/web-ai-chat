# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install pipenv
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install project dependencies from Pipfile.lock into the system Python
# Using --system to install packages globally in the Docker image
# Using --deploy to ensure Pipfile.lock is up-to-date and fail if not
# Using --ignore-pipfile to prevent re-locking if Pipfile has changed without lock update
RUN pipenv install --system --deploy --ignore-pipfile

# Copy the rest of the application code
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run the application
# Note: If your main FastAPI app instance is in backend/main.py and named 'app',
# and WORKDIR is /app, then "main:app" is correct.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 