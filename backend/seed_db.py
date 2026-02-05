import asyncio
import os
import random
from faker import Faker
from database import db  # Import the database connection

fake = Faker()

ROLES = ["Software Engineer", "Product Manager", "HR Specialist", "Data Scientist", "Sales Associate", "Marketing Lead"]
DEPARTMENTS = ["Engineering", "Product", "Human Resources", "Data", "Sales", "Marketing"]

async def seed_data():
    print("🌱 Seeding Database with Mock HR Data...")
    
    # 1. Clear existing data
    await db.users.delete_many({})
    await db.leaves.delete_many({})
    print("Cleaning old records... Done.")

    users = []
    
    # 2. Create 50 Mock Employees
    for i in range(1, 51):
        emp_id = f"EMP{i:03d}" # EMP001, EMP002, etc.
        name = fake.name()
        dept = random.choice(DEPARTMENTS)
        
        user = {
            "user_id": emp_id,
            "name": name,
            "role": random.choice(ROLES),
            "department": dept,
            "manager": fake.name(),
            "join_date": fake.date_between(start_date='-5y', end_date='today').isoformat(),
            "performance_rating": random.randint(1, 5),
            "annual_leave": random.randint(0, 25),
            "sick_leave": random.randint(0, 10),
            "email": f"{name.lower().replace(' ', '.')}@company.com",
            "metadata": {
                "salary_band": f"L{random.randint(1,6)}",
                "location": fake.city()
            }
        }
        users.append(user)

        # 3. Create Random Leave History for some
        if random.random() > 0.5:
             days = random.randint(1, 5)
             await db.leaves.insert_one({
                 "user_id": emp_id,
                 "days": days,
                 "status": random.choice(["Approved", "Pending", "Rejected"]),
                 "timestamp": fake.date_this_year().isoformat()
             })

    # Bulk Insert
    await db.users.insert_many(users)
    print(f"✅ Successfully inserted {len(users)} employees.")
    print("Example IDs to try: EMP001, EMP005, EMP042")

if __name__ == "__main__":
    asyncio.run(seed_data())
