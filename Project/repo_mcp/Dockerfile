FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
ENV FLASK_APP=app.server
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
