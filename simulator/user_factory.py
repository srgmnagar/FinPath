import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('en_IN')

DEVICE_TYPES = ['android', 'ios', 'web']
DEVICE_WEIGHTS = [0.50, 0.35, 0.15]

COUNTRIES = ['IN', 'IN', 'IN', 'IN', 'IN', 'US', 'SG', 'AE', 'GB', 'CA']

RISK_PROFILES = ['low', 'medium', 'high']
RISK_WEIGHTS = [0.35, 0.45, 0.20]

SIM_START = datetime(2024, 1, 1)
SIM_END   = datetime(2024, 12, 31)


def random_signup_time() -> datetime:
    delta = SIM_END - SIM_START
    return SIM_START + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_users(n: int) -> list[dict]:
    users = []
    for i in range(1, n + 1):
        users.append({
            "user_id":   i,
            "signup_at": random_signup_time(),
            "device_type": random.choices(DEVICE_TYPES, DEVICE_WEIGHTS)[0],
            "country":   random.choice(COUNTRIES),
            "risk_profile": random.choices(RISK_PROFILES, RISK_WEIGHTS)[0],
            "activated_at":    None,
            "first_deposit_at": None,
        })
    return users
