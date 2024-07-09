import shodan
import os
import fileinput
import json
import pymongo
from datetime import datetime

def get_mongo_collection():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["recon"]
    shodan_collection = db["shodan_results"]
    return shodan_collection

def sanitize_document(document):
    """ Sanitize the document to ensure no values exceed MongoDB's limits. """
    if isinstance(document, dict):
        for key, value in document.items():
            if isinstance(value, int) and value > 2**63 - 1:
                document[key] = str(value)
            elif isinstance(value, (dict, list)):
                sanitize_document(value)
    elif isinstance(document, list):
        for item in document:
            sanitize_document(item)

def filter_fields(result):
    """ Filter required fields from the result """
    filtered_result = {
        "data": result.get("data"),
        "org": result.get("org"),
        "isp": result.get("isp"),
        "ip_str": result.get("ip_str"),
        "location": result.get("location"),
        "http": result.get("http"),
        "port": result.get("port"),
        "status": "Open"
    }
    return filtered_result

def search_shodan(organization, output_dir, shodan_api_key):
    api = shodan.Shodan(shodan_api_key)
    replace_org = "${organization}"  # Replace part in dork file for organization.

    with open(r'dorks.txt', 'r') as file:  # dorks.txt is the file which has all dorks.
        dorks = file.read()
        dorks = dorks.replace(replace_org, organization)

    with open(r'tmp.txt', 'w') as file:  # Just a temporary file for code, need to be always present in directory.
        file.write(dorks)

    collection = get_mongo_collection()

    for line in fileinput.FileInput(files="tmp.txt"):
        name = line.split("::")[0]
        dork = line.split("::")[1].strip()
        print(f"Using dork: {dork}")  # Print the dork being used

        try:
            print(f"Searching Shodan with dork: {dork}, page: 1")
            shodan_search = api.search(dork, page=1)
            total_results = shodan_search['matches']
            print(f"Page 1 results: {len(shodan_search['matches'])} matches")
        except shodan.APIError as e:
            print(f"Shodan API error: {e}")
            total_results = []

        shodan_count = len(total_results)
        print(f'Dorking for {name} = {shodan_count} total results')

        for result in total_results:
            filtered_result = filter_fields(result)
            result_data = {
                "organization": organization,
                "dork": dork,
                "name": name,
                "shodan_count": shodan_count,
                "date_found": datetime.now().strftime("%d-%m-%y"),
                **filtered_result
            }

            existing_entry = collection.find_one({
                "organization": organization,
                "dork": dork,
                "name": name,
                "ip_str": result_data["ip_str"]
            })

            if not existing_entry:
                result_data["age"] = "new"
                sanitize_document(result_data)
                collection.insert_one(result_data)
                print(f"New result for {filtered_result['ip_str']} saved to MongoDB")
            else:
                age_value = existing_entry.get("age", "")
                if age_value == "new":
                    age_value = ""
                collection.update_one(
                    {"_id": existing_entry["_id"]},
                    {"$set": {
                        "data": result_data["data"],
                        "org": result_data["org"],
                        "isp": result_data["isp"],
                        "location": result_data["location"],
                        "http": result_data["http"],
                        "port": result_data["port"],
                        "status": result_data["status"],
                        "age": age_value
                    }},
                    upsert=True
                )
                print(f"Updated result for {filtered_result['ip_str']} in MongoDB")

if __name__ == "__main__":
    config_file_path = 'config.json'
    with open(config_file_path) as config_file:
        config = json.load(config_file)
    
    organization = "Nykaa"  # Example organization name
    output_dir = os.path.join(os.getcwd(), "Recon")
    shodan_api_key = config["shodan_api_key"]
    
    search_shodan(organization, output_dir, shodan_api_key)
