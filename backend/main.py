import os
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "todos_db")
DB_USER = os.getenv("DB_USER", "myuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mypassword")


def resolve_frontend_dir() -> Path:
    candidate_dirs = [
        Path(__file__).resolve().parent.parent / "frontend",
        Path(__file__).resolve().parent / "frontend",
        Path("/app/frontend"),
        Path("/frontend"),
    ]
    for candidate in candidate_dirs:
        if candidate.exists():
            return candidate
    return candidate_dirs[0]


FRONTEND_DIR = resolve_frontend_dir()

app = FastAPI(title="Todo App", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TodoCreate(BaseModel):
    title: str


class TodoUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    completed BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
                """
            )
            conn.commit()


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok"}


@app.get("/api/todos")
def list_todos() -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, title, completed, created_at FROM todos ORDER BY id DESC"
            )
            rows = cur.fetchall()
    return [dict(row) for row in rows]


@app.post("/api/todos", status_code=201)
def create_todo(payload: TodoCreate) -> dict[str, Any]:
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title is required")

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO todos (title) VALUES (%s) RETURNING id, title, completed, created_at",
                (title,),
            )
            row = cur.fetchone()
            conn.commit()
    return dict(row)


@app.put("/api/todos/{todo_id}")
def update_todo(todo_id: int, payload: TodoUpdate) -> dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if payload.title is not None:
                cur.execute(
                    "UPDATE todos SET title = %s WHERE id = %s RETURNING id, title, completed, created_at",
                    (payload.title.strip(), todo_id),
                )
            elif payload.completed is not None:
                cur.execute(
                    "UPDATE todos SET completed = %s WHERE id = %s RETURNING id, title, completed, created_at",
                    (payload.completed, todo_id),
                )
            else:
                raise HTTPException(status_code=400, detail="No changes supplied")

            row = cur.fetchone()
            conn.commit()

    if row is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return dict(row)


@app.delete("/api/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
            conn.commit()


@app.get("/")
def get_index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/index.html")
def get_index_html() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")

print("Hello World")
