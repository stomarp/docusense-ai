from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func

from .database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False, unique=True, index=True)
    file_type = Column(String, nullable=False)  # pdf/docx/txt
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    risk_score = Column(Integer, nullable=False)
    missing_sections = Column(JSON, nullable=False)
    risky_phrases = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())