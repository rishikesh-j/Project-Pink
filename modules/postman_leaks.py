import subprocess
import re
import pymongo

def get_mongo_collection():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["recon"]
    collection = db["postman_leaks"]
    return collection

def run_porch_pirate(domain, output_file):
    command = f'porch-pirate -s {domain} | grep -oP "(Author: .*|Workspace: .*|Name: .*)" > {output_file}'
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error running porch-pirate: {result.stderr}")
    return result.returncode

def parse_porch_pirate_output(output_file):
    leaks = []
    with open(output_file, 'r') as file:
        content = file.read()
        # Remove ANSI color codes
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        content = ansi_escape.sub('', content)
        regex = re.compile(r'Author: (.*?)\nWorkspace: (.*?)\nName: (.*?)\n', re.DOTALL)
        matches = regex.findall(content)
        for match in matches:
            author = match[0]
            workspace_id = match[1]
            name = match[2]
            url = f"https://www.postman.com/_api/workspace/{workspace_id}"
            leaks.append({
                "author": author,
                "workspace_id": workspace_id,
                "name": name,
                "url": url,
                "status": "Open"
            })
    return leaks

def save_to_mongo(domain, leaks):
    collection = get_mongo_collection()
    for leak in leaks:
        existing_entry = collection.find_one({"url": leak["url"]})
        if existing_entry:
            print(f"Updating existing entry: {leak['url']}")
            collection.update_one({"_id": existing_entry["_id"]}, {"$set": leak})
        else:
            print(f"Inserting new entry: {leak['url']}")
            leak["domain"] = domain
            collection.insert_one(leak)

def postman_leaks(domain):
    output_file = "porch_pirate_output.txt"
    if run_porch_pirate(domain, output_file) == 0:
        leaks = parse_porch_pirate_output(output_file)
        save_to_mongo(domain, leaks)
    else:
        print("Failed to run porch-pirate.")

if __name__ == "__main__":
    domain = "example.com"
    postman_leaks(domain)
