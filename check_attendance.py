
from sqlalchemy import text
from src.app.db.database import engine

try:
    with engine.connect() as connection:
        count = connection.execute(
            text("SELECT COUNT(*) FROM attendance")
        ).scalar_one()

        print("Attendance records:", count)

        revision = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()

        print("Current migration revision:", revision)

except Exception as error:
    print("Database check failed:", error)
