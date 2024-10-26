# Use the official Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all application files into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the main Python script
CMD ["python", "src/weather_monitoring.py"]
