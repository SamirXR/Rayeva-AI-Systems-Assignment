"""
Rayeva AI — Proposal API Endpoints (Module 2)
Generate B2B sustainable product proposals with AI-powered product mix and impact analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.proposal import Proposal
from app.schemas.proposal import ProposalRequest, ProposalResponse
from app.services.proposal_service import ProposalService

router = APIRouter(prefix="/api/v1", tags=["B2B Proposals — Module 2"])


@router.post("/proposals/generate", response_model=ProposalResponse)
async def generate_proposal(
    request_body: ProposalRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    AI B2B Proposal Generator.

    Takes client requirements and returns:
    - Suggested sustainable product mix
    - Server-validated cost breakdown (math done in Python)
    - Impact positioning summary
    - Structured JSON output stored in database
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    service = ProposalService(db=db, correlation_id=correlation_id)

    try:
        result = await service.generate_proposal(request_body)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proposal generation failed: {str(e)}")


@router.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: int, db: Session = Depends(get_db)):
    """Retrieve a previously generated proposal."""
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    return {
        "id": proposal.id,
        "client_name": proposal.client_name,
        "budget": proposal.budget,
        "category_preferences": proposal.category_preferences,
        "sustainability_goals": proposal.sustainability_goals,
        "occasion": proposal.occasion,
        "product_mix": proposal.product_mix,
        "budget_allocation": proposal.budget_allocation,
        "cost_breakdown": proposal.cost_breakdown,
        "impact_summary": proposal.impact_summary,
        "status": proposal.status,
        "created_at": str(proposal.created_at) if proposal.created_at else None,
    }


@router.get("/proposals")
async def list_proposals(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List all generated proposals with pagination."""
    proposals = db.query(Proposal).order_by(Proposal.id.desc()).offset(skip).limit(limit).all()
    total = db.query(Proposal).count()

    return {
        "proposals": [
            {
                "id": p.id,
                "client_name": p.client_name,
                "budget": p.budget,
                "occasion": p.occasion,
                "status": p.status,
                "created_at": str(p.created_at) if p.created_at else None,
            }
            for p in proposals
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }
