from fastapi import APIRouter, HTTPException, status, Depends
from app.models.review import ReviewCreate, ReviewResponse
from app.schemas.review import list_serial
from app.database import reviews_collection, events_collection, bookings_collection
from app.auth import get_current_user
from bson.objectid import ObjectId
from typing import List
from datetime import datetime
from app.models.user import UserInDB

router = APIRouter()

@router.post("/", response_model= ReviewCreate, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role !="attendee":
        raise HTTPException (status_code=403, detail="Only attendees can leave a review")
    if not ObjectId.is_valid(review.event_id):
        raise HTTPException (status_code=400, detail="Invalid event ID")
    event = await events_collection.find_one({"_id":ObjectId(review.event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # check if user attended the event
    booking = await bookings_collection.find_one({"event_id": review.event_id, "attendee_id": ObjectId(current_user.id)})
    if not booking:
        raise HTTPException (status_code=403, detail="You have not attended the event")
    

    review_dict = review.dict()
    review_dict["attendee_id"] = ObjectId(current_user.id)
    review_dict["created_at"] = datetime.utcnow()

    result = await reviews_collection.insert_one(review_dict)
    created_review = await reviews_collection.find_one({"_id":result.inserted_id})

    return ReviewResponse(
        id=str(created_review["_id"]),
        event_id=created_review["event_id"],
        rating=created_review["rating"],
        comment=created_review.get("comment"),
        attendee_id=str(created_review["attendee_id"]),
        created_at=created_review.get("created_at", None)
    )


@router.get("/event/{event_id}", response_model=List[ReviewResponse])
async def get_reviews(event_id: str, current_user: UserInDB = Depends(get_current_user)):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID")
    reviews_cursor = reviews_collection.find({"event_id": event_id})
    reviews = await reviews_cursor.to_list(length=100)
    return [
        ReviewResponse(
            id=str(review["_id"]),
            event_id=review["event_id"],
            rating=review["rating"],
            comment=review.get("comment"),
            attendee_id=str(review["attendee_id"]),
            created_at=review.get("created_at")
        ) for review in reviews
    ]