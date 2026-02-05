import json
import os
import random
from faker import Faker

fake = Faker()

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
EMPLOYEES_FILE = os.path.join(DATA_DIR, "employees.json")
LEAVES_FILE = os.path.join(DATA_DIR, "leaves.json")

ROLES = ["Software Engineer", "Product Manager", "HR Specialist", "Data Scientist", "Sales Associate", "Marketing Lead"]
DEPARTMENTS = ["Engineering", "Product", "Human Resources", "Data", "Sales", "Marketing"]

def seed_data():
    print("🌱 Generating Mock HR Data (JSON)...")
    
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    users = []
    leaves = []
    
    # Create 50 Mock Employees
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

        # Create Random Leave History for some
        if random.random() > 0.5:
             days = random.randint(1, 5)
             status = random.choice(["Approved", "Pending", "Rejected"])
             leaves.append({
                 "application_id": fake.uuid4(),
                 "user_id": emp_id,
                 "days": days,
                 "status": status,
                 "timestamp": fake.date_this_year().isoformat()
             })

    # Save to JSON Files
    with open(EMPLOYEES_FILE, "w") as f:
        json.dump(users, f, indent=2)
        
    with open(LEAVES_FILE, "w") as f:
        json.dump(leaves, f, indent=2)

    print(f"✅ Successfully saved {len(users)} employees to 'backend/data/employees.json'.")
    print(f"✅ Successfully saved {len(leaves)} leave records to 'backend/data/leaves.json'.")
    print("Example IDs to try: EMP001, EMP005, EMP042")

if __name__ == "__main__":
    seed_data()
