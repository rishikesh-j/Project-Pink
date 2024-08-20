import subprocess
import os
import re
from datetime import datetime
from utils.mongo_utils import save_to_mongo
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)

def run_subfinder(domain, output_dir, threads):
    logger.info(f"Running Subfinder for domain: {domain} with {threads} threads")
    output_file = os.path.join(output_dir, f"{domain}_subfinder.txt")
    try:
        subprocess.run(['subfinder', '-d', domain, '-o', output_file, '-t', str(threads)], check=True)
        logger.info(f"Subfinder results saved to {output_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Subfinder failed: {e}")
    return output_file

def combine_results(domain, output_dir, subfinder_output):
    logger.info(f"Combining results for domain: {domain}")
    combined_output_file = os.path.join(output_dir, f"{domain}_all_subdomains.txt")
    try:
        with open(combined_output_file, 'w') as outfile:
            for fname in [subfinder_output]:
                with open(fname) as infile:
                    outfile.write(infile.read())
        logger.info(f"Combined subdomains saved to {combined_output_file}")
    except IOError as e:
        logger.error(f"Failed to combine results: {e}")
    return combined_output_file

def run_gotator(domain, input_file, output_dir):
    logger.info(f"Running Gotator for domain: {domain}")
    output_file = os.path.join(output_dir, f"{domain}_gotator.txt")
    permutations_list = os.path.join(output_dir, "permutations_list.txt")
    gotator_command = f'gotator -sub {input_file} -depth 1 -numbers 3 -mindup -adv -md -perm {permutations_list} -silent > {output_file}'
    try:
        subprocess.run(gotator_command, shell=True, check=True)
        logger.info(f"Gotator results saved to {output_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Gotator failed: {e}")
    return output_file

def remove_color_codes(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def run_httpx(domain, input_file, output_dir, threads, rate_limit):
    logger.info(f"Running Httpx for domain: {domain}")
    output_file = os.path.join(output_dir, f"{domain}_httpx.txt")
    try:
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
        logger.info(f"Httpx results saved to {output_file}")
        save_to_mongo_httpx(domain, output_file, collection_name="verified_subdomains")
    except subprocess.CalledProcessError as e:
        logger.error(f"Httpx failed: {e}")
    
    clean_output_file = os.path.join(output_dir, f"{domain}_httpx_clean.txt")
    try:
        with open(output_file, 'r') as infile, open(clean_output_file, 'w') as outfile:
            for line in infile:
                parts = line.strip().split(' ')
                if parts:
                    url = parts[0]
                    outfile.write(url + '\n')
        logger.info(f"Httpx cleaned results saved to {clean_output_file}")
    except IOError as e:
        logger.error(f"Failed to clean Httpx results: {e}")

    return clean_output_file

def save_to_mongo_subdomains(domain, output_file):
    logger.info(f"Saving subdomains to MongoDB for domain: {domain}")
    with open(output_file, 'r') as file:
        for line in file:
            subdomain = line.strip()
            if not subdomain:
                continue
            unique_fields = {"domain": domain, "subdomain": subdomain}
            data = {
                "domain": domain,
                "subdomain": subdomain,
                "date_found": datetime.now().strftime("%d-%m-%Y"),
                "status": "Open",
            }
            save_to_mongo("subdomains", unique_fields, data)

def save_to_mongo_httpx(domain, output_file, collection_name):
    logger.info(f"Saving Httpx results to MongoDB for domain: {domain}")
    with open(output_file, 'r') as file:
        for line in file:
            line = remove_color_codes(line).strip()
            parts = re.split(r'\s+\[|\]\s+\[|\]\s*$', line)
            if len(parts) >= 3:
                subdomain = parts[0]
                status_code = parts[1].strip('[]')
                tech = parts[2].strip('[]')
                
                unique_fields = {"domain": domain, "subdomain": subdomain}
                data = {
                    "domain": domain,
                    "subdomain": subdomain,
                    "status_code": status_code,
                    "tech": tech,
                    "date_found": datetime.now().strftime("%d-%m-%Y"),
                }
                save_to_mongo(collection_name, unique_fields, data)
