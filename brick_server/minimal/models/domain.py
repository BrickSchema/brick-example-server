from beanie import Document, Indexed


class Domain(Document):
    name: Indexed(str, unique=True)
    initialized: bool = False

    class Settings:
        name = "domains"
