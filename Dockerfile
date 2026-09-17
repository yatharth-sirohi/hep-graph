FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Runtime is limited to the service and browser assets. The graph lives in Neon.
COPY hepgraph /app/hepgraph
COPY static /app/static

RUN addgroup --system hepgraph \
    && adduser --system --ingroup hepgraph hepgraph \
    && chown -R hepgraph:hepgraph /app

USER hepgraph
EXPOSE 8765

CMD ["python", "-m", "hepgraph.server", "--host", "0.0.0.0", "--port", "8765"]
