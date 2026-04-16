from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional

from src.db.database import get_db
from src.db.models import Material, User
from src.db.schemas import MaterialCreate, MaterialResponse
from src.api.deps import get_current_user
import uuid

router = APIRouter(prefix="/materials", tags=["materials"])


@router.get("", response_model=List[MaterialResponse])
async def get_materials(
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Material)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Material.name.ilike(search_term),
                Material.description.ilike(search_term),
            )
        )

    query = query.offset(skip).limit(limit).order_by(Material.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.post("", response_model=MaterialResponse)
async def create_material(
    material_data: MaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    material = Material(
        id=str(uuid.uuid4()),
        name=material_data.name,
        type=material_data.type.value,
        description=material_data.description,
        file_url=material_data.file_url,
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return material
