from sqlalchemy import text

from app.database.connection import engine


def test_connection():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT 1")
        )

        print(
            "Database result:",
            result.scalar()
        )


if __name__ == "__main__":
    test_connection()