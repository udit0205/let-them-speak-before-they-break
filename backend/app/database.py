from sqlmodel import SQLModel, Session, create_engine
from .config import get_settings

settings = get_settings()

database_url = settings.database_url

# Use Psycopg 3 for PostgreSQL.
if database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )
elif database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql+psycopg://",
        1,
    )

connect_args = (
    {"check_same_thread": False}
    if database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    database_url,
    echo=False,
    connect_args=connect_args,
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
