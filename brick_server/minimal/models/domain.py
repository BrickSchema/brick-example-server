from beanie import Document
from pymongo import IndexModel


class Domain(Document):
    name: str
    initialized: bool = False

    class Settings:
        indexes = [
            IndexModel("name", unique=True),
        ]
