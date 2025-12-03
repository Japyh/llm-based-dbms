"""FastAPI application exposing SQL and NL endpoints."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
import uvicorn

from src import config
from src.db import core as db_core
from src.llm.provider import get_llm_provider
from src.nl2sql.engine import NL2SQLEngine
from src.validation import sql_validator

logger = logging.getLogger(__name__)

app = FastAPI(title="LLM DBMS", version="0.1.0")
settings = config.get_settings()
schema_info = db_core.get_schema_info(settings)
llm_provider = None
try:  # pragma: no cover - runtime dependency
    llm_provider = get_llm_provider(settings)
except Exception as exc:
    logger.warning("LLM provider not initialized: %s", exc)
engine = NL2SQLEngine(db_module=db_core, llm=llm_provider, settings=settings) if llm_provider else None


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/query_sql")
def query_sql(payload: Dict[str, Any]) -> Dict[str, Any]:
    sql = payload.get("sql", "")
    try:
        sql_validator.validate_sql(sql, schema_info)
        rows = db_core.run_query(sql, settings=settings)
        return {"rows": rows}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/query_nl")
def query_nl(payload: Dict[str, Any]) -> Dict[str, Any]:
    if engine is None:
        raise HTTPException(status_code=500, detail="LLM provider not configured")
    nl_query = payload.get("query", "")
    try:
        sql, rows = engine.run_nl_query(nl_query)
        return {"sql": sql, "rows": rows}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="0.0.0.0", port=8000)
