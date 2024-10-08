from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BookingBase(BaseModel):
    event_id: str
    tickets: int = Field(..., gt=0)
    payment_status: str = "pending"  # or "paid", "refunded"

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: str
    attendee_id: str
    booking_date: datetime
    status: str  # "confirmed", "pending", "canceled"
    total_amount: float


def list_serial(items: List[BaseModel]) -> List[dict]:
    return [item.dict() for item in items]