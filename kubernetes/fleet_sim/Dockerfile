# Use the official Python 3.10 image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt /app/

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --pre mesa[viz]

# Copy the rest of the application code
COPY . /app/

# Command to run the application
CMD ["python", "run.py"]