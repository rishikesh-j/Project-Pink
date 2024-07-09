import subprocess
import os
import re
import pymongo
from datetime import datetime

def get_mongo_collection():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["recon"]
    phishing_collection = db["phishing_results"]
    return phishing_collection

def run_dnstwist(domain, output_dir):
    output_file = os.path.join(output_dir, f"{domain}_dnstwist.txt")
    # Delete the file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
    subprocess.run(['dnstwist', '-r', domain, '-o', output_file], check=True)
    return output_file

def remove_color_codes(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def parse_dnstwist_output(output_file):
    results = []
    with open(output_file, 'r') as file:
        for line in file:
            clean_line = remove_color_codes(line).strip()
            if clean_line.startswith("*original"):
                continue  # Skip the header line
            parts = clean_line.split()
            if len(parts) < 3:
                continue  # Skip lines that do not have the expected format
            entry_type = parts[0]
            phishing_domain = parts[1]
            domain_details = ' '.join(parts[2:])
            results.append({
                "type": entry_type,
                "phishing_domain": phishing_domain,
                "details": domain_details,
                "status": "Open",
                "date_found": datetime.now().strftime("%d-%m-%y")
            })
    return results

def save_to_mongo(domain, results):
    collection = get_mongo_collection()
    for result in results:
        result["domain"] = domain
        existing_entry = collection.find_one({
            "domain": domain,
            "phishing_domain": result["phishing_domain"],
            "type": result["type"]
        })
        if not existing_entry:
            result["age"] = "new"
            collection.insert_one(result)
            print(f"New result for {result['phishing_domain']} saved to MongoDB")
        else:
            age_value = existing_entry.get("age", "")
            if age_value == "new":
                age_value = ""
            collection.update_one(
                {"_id": existing_entry["_id"]},
                {"$set": {
                    "details": result["details"],
                    "status": result["status"],
                    "age": age_value
                }},
                upsert=True
            )
            print(f"Updated result for {result['phishing_domain']} in MongoDB")

def phishing_scan(domain, output_dir):
    print(f"Running DNSTwist for {domain}...")
    output_file = run_dnstwist(domain, output_dir)
    print(f"DNSTwist results saved to {output_file}")

    print(f"Parsing DNSTwist results for {domain}...")
    results = parse_dnstwist_output(output_file)
    print(f"Parsed {len(results)} results from DNSTwist")

    print(f"Saving DNSTwist results to MongoDB for {domain}...")
    save_to_mongo(domain, results)
    print(f"DNSTwist results saved to MongoDB")

if __name__ == "__main__":
    config_file_path = 'config.json'
    with open(config_file_path) as config_file:
        config = json.load(config_file)

    domain = "example.com"  # Example domain
    output_dir = os.path.join(os.getcwd(), "Recon")

    phishing_scan(domain, output_dir)
