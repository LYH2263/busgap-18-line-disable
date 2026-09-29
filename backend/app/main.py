from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.api.router import api_router
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.services.seed import seed_if_empty


def ensure_schema() -> None:
    """Create tables and add columns introduced after the initial snapshot.

    ``create_all`` only handles missing tables, so an existing database built
    from the first snapshot lacks later columns. Add them idempotently via the
    inspector (portable across PostgreSQL and SQLite); the ``DEFAULT true``
    keeps already-seeded lines active.
    """
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    if "lines" in inspector.get_table_names() and "is_active" not in [c["name"] for c in inspector.get_columns("lines")]:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE lines ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE"))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_schema()
    if settings.seed_on_empty:
        db = SessionLocal()
        try:
            seed_if_empty(db)
        finally:
            db.close()
    yield


app = FastAPI(title="BusGap", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api")
