import subprocess
import os
import re
import pymongo
from datetime import datetime

def get_mongo_collection():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["recon"]
    collection = db["network_scan_results"]
    return collection

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
    with open(nmap_output_file, 'r') as file:
        content = file.read()
        matches = re.findall(
            r'<host .*?>.*?<address addr="(.*?)" addrtype="ipv4"/>.*?<port protocol="(.*?)" portid="(.*?)".*?<state state="(.*?)".*?<service name="(.*?)" product="(.*?)".*?</host>',
            content, re.DOTALL
        )
        for match in matches:
            results.append({
                "ip_address": match[0],
                "protocol": match[1],
                "port": match[2],
                "state": match[3],
                "service_name": match[4],
                "product": match[5],
                "date_found": datetime.now().strftime("%d-%m-%y"),
                "age": "new"
            })
    
    return results

def save_to_mongo(results):
    collection = get_mongo_collection()
    for result in results:
        existing_result = collection.find_one({
            "ip_address": result['ip_address'],
            "protocol": result['protocol'],
            "port": result['port'],
            "service_name": result['service_name'],
            "product": result['product']
        })
        if not existing_result:
            collection.insert_one(result)
        else:
            if existing_result.get("age") == "new":
                collection.update_one(
                    {"_id": existing_result["_id"]},
                    {"$set": {"age": ""}},
                    upsert=True
                )
            collection.update_one(
                {"_id": existing_result["_id"]},
                {"$setOnInsert": result},
                upsert=True
            )

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
    
    results = parse_nmap_output(nmap_output)
    print(f"Parsed {len(results)} results from Nmap")
    
    print(f"Saving Nmap results to MongoDB for {domain}...")
    save_to_mongo(results)
    print(f"Nmap results saved to MongoDB")
