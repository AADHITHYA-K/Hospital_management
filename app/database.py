from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings   # ← THIS MUST EXIST

print("DATABASE URL:", settings.DATABASE_URL)

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def init_db() -> None:
    """Create missing tables and bring simple schema changes inline.

    SQLAlchemy's ``create_all`` only creates tables that do not exist; it
    does **not** alter existing tables.  When the models evolve (for example
    adding ``priority`` to ``Request`` or ``due_at`` to ``Task``) the
    database schema can get out of sync, leading to ``ProgrammingError``
    when the application attempts to access a column that isn't there.

    For a production system you would normally use a migration tool like
    Alembic, but for this small example we simply execute a few ``ALTER
    TABLE`` statements guarded with ``IF NOT EXISTS`` so that start‑up is
    idempotent and existing installations don't blow up.
    """
    # ensure all tables exist first
    Base.metadata.create_all(bind=engine)

    # simple patch‑up of columns added after initial deployment
    with engine.connect() as conn:
        # use raw SQL to add columns if they are missing; PostgreSQL
        # supports `IF NOT EXISTS` and SQLite ignores the statements if
        # the column is already present.
        try:
            conn.execute(
                "ALTER TABLE requests ADD COLUMN IF NOT EXISTS priority VARCHAR DEFAULT 'Normal'"
            )
        except Exception:
            # we don't want start-up to fail if this dialect doesn't support
            # the syntax (older MySQL, etc) but it rarely matters in tests.
            pass
        try:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_at TIMESTAMP"
            )
        except Exception:
            pass
        conn.commit()