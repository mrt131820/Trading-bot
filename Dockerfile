FROM python:3.11-slim
WORKDIR /src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/test_main_final.py .
COPY config/ config/

EXPOSE 8080