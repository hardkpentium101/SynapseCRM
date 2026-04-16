import asyncio
import sys

sys.path.insert(0, ".")

from src.db.database import init_db, async_session_maker
from src.db.models import User, HCP, Material
from src.api.deps import get_password_hash
import uuid


async def seed_database():
    await init_db()

    async with async_session_maker() as session:
        # Check if data already exists
        from sqlalchemy import select

        result = await session.execute(select(User))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping...")
            return

        # Create demo users
        users = [
            User(
                id="rep_001",
                email="rep@pharma.com",
                password_hash=get_password_hash("rep123"),
                name="John Smith",
                role="rep",
                territory="North India",
            ),
            User(
                id="mgr_001",
                email="manager@pharma.com",
                password_hash=get_password_hash("mgr123"),
                name="Sarah Johnson",
                role="manager",
                territory="North India",
            ),
            User(
                id="admin_001",
                email="admin@pharma.com",
                password_hash=get_password_hash("admin123"),
                name="Mike Davis",
                role="admin",
                territory="All India",
            ),
        ]

        for user in users:
            session.add(user)

        # Create demo HCPs
        hcps = [
            HCP(
                id=str(uuid.uuid4()),
                name="Dr. Priya Sharma",
                specialty="Oncology",
                institution="Tata Memorial Hospital, Mumbai",
                email="priya.sharma@tata.org",
                phone="+91 98765 43210",
                notes="Leading oncologist specializing in breast cancer research",
            ),
            HCP(
                id=str(uuid.uuid4()),
                name="Dr. Rajesh Kumar",
                specialty="Cardiology",
                institution="AIIMS Delhi",
                email="rajesh.kumar@aiims.ac.in",
                phone="+91 98765 43211",
                notes="Interventional cardiologist with expertise in complex angioplasties",
            ),
            HCP(
                id=str(uuid.uuid4()),
                name="Dr. Ananya Patel",
                specialty="Neurology",
                institution="NIMHANS Bangalore",
                email="ananya.patel@nimhans.edu.in",
                phone="+91 98765 43212",
                notes="Epilepsy specialist, research focus on pediatric neurology",
            ),
            HCP(
                id=str(uuid.uuid4()),
                name="Dr. Vikram Singh",
                specialty="Pulmonology",
                institution="Apollo Hospitals, Chennai",
                email="vikram.singh@apollo.in",
                phone="+91 98765 43213",
                notes="Expert in respiratory diseases and lung transplantation",
            ),
            HCP(
                id=str(uuid.uuid4()),
                name="Dr. Meera Joshi",
                specialty="Endocrinology",
                institution="Medanta Gurgaon",
                email="meera.joshi@medanta.in",
                phone="+91 98765 43214",
                notes="Diabetes and thyroid disorders specialist",
            ),
        ]

        for hcp in hcps:
            session.add(hcp)

        # Create demo materials
        materials = [
            Material(
                id=str(uuid.uuid4()),
                name="OncoBoost Phase III Brochure",
                type="pdf",
                description="Clinical trial data and efficacy information for OncoBoost",
            ),
            Material(
                id=str(uuid.uuid4()),
                name="CardioProtect Product Sheet",
                type="pdf",
                description="Overview of CardioProtect formulation and benefits",
            ),
            Material(
                id=str(uuid.uuid4()),
                name="NeuroPlus Clinical Summary",
                type="pdf",
                description="Clinical study results for NeuroPlus in epilepsy treatment",
            ),
            Material(
                id=str(uuid.uuid4()),
                name="Sample Kit - OncoBoost",
                type="physical",
                description="30-unit sample kit for OncoBoost 50mg tablets",
            ),
            Material(
                id=str(uuid.uuid4()),
                name="Sample Kit - CardioProtect",
                type="physical",
                description="30-unit sample kit for CardioProtect 25mg capsules",
            ),
        ]

        for material in materials:
            session.add(material)

        await session.commit()
        print("Database seeded successfully!")
        print("\nDemo accounts:")
        print("  rep@pharma.com / rep123 (Field Rep)")
        print("  manager@pharma.com / mgr123 (Manager)")
        print("  admin@pharma.com / admin123 (Admin)")


if __name__ == "__main__":
    asyncio.run(seed_database())
