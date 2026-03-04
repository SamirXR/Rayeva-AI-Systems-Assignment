"""
Rayeva AI — AI Logs API Endpoint
View prompt + response logs, token usage, latency, and costs.
Satisfies Technical Requirement #2: Prompt + response logging.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.ai_log import AILog

router = APIRouter(prefix="/api/v1", tags=["AI Logs & Metrics"])


@router.get("/logs")
async def list_ai_logs(
    module: str | None = None,
    success_only: bool | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List AI call logs with optional filters."""
    query = db.query(AILog).order_by(AILog.id.desc())

    if module:
        query = query.filter(AILog.module == module)
    if success_only is not None:
        query = query.filter(AILog.parsed_success == success_only)

    logs = query.offset(skip).limit(limit).all()
    total = query.count()

    return {
        "logs": [
            {
                "id": log.id,
                "correlation_id": log.correlation_id,
                "module": log.module,
                "prompt_version": log.prompt_version,
                "model": log.model,
                "provider": log.provider,
                "input_tokens": log.input_tokens,
                "output_tokens": log.output_tokens,
                "thinking_tokens": log.thinking_tokens,
                "latency_ms": log.latency_ms,
                "parsed_success": log.parsed_success,
                "error": log.error,
                "raw_input": log.raw_input,
                "raw_output": log.raw_output,
                "created_at": str(log.created_at) if log.created_at else None,
            }
            for log in logs
        ],
        "total": total,
    }


@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    """
    Dashboard metrics: total calls, avg latency, token usage, success rate.
    """
    total_calls = db.query(func.count(AILog.id)).scalar() or 0
    successful = db.query(func.count(AILog.id)).filter(AILog.parsed_success == True).scalar() or 0
    avg_latency = db.query(func.avg(AILog.latency_ms)).scalar() or 0
    total_input_tokens = db.query(func.sum(AILog.input_tokens)).scalar() or 0
    total_output_tokens = db.query(func.sum(AILog.output_tokens)).scalar() or 0
    total_thinking_tokens = db.query(func.sum(AILog.thinking_tokens)).scalar() or 0

    # Module breakdown
    module_stats = (
        db.query(
            AILog.module,
            func.count(AILog.id).label("calls"),
            func.avg(AILog.latency_ms).label("avg_latency"),
        )
        .group_by(AILog.module)
        .all()
    )

    return {
        "total_calls": total_calls,
        "successful_calls": successful,
        "failed_calls": total_calls - successful,
        "success_rate": round(successful / total_calls * 100, 1) if total_calls > 0 else 0,
        "avg_latency_ms": round(avg_latency, 2),
        "total_tokens": {
            "input": total_input_tokens,
            "output": total_output_tokens,
            "thinking": total_thinking_tokens,
            "total": total_input_tokens + total_output_tokens + total_thinking_tokens,
        },
        "module_breakdown": [
            {
                "module": m.module,
                "calls": m.calls,
                "avg_latency_ms": round(m.avg_latency, 2) if m.avg_latency else 0,
            }
            for m in module_stats
        ],
    }
