from typing import List, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from models.url_model import URLModel

class URLRepository:

    def __init__(self, mongo_uri: str = "mongodb://localhost:27017", db_name: str = "url_shortener"):
        self._client: MongoClient = MongoClient(mongo_uri)
        self._db: Database = self._client[db_name]
        self._collection: Collection = self._db["urls"]
        self._counter_collection: Collection = self._db["counters"]
        self._init_counter()

    def _init_counter(self) -> None:
        # initialize the ID counter if it doesn't exist
        if self._counter_collection.find_one({"_id": "url_id"}) is None:
            self._counter_collection.insert_one({"_id": "url_id", "seq": 0})

    def _get_next_id(self) -> int:
        # atomically increment and return the next ID
        result = self._counter_collection.find_one_and_update(
            {"_id": "url_id"},
            {"$inc": {"seq": 1}},
            return_document=True
        )
        return result["seq"]

    @staticmethod
    def _base62_encode(num: int) -> str:
        if num == 0:
            return "0"
        base62_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = []
        while num > 0:
            result.append(base62_chars[num % 62])
            num //= 62
        return "".join(reversed(result))

    def generate_id(self) -> str:
        # generate a unique short ID using base62 encoding
        return self._base62_encode(self._get_next_id())

    def create(self, url: str, username: str) -> URLModel:
        # create a new URL entry and return the model
        new_id = self.generate_id()
        model = URLModel(id=new_id, url=url, username=username)
        self._collection.insert_one(model.to_dict())
        return model

    def get_by_id(self, url_id: str) -> Optional[URLModel]:
        doc = self._collection.find_one({"_id": url_id})
        return URLModel.from_dict(doc)

    def get_all_ids(self, username: str) -> List[str]:
        return [doc["_id"] for doc in self._collection.find({"username": username}, {"_id": 1})]

    def update(self, url_id: str, new_url: str) -> bool:
        result = self._collection.update_one(
            {"_id": url_id},
            {"$set": {"url": new_url}}
        )
        return result.matched_count > 0

    def delete(self, url_id: str) -> bool:
        result = self._collection.delete_one({"_id": url_id})
        return result.deleted_count > 0

    def exists(self, url_id: str) -> bool:
        return self._collection.find_one({"_id": url_id}) is not None

    def get_by_url(self, url: str) -> Optional[URLModel]:
        doc = self._collection.find_one({"url": url})
        return URLModel.from_dict(doc)

    def close(self) -> None:
        self._client.close()
