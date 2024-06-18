import os
import json
import argparse
from modules import sub_enum, vuln_scan, shodan_module

def create_output_directory():
    output_dir = os.path.join(os.getcwd(), "Recon")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def process_domain(domain, organization, output_dir, config):
    subfinder_threads = config['subfinder_threads']
    nuclei_rate_limit = config['nuclei_rate_limit']
    nuclei_threads = config['nuclei_threads']
    httpx_threads = config['httpx_threads']
    httpx_rate_limit = config['httpx_rate_limit']

    print(f"Running Subdomain Enumeration for {domain}...")
#    subfinder_output = sub_enum.run_subfinder(domain, output_dir, subfinder_threads)
#    print(f"Subfinder results saved to {subfinder_output}")

#    combined_subdomains_file = sub_enum.combine_results(domain, output_dir, subfinder_output)
#    print(f"Combined subdomains saved to {combined_subdomains_file}")

#    print(f"Running Gotator for {domain}...")
#    gotator_output = sub_enum.run_gotator(domain, combined_subdomains_file, output_dir)
#    print(f"Gotator results saved to {gotator_output}")

#    final_subdomains_file = os.path.join(output_dir, f"{domain}_final_subdomains.txt")
#    with open(final_subdomains_file, 'w') as outfile:
#        with open(combined_subdomains_file) as infile:
#            outfile.write(infile.read())
#        with open(gotator_output) as infile:
#            outfile.write(infile.read())
#    print(f"Final subdomains file saved to {final_subdomains_file}")

#    sub_enum.save_to_mongo(domain, final_subdomains_file, collection="subdomains")

#    print(f"Running Subdomain Verification for {domain}...")
#    httpx_output = sub_enum.run_httpx(domain, final_subdomains_file, output_dir, httpx_threads, httpx_rate_limit)
#    print(f"Httpx verified results saved to {httpx_output}")

    print(f"Running Shodan Dorking for organization {organization}...")
    shodan_module.search_shodan(organization, output_dir)
    print(f"Shodan results saved to the database")

    print(f"Running Vulnerability Scanning for subdomains in {httpx_output}...")
    nuclei_output = vuln_scan.run_nuclei(httpx_output, output_dir, nuclei_rate_limit, nuclei_threads)
    print(f"Nuclei results saved to {nuclei_output}")

def main():
    parser = argparse.ArgumentParser(description='Recon script for subdomain enumeration, vulnerability scanning, and Shodan dorking.')
    parser.add_argument('-t', '--target', type=str, help='Single target domain', required=True)
    parser.add_argument('-o', '--organization', type=str, help='Organization name', required=True)
    parser.add_argument('-l', '--list', type=str, help='File containing list of target domains')
    args = parser.parse_args()

    with open('config.json') as config_file:
        config = json.load(config_file)
    
    output_dir = create_output_directory()

    if args.target:
        process_domain(args.target, args.organization, output_dir, config)
    elif args.list:
        with open(args.list, 'r') as file:
            domains = [line.strip() for line in file.readlines()]
            for domain in domains:
                process_domain(domain, args.organization, output_dir, config)
    else:
        print("Please provide a target domain with -t or a list of domains with -l.")

if __name__ == "__main__":
    main()
