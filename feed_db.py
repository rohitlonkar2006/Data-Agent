import os
import csv
import psycopg2
from dotenv import load_dotenv
load_dotenv()

DB_CONFIG = {
    "host" : os.getenv("host"),
    "" : 
}

conn = psycopg2.connect()