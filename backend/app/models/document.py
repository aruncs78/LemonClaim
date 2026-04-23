"""Document database model."""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Integer, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid
import enum


class DocumentType(str, enum.Enum):
    ID_PROOF = "id_proof"
    ADDRESS_PROOF = "address_proof"
    CLAIM_PHOTO = "claim_photo"
    CLAIM_VIDEO = "claim_video"
    POLICE_REPORT = "police_report"
    MEDICAL_REPORT = "medical_report"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    OTHER = "other"


class Document(Base):
    """Document model for storing uploaded files."""
    
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=True, index=True)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    file_name = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    blob_url = Column(String(500), nullable=True)
    local_path = Column(String(500), nullable=True)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    ocr_data = Column(JSON, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    claim = relationship("Claim", back_populates="documents")
    
    def to_dict(self):
        """Convert document to dictionary."""
        return {
            "id": self.id,
            "document_type": self.document_type.value,
            "file_name": self.file_name,
            "original_name": self.original_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "is_verified": self.is_verified,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
