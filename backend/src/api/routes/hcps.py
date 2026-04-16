from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional

from src.db.database import get_db
from src.db.models import HCP, User
from src.db.schemas import HCPCreate, HCPUpdate, HCPSimpleResponse, HCPDetailResponse
from src.api.deps import get_current_user
import uuid

router = APIRouter(prefix="/hcps", tags=["hcps"])


@router.get("", response_model=List[HCPSimpleResponse])
async def get_hcps(
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(HCP)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                HCP.name.ilike(search_term),
                HCP.specialty.ilike(search_term),
                HCP.institution.ilike(search_term),
            )
        )

    query = query.offset(skip).limit(limit).order_by(HCP.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{hcp_id}", response_model=HCPDetailResponse)
async def get_hcp(
    hcp_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(HCP).where(HCP.id == hcp_id))
    hcp = result.scalar_one_or_none()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    return hcp


@router.post("", response_model=HCPSimpleResponse)
async def create_hcp(
    hcp_data: HCPCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    hcp = HCP(
        id=str(uuid.uuid4()),
        name=hcp_data.name,
        specialty=hcp_data.specialty,
        institution=hcp_data.institution,
        email=hcp_data.email,
        phone=hcp_data.phone,
        notes=hcp_data.notes,
        created_by=current_user.id,
    )
    db.add(hcp)
    await db.commit()
    await db.refresh(hcp)
    return hcp


@router.put("/{hcp_id}", response_model=HCPSimpleResponse)
async def update_hcp(
    hcp_id: str,
    hcp_data: HCPUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(HCP).where(HCP.id == hcp_id))
    hcp = result.scalar_one_or_none()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    update_data = hcp_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hcp, field, value)

    await db.commit()
    await db.refresh(hcp)
    return hcp


@router.delete("/{hcp_id}")
async def delete_hcp(
    hcp_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(HCP).where(HCP.id == hcp_id))
    hcp = result.scalar_one_or_none()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    await db.delete(hcp)
    await db.commit()
    return {"message": "HCP deleted successfully"}
