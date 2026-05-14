from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from src.db.database import get_db
from src.db.models import Interaction, User, HCP, Material, Sample, InteractionMaterial
from src.db.schemas import (
    InteractionCreate,
    InteractionUpdate,
    InteractionDetailResponse,
    InteractionListResponse,
)
from src.api.deps import get_current_user
import uuid

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.get("", response_model=List[InteractionListResponse])
async def get_interactions(
    hcp_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Interaction).options(selectinload(Interaction.hcp))

    if hcp_id:
        query = query.where(Interaction.hcp_id == hcp_id)
    if user_id:
        query = query.where(Interaction.user_id == user_id)

    query = query.offset(skip).limit(limit).order_by(Interaction.date_time.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{interaction_id}", response_model=InteractionDetailResponse)
async def get_interaction(
    interaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Interaction)
        .options(
            selectinload(Interaction.hcp),
            selectinload(Interaction.materials).selectinload(
                InteractionMaterial.material
            ),
            selectinload(Interaction.samples),
            selectinload(Interaction.follow_ups),
        )
        .where(Interaction.id == interaction_id)
    )
    interaction = result.scalar_one_or_none()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.post("", response_model=InteractionDetailResponse)
async def create_interaction(
    interaction_data: InteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    hcp_result = await db.execute(select(HCP).where(HCP.id == interaction_data.hcp_id))
    if not hcp_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="HCP not found")

    interaction = Interaction(
        id=str(uuid.uuid4()),
        hcp_id=interaction_data.hcp_id,
        user_id=current_user.id,
        type=interaction_data.type.value,
        date_time=interaction_data.date_time,
        attendees=interaction_data.attendees,
        topics=interaction_data.topics,
        sentiment=interaction_data.sentiment.value
        if interaction_data.sentiment
        else None,
        outcome=interaction_data.outcome,
        voice_note_url=interaction_data.voice_note_url,
    )
    db.add(interaction)
    await db.flush()

    for material_id in interaction_data.material_ids:
        im = InteractionMaterial(interaction_id=interaction.id, material_id=material_id)
        db.add(im)

    for sample_data in interaction_data.samples:
        sample = Sample(
            id=str(uuid.uuid4()),
            interaction_id=interaction.id,
            product_name=sample_data.product_name,
            lot_number=sample_data.lot_number,
            quantity=sample_data.quantity,
        )
        db.add(sample)

    await db.commit()

    result = await db.execute(
        select(Interaction)
        .options(
            selectinload(Interaction.hcp),
            selectinload(Interaction.materials).selectinload(
                InteractionMaterial.material
            ),
            selectinload(Interaction.samples),
            selectinload(Interaction.follow_ups),
        )
        .where(Interaction.id == interaction.id)
    )
    return result.scalar_one()


@router.put("/{interaction_id}", response_model=InteractionDetailResponse)
async def update_interaction(
    interaction_id: str,
    interaction_data: InteractionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Interaction).where(Interaction.id == interaction_id)
    )
    interaction = result.scalar_one_or_none()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    update_data = interaction_data.model_dump(
        exclude_unset=True, exclude={"material_ids", "samples"}
    )

    for field, value in update_data.items():
        if value is not None:
            if field == "type":
                setattr(interaction, field, value.value)
            elif field == "sentiment" and value:
                setattr(
                    interaction,
                    field,
                    value.value if hasattr(value, "value") else value,
                )
            else:
                setattr(interaction, field, value)

    if interaction_data.material_ids is not None:
        await db.execute(
            InteractionMaterial.__table__.delete().where(
                InteractionMaterial.interaction_id == interaction_id
            )
        )
        for material_id in interaction_data.material_ids:
            im = InteractionMaterial(
                interaction_id=interaction.id, material_id=material_id
            )
            db.add(im)

    if interaction_data.samples is not None:
        await db.execute(
            Sample.__table__.delete().where(Sample.interaction_id == interaction_id)
        )
        for sample_data in interaction_data.samples:
            sample = Sample(
                id=str(uuid.uuid4()),
                interaction_id=interaction.id,
                product_name=sample_data.product_name,
                lot_number=sample_data.lot_number,
                quantity=sample_data.quantity,
            )
            db.add(sample)

    await db.commit()

    result = await db.execute(
        select(Interaction)
        .options(
            selectinload(Interaction.hcp),
            selectinload(Interaction.materials).selectinload(
                InteractionMaterial.material
            ),
            selectinload(Interaction.samples),
            selectinload(Interaction.follow_ups),
        )
        .where(Interaction.id == interaction_id)
    )
    return result.scalar_one()


@router.delete("/{interaction_id}")
async def delete_interaction(
    interaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Interaction).where(Interaction.id == interaction_id)
    )
    interaction = result.scalar_one_or_none()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    await db.delete(interaction)
    await db.commit()
    return {"message": "Interaction deleted successfully"}
