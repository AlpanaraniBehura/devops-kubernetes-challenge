import os

import psycopg2
from fastapi import FastAPI

app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


@app.get("/")
def root():
    return {"message": "DevOps Challenge API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-health")
def db_health():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT 1")
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return {
        "database": "connected",
        "result": result[0]
    }


@app.post("/items/{name}")
def create_item(name: str):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS items (id SERIAL PRIMARY KEY, name TEXT)"
    )

    cursor.execute(
        "INSERT INTO items (name) VALUES (%s) RETURNING id",
        (name,)
    )

    item_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "id": item_id,
        "name": name
    }


@app.get("/items")
def get_items():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS items (id SERIAL PRIMARY KEY, name TEXT)"
    )

    cursor.execute("SELECT id, name FROM items ORDER BY id")

    items = cursor.fetchall()

    cursor.close()
    connection.close()

    return [
        {
            "id": item[0],
            "name": item[1]
        }
        for item in items
    ]