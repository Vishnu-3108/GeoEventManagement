from fastapi import APIRouter, status, Depends, HTTPException
from app.models.event import EventCreate, EventUpdate, EventResponse
from app.schemas.event import list_serial
from app.database import events_collection
from app.auth import get_current_user
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime
from app.models.user import UserInDB

router = APIRouter()

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != "organizer":
        raise HTTPException(status_code=403, detail="Only organizers can create events.")
    
    event_dict = event.dict()
    event_dict["organizer_id"] = current_user.id
    event_dict["created_at"] = datetime.utcnow()
    event_dict["updated_at"] = datetime.utcnow()

    event_dict["location"] = {
        "type": "Point",
        "coordinates": event.location.coordinates  # [longitude, latitude]
    }

    result = await events_collection.insert_one(event_dict)
    created_event = await events_collection.find_one({"_id": result.inserted_id})

    return EventResponse(
        id=str(created_event["_id"]),
        name=created_event["name"],
        description=created_event["description"],
        category=created_event["category"],
        date=created_event["date"],
        time=created_event["time"],
        location=created_event["location"],
        capacity=created_event["capacity"],
        pricing=created_event["pricing"],
        organizer_id=str(created_event["organizer_id"]),
        created_at=created_event["created_at"],
        updated_at=created_event["updated_at"]
    )

@router.get("/", response_model=List[EventResponse])
async def get_events(
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: Optional[int] = 1000,
    current_user: UserInDB = Depends(get_current_user)
):
    query = {}
    
    if category:
        query["category"] = category
    
    if start_date and end_date:
        query["date"] = {"$gte": start_date, "$lte": end_date}
    
    if latitude and longitude:
        query["location"] = {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": radius
            }
        }

    cursor = events_collection.find(query)
    events = await cursor.to_list(length=100)

    return [
        EventResponse(
            id=str(event["_id"]),
            name=event["name"],
            description=event["description"],
            category=event["category"],
            date=event["date"],
            time=event["time"],
            location=event["location"],
            capacity=event["capacity"],
            pricing=event["pricing"],
            organizer_id=str(event["organizer_id"]),
            created_at=event["created_at"],
            updated_at=event["updated_at"]
        ) for event in events
    ]

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, event: EventUpdate, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != "organizer":
        raise HTTPException(status_code=403, detail="Only organizers can update events.")
    
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID.")
    
    existing_event = await events_collection.find_one({"_id": ObjectId(event_id)})
    if not existing_event:
        raise HTTPException(status_code=404, detail="Event not found.")
    
    if str(existing_event["organizer_id"]) != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the organizer of this event.")
    
    update_data = event.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    await events_collection.update_one({"_id": ObjectId(event_id)}, {"$set": update_data})

    updated_event = await events_collection.find_one({"_id": ObjectId(event_id)})

    return EventResponse(
        id=str(updated_event["_id"]),
        name=updated_event["name"],
        description=updated_event["description"],
        category=updated_event["category"],
        date=updated_event["date"],
        time=updated_event["time"],
        location=updated_event["location"],
        capacity=updated_event["capacity"],
        pricing=updated_event["pricing"],
        organizer_id=str(updated_event["organizer_id"]),
        created_at=updated_event["created_at"],
        updated_at=updated_event["updated_at"]
    )

@router.delete("/{event_id}")
async def delete_event(event_id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != "organizer":
        raise HTTPException(status_code=403, detail="Only organizers can delete events.")
    
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID.")
    
    event = await events_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    
    if str(event["organizer_id"]) != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the organizer of this event.")
    
    await events_collection.delete_one({"_id": ObjectId(event_id)})
    return {"detail": "Event deleted successfully."}
