import os
import re
import pymongo
from datetime import datetime

def get_mongo_collection():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["recon"]
    collection = db["postman_leaks"]
    return collection

def parse_pirate_output(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    parsed_data = re.findall(r"Author:\s*(.*?)\s*Workspace:\s*(.*?)\s*Name:\s*(.*?)\s", content, re.DOTALL)

    leaks = []
    for author, workspace, name in parsed_data:
        leak = {
            "author": author,
            "workspace": workspace,
            "name": name,
            "status": "Open",
            "url": f"https://www.postman.com/_api/workspace/{workspace}",
            "date_found": datetime.now().strftime("%d-%m-%Y")
        }
        leaks.append(leak)

    return leaks

def save_to_mongo(leaks):
    collection = get_mongo_collection()
    for leak in leaks:
        existing_leak = collection.find_one({
            "author": leak['author'],
            "workspace": leak['workspace'],
            "name": leak['name'],
            "url": leak['url']
        })
        if existing_leak:
            collection.update_one(
                {"_id": existing_leak["_id"]},
                {"$set": {"status": existing_leak.get("status", "Open"), "age": ""}}
            )
        else:
            leak["age"] = "new"
            collection.insert_one(leak)

def postman_leaks(domain, output_dir):
    output_file = os.path.join(output_dir, f"pirate_output_{domain}.txt")
    os.makedirs(output_dir, exist_ok=True)
    command = f"porch-pirate -s {domain} | grep -E '(Author:|Workspace:|Name:)' | sed -r 's/\\x1B\\[[0-9;]*[mG]//g' > {output_file}"
    os.system(command)

    leaks = parse_pirate_output(output_file)
    if leaks:
        print(f"Parsed leaks: {leaks}")
        save_to_mongo(leaks)
        print("Postman leaks results saved to the database")
    else:
        print("No leaks found")
