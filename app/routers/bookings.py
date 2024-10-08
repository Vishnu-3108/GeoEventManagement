from fastapi import APIRouter, HTTPException, status, Depends
import stripe.error
from app.models.booking import BookingCreate, BookingResponse
from app.schemas.booking import list_serial
from app.database import events_collection, bookings_collection
from app.auth import get_current_user
from bson.objectid import ObjectId
from typing import List
from datetime import datetime
import stripe
from app.models.user import UserInDB

router = APIRouter()

#stripe initialization
stripe.api_key = "Your-secret-key"

@router.post("/",response_model=BookingCreate, status_code=status.HTTP_201_CREATED)
async def create_booking(booking: BookingCreate, current_user: UserInDB=Depends(get_current_user)):
    
    #Validate event existence 
    if not ObjectId.is_valid(booking.event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID")
    event = await events_collection.find_one({"_id":ObjectId(booking.event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    #checking capacity
    existing_bookings = await bookings_collection.count_documents({"event_id":booking.event_id, "status":"confirmed"})
    if existing_bookings + booking.tickets > event["capacity"]:
        raise HTTPException(status_code=400, detail="Not enough tickets available")
    
    #caluculate total amount
    standard_price = event["pricing"].get("standard",0)
    total_amount = standard_price * booking.tickets

    # Create a stripe payment intent
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount = int(total_amount*100),
            currency='usd',
            metadata={'integration_check':'accept_a_payment'}
            )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    booking_dict = booking.dict()
    booking_dict["attendee_id"] = ObjectId(current_user.id)
    booking_dict["booking_date"] = datetime.utcnow()
    booking_dict["status"] = "pending"
    booking_dict["total_amount"] = total_amount
    booking_dict["payment_intent_id"] = payment_intent.id
    booking_dict["payment_status"] = "pending"

    result = await bookings_collection.insert_one(booking_dict)
    created_booking = await bookings_collection.find_one({"_id":ObjectId(result.inserted_id)})

    # returning booking responce
    return BookingResponse(
        id=str(created_booking["_id"]),
        event_id=created_booking["event_id"],
        tickets=created_booking["tickets"],
        payment_status=created_booking["payment_status"],
        attendee_id=str(created_booking["attendee_id"]),
        booking_date=created_booking["booking_date"],
        status=created_booking["status"],
        total_amount=created_booking["total_amount"]
    )

# to get all the bookings on the current_user.id

@router.get("/",response_model=List[BookingResponse])
async def get_user_bookings(current_user: UserInDB=Depends(get_current_user)):
    cursor = bookings_collection.find({"attendee_id": ObjectId(current_user.id)})
    bookings = await cursor.to_list(length=100)
    return[
        BookingResponse(
            id=str(booking["_id"]),
            event_id=booking["event_id"],
            tickets=booking["tickets"],
            payment_status=booking["payment_status"],
            attendee_id=str(booking["attendee_id"]),
            booking_date=booking["booking_date"],
            status=booking["status"],
            total_amount=booking["total_amount"]
        ) for booking in bookings
    ]    


# updating the booking_collevtion status 

@router.put("/{booking_id}",response_model=BookingResponse)
async def update_booking(booking_id:str, status_update: str, current_user: UserInDB=Depends(get_current_user)):
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(status_code=400, detail="Invalid booking ID")
    booking = await bookings_collection.find_one({"_id":ObjectId(booking_id), "attendee_id": ObjectId(current_user.id)})
    if not booking:
        raise HTTPException(status_code=404,detail="booking not found")
    if booking["status"] == "canceled":
        raise HTTPException(status_code=400, detail="Booking already canceled")
    
    if status_update == "canceled":
        await bookings_collection.update_one({"_id":ObjectId(booking_id)}, {"$set": {"status":"canceled","payment_status":"refunded"}})
    else:
        raise HTTPException(status_code=400,detail="Invalid status update")
    
    updated_booking = await bookings_collection({"_id":ObjectId(booking_id)})
    return BookingResponse(
        id=str(updated_booking["_id"]),
        event_id=updated_booking["event_id"],
        tickets=updated_booking["tickets"],
        payment_status=updated_booking["payment_status"],
        attendee_id=str(updated_booking["attendee_id"]),
        booking_date=updated_booking["booking_date"],
        status=updated_booking["status"],
        total_amount=updated_booking["total_amount"]
    )