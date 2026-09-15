FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Runtime is intentionally limited to the service, browser assets, and the
# already-published snapshot. No ingestion cache, tests, docs, or dev packages
# are included in the local image.
COPY hepgraph /app/hepgraph
COPY static /app/static
COPY data/current.json /app/data/current.json

RUN addgroup --system hepgraph \
    && adduser --system --ingroup hepgraph hepgraph \
    && chown -R hepgraph:hepgraph /app

USER hepgraph
EXPOSE 8765

CMD ["python", "-m", "hepgraph.server", "--host", "0.0.0.0", "--port", "8765", "--snapshot", "/app/data/current.json"]
