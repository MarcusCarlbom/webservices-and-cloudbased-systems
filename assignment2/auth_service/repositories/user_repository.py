from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from models.user_model import UserModel

class UserRepository:

    def __init__(self, mongo_uri: str = "mongodb://localhost:27017", db_name: str = "auth_service"):
        self._client: MongoClient = MongoClient(mongo_uri)
        self._db: Database = self._client[db_name]
        self._collection: Collection = self._db["users"]

    def create(self, username: str, hashed_password: str) -> bool:
        # create a new user entry and return True if successful
        model = UserModel(username=username, password=hashed_password)
        self._collection.insert_one(model.to_dict())
        return True
    
    def find_by_username(self, username: str) -> Optional[UserModel]:
        doc = self._collection.find_one({"_id": username})
        return UserModel.from_dict(doc)
        
    def update_password(self, username: str, new_hashed_password: str) -> bool:
        result = self._collection.update_one(
            {"_id": username},
            {"$set": {"password": new_hashed_password}}
        )
        return result.matched_count > 0


    def close(self) -> None:
        self._client.close()
