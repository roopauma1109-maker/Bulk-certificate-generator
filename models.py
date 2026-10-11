from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(200), nullable=False)
    issuer = Column(String(200), nullable=False)
    certificate_date = Column(String(40), nullable=False)
    status = Column(String(30), nullable=False, default="processing")
    total = Column(Integer, nullable=False, default=0)
    succeeded = Column(Integer, nullable=False, default=0)
    failed = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    certificates = relationship("CertificateRecord", back_populates="job", cascade="all, delete-orphan")

class CertificateRecord(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    recipient_name = Column(String(200), nullable=False)
    recipient_email = Column(String(320), nullable=False, default="")
    status = Column(String(30), nullable=False, default="pending")
    file_path = Column(String(500), nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    job = relationship("Job", back_populates="certificates")
