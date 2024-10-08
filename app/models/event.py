from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal, List
from datetime import datetime

class Location(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float]  # [longitude, latitude]


class Pricing(BaseModel):
    standard: Optional[float] = None
    vip: Optional[float] = None



class EventBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str
    category: str
    date: datetime
    time: str  # Could be datetime as well
    location: Location # {"type": "Point", "coordinates": [longitude, latitude]}
    capacity: int
    pricing:Pricing # e.g., {"standard": 100.0, "vip": 250.0}

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    date: Optional[datetime] = None
    time: Optional[str] = None
    location: Optional[Location] = None
    capacity: Optional[int] = None
    pricing: Optional[Pricing] = None

class EventResponse(EventBase):
    id: str
    organizer_id: str
    created_at: datetime
    updated_at: datetime
