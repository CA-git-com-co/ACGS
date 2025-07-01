from datetime import datetime, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import FastAPI, Depends, Query, HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy import Column, DateTime, Enum, Float, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
import enum

Base = declarative_base()

class ComplianceLevel(enum.Enum):
    COMPLIANT = "compliant"
    EXEMPLARY = "exemplary"

class ConstitutionalComplianceLog(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    improvement_id = Column(String, nullable=True)
    compliance_level = Column(Enum(ComplianceLevel), nullable=False)
    compliance_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    violations = Column(String)

app = FastAPI()

_db_session: AsyncSession | None = None

async def get_db_session_override():
    if _db_session is None:
        raise RuntimeError("DB session not set")
    yield _db_session

@app.get("/api/v1/constitutional/compliance/history")
async def get_compliance_history(
    improvement_id: str | None = Query(None),
    days: int = Query(30),
    min_score: float | None = Query(None),
    db: AsyncSession = Depends(get_db_session_override),
):
    try:
        stmt = select(ConstitutionalComplianceLog).where(
            ConstitutionalComplianceLog.created_at >= datetime.utcnow() - timedelta(days=days)
        )
        if improvement_id:
            stmt = stmt.where(ConstitutionalComplianceLog.improvement_id == improvement_id)
        if min_score is not None:
            stmt = stmt.where(ConstitutionalComplianceLog.compliance_score >= min_score)
        result = await db.execute(stmt)
        logs = result.scalars().all()
        total_validations = len(logs)
        average_score = sum(l.compliance_score for l in logs) / total_validations if total_validations else 0.0
        return {"period_days": days, "total_validations": total_validations, "average_score": average_score}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()

@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    global _db_session
    _db_session = db_session
    app.dependency_overrides[get_db_session_override] = get_db_session_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_compliance_history_returns_data(client, db_session: AsyncSession):
    improvement_id = str(uuid4())
    log = ConstitutionalComplianceLog(
        improvement_id=improvement_id,
        compliance_level=ComplianceLevel.COMPLIANT,
        compliance_score=0.9,
        created_at=datetime.utcnow(),
    )
    db_session.add(log)
    await db_session.commit()

    response = client.get("/api/v1/constitutional/compliance/history")
    assert response.status_code == 200
    data = response.json()
    assert data["total_validations"] == 1
    assert data["average_score"] == pytest.approx(0.9)
