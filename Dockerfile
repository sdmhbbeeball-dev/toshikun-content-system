FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    HOST=0.0.0.0 \
    PORT=10000

WORKDIR /app
COPY src ./src

EXPOSE 10000
CMD ["python", "-m", "toshikun_sns.web"]
