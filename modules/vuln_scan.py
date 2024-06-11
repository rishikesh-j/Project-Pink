import subprocess
import os

def run_nuclei(target_file, output_dir, rate_limit, threads):
    output_file = os.path.join(output_dir, "nuclei_results.txt")
    subprocess.run(['nuclei', '-silent', '-retries', '3', '-rl', str(rate_limit), '-c', str(threads), '-l', target_file, '-o', output_file], check=True)
    return output_file
