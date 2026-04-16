from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from src.db.database import get_db
from src.db.models import FollowUp, User
from src.db.schemas import FollowUpCreate, FollowUpUpdate, FollowUpResponse
from src.api.deps import get_current_user
import uuid

router = APIRouter(prefix="/follow-ups", tags=["follow-ups"])


@router.get("", response_model=List[FollowUpResponse])
async def get_follow_ups(
    interaction_id: Optional[str] = Query(None),
    assignee_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(FollowUp)

    if interaction_id:
        query = query.where(FollowUp.interaction_id == interaction_id)
    if assignee_id:
        query = query.where(FollowUp.assignee_id == assignee_id)
    if status_filter:
        query = query.where(FollowUp.status == status_filter)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=FollowUpResponse)
async def create_follow_up(
    follow_up_data: FollowUpCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    follow_up = FollowUp(
        id=str(uuid.uuid4()),
        interaction_id=follow_up_data.interaction_id,
        type=follow_up_data.type.value,
        description=follow_up_data.description,
        status=follow_up_data.status.value,
        due_date=follow_up_data.due_date,
        assignee_id=current_user.id,
        created_by=current_user.id,
        ai_generated=follow_up_data.ai_generated,
    )
    db.add(follow_up)
    await db.commit()
    await db.refresh(follow_up)
    return follow_up


@router.put("/{follow_up_id}", response_model=FollowUpResponse)
async def update_follow_up(
    follow_up_id: str,
    follow_up_data: FollowUpUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(FollowUp).where(FollowUp.id == follow_up_id))
    follow_up = result.scalar_one_or_none()
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")

    update_data = follow_up_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field in ("type", "status") and hasattr(value, "value"):
                setattr(follow_up, field, value.value)
            else:
                setattr(follow_up, field, value)

    await db.commit()
    await db.refresh(follow_up)
    return follow_up


@router.delete("/{follow_up_id}")
async def delete_follow_up(
    follow_up_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(FollowUp).where(FollowUp.id == follow_up_id))
    follow_up = result.scalar_one_or_none()
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")

    await db.delete(follow_up)
    await db.commit()
    return {"message": "Follow-up deleted successfully"}
