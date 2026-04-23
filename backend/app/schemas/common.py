"""Common schemas used across the application."""
from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional, Any

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Standard message response."""
    success: bool = True
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    success: bool = True
    data: List[T]
    meta: dict
    
    @classmethod
    def create(cls, items: List[T], page: int, per_page: int, total: int):
        return cls(
            data=items,
            meta={
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        )


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    errors: Optional[List[dict]] = None


class ErrorResponse(BaseModel):
    """Error response."""
    success: bool = False
    message: str
    errors: Optional[List[dict]] = None
