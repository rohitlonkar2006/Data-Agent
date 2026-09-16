import os
import csv
import psycopg2
from dotenv import load_dotenv
load_dotenv()

if 'port' not in os.environ:
    os.environ['port'] = '5432'

DB_CONFIG = {
    "host" : os.environ['host'],
    "port" : int(os.environ['port']),
    "database" : os.environ['database'],
    "user" : os.environ['user'],
    "password" : os.environ['password'] 
}

CSV_DIR = "data"

conn = psycopg2.connect(**DB_CONFIG)
conn.autocommit = False

cursor = conn.cursor()

print("Connected To PostgreSQL")

create_table_sql = """

CREATE SCHEMA IF NOT EXISTS public;

-- ###########################################
-- USERS
-- ###########################################

CREATE TABLE IF NOT EXISTS public.users(
    user_id INTEGER PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(90) NOT NULL,
    email VARCHAR(90) NOT NULL UNIQUE,
    phone VARCHAR(90),
    city VARCHAR(100),
    province VARCHAR(100),
    user_type VARCHAR(20) NOT NULL,
    signup_date DATE,
    is_active BOOLEAN    
);

-- ###########################################
-- VEHICLES
-- ###########################################

CREATE TABLE IF NOT EXISTS public.vehicles(
    vehicle_id INTEGER PRIMARY KEY,
    driver_id INTEGER NOT NULL,
    make VARCHAR(90),
    model VARCHAR(90),
    year INTEGER,
    licence_plate VARCHAR(20) UNIQUE,
    color VARCHAR(30),
    is_active BOOLEAN,
    
    CONSTRAINT fk_vehicle_driver
    FOREIGN KEY(driver_id)
    REFERENCES public.users(user_id)    
);

-- RIDES

"""
