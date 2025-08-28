FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Use enhanced price recommendation API
CMD ["python", "ml_model/price_recommendation_app.py"]
