import subprocess
import os

def run_amass(domain, output_dir):
    output_file = os.path.join(output_dir, f"{domain}_amass.txt")
    subprocess.run(['amass', 'enum', '-d', domain, '-o', output_file], check=True)
    return output_file

def run_subfinder(domain, output_dir, threads):
    output_file = os.path.join(output_dir, f"{domain}_subfinder.txt")
    subprocess.run(['subfinder', '-d', domain, '-o', output_file, '-t', str(threads)], check=True)
    return output_file
