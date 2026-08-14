"""
Development seed data script.

Creates sample users and complaints to demonstrate the system.
Run with: python -m scripts.seed (from backend/ directory)

⚠️  DEVELOPMENT ONLY — never use these credentials in production.

Default credentials:
  admin@example.com    / admin123
  agent@example.com    / agent123
  customer@example.com / customer123
"""

import sys
import os
from datetime import datetime, timezone, timedelta

# Add the backend directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.db.models.user import User, UserRole
from app.db.models.complaint import Complaint, ComplaintStatus, ComplaintPriority
from app.db.models.complaint_history import ComplaintStatusHistory


def seed():
    """Populate the database with development sample data."""
    db = SessionLocal()

    try:
        # Check if data already exists
        existing = db.query(User).first()
        if existing:
            print("⚠️  Database already has data. Skipping seed.")
            print("   To re-seed, drop and recreate the database first.")
            return

        print("🌱 Seeding database with development data...")

        # ── Create Users ─────────────────────────────────────────
        admin = User(
            name="Admin User",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            role=UserRole.ADMIN,
        )
        agent1 = User(
            name="Agent Smith",
            email="agent@example.com",
            hashed_password=hash_password("agent123"),
            role=UserRole.AGENT,
        )
        agent2 = User(
            name="Agent Johnson",
            email="agent2@example.com",
            hashed_password=hash_password("agent123"),
            role=UserRole.AGENT,
        )
        customer1 = User(
            name="John Customer",
            email="customer@example.com",
            hashed_password=hash_password("customer123"),
            role=UserRole.CUSTOMER,
        )
        customer2 = User(
            name="Jane Doe",
            email="jane@example.com",
            hashed_password=hash_password("customer123"),
            role=UserRole.CUSTOMER,
        )

        db.add_all([admin, agent1, agent2, customer1, customer2])
        db.flush()

        print(f"  ✓ Created {5} users")

        # ── Create Complaints (various statuses) ─────────────────
        now = datetime.now(timezone.utc)

        # Complaint 1: SUBMITTED (unassigned)
        c1 = Complaint(
            customer_id=customer1.id,
            title="Generator not starting after delivery",
            description="Purchased a 20KVA generator last week. It was delivered on Monday but has not started since. The pull cord seems stuck and the fuel gauge reads empty even though the tank was filled.",
            status=ComplaintStatus.SUBMITTED,
            priority=ComplaintPriority.HIGH,
        )
        db.add(c1)
        db.flush()
        db.add(ComplaintStatusHistory(
            complaint_id=c1.id, old_status=None,
            new_status="SUBMITTED", changed_by=customer1.id,
            comment="Complaint submitted",
        ))

        # Complaint 2: ASSIGNED
        c2 = Complaint(
            customer_id=customer1.id,
            assigned_agent_id=agent1.id,
            title="Frequent power fluctuations from inverter",
            description="The 5KVA inverter system installed two months ago is causing frequent power fluctuations. Lights flicker and sensitive electronics have been damaged.",
            status=ComplaintStatus.ASSIGNED,
            priority=ComplaintPriority.CRITICAL,
        )
        db.add(c2)
        db.flush()
        db.add(ComplaintStatusHistory(
            complaint_id=c2.id, old_status=None,
            new_status="SUBMITTED", changed_by=customer1.id,
            comment="Complaint submitted",
        ))
        db.add(ComplaintStatusHistory(
            complaint_id=c2.id, old_status="SUBMITTED",
            new_status="ASSIGNED", changed_by=admin.id,
            comment="Assigned to Agent Smith",
        ))

        # Complaint 3: IN_PROGRESS
        c3 = Complaint(
            customer_id=customer2.id,
            assigned_agent_id=agent1.id,
            title="Billing discrepancy on maintenance contract",
            description="I was charged twice for the quarterly maintenance visit in June. The contract states NGN 45,000 per visit but I was billed NGN 90,000.",
            status=ComplaintStatus.IN_PROGRESS,
            priority=ComplaintPriority.MEDIUM,
        )
        db.add(c3)
        db.flush()
        db.add(ComplaintStatusHistory(
            complaint_id=c3.id, old_status=None,
            new_status="SUBMITTED", changed_by=customer2.id,
            comment="Complaint submitted",
        ))
        db.add(ComplaintStatusHistory(
            complaint_id=c3.id, old_status="SUBMITTED",
            new_status="ASSIGNED", changed_by=admin.id,
            comment="Assigned to Agent Smith for billing review",
        ))
        db.add(ComplaintStatusHistory(
            complaint_id=c3.id, old_status="ASSIGNED",
            new_status="IN_PROGRESS", changed_by=agent1.id,
            comment="Reviewing billing records with finance team",
        ))

        # Complaint 4: RESOLVED
        c4 = Complaint(
            customer_id=customer2.id,
            assigned_agent_id=agent2.id,
            title="Noise complaint — generator too loud",
            description="The 15KVA generator installed at our office produces excessive noise. Neighbors have complained and the noise exceeds acceptable levels during business hours.",
            status=ComplaintStatus.RESOLVED,
            priority=ComplaintPriority.LOW,
            resolved_at=now - timedelta(hours=6),
        )
        db.add(c4)
        db.flush()
        db.add(ComplaintStatusHistory(
            complaint_id=c4.id, old_status=None,
            new_status="SUBMITTED", changed_by=customer2.id,
            comment="Complaint submitted",
        ))
        db.add(ComplaintStatusHistory(
            complaint_id=c4.id, old_status="SUBMITTED",
            new_status="ASSIGNED", changed_by=admin.id,
            comment="Assigned to Agent Johnson",
        ))
        db.add(ComplaintStatusHistory(
            complaint_id=c4.id, old_status="ASSIGNED",
            new_status="IN_PROGRESS", changed_by=agent2.id,
            comment="Scheduling noise assessment visit",
        ))
        db.add(ComplaintStatusHistory(
            complaint_id=c4.id, old_status="IN_PROGRESS",
            new_status="RESOLVED", changed_by=agent2.id,
            comment="Installed acoustic enclosure. Noise levels now within acceptable range.",
        ))

        # Complaint 5: SUBMITTED (unassigned, from customer2)
        c5 = Complaint(
            customer_id=customer1.id,
            title="Request for warranty extension",
            description="I would like to request an extension of the warranty on my 10KVA generator. The current warranty expires next month and I want to ensure continued coverage.",
            status=ComplaintStatus.SUBMITTED,
            priority=ComplaintPriority.LOW,
        )
        db.add(c5)
        db.flush()
        db.add(ComplaintStatusHistory(
            complaint_id=c5.id, old_status=None,
            new_status="SUBMITTED", changed_by=customer1.id,
            comment="Complaint submitted",
        ))

        db.commit()

        # ── Ingest knowledge base into RAG vector store ──────────
        try:
            from app.ai.ingest import ingest_knowledge_base, ingest_resolved_complaint

            print("\n🤖 Indexing RAG knowledge base...")
            kb_result = ingest_knowledge_base()
            print(f"  ✓ Indexed {kb_result.get('chunks_ingested', 0)} chunks from {kb_result.get('source_files', 0)} documents")

            # Ingest the resolved complaint (c4) into the vector store
            print("  Ingesting resolved complaints...")
            ingest_resolved_complaint(
                complaint_id=str(c4.id),
                title=c4.title,
                description=c4.description,
                resolution_comments=[
                    "Scheduling noise assessment visit",
                    "Installed acoustic enclosure. Noise levels now within acceptable range.",
                ],
            )
            print("  ✓ Ingested 1 resolved complaint")

        except ImportError:
            print("\n⚠️  AI dependencies not installed — skipping RAG indexing.")
            print("   To enable RAG: pip install chromadb sentence-transformers")
        except Exception as e:
            print(f"\n⚠️  RAG indexing failed (non-critical): {e}")


        print(f"  ✓ Created {5} complaints with status history")

        print("\n✅ Seed data created successfully!")
        print("\n📋 Login credentials:")
        print("   Admin:    admin@example.com    / admin123")
        print("   Agent:    agent@example.com    / agent123")
        print("   Agent 2:  agent2@example.com   / agent123")
        print("   Customer: customer@example.com / customer123")
        print("   Customer: jane@example.com     / customer123")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
