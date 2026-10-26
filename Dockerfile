FROM python:3.12-slim
WORKDIR /app
COPY . /app
EXPOSE 8000
CMD ["python3", "jobhunter_server.py"]
