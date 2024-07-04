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
    all_results_file = os.path.join(output_dir, "nuclei_all_results.txt")
    
    with open(target_file, 'r') as url_file, open(all_results_file, 'w') as all_file:
        for url in url_file:
            url = url.strip()
            if not url:
                continue
            output_file = os.path.join(output_dir, f"nuclei_results_{url.replace('://', '_').replace('/', '_')}.txt")
            command = [
                'nuclei',
                '-silent',
                '-retries', '3',
                '-rl', str(rate_limit),
                '-c', str(threads),
                '-u', url,
                '-o', output_file,
                '-t', templates_path
            ]
            print(f"Running command: {' '.join(command)}")  # Print the command for debugging
            subprocess.run(command, check=True)
            
            with open(output_file, 'r') as result_file:
                all_file.write(result_file.read())
    
    remove_duplicates(all_results_file)
    save_to_mongo(target_file, all_results_file)
    return all_results_file

def remove_duplicates(file_path):
    seen = set()
    with open(file_path, 'r') as infile, open(f"{file_path}_nodups", 'w') as outfile:
        for line in infile:
            if line not in seen:
                outfile.write(line)
                seen.add(line)
    os.rename(f"{file_path}_nodups", file_path)

def save_to_mongo(target_file, output_file):
    collection = get_mongo_collection()
    seen_lines = set()
    with open(output_file, 'r') as file:
        for line in file:
            if line in seen_lines:
                continue
            seen_lines.add(line)
            parts = line.strip().split(' ', 4)
            if len(parts) >= 4:
                vulnerability = parts[0].strip('[]')
                vuln_type = parts[1].strip('[]')
                severity = parts[2].strip('[]')
                url = parts[3]
                description = parts[4].strip('[]') if len(parts) > 4 else ''
                print(f"Saving to DB: {vulnerability}, {vuln_type}, {severity}, {url}, {description}")  # Debug statement
                collection.update_one(
                    {"vulnerability": vulnerability, "type": vuln_type, "severity": severity, "url": url},
                    {"$set": {"description": description, "status": "Open"}},
                    upsert=True
                )
