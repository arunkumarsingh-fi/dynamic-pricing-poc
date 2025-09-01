FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Ensure data directory exists
RUN mkdir -p /app/data
EXPOSE 8502
CMD ["streamlit", "run", "ui.py", "--server.port=8502", "--server.address=0.0.0.0"]
