import subprocess
import os
import pymongo

def get_mongo_collection():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["recon"]
    collection = db["vulnerabilities"]
    return collection

def run_nuclei(target_file, output_dir, rate_limit, threads):
    templates_path = os.path.expanduser("~/nuclei-templates")
    output_file = os.path.join(output_dir, "nuclei_results.txt")
    subprocess.run([
        'nuclei', 
        '-silent', 
        '-retries', '3', 
        '-rl', str(rate_limit), 
        '-c', str(threads), 
        '-l', target_file, 
        '-o', output_file, 
        '-t', templates_path
    ], check=True)
    save_to_mongo(target_file, output_file)
    return output_file

def save_to_mongo(target_file, output_file):
    collection = get_mongo_collection()
    with open(output_file, 'r') as file:
        for line in file:
            parts = line.strip().split(' ')
            if len(parts) >= 4:
                vulnerability = parts[0].strip('[]')
                vuln_type = parts[1].strip('[]')
                severity = parts[2].strip('[]')
                url = parts[3]
                description = ' '.join(parts[4:]).strip('[]') if len(parts) > 4 else ''
                collection.insert_one({
                    "vulnerability": vulnerability,
                    "type": vuln_type,
                    "severity": severity,
                    "url": url,
                    "description": description
                })
