# github_leaks.py

import os
import re
import pymongo
from datetime import datetime

def get_mongo_collection():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["recon"]
    collection = db["github_leaks"]
    return collection

def parse_trufflehog_output(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    regex_pattern = re.compile(
        r"Detector Type:\s*(?P<detector_type>.*?)\n"
        r"Decoder Type:\s*(?P<decoder_type>.*?)\n"
        r"Raw result:\s*(?P<raw_result>.*?)\n"
        r"Commit:\s*(?P<commit>.*?)\n"
        r"Email:\s*(?P<email>.*?)\n"
        r"File:\s*(?P<file>.*?)\n"
        r"Line:\s*(?P<line>\d+)\n"
        r"Repository:\s*(?P<repository>.*?)\n"
        r"Timestamp:\s*(?P<timestamp>.*?)\n"
    )

    matches = regex_pattern.finditer(content)

    leaks = []
    for match in matches:
        leak = match.groupdict()
        leak['status'] = 'Open'
        leak['date_found'] = datetime.now().strftime("%d-%m-%y")
        leaks.append(leak)

    return leaks

def save_to_mongo(leaks):
    collection = get_mongo_collection()
    for leak in leaks:
        existing_leak = collection.find_one({
            "detector_type": leak['detector_type'],
            "decoder_type": leak['decoder_type'],
            "raw_result": leak['raw_result'],
            "commit": leak['commit'],
            "email": leak['email'],
            "file": leak['file'],
            "line": leak['line'],
            "repository": leak['repository'],
            "timestamp": leak['timestamp'],
        })
        if not existing_leak:
            leak["age"] = "new"
            collection.insert_one(leak)
            print(f"New result for {leak['repository']} saved to MongoDB")
        else:
            age_value = existing_leak.get("age", "")
            if age_value == "new":
                age_value = ""
            collection.update_one(
                {"_id": existing_leak["_id"]},
                {"$set": {
                    "status": leak["status"],
                    "age": age_value
                }},
                upsert=True
            )
            print(f"Updated result for {leak['repository']} in MongoDB")

def github_leaks(github_org, output_dir):
    output_file = os.path.join(output_dir, "trufflehog_output.txt")
    command = f"trufflehog github --org={github_org} | grep -E \"(Detector Type:|Decoder Type:|Raw result:|Commit:|Email:|File:|Line:|Repository:|Timestamp:)\" | sed -r 's/\\x1B\\[[0-9;]*[mG]//g' > {output_file}"
    os.system(command)

    leaks = parse_trufflehog_output(output_file)
    if leaks:
        print(f"Parsed leaks: {leaks}")
        save_to_mongo(leaks)
        print("GitHub leaks results saved to the database")
    else:
        print("No leaks found")

if __name__ == "__main__":
    config_file_path = 'config.json'
    with open(config_file_path) as config_file:
        config = json.load(config_file)

    github_org = "example_org"  # Example GitHub organization
    output_dir = os.path.join(os.getcwd(), "Recon")
    os.makedirs(output_dir, exist_ok=True)

    github_leaks(github_org, output_dir)
