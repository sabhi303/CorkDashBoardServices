# official Python runtime as a base image
FROM python:3.9

WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container at /app
COPY . .

# Ensure the .env file is copied
COPY .env .env

# Export environment variables from the .env file (optional during build)
# RUN export $(cat .env | xargs)

CMD ["python", "main.py"]
