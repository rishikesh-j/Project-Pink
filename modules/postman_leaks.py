import os
import re
from datetime import datetime
from utils.mongo_utils import save_to_mongo

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
            "date_found": datetime.now().strftime("%d-%m-%y"),
        }
        leaks.append(leak)

    return leaks

def save_to_mongo_postman(leaks):
    for leak in leaks:
        unique_fields = {
            "author": leak['author'],
            "workspace": leak['workspace'],
            "name": leak['name'],
            "url": leak['url'],
        }
        save_to_mongo("postman_leaks", unique_fields, leak)

def postman_leaks(domain, output_dir):
    output_file = os.path.join(output_dir, f"pirate_output_{domain}.txt")
    os.makedirs(output_dir, exist_ok=True)
    command = f"porch-pirate -s {domain} | grep -E '(Author:|Workspace:|Name:)' | sed -r 's/\\x1B\\[[0-9;]*[mG]//g' > {output_file}"
    os.system(command)

    leaks = parse_pirate_output(output_file)
    if leaks:
        print(f"Parsed leaks: {leaks}")
        save_to_mongo_postman(leaks)
        print("Postman leaks results saved to the database")
    else:
        print("No leaks found")

if __name__ == "__main__":
    domain = "example.com"  # Example domain
    output_dir = os.path.join(os.getcwd(), "Recon")

    postman_leaks(domain, output_dir)
