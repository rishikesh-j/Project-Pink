import subprocess
import os

def run_nuclei(target_file, output_dir):
    output_file = os.path.join(output_dir, "nuclei_results.txt")
    subprocess.run(['nuclei', '-l', target_file, '-o', output_file], check=True)
    return output_file
