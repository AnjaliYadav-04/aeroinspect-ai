FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir pydantic-settings==2.1.0

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/models /app/reports

COPY models/ /app/models/

COPY src/ /app/src/

WORKDIR /app/src

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]