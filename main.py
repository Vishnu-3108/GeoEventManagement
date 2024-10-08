from fastapi import FastAPI
from app.database import create_indexes
from app.routers import users, events, bookings, reviews

app = FastAPI(title="Event Management and Bookings System")

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])

@app.on_event("startup")
async def startup_event():
    await create_indexes()
    print("Indexes created successfully.")

    