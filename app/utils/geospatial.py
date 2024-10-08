from typing import List, Dict

def list_serial(cursor) -> List[Dict]:
    return [
        {
            **doc,
            "id": str(doc["_id"]),
            "organizer_id": str(doc["organizer_id"]),
            "location": doc["location"],
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"]
        } for doc in cursor
    ]
