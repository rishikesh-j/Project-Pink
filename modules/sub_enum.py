import subprocess
import os
import pymongo

def get_mongo_collection():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["recon"]
    subdomains_collection = db["subdomains"]
    verified_subdomains_collection = db["verified_subdomains"]
    return subdomains_collection, verified_subdomains_collection

def run_subfinder(domain, output_dir, threads):
    output_file = os.path.join(output_dir, f"{domain}_subfinder.txt")
    subprocess.run(['subfinder', '-d', domain, '-o', output_file, '-t', str(threads)], check=True)
    save_to_mongo(domain, output_file, collection="subdomains")
    return output_file

def run_httpx(domain, input_file, output_dir, threads, rate_limit):
    output_file = os.path.join(output_dir, f"{domain}_httpx.txt")
    subprocess.run(['httpx', '-silent', '-l', input_file, '-o', output_file, '-threads', str(threads), '-rl', str(rate_limit)], check=True)
    save_to_mongo(domain, output_file, collection="verified_subdomains")
    return output_file

def save_to_mongo(domain, output_file, collection):
    subdomains_collection, verified_subdomains_collection = get_mongo_collection()
    collection = subdomains_collection if collection == "subdomains" else verified_subdomains_collection
    
    with open(output_file, 'r') as file:
        subdomains = file.read().splitlines()
        for subdomain in subdomains:
            collection.update_one(
                {"domain": domain, "subdomain": subdomain},
                {"$set": {"domain": domain, "subdomain": subdomain}},
                upsert=True
            )
