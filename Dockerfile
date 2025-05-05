FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y espeak libsndfile1 ffmpeg

RUN pip install --no-cache-dir grpcio requests TTS gradio

EXPOSE 5000
EXPOSE 5001

CMD ["python", "app.py"]
