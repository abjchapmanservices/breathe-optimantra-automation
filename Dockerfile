FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY src/ /app/src/
COPY tests/fixtures/synthetic_daily.csv /app/tests/fixtures/synthetic_daily.csv
CMD ["python", "-m", "src.cloud_run_job"]
