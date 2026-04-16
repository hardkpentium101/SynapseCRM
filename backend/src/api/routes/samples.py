from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from src.db.database import get_db
from src.db.models import Sample, User
from src.db.schemas import SampleCreate, SampleResponse
from src.api.deps import get_current_user
import uuid

router = APIRouter(prefix="/samples", tags=["samples"])


@router.get("", response_model=List[SampleResponse])
async def get_samples(
    interaction_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Sample)

    if interaction_id:
        query = query.where(Sample.interaction_id == interaction_id)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=SampleResponse)
async def create_sample(
    sample_data: SampleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sample = Sample(
        id=str(uuid.uuid4()),
        interaction_id=sample_data.interaction_id,
        product_name=sample_data.product_name,
        lot_number=sample_data.lot_number,
        quantity=sample_data.quantity,
    )
    db.add(sample)
    await db.commit()
    await db.refresh(sample)
    return sample


@router.delete("/{sample_id}")
async def delete_sample(
    sample_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Sample).where(Sample.id == sample_id))
    sample = result.scalar_one_or_none()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    await db.delete(sample)
    await db.commit()
    return {"message": "Sample deleted successfully"}
