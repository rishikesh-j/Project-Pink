import os
import json
import argparse
from modules import sub_enum, vuln_scan

def create_output_directory():
    output_dir = os.path.join(os.getcwd(), "Recon")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def process_domain(domain, output_dir, subfinder_threads, nuclei_rate_limit, nuclei_threads, httpx_threads, httpx_rate_limit):
    print(f"Running Subdomain Enumeration for {domain}...")
    subfinder_output = sub_enum.run_subfinder(domain, output_dir, subfinder_threads)
    print(f"Subfinder results saved to {subfinder_output}")

    combined_subdomains_file = os.path.join(output_dir, f"{domain}_all_subdomains.txt")
    with open(combined_subdomains_file, 'w') as outfile:
        with open(subfinder_output) as infile:
            outfile.write(infile.read())
    print(f"Combined subdomains saved to {combined_subdomains_file}")

    print(f"Running Subdomain Verification for {domain}...")
    httpx_output = sub_enum.run_httpx(domain, combined_subdomains_file, output_dir, httpx_threads, httpx_rate_limit)
    print(f"Httpx verified results saved to {httpx_output}")

    print(f"Running Vulnerability Scanning for subdomains in {httpx_output}...")
    nuclei_output = vuln_scan.run_nuclei(httpx_output, output_dir, nuclei_rate_limit, nuclei_threads)
    print(f"Nuclei results saved to {nuclei_output}")

def main():
    parser = argparse.ArgumentParser(description='Recon script for subdomain enumeration and vulnerability scanning.')
    parser.add_argument('-t', '--target', type=str, help='Single target domain')
    parser.add_argument('-l', '--list', type=str, help='File containing list of target domains')
    args = parser.parse_args()

    with open('config.json') as config_file:
        config = json.load(config_file)
    
    subfinder_threads = config.get('subfinder_threads', 10)
    nuclei_rate_limit = config.get('nuclei_rate_limit', 20)
    nuclei_threads = config.get('nuclei_threads', 5)
    httpx_threads = config.get('httpx_threads', 50)
    httpx_rate_limit = config.get('httpx_rate_limit', 150)
    output_dir = create_output_directory()

    if args.target:
        process_domain(args.target, output_dir, subfinder_threads, nuclei_rate_limit, nuclei_threads, httpx_threads, httpx_rate_limit)
    elif args.list:
        with open(args.list, 'r') as file:
            domains = [line.strip() for line in file.readlines()]
            for domain in domains:
                process_domain(domain, output_dir, subfinder_threads, nuclei_rate_limit, nuclei_threads, httpx_threads, httpx_rate_limit)
    else:
        print("Please provide a target domain with -t or a list of domains with -l.")

if __name__ == "__main__":
    main()
