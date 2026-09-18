import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"
RANDOM = random.Random(42)
START_DATE = datetime(2024, 1, 1)


def write_csv(filename, fieldnames, rows):
    with (DATA_DIR / filename).open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def random_datetime():
    return (START_DATE + timedelta(days=RANDOM.randint(0, 730), minutes=RANDOM.randint(0, 1439))).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def main():
    DATA_DIR.mkdir(exist_ok=True)

    first_names = ["Ava", "Liam", "Mia", "Noah", "Emma", "Ethan", "Zoe", "Lucas"]
    last_names = ["Smith", "Patel", "Brown", "Wilson", "Garcia", "Lee", "Martin", "Clark"]
    cities = [("Toronto", "ON"), ("Vancouver", "BC"), ("Calgary", "AB"), ("Montreal", "QC")]

    users = []
    for user_id in range(1, 10001):
        city, province = RANDOM.choice(cities)
        users.append(
            {
                "user_id": user_id,
                "first_name": RANDOM.choice(first_names),
                "last_name": RANDOM.choice(last_names),
                "email": f"user{user_id}@example.com",
                "phone": f"555-{user_id // 10000:01d}{user_id % 10000:04d}",
                "city": city,
                "province": province,
                "user_type": "driver" if user_id <= 3000 else "rider",
                "signup_date": (START_DATE + timedelta(days=RANDOM.randint(0, 730))).date(),
                "is_active": RANDOM.random() > 0.05,
            }
        )
    write_csv("users.csv", users[0].keys(), users)

    vehicles = []
    for vehicle_id in range(1, 3001):
        vehicles.append(
            {
                "vehicle_id": vehicle_id,
                "driver_id": vehicle_id,
                "make": RANDOM.choice(["Toyota", "Honda", "Ford", "Hyundai"]),
                "model": RANDOM.choice(["Civic", "Corolla", "Focus", "Elantra"]),
                "year": RANDOM.randint(2015, 2024),
                "licence_plate": f"DA{vehicle_id:05d}",
                "color": RANDOM.choice(["Black", "White", "Silver", "Blue"]),
                "is_active": RANDOM.random() > 0.08,
            }
        )
    write_csv("vehicles.csv", vehicles[0].keys(), vehicles)

    rides = []
    for ride_id in range(1, 20001):
        status = RANDOM.choices(["completed", "cancelled", "requested"], weights=[80, 12, 8])[0]
        requested_at = random_datetime()
        rides.append(
            {
                "ride_id": ride_id,
                "rider_id": RANDOM.randint(3001, 10000),
                "driver_id": RANDOM.randint(1, 3000),
                "requested_at": requested_at,
                "pickup_time": requested_at if status != "requested" else "",
                "dropoff_time": requested_at if status == "completed" else "",
                "pickup_latitude": f"{RANDOM.uniform(43.5, 49.2):.6f}",
                "pickup_longitude": f"{RANDOM.uniform(-123.2, -73.5):.6f}",
                "dropoff_latitude": f"{RANDOM.uniform(43.5, 49.2):.6f}",
                "dropoff_longitude": f"{RANDOM.uniform(-123.2, -73.5):.6f}",
                "distance_km": f"{RANDOM.uniform(1, 45):.2f}",
                "fare": f"{RANDOM.uniform(8, 150):.2f}",
                "surge_multiplier": f"{RANDOM.uniform(1, 2.5):.2f}",
                "status": status,
                "cancellation_reason": "Rider cancelled" if status == "cancelled" else "",
            }
        )
    write_csv("rides.csv", rides[0].keys(), rides)

    payments = []
    for payment_id in range(1, 16001):
        ride = rides[payment_id - 1]
        payments.append(
            {
                "payment_id": payment_id,
                "ride_id": ride["ride_id"],
                "user_id": ride["rider_id"],
                "amount": ride["fare"],
                "payment_method": RANDOM.choice(["card", "cash", "wallet"]),
                "payment_status": "completed" if ride["status"] == "completed" else "refunded",
                "transaction_id": f"TXN{payment_id:08d}",
                "payment_time": ride["requested_at"],
            }
        )
    write_csv("payments.csv", payments[0].keys(), payments)

    ratings = []
    for rating_id in range(1, 12001):
        ride = rides[rating_id - 1]
        ratings.append(
            {
                "rating_id": rating_id,
                "ride_id": ride["ride_id"],
                "rider_id": ride["rider_id"],
                "driver_id": ride["driver_id"],
                "rating": RANDOM.randint(1, 5),
                "comment": "Good ride" if rating_id % 3 else "Smooth trip",
                "rated_at": ride["requested_at"],
            }
        )
    write_csv("ratings.csv", ratings[0].keys(), ratings)

    print("Generated 10,000 users, 3,000 vehicles, 20,000 rides, 16,000 payments, and 12,000 ratings.")


if __name__ == "__main__":
    main()