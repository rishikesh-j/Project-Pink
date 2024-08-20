import os
import re
from datetime import datetime
from utils.mongo_utils import save_to_mongo
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)

def parse_pirate_output(file_path):
    logger.info(f"Parsing Pirate output from {file_path}")
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
            "date_found": datetime.now().strftime("%d-%m-%y"),
        }
        leaks.append(leak)

    logger.info(f"Parsed {len(leaks)} leaks from Pirate output")
    return leaks

def save_to_mongo_postman(leaks):
    logger.info("Saving parsed leaks to MongoDB")
    for leak in leaks:
        unique_fields = {
            "author": leak['author'],
            "workspace": leak['workspace'],
            "name": leak['name'],
            "url": leak['url'],
        }
        save_to_mongo("postman_leaks", unique_fields, leak)
    logger.info("Saved leaks to MongoDB successfully")

def postman_leaks(domain, output_dir):
    logger.info(f"Running Postman Leaks scan for domain: {domain}")
    output_file = os.path.join(output_dir, f"pirate_output_{domain}.txt")
    os.makedirs(output_dir, exist_ok=True)
    command = f"porch-pirate -s {domain} | grep -E '(Author:|Workspace:|Name:)' | sed -r 's/\\x1B\\[[0-9;]*[mG]//g' > {output_file}"
    logger.info(f"Executing command: {command}")
    os.system(command)

    leaks = parse_pirate_output(output_file)
    if leaks:
        logger.info(f"Parsed leaks: {leaks}")
        save_to_mongo_postman(leaks)
        logger.info("Postman leaks results saved to the database")
    else:
        logger.info("No leaks found")

if __name__ == "__main__":
    domain = "example.com"  # Example domain
    output_dir = os.path.join(os.getcwd(), "Recon")

    postman_leaks(domain, output_dir)
