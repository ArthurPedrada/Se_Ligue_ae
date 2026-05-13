import os

class Config:
    uri = os.getenv("DATABASE_URL", "sqlite:///database.db")

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
