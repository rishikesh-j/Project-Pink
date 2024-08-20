import subprocess
import os
import re
from datetime import datetime
from utils.mongo_utils import save_to_mongo
from utils.logging_utils import setup_logger

# Set up the logger
logger = setup_logger(__name__)

def run_dnstwist(domain, output_dir):
    logger.info(f"Running DNSTwist for {domain}...")
    output_file = os.path.join(output_dir, f"{domain}_dnstwist.txt")
    
    # Delete the file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
        logger.info(f"Deleted existing file {output_file}")
    
    logger.debug(f"Executing DNSTwist command for domain {domain}")
    subprocess.run(['dnstwist', '-r', domain, '-o', output_file], check=True)
    logger.info(f"DNSTwist results saved to {output_file}")
    
    return output_file

def remove_color_codes(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def parse_dnstwist_output(output_file):
    logger.info(f"Parsing DNSTwist output from {output_file}")
    results = []
    with open(output_file, 'r') as file:
        for line in file:
            clean_line = remove_color_codes(line).strip()
            if clean_line.startswith("*original"):
                continue  # Skip the header line
            parts = clean_line.split()
            if len(parts) < 3:
                logger.debug(f"Skipping line due to unexpected format: {clean_line}")
                continue  # Skip lines that do not have the expected format
            entry_type = parts[0]
            phishing_domain = parts[1]
            domain_details = ' '.join(parts[2:])
            results.append({
                "type": entry_type,
                "phishing_domain": phishing_domain,
                "details": domain_details,
                "status": "Open",
                "date_found": datetime.now().strftime("%d-%m-%y"),
            })
    logger.info(f"Parsed {len(results)} results from DNSTwist output")
    return results

def save_to_mongo_phishing(domain, results):
    logger.info(f"Saving DNSTwist results to MongoDB for {domain}")
    for result in results:
        result["domain"] = domain
        unique_fields = {
            "domain": domain,
            "phishing_domain": result["phishing_domain"],
            "type": result["type"]
        }
        save_to_mongo("phishing_results", unique_fields, result)
    logger.info(f"DNSTwist results saved to MongoDB for {domain}")

def phishing_scan(domain, output_dir):
    logger.info(f"Starting phishing scan for {domain}")
    output_file = run_dnstwist(domain, output_dir)

    results = parse_dnstwist_output(output_file)
    if results:
        save_to_mongo_phishing(domain, results)
    else:
        logger.info("No phishing domains found")

if __name__ == "__main__":
    domain = "example.com"  # Example domain
    output_dir = os.path.join(os.getcwd(), "Recon")
    os.makedirs(output_dir, exist_ok=True)

    phishing_scan(domain, output_dir)
