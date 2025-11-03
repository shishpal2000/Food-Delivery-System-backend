# Use the official lightweight Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .


# Expose Django's default port
EXPOSE 8000

# Run migrations and start the Django app using Gunicorn
CMD ["gunicorn", "food_delivery.wsgi:application", "--bind", "0.0.0.0:8000"]