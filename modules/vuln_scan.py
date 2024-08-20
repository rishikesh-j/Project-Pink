import subprocess
import os
from datetime import datetime
from utils.mongo_utils import save_to_mongo
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)

def run_nuclei(target_file, output_dir, rate_limit, threads):
    logger.info(f"Running Nuclei scan on target file: {target_file}")
    templates_path = os.path.expanduser("~/nuclei-templates")
    all_results_file = os.path.join(output_dir, "nuclei_all_results.txt")
    
    try:
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
                logger.debug(f"Running command: {' '.join(command)}")
                subprocess.run(command, check=True)
                
                with open(output_file, 'r') as result_file:
                    all_file.write(result_file.read())
        logger.info(f"Nuclei scan completed. Results saved to {all_results_file}")
        
        remove_duplicates(all_results_file)
        save_to_mongo_vuln(target_file, all_results_file)
    except subprocess.CalledProcessError as e:
        logger.error(f"Nuclei scan failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during Nuclei scan: {e}")
    
    return all_results_file

def remove_duplicates(file_path):
    logger.info(f"Removing duplicate entries from {file_path}")
    seen = set()
    try:
        with open(file_path, 'r') as infile, open(f"{file_path}_nodups", 'w') as outfile:
            for line in infile:
                if line not in seen:
                    outfile.write(line)
                    seen.add(line)
        os.rename(f"{file_path}_nodups", file_path)
        logger.info(f"Duplicates removed. Updated file saved as {file_path}")
    except IOError as e:
        logger.error(f"Failed to remove duplicates from {file_path}: {e}")

def save_to_mongo_vuln(target_file, output_file):
    logger.info(f"Saving vulnerabilities from {output_file} to MongoDB")
    try:
        with open(output_file, 'r') as file:
            for line in file:
                parts = line.strip().split(' ', 4)
                if len(parts) >= 4:
                    vulnerability = parts[0].strip('[]')
                    vuln_type = parts[1].strip('[]')
                    severity = parts[2].strip('[]')
                    url = parts[3]
                    description = parts[4].strip('[]') if len(parts) > 4 else ''
                    
                    unique_fields = {
                        "vulnerability": vulnerability,
                        "type": vuln_type,
                        "severity": severity,
                        "url": url
                    }
                    data = {
                        "vulnerability": vulnerability,
                        "type": vuln_type,
                        "severity": severity,
                        "url": url,
                        "description": description,
                        "status": "Open",
                        "date_found": datetime.now().strftime("%d-%m-%Y"),
                    }
                    save_to_mongo("vulnerabilities", unique_fields, data)
                    logger.info(f"Saved vulnerability for {url} to MongoDB")
    except IOError as e:
        logger.error(f"Failed to read or parse the file {output_file}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while saving to MongoDB: {e}")
