""" 
User data generation for seeding. 
"""

from faker import Faker


faker = Faker("en_GB")

def create_random_user_payload():
    first = faker.first_name()
    last = faker.last_name()

    return {
        "username": f"@{first.lower()}{last.lower()}",
        "email": f"{first}.{last}@example.org",
        "first_name": first,
        "last_name": last,
    }

def create_fixture_user_payload(user_data):
    return {
        **user_data,
        "is_admin": user_data.get("is_admin", False),
    }
