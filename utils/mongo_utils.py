# mongo_utils.py
import pymongo
from datetime import datetime

def get_mongo_collection(db_name, collection_name):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    collection = db[collection_name]
    return collection

def save_to_mongo(collection_name, unique_fields, data, db_name="recon"):
    collection = get_mongo_collection(db_name, collection_name)
    
    existing_entry = collection.find_one(unique_fields)

    if not existing_entry:
        data["comment"] = ""
        data["date_found"] = datetime.now().strftime("%d-%m-%Y")
        collection.insert_one(data)
        print(f"New result saved to MongoDB")
    else:
        collection.update_one(
            {"_id": existing_entry["_id"]},
            {"$set": {**data, "status": existing_entry.get("status", "Open"), "comment": existing_entry.get("comment", "")}},
            upsert=True
        )
        print(f"Updated result in MongoDB")
