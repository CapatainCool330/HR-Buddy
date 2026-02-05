import json
import os
import asyncio
from datetime import datetime

# Define Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
EMPLOYEES_FILE = os.path.join(DATA_DIR, "employees.json")
LEAVES_FILE = os.path.join(DATA_DIR, "leaves.json")

# In-Memory Cache (Simulates Database)
users_cache = []
leaves_cache = []

def _load_data():
    """Load JSON data into memory."""
    global users_cache, leaves_cache
    if os.path.exists(EMPLOYEES_FILE):
        with open(EMPLOYEES_FILE, "r") as f:
            users_cache = json.load(f)
    else:
        users_cache = []

    if os.path.exists(LEAVES_FILE):
        with open(LEAVES_FILE, "r") as f:
            leaves_cache = json.load(f)
    else:
        leaves_cache = []

def _save_leaves():
    """Persist new leaves to JSON."""
    with open(LEAVES_FILE, "w") as f:
        json.dump(leaves_cache, f, indent=2)

# Initial Load
_load_data()

# --- ASYNC INTERFACE (Compatible with engine.py) ---

async def get_user_balance(user_id: str):
    # Simulate Async DB Delay
    await asyncio.sleep(0.01)
    
    # Find user in cache
    user = next((u for u in users_cache if u["user_id"] == user_id), None)
    
    if not user:
        # Create default user if not found (Auto-provision)
        new_user = {
            "user_id": user_id,
            "name": "Guest User",
            "role": "General Staff",
            "department": "Unknown",
            "manager": "System Admin",
            "annual_leave": 20,
            "sick_leave": 10,
            "email": "guest@company.com",
            "metadata": {"salary_band": "L1"}
        }
        users_cache.append(new_user)
        # Note: We don't save new employees to file in this simple version
        return new_user
        
    return user

async def create_leave_application(user_id: str, days: int):
    await asyncio.sleep(0.01)
    
    app_id = f"APP-{len(leaves_cache) + 1000}"
    new_leave = {
        "application_id": app_id,
        "user_id": user_id,
        "days": days,
        "status": "Pending Approval",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    leaves_cache.append(new_leave)
    _save_leaves() # Persist to disk
    
    return app_id

async def get_user_applications(user_id: str):
    await asyncio.sleep(0.01)
    # Filter and Sort (Newest first)
    user_leaves = [app for app in leaves_cache if app["user_id"] == user_id]
    user_leaves.sort(key=lambda x: x["timestamp"], reverse=True)
    return user_leaves[:10]

async def get_employee_full_details(user_id: str):
    await asyncio.sleep(0.01)
    
    user = next((u for u in users_cache if u["user_id"] == user_id), None)
    
    if user:
        # Get recent leaves
        leaves = await get_user_applications(user_id)
        # Create a copy to avoid mutating the cache
        user_copy = user.copy()
        user_copy["recent_leaves"] = leaves
        return user_copy
    return None
