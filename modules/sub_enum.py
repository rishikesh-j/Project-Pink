import subprocess
import os
import re
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
    return output_file

# Commented out the amass function
# def run_amass(domain, output_dir):
#     output_file = os.path.join(output_dir, f"{domain}_amass.txt")
#     subprocess.run(['amass', 'enum', '-d', domain, '-o', output_file], check=True)
#     return output_file

def combine_results(domain, output_dir, subfinder_output):
    combined_output_file = os.path.join(output_dir, f"{domain}_all_subdomains.txt")
    with open(combined_output_file, 'w') as outfile:
        for fname in [subfinder_output]:
            with open(fname) as infile:
                outfile.write(infile.read())
    return combined_output_file

def run_gotator(domain, input_file, output_dir):
    output_file = os.path.join(output_dir, f"{domain}_gotator.txt")
    permutations_list = os.path.join(output_dir, "permutations_list.txt")
    gotator_command = f'gotator -sub {input_file} -depth 1 -numbers 3 -mindup -adv -md -perm {permutations_list} -silent > {output_file}'
    subprocess.run(gotator_command, shell=True, check=True)
    return output_file

def remove_color_codes(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def run_httpx(domain, input_file, output_dir, threads, rate_limit):
    output_file = os.path.join(output_dir, f"{domain}_httpx.txt")
    subprocess.run([
        'httpx', 
        '-silent', 
        '-l', input_file, 
        '-o', output_file, 
        '-threads', str(threads), 
        '-rl', str(rate_limit),
        '-status-code',
        '-tech-detect'
    ], check=True)
    save_to_mongo(domain, output_file, collection="verified_subdomains")

    clean_output_file = os.path.join(output_dir, f"{domain}_httpx_clean.txt")
    with open(output_file, 'r') as infile, open(clean_output_file, 'w') as outfile:
        for line in infile:
            parts = line.strip().split(' ')
            if parts:
                url = parts[0]
                outfile.write(url + '\n')

    return clean_output_file

def save_to_mongo(domain, output_file, collection):
    subdomains_collection, verified_subdomains_collection = get_mongo_collection()
    collection = subdomains_collection if collection == "subdomains" else verified_subdomains_collection
    
    with open(output_file, 'r') as file:
        for line in file:
            line = remove_color_codes(line).strip()
            parts = re.split(r'\s+\[|\]\s+\[|\]\s*$', line)
            if len(parts) >= 3:
                subdomain = parts[0]
                status_code = parts[1].strip('[]')
                tech = parts[2].strip('[]')

                print(f"Saving to DB: {subdomain}, {status_code}, {tech}")  # Debug statement

                collection.update_one(
                    {"domain": domain, "subdomain": subdomain},
                    {"$set": {
                        "status_code": status_code,
                        "tech": tech
                    }},
                    upsert=True
                )
