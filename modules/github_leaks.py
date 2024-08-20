import os
import re
from datetime import datetime
from utils.mongo_utils import save_to_mongo
from utils.logging_utils import setup_logger

# Set up the logger
logger = setup_logger(__name__)

def parse_trufflehog_output(file_path):
    logger.info(f"Parsing TruffleHog output from file: {file_path}")
    with open(file_path, 'r') as file:
        content = file.read()

    regex_pattern = re.compile(
        r"Detector Type:\s*(?P<detector_type>.*?)\n"
        r"Decoder Type:\s*(?P<decoder_type>.*?)\n"
        r"Raw result:\s*(?P<raw_result>.*?)\n"
        r"Commit:\s*(?P<commit>.*?)\n"
        r"Email:\s*(?P<email>.*?)\n"
        r"File:\s*(?P<file>.*?)\n"
        r"Line:\s*(?P<line>\d+)\n"
        r"Repository:\s*(?P<repository>.*?)\n"
        r"Timestamp:\s*(?P<timestamp>.*?)\n"
    )

    matches = regex_pattern.finditer(content)

    leaks = []
    for match in matches:
        leak = match.groupdict()
        leak['status'] = 'Open'
        leak['date_found'] = datetime.now().strftime("%d-%m-%y")
        leaks.append(leak)

    logger.info(f"Found {len(leaks)} leaks in TruffleHog output")
    return leaks

def save_github_leaks(leaks):
    logger.info(f"Saving {len(leaks)} GitHub leaks to MongoDB")
    for leak in leaks:
        unique_fields = {
            "detector_type": leak['detector_type'],
            "decoder_type": leak['decoder_type'],
            "raw_result": leak['raw_result'],
            "commit": leak['commit'],
            "email": leak['email'],
            "file": leak['file'],
            "line": leak['line'],
            "repository": leak['repository'],
            "timestamp": leak['timestamp']
        }
        save_to_mongo("github_leaks", unique_fields, leak)
    logger.info("GitHub leaks saved to MongoDB")

def github_leaks(github_org, output_dir):
    output_file = os.path.join(output_dir, "trufflehog_output.txt")
    command = f"trufflehog github --org={github_org} | grep -E \"(Detector Type:|Decoder Type:|Raw result:|Commit:|Email:|File:|Line:|Repository:|Timestamp:)\" | sed -r 's/\\x1B\\[[0-9;]*[mG]//g' > {output_file}"
    
    logger.info(f"Running TruffleHog command: {command}")
    os.system(command)
    logger.info(f"TruffleHog output saved to {output_file}")

    leaks = parse_trufflehog_output(output_file)
    if leaks:
        save_github_leaks(leaks)
        logger.info("GitHub leaks results saved to the database")
    else:
        logger.info("No leaks found")

if __name__ == "__main__":
    github_org = "example_org"  # Example GitHub organization
    output_dir = os.path.join(os.getcwd(), "Recon")
    os.makedirs(output_dir, exist_ok=True)

    github_leaks(github_org, output_dir)
