from motor.motor_asyncio import AsyncIOMotorClient

#mongo_client = AsyncIOMotorClient("mongodb://mongo_database:27017")
mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
db = mongo_client["adie-sn-bot"]


def documents():
    documents_collection = db["documents"]
    return documents_collection
