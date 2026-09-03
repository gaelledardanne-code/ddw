"""Stats API."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.stats_service import Stats, StatsService

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=Stats)
def get_stats(db: Session = Depends(get_db)) -> Stats:
    return StatsService(db).compute()
