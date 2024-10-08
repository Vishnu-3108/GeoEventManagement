from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb+srv://<userrname><password>@cluster0.0plzl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client.event_management

users_collection = db["users"]
events_collection = db["events"]
bookings_collection = db["bookings"]
reviews_collection = db["reviews"]

async def create_indexes():
    await events_collection.create_index([("location", "2dsphere")])
    await users_collection.create_index("email", unique=True)
    await events_collection.create_index("name")
    await bookings_collection.create_index([("event_id", 1), ("attendee_id", 1)], unique=True)
