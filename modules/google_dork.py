import requests
import re
import urllib.parse
import time
import urllib3
from datetime import datetime
from pymongo import MongoClient

# Suppress only the single InsecureRequestWarning from urllib3 needed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Read dorks from the file
def read_dorks(filename):
    with open(filename, 'r') as file:
        dorks = [line.strip() for line in file.readlines()]
    return dorks

# Perform Google search
def google_search(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(f'https://www.google.com/search?q={urllib.parse.quote_plus(query)}', headers=headers, verify=False)
    return response.text

# Parse the search results using regex
def parse_results(html, dork_label):
    results = []
    pattern = re.compile(r'data-id="atritem-(https?://[^"]+)"')
    matches = pattern.findall(html)
    for match in matches:
        results.append({
            "dork": dork_label,
            "result": match,
            "date": datetime.now().strftime("%d-%m-%y"),
            "age": "new",
            "status": "Open"
        })
    return results

# Update results in MongoDB
def update_results_in_mongo(results, db_name='recon', collection_name='google_dorks'):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    collection = db[collection_name]

    for result in results:
        existing_entry = collection.find_one({"result": result["result"]})
        if existing_entry:
            result["age"] = ""
            result["status"] = existing_entry.get("status", "Open")
            collection.update_one({"_id": existing_entry["_id"]}, {"$set": result})
        else:
            collection.insert_one(result)

# Main function
def run_google_dorks(target):
    dorks = read_dorks('google_dorks.txt')
    all_results = []
    for dork in dorks:
        dork_label, dork_query = dork.split(' :: ')
        query = dork_query.replace('{target}', target)
        html = google_search(query)
        results = parse_results(html, dork_label)
        all_results.extend(results)
        time.sleep(5)  # Adding a delay of 5 seconds between requests
    
    # Update results in MongoDB
    if all_results:
        update_results_in_mongo(all_results)
