Event Management API with Geospatial Feature

This project is a comprehensive Event Management API built with FastAPI and MongoDB. It facilitates event creation, booking, and review functionalities, integrating geolocation capabilities for enhanced event discovery. The API also incorporates Stripe for secure payment processing.

Key Features-


>Event Management: Create, update, and delete events.

>Booking System: Users can book events and manage their bookings.

>Review System: Attendees can leave reviews and ratings for events.

>Geolocation: Locate events based on geographical data.

>Payment Integration: Secure payments via the Stripe API.

>User Authentication: Role-based access control for attendees and admins.


Technologies Used-


>Python: FastAPI framework for building the API.

>MongoDB: Database for storing user, event, booking, and review data.

>Stripe API: For handling payments securely.

File Structure-

/app

    ├── auth.py
    ├── database.py
    ├── models
    │   ├── booking.py
    │   ├── event.py
    │   ├── review.py
    │   └── user.py
    ├── routers
    │   ├── bookings.py
    │   ├── events.py
    │   ├── reviews.py
    │   └── users.py
    ├── schemas
    │   ├── booking.py
    │   ├── event.py
    │   ├── review.py
    │   └── user.py
    ├── utils
    │   ├── geospatial.py
    │   └── notifications.py
    └── __init__.py
main.py

Installation
>Clone the repository-

>git clone https://github.com/yourusername/event-management-api.git
cd event-management-api

Set up a virtual environment-

>python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

Install the required dependencies-

>pip install -r requirements.txt

Configure your environment variables and database connection in a .env file (do not include this file in your repository).

Run the application-

>uvicorn main:app --reload


API Documentation-

>You can access the interactive API documentation at http://127.0.0.1:8000/docs after running the application.

Contributing-

>Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.




