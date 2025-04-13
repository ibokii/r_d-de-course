import os
import requests
import sqlite3
import time
from typing import Any

DB_DIR: str = "/app/db"
print("/app/db:", os.listdir(DB_DIR))
print("IS EXISTS rides.db?:", os.path.exists(os.path.join(DB_DIR, "rides.db")))

def init_db() -> sqlite3.Connection:
    conn: sqlite3.Connection = sqlite3.connect(os.path.join(DB_DIR, 'rides.db'))
    c: sqlite3.Cursor = conn.cursor()

    # Create tables if they do not exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            ride_uuid TEXT PRIMARY KEY,
            user_uuid TEXT,
            driver_uuid TEXT,
            distance REAL,
            price REAL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            driver_uuid TEXT PRIMARY KEY,
            name TEXT,
            surname TEXT,
            car_uuid TEXT,
            effective_from TEXT,
            expiry_date TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_uuid TEXT PRIMARY KEY,
            name TEXT,
            surname TEXT,
            is_driver BOOLEAN
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS driver_statistics (
            driver_uuid TEXT PRIMARY KEY,
            total_distance REAL
        )
    ''')

    conn.commit()
    return conn

def insert_data(conn: sqlite3.Connection, data: dict[str, Any]) -> None:
    c: sqlite3.Cursor = conn.cursor()
    ride: dict[str, Any] = data['ride']
    driver: dict[str, Any] = data['driver']
    user: dict[str, Any] = data['user']

    c.execute('''
        INSERT OR REPLACE INTO rides (ride_uuid, user_uuid, driver_uuid, distance, price)
        VALUES (?, ?, ?, ?, ?)
    ''', (ride['ride_uuid'], ride['user_uuid'], ride['driver_uuid'], ride['distance'], ride['price']))

    c.execute('''
        INSERT OR REPLACE INTO drivers (driver_uuid, name, surname, car_uuid, effective_from, expiry_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (driver['driver_uuid'], driver['name'], driver['surname'], driver['car_uuid'], driver['effective_from'], driver['expiry_date']))

    c.execute('''
        INSERT OR REPLACE INTO users (user_uuid, name, surname, is_driver)
        VALUES (?, ?, ?, ?)
    ''', (user['user_uuid'], user['name'], user['surname'], user['is_driver']))

    conn.commit()

def calculate_driver_statistics(conn: sqlite3.Connection) -> None:
    c: sqlite3.Cursor = conn.cursor()

    c.execute('''
        SELECT driver_uuid, SUM(distance) as total_distance
        FROM rides
        GROUP BY driver_uuid
    ''')
    results: list[tuple[str, float]] = c.fetchall()

    for driver_uuid, total_distance in results:
        c.execute('''
            INSERT OR REPLACE INTO driver_statistics (driver_uuid, total_distance)
            VALUES (?, ?)
        ''', (driver_uuid, total_distance))

    conn.commit()
    print("Driver statistics updated.")

def poll_api(conn: sqlite3.Connection) -> None:
    while True:
        try:
            print("Waiting for data...")
            response: requests.Response = requests.get('http://flask_api:8081/ride')
            if response.status_code == 200:
                data: dict[str, Any] = response.json()
                insert_data(conn, data)
                print("Data inserted:", data)

                # Update statistics after every new ride
                calculate_driver_statistics(conn)
            else:
                print("Failed to get data from API. Status code:", response.status_code)
        except Exception as e:
            print("Error while fetching data:", e)
        time.sleep(5)

if __name__ == '__main__':
    conn: sqlite3.Connection = init_db()
    poll_api(conn)
