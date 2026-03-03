from dataclasses import dataclass
from typing import Optional

@dataclass
class UserModel:
    username: str
    password: str

    def to_dict(self) -> dict:
        return {
            "_id": self.username,
            "password": self.password
        }

    @classmethod
    def from_dict(cls, data: dict) -> Optional["UserModel"]:
        if data is None:
            return None
        return cls(
            username=data["_id"],
            password=data["password"]
        )
