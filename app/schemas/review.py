from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ReviewBase(BaseModel):
    event_id: str
    rating: int
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: str
    attendee_id: str
    created_at: datetime
def list_serial(items: List[BaseModel]) -> List[dict]:
    return [item.dict() for item in items]