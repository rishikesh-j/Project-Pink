import requests
import re
import urllib.parse
import time
import urllib3
from datetime import datetime
from utils.mongo_utils import save_to_mongo
from utils.logging_utils import setup_logger

# Suppress only the single InsecureRequestWarning from urllib3 needed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up the logger
logger = setup_logger(__name__)

# Read dorks from the file
def read_dorks(filename):
    logger.info(f"Reading dorks from file: {filename}")
    with open(filename, 'r') as file:
        dorks = [line.strip() for line in file.readlines()]
    logger.info(f"Read {len(dorks)} dorks")
    return dorks

# Perform Google search
def google_search(query):
    logger.info(f"Performing Google search for query: {query}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(f'https://www.google.com/search?q={urllib.parse.quote_plus(query)}', headers=headers, verify=False)
    logger.info(f"Google search completed for query: {query}")
    return response.text

# Parse the search results using regex
def parse_results(html, dork_label):
    logger.info(f"Parsing results for dork: {dork_label}")
    results = []
    pattern = re.compile(r'data-id="atritem-(https?://[^"]+)"')
    matches = pattern.findall(html)
    for match in matches:
        results.append({
            "dork": dork_label,
            "result": match,
            "date": datetime.now().strftime("%d-%m-%y"),
            "status": "Open"  # Default status
        })
    logger.info(f"Parsed {len(results)} results for dork: {dork_label}")
    return results

# Update results in MongoDB
def save_google_dork_results(results):
    logger.info(f"Saving {len(results)} Google dork results to MongoDB")
    for result in results:
        unique_fields = {
            "dork": result["dork"],
            "result": result["result"],
        }
        save_to_mongo("google_dorks", unique_fields, result)
    logger.info("Google dork results saved to MongoDB")

# Main function
def run_google_dorks(target):
    logger.info(f"Starting Google Dorking for target: {target}")
    dorks = read_dorks('google_dorks.txt')
    all_results = []
    for dork in dorks:
        dork_label, dork_query = dork.split(' :: ')
        query = dork_query.replace('{target}', target)
        html = google_search(query)
        results = parse_results(html, dork_label)
        all_results.extend(results)
        time.sleep(5)  # Adding a delay of 5 seconds between requests
    
    # Save results to MongoDB
    if all_results:
        save_google_dork_results(all_results)
    logger.info(f"Google Dorking completed for target: {target}")

if __name__ == '__main__':
    target = input("Enter the target domain: ")
    run_google_dorks(target)
