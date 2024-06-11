import os
import argparse
from modules import sub_enum, vuln_scan

def create_output_directory():
    output_dir = os.path.join(os.getcwd(), "Recon")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def process_domain(domain, output_dir):
    print(f"Running Subdomain Enumeration for {domain}...")
    amass_output = sub_enum.run_amass(domain, output_dir)
    subfinder_output = sub_enum.run_subfinder(domain, output_dir)
    print(f"Amass results saved to {amass_output}")
    print(f"Subfinder results saved to {subfinder_output}")

    combined_subdomains_file = os.path.join(output_dir, f"{domain}_all_subdomains.txt")
    with open(combined_subdomains_file, 'w') as outfile:
        for fname in [amass_output, subfinder_output]:
            with open(fname) as infile:
                outfile.write(infile.read())
    print(f"Combined subdomains saved to {combined_subdomains_file}")

    print(f"Running Vulnerability Scanning for subdomains in {combined_subdomains_file}...")
    nuclei_output = vuln_scan.run_nuclei(combined_subdomains_file, output_dir)
    print(f"Nuclei results saved to {nuclei_output}")

def main():
    parser = argparse.ArgumentParser(description='Recon script for subdomain enumeration and vulnerability scanning.')
    parser.add_argument('-t', '--target', type=str, help='Single target domain')
    parser.add_argument('-l', '--list', type=str, help='File containing list of target domains')
    args = parser.parse_args()

    output_dir = create_output_directory()

    if args.target:
        process_domain(args.target, output_dir)
    elif args.list:
        with open(args.list, 'r') as file:
            domains = [line.strip() for line in file.readlines()]
            for domain in domains:
                process_domain(domain, output_dir)
    else:
        print("Please provide a target domain with -t or a list of domains with -l.")

if __name__ == "__main__":
    main()
