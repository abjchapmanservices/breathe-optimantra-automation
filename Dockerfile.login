FROM mcr.microsoft.com/playwright/python:v1.55.0-noble
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir playwright==1.55.0
COPY src/ /app/src/
RUN useradd -m runner && chown -R runner:runner /app
USER runner
CMD ["python", "-m", "src.login_smoke"]
