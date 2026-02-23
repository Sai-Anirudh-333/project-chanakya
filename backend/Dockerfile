# Use official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first (for docker caching)
COPY requirements.txt .

#Install dependencies

RUN pip install --no-cache-dir -r requirements.txt

#copy the rest of the backend code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Run the uvicorn server
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]