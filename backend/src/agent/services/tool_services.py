"""
Tool Services - Direct database operations for agent tools (no HTTP calls)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload
import logging

logger = logging.getLogger(__name__)

try:
    from src.db.models import HCP, Interaction, FollowUp, User, Material
    from src.db.database import async_session_maker
    from src.agent.services.async_runner import run_async

    DB_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Database not available: {e}")
    DB_AVAILABLE = False


class HCPService:
    # Exposed fields - only fields user can query/see
    EXPOSED_FIELDS = ["id", "name", "specialty", "institution"]
    # DB fields - additional fields for validation
    DB_FIELDS = ["id", "name", "specialty", "institution", "email", "phone", "notes"]

    @staticmethod
    def search_hcp(query: str, limit: int = 5, user_id: str = None) -> List[Dict]:
        if not DB_AVAILABLE:
            return [{"error": "Database not available"}]

        async def _search():
            try:
                async with async_session_maker() as session:
                    query_lower = query.lower()

                    stmt = select(HCP).where(
                        or_(
                            HCP.name.ilike(f"%{query}%"),
                            HCP.name.ilike(f"%{query_lower}%"),
                            HCP.specialty.ilike(f"%{query}%"),
                            HCP.institution.ilike(f"%{query}%"),
                            HCP.name.ilike(f"%{query_lower}%"),
                            HCP.name.ilike(f"{query_lower}%"),
                        )
                    )
                    if user_id:
                        stmt = stmt.where(HCP.created_by == user_id)
                    stmt = stmt.limit(limit)
                    result = await session.execute(stmt)
                    hcps = result.scalars().all()
                    return [
                        {
                            "id": str(hcp.id),
                            "name": hcp.name,
                            "specialty": hcp.specialty,
                            "institution": hcp.institution,
                            "email": hcp.email,
                            "phone": hcp.phone,
                        }
                        for hcp in hcps
                    ]
            except Exception as e:
                logger.error(f"DB search error: {e}")
                raise

        return run_async(_search())

    @staticmethod
    def search_hcp_exposed(
        query: str, limit: int = 5, user_id: str = None
    ) -> List[Dict]:
        """Search HCPs - returns only exposed fields for user queries"""
        if not DB_AVAILABLE:
            return [{"error": "Database not available"}]

        async def _search():
            try:
                async with async_session_maker() as session:
                    search_term = f"%{query}%"
                    query_lower = query.lower()

                    stmt = select(HCP).where(
                        or_(
                            HCP.name.ilike(search_term),
                            HCP.name.ilike(f"%{query_lower}%"),
                            HCP.specialty.ilike(search_term),
                            HCP.institution.ilike(search_term),
                        )
                    )
                    if user_id:
                        stmt = stmt.where(HCP.created_by == user_id)
                    stmt = stmt.limit(limit)
                    result = await session.execute(stmt)
                    hcps = result.scalars().all()
                    # Only return exposed fields
                    return [
                        {
                            "id": str(hcp.id),
                            "name": hcp.name,
                            "specialty": hcp.specialty,
                            "institution": hcp.institution,
                        }
                        for hcp in hcps
                    ]
            except Exception as e:
                logger.error(f"DB exposed search error: {e}")
                raise

        return run_async(_search())

    @staticmethod
    def get_hcp_for_validation(hcp_id: str) -> Optional[Dict]:
        """Get HCP with all fields for entity validation"""
        if not DB_AVAILABLE:
            return {"error": "Database not available"}

        async def _get():
            try:
                async with async_session_maker() as session:
                    stmt = select(HCP).where(HCP.id == hcp_id)
                    result = await session.execute(stmt)
                    hcp = result.scalar_one_or_none()
                    if not hcp:
                        return None
                    return {
                        "id": str(hcp.id),
                        "name": hcp.name,
                        "specialty": hcp.specialty,
                        "institution": hcp.institution,
                        "email": hcp.email,
                        "phone": hcp.phone,
                        "notes": hcp.notes,
                    }
            except Exception as e:
                logger.error(f"DB get error: {e}")
                raise

        return run_async(_get())

    @staticmethod
    def get_hcp_by_id(hcp_id: str) -> Optional[Dict]:
        if not DB_AVAILABLE:
            return {"error": "Database not available"}

        async def _get():
            try:
                async with async_session_maker() as session:
                    stmt = select(HCP).where(HCP.id == hcp_id)
                    result = await session.execute(stmt)
                    hcp = result.scalar_one_or_none()
                    if not hcp:
                        return None
                    return {
                        "id": str(hcp.id),
                        "name": hcp.name,
                        "specialty": hcp.specialty,
                        "institution": hcp.institution,
                        "email": hcp.email,
                        "phone": hcp.phone,
                        "notes": hcp.notes,
                    }
            except Exception as e:
                logger.error(f"DB get error: {e}")
                raise

        return run_async(_get())

    @staticmethod
    def create_hcp(
        name: str,
        specialty: str = None,
        institution: str = None,
        email: str = None,
        phone: str = None,
        user_id: str = None,
    ) -> Dict:
        if not DB_AVAILABLE:
            return {"error": "Database not available", "created": False}

        async def _create():
            try:
                async with async_session_maker() as session:
                    hcp = HCP(
                        name=name,
                        specialty=specialty,
                        institution=institution,
                        email=email,
                        phone=phone,
                        created_by=user_id,
                    )
                    session.add(hcp)
                    await session.commit()
                    await session.refresh(hcp)
                    return {
                        "id": str(hcp.id),
                        "name": hcp.name,
                        "specialty": hcp.specialty,
                        "institution": hcp.institution,
                    }
            except Exception as e:
                logger.error(f"DB create error: {e}")
                raise

        return run_async(_create())

    @staticmethod
    def get_hcp_history(hcp_id: str, limit: int = 10) -> List[Dict]:
        if not DB_AVAILABLE:
            return []

        async def _get_history():
            try:
                async with async_session_maker() as session:
                    stmt = (
                        select(Interaction)
                        .where(Interaction.hcp_id == hcp_id)
                        .order_by(Interaction.date_time.desc())
                        .limit(limit)
                    )
                    result = await session.execute(stmt)
                    interactions = result.scalars().all()
                    return [
                        {
                            "id": str(i.id),
                            "type": i.type,
                            "date_time": i.date_time.isoformat()
                            if i.date_time
                            else None,
                            "topics": i.topics,
                            "sentiment": i.sentiment,
                            "outcome": i.outcome,
                        }
                        for i in interactions
                    ]
            except Exception as e:
                logger.error(f"DB history error: {e}")
                raise

        return run_async(_get_history())


class InteractionService:
    @staticmethod
    def create_interaction(
        hcp_id: str,
        type: str,
        date_time: str,
        user_id: str,
        topics: List[str] = None,
        sentiment: str = None,
        outcome: str = None,
        attendees: List[str] = None,
        notes: str = None,
    ) -> Dict:
        if not DB_AVAILABLE:
            return {"error": "Database not available", "created": False}

        async def _create():
            try:
                async with async_session_maker() as session:
                    parsed_date = None
                    try:
                        parsed_date = datetime.fromisoformat(
                            date_time.replace("Z", "+00:00")
                        )
                    except:
                        parsed_date = datetime.utcnow()

                    interaction = Interaction(
                        hcp_id=hcp_id,
                        user_id=user_id,
                        type=type,
                        date_time=parsed_date,
                        topics=",".join(topics) if topics else None,
                        sentiment=sentiment,
                        outcome=outcome,
                        attendees=attendees or [],
                    )
                    session.add(interaction)
                    await session.commit()
                    await session.refresh(interaction)
                    return {
                        "id": str(interaction.id),
                        "hcpId": str(interaction.hcp_id),
                        "type": interaction.type,
                        "dateTime": interaction.date_time.isoformat()
                        if interaction.date_time
                        else None,
                        "topics": interaction.topics,
                        "sentiment": interaction.sentiment,
                        "outcome": interaction.outcome,
                        "attendees": interaction.attendees,
                        "notes": None,
                    }
            except Exception as e:
                logger.error(f"DB create interaction error: {e}")
                raise

        return run_async(_create())

    @staticmethod
    def get_interactions(
        hcp_id: str = None, user_id: str = None, limit: int = 20
    ) -> List[Dict]:
        if not DB_AVAILABLE:
            return []

        async def _get():
            try:
                async with async_session_maker() as session:
                    stmt = select(Interaction).order_by(Interaction.date_time.desc())
                    if hcp_id:
                        stmt = stmt.where(Interaction.hcp_id == hcp_id)
                    if user_id:
                        stmt = stmt.where(Interaction.user_id == user_id)
                    stmt = stmt.limit(limit)
                    result = await session.execute(stmt)
                    interactions = result.scalars().all()
                    return [
                        {
                            "id": str(i.id),
                            "hcp_id": str(i.hcp_id),
                            "type": i.type,
                            "date_time": i.date_time.isoformat()
                            if i.date_time
                            else None,
                            "sentiment": i.sentiment,
                        }
                        for i in interactions
                    ]
            except Exception as e:
                logger.error(f"DB get interactions error: {e}")
                raise

        return run_async(_get())

    @staticmethod
    def get_interaction_summary(interaction_id: str) -> Optional[Dict]:
        if not DB_AVAILABLE:
            return {"error": "Database not available"}

        async def _get():
            try:
                async with async_session_maker() as session:
                    stmt = (
                        select(Interaction)
                        .options(selectinload(Interaction.hcp))
                        .where(Interaction.id == interaction_id)
                    )
                    result = await session.execute(stmt)
                    interaction = result.scalar_one_or_none()
                    if not interaction:
                        return None
                    return {
                        "id": str(interaction.id),
                        "hcp": {
                            "id": str(interaction.hcp.id),
                            "name": interaction.hcp.name,
                        }
                        if interaction.hcp
                        else None,
                        "type": interaction.type,
                        "date_time": interaction.date_time.isoformat()
                        if interaction.date_time
                        else None,
                        "topics": interaction.topics,
                    }
            except Exception as e:
                logger.error(f"DB get interaction summary error: {e}")
                raise

        return run_async(_get())


class FollowUpService:
    @staticmethod
    def create_follow_up(
        description: str,
        interaction_id: str = None,
        hcp_id: str = None,
        type: str = None,
        due_date: str = None,
        user_id: str = None,
    ) -> Dict:
        if not DB_AVAILABLE:
            return {"error": "Database not available", "created": False}

        async def _create():
            try:
                async with async_session_maker() as session:
                    parsed_due_date = None
                    if due_date:
                        try:
                            parsed_due_date = datetime.fromisoformat(
                                due_date.replace("Z", "+00:00")
                            )
                        except:
                            pass

                    follow_up = FollowUp(
                        interaction_id=interaction_id,
                        type=type or "follow_up_meeting",
                        description=description,
                        due_date=parsed_due_date,
                        created_by=user_id,
                        ai_generated=True,
                    )
                    session.add(follow_up)
                    await session.commit()
                    await session.refresh(follow_up)
                    return {
                        "id": str(follow_up.id),
                        "description": follow_up.description,
                        "type": follow_up.type,
                        "status": follow_up.status,
                    }
            except Exception as e:
                logger.error(f"DB create follow-up error: {e}")
                raise

        return run_async(_create())

    @staticmethod
    def get_follow_ups(
        interaction_id: str = None,
        hcp_id: str = None,
        status: str = None,
        limit: int = 20,
    ) -> List[Dict]:
        if not DB_AVAILABLE:
            return []

        async def _get():
            try:
                async with async_session_maker() as session:
                    stmt = select(FollowUp).order_by(FollowUp.due_date.asc())
                    if interaction_id:
                        stmt = stmt.where(FollowUp.interaction_id == interaction_id)
                    if status:
                        stmt = stmt.where(FollowUp.status == status)
                    stmt = stmt.limit(limit)
                    result = await session.execute(stmt)
                    follow_ups = result.scalars().all()
                    return [
                        {
                            "id": str(fu.id),
                            "interaction_id": str(fu.interaction_id)
                            if fu.interaction_id
                            else None,
                            "type": fu.type,
                            "description": fu.description,
                            "status": fu.status,
                            "due_date": fu.due_date.isoformat()
                            if fu.due_date
                            else None,
                        }
                        for fu in follow_ups
                    ]
            except Exception as e:
                logger.error(f"DB get follow-ups error: {e}")
                raise

        return run_async(_get())

    @staticmethod
    def update_follow_up(
        follow_up_id: str, status: str, notes: str = None
    ) -> Optional[Dict]:
        if not DB_AVAILABLE:
            return {"error": "Database not available", "updated": False}

        async def _update():
            try:
                async with async_session_maker() as session:
                    stmt = select(FollowUp).where(FollowUp.id == follow_up_id)
                    result = await session.execute(stmt)
                    follow_up = result.scalar_one_or_none()
                    if not follow_up:
                        return None
                    follow_up.status = status
                    await session.commit()
                    await session.refresh(follow_up)
                    return {
                        "id": str(follow_up.id),
                        "status": follow_up.status,
                        "updated": True,
                    }
            except Exception as e:
                logger.error(f"DB update follow-up error: {e}")
                raise

        return run_async(_update())


class MaterialService:
    @staticmethod
    def search_material(query: str, limit: int = 5) -> List[Dict]:
        if not DB_AVAILABLE:
            return [{"error": "Database not available"}]

        async def _search():
            try:
                async with async_session_maker() as session:
                    search_term = f"%{query}%"
                    query_lower = query.lower()

                    stmt = select(Material).where(
                        or_(
                            Material.name.ilike(search_term),
                            Material.name.ilike(f"%{query_lower}%"),
                        )
                    )
                    stmt = stmt.limit(limit)
                    result = await session.execute(stmt)
                    materials = result.scalars().all()
                    return [
                        {
                            "id": str(m.id),
                            "name": m.name,
                            "type": m.type,
                            "description": m.description,
                        }
                        for m in materials
                    ]
            except Exception as e:
                logger.error(f"DB material search error: {e}")
                raise

        return run_async(_search())

    @staticmethod
    def get_material_by_id(material_id: str) -> Optional[Dict]:
        if not DB_AVAILABLE:
            return {"error": "Database not available"}

        async def _get():
            try:
                async with async_session_maker() as session:
                    stmt = select(Material).where(Material.id == material_id)
                    result = await session.execute(stmt)
                    material = result.scalar_one_or_none()
                    if not material:
                        return None
                    return {
                        "id": str(material.id),
                        "name": material.name,
                        "type": material.type,
                        "description": material.description,
                        "file_url": material.file_url,
                    }
            except Exception as e:
                logger.error(f"DB get material error: {e}")
                raise

        return run_async(_get())
