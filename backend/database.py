import os
import motor.motor_asyncio
from datetime import datetime

# Default to local MongoDB if not set
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "hr_buddy_db"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

async def get_user_balance(user_id: str):
    user = await db.users.find_one({"user_id": user_id})
    if not user:
        # Create default user with balance
        new_user = {
            "user_id": user_id,
            "annual_leave": 20,
            "sick_leave": 10,
            "created_at": datetime.utcnow()
        }
        await db.users.insert_one(new_user)
        return new_user
    return user

async def create_leave_application(user_id: str, days: int):
    application = {
        "user_id": user_id,
        "days": days,
        "status": "Pending Approval",
        "timestamp": datetime.utcnow()
    }
    result = await db.leaves.insert_one(application)
    return str(result.inserted_id)

async def get_user_applications(user_id: str):
    cursor = db.leaves.find({"user_id": user_id}).sort("timestamp", -1)
    return await cursor.to_list(length=10)

async def get_employee_full_details(user_id: str):
    user = await db.users.find_one({"user_id": user_id})
    if user:
        # Get recent leaves
        leaves = await get_user_applications(user_id)
        user["recent_leaves"] = leaves
    return user
