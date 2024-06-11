import subprocess
import os
import pymongo

def get_mongo_collection():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["recon"]
    collection = db["subdomains"]
    return collection

def run_subfinder(domain, output_dir, threads):
    output_file = os.path.join(output_dir, f"{domain}_subfinder.txt")
    subprocess.run(['subfinder', '-d', domain, '-o', output_file, '-t', str(threads)], check=True)
    save_to_mongo(domain, output_file)
    return output_file

def save_to_mongo(domain, output_file):
    collection = get_mongo_collection()
    with open(output_file, 'r') as file:
        subdomains = file.read().splitlines()
        for subdomain in subdomains:
            collection.update_one(
                {"domain": domain, "subdomain": subdomain},
                {"$set": {"domain": domain, "subdomain": subdomain}},
                upsert=True
            )
