import os
import json
import httpx
from app_factory import create_app
from fastapi import Body, Response, HTTPException
from integrations.ollama import ollama_client
from integrations.qdrant import qdrant_client
from integrations.redis import redis_client
from qdrant_client import QdrantClient
from utils.parser import PARSER_METRICS, LogParser

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
log_store: list[dict] = []
total_logs_ingested: int = 0

app = create_app()

@app.get("/metrics/parser")
async def parser_metrics():
    return {
        "parser_metrics": PARSER_METRICS
    }

@app.get("/dashboard")
async def dashboard():
    recent_logs = list(reversed(log_store[-10:]))
    anomalies = sum(1 for log in log_store if log.get("level") == "ERROR")
    active_services = len({log.get("service", "unknown") for log in log_store})

    return {
        "logs_processed": total_logs_ingested,
        "anomalies": anomalies,
        "active_services": active_services,
        "ai_insights": anomalies,
        "recent_logs": recent_logs,
        "ai_summary": (
            "No anomalies detected."
            if anomalies == 0
            else f"{anomalies} ERROR-level events detected across {active_services} service(s). Review recent logs for details."
        )
    }

@app.get("/logs")
async def get_logs():
    return {
        "logs": list(reversed(log_store)),
        "count": len(log_store)
    }

@app.get("/health", status_code=200)
async def health_check(response: Response):
    services = {}

    try:
        redis_client.ping()
        services["redis"] = {"status": "healthy"}
    except Exception as e:
        services["redis"] = {"status": "unhealthy", "error": str(e)}

    try:
        qclient = QdrantClient(url=QDRANT_URL, timeout=3)
        qclient.get_collections()
        services["qdrant"] = {"status": "healthy"}
    except Exception as e:
        services["qdrant"] = {"status": "unhealthy", "error": str(e)}

    try:
        r = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3.0)
        if r.status_code == 200:
            services["ollama"] = {"status": "healthy"}
        else:
            services["ollama"] = {"status": "unhealthy", "error": f"HTTP {r.status_code}"}
    except Exception as e:
        services["ollama"] = {"status": "unhealthy", "error": str(e)}

    overall = "unhealthy" if any(
        s["status"] == "unhealthy" for s in services.values()
    ) else "healthy"

    if overall == "unhealthy":
        response.status_code = 503

    return {
        "status": overall,
        "services": services
    }