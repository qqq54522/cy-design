FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8100

FROM base AS dev
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100", "--reload"]

FROM base AS prod
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100", "--workers", "2"]
