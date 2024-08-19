import subprocess
import os
import re
import json
from datetime import datetime
from utils.mongo_utils import save_to_mongo
import xml.etree.ElementTree as ET

def run_dnsx(input_file, output_dir, threads):
    dnsx_output_file = os.path.join(output_dir, "dnsx.txt")
    grep_output_file = os.path.join(output_dir, "grep_dnsx_ip.txt")
    
    # Run dnsx command
    subprocess.run([
        'dnsx', '-silent', '-a', '-resp', '-t', str(threads), '-l', input_file, '-o', dnsx_output_file
    ], check=True)
    
    # Extract IPs
    with open(grep_output_file, 'w') as output_file:
        subprocess.run([
            'grep', '-oE', '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', dnsx_output_file
        ], stdout=output_file, check=True)
    
    return grep_output_file

def run_masscan(input_file, output_dir):
    masscan_output_file = os.path.join(output_dir, "masscan.xml")
    
    # Run masscan command
    subprocess.run([
        'masscan', '-p', '1-65535', '--rate', '100000', '--wait', '0', '--open', '-iL', input_file, '-oX', masscan_output_file
    ], check=True)
    
    return masscan_output_file

def parse_masscan_output(masscan_output_file):
    ports = set()
    with open(masscan_output_file, 'r') as file:
        content = file.read()
        ports.update(re.findall(r'portid="(\d+)"', content))
    
    return ','.join(sorted(ports))

def run_nmap(input_file, ports, output_dir):
    nmap_output_file = os.path.join(output_dir, "nmap.xml")
    
    # Run nmap command
    subprocess.run([
        'nmap', '-sV', '-p', ports, '--open', '-v', '-Pn', '-n', '-T4', '--min-rate', '1000', '--max-rate', '10000', '-iL', input_file, '-oX', nmap_output_file
    ], check=True)
    
    return nmap_output_file

def parse_nmap_output(nmap_output_file):
    results = []
    tree = ET.parse(nmap_output_file)
    root = tree.getroot()

    for host in root.findall('host'):
        ip_address = host.find('address').attrib['addr']
        for port in host.findall('ports/port'):
            protocol = port.attrib['protocol']
            portid = port.attrib['portid']
            state = port.find('state').attrib['state']
            service = port.find('service')
            service_name = service.attrib.get('name', '')
            product = service.attrib.get('product', '')

            results.append({
                "ip_address": ip_address,
                "protocol": protocol,
                "port": portid,
                "state": state,
                "service_name": service_name,
                "product": product,
                "date_found": datetime.now().strftime("%d-%m-%y"),
                "status": "Open"  # Default status
            })

    return results

def save_results_locally(results, output_dir):
    output_file = os.path.join(output_dir, "parsed_results.json")
    with open(output_file, 'w') as file:
        json.dump(results, file, indent=4)
    print(f"Results saved locally to {output_file}")

def save_to_mongo_network_scan(results):
    for result in results:
        unique_fields = {
            "ip_address": result['ip_address'],
            "protocol": result['protocol'],
            "port": result['port'],
            "service_name": result['service_name'],
            "product": result['product']
        }
        save_to_mongo("network_scan_results", unique_fields, result)

def network_scan(domain, output_dir, config):
    input_file = os.path.join(output_dir, f"{domain}_final_subdomains.txt")
    threads = config['dnsx_threads']
    
    print(f"Running DNSX for {domain}...")
    dnsx_output = run_dnsx(input_file, output_dir, threads)
    print(f"DNSX results saved to {dnsx_output}")
    
    print(f"Running Masscan for {domain}...")
    masscan_output = run_masscan(dnsx_output, output_dir)
    print(f"Masscan results saved to {masscan_output}")
    
    ports = parse_masscan_output(masscan_output)
    print(f"Open ports: {ports}")
    
    print(f"Running Nmap for {domain}...")
    nmap_output = run_nmap(dnsx_output, ports, output_dir)
    print(f"Nmap results saved to {nmap_output}")
    
    print(f"Parsing Nmap results from {nmap_output}...")
    results = parse_nmap_output(nmap_output)
    print(f"Parsed {len(results)} results from Nmap")
    
    print(f"Saving results locally for debugging...")
    save_results_locally(results, output_dir)
    
    print(f"Saving Nmap results to MongoDB for {domain}...")
    save_to_mongo_network_scan(results)
    print(f"Nmap results saved to MongoDB")

if __name__ == "__main__":
    config_file_path = 'config.json'
    with open(config_file_path) as config_file:
        config = json.load(config_file)

    domain = "nykaaman.com"  # Example domain
    output_dir = os.path.join(os.getcwd(), "Recon")
    os.makedirs(output_dir, exist_ok=True)

    network_scan(domain, output_dir, config)
