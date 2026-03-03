from dataclasses import dataclass
from typing import Optional

@dataclass
class URLModel:
    id: str
    url: str
    username: str

    def to_dict(self) -> dict:
        return {
            "_id": self.id,
            "url": self.url,
            "username": self.username
        }

    @classmethod
    def from_dict(cls, data: dict) -> Optional["URLModel"]:
        if data is None:
            return None
        return cls(
            id=data["_id"],
            url=data["url"],
            username=data["username"]
        )
