# Use the official Python 3.10 image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install any necessary dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python scripts into the container
COPY fleet_model.py run.py

# Command to run the application
CMD ["python", "run.py"]