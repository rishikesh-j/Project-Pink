import shodan
import os
import fileinput
import json
import pymongo

SHODAN_API_KEY = "rZkzrPr7vQYHI9V3oMS0uUTJNsEgimmo"

api = shodan.Shodan(SHODAN_API_KEY)

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

def search_shodan(organization, output_dir):
    replace_org = "${target}"  # Replace part in dork file for organization.

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
        shodan_count = api.count(dork)
        print(f'Dorking for {name} = {shodan_count}')
        shodan_search = api.search(dork)

        result = {
            "organization": organization,
            "dork": dork,
            "name": name,
            "shodan_count": shodan_count,
            "results": shodan_search['matches']
        }

        sanitize_document(result)
        collection.insert_one(result)
