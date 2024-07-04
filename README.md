# Project Pink - An Inhouse ASM

## Overview

Project Pink is a comprehensive reconnaissance automation script designed to streamline the process of subdomain enumeration, vulnerability scanning, Shodan dorking, phishing domain detection, Postman leaks detection, and GitHub leaks detection. The script leverages various open-source tools to automate these tasks and stores the results in a MongoDB database.

## Features

1. **Subdomain Enumeration**
   - Uses Subfinder and Gotator for extensive subdomain enumeration.
   - Verifies subdomains using Httpx.

2. **Vulnerability Scanning**
   - Employs Nuclei to scan verified subdomains for vulnerabilities.

3. **Shodan Dorking**
   - Searches Shodan for exposed services and devices associated with the given organization.

4. **Phishing Domain Detection**
   - Uses Dnstwist to detect potential phishing domains.

5. **Postman Leaks Detection**
   - Utilizes Porch Pirate to find potential API leaks in Postman collections.

6. **GitHub Leaks Detection**
   - Leverages TruffleHog to find secrets and sensitive information in GitHub repositories.

## Prerequisites

- Python 3.x
- MongoDB
- Go environment
- Various tools (Subfinder, Gotator, Httpx, Nuclei, Shodan, Dnstwist, Porch Pirate, TruffleHog)

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/Project-Pink.git
   cd Project-Pink
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Go and Go Tools**
   - Follow the installation guide for Go from [golang.org](https://golang.org/doc/install).
   - Install required Go tools:
     ```bash
     go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
     go install -v github.com/tomnomnom/httprobe@latest
     ```

4. **Configure MongoDB**
   - Ensure MongoDB is installed and running.
   - Update `config.json` with the appropriate MongoDB connection string.

5. **Install and Configure Other Tools**
   - Install Nuclei, Dnstwist, Porch Pirate, and TruffleHog as per their respective documentation.

## Configuration

Update the `config.json` file with the necessary configurations:

```json
{
  "subfinder_threads": 10,
  "nuclei_rate_limit": 20,
  "nuclei_threads": 5,
  "httpx_threads": 10,
  "httpx_rate_limit": 20,
  "shodan_api_key": "YOUR_SHODAN_API_KEY"
}
```

## Usage

### General Usage

```bash
python main.py -t <target_domain> -o <organization_name> [-g <github_org>]
```

### Running Specific Modules

#### Only Shodan Module

```bash
python main.py -s -o <organization_name>
```

#### Using a List of Domains

```bash
python main.py -l <list_of_domains.txt> -o <organization_name> [-g <github_org>]
```

## Modules

### Subdomain Enumeration

- Combines results from Subfinder and Gotator.
- Verifies subdomains using Httpx.

### Vulnerability Scanning

- Scans verified subdomains for vulnerabilities using Nuclei.
- Saves results to MongoDB, avoiding duplicates.

### Shodan Dorking

- Searches Shodan for exposed services associated with the organization.
- Saves results to MongoDB, avoiding duplicates and preserving the status field.

### Phishing Domain Detection

- Uses Dnstwist to detect potential phishing domains.
- Saves results to MongoDB, avoiding duplicates.

### Postman Leaks Detection

- Uses Porch Pirate to find potential API leaks in Postman collections.
- Saves results to MongoDB, avoiding duplicates and preserving the status field.

### GitHub Leaks Detection

- Uses TruffleHog to find secrets in GitHub repositories.
- Saves results to MongoDB, avoiding duplicates and preserving the status field.

## Debugging

For debugging purposes, you can add print statements or use logging to trace issues.

## Contribution

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Happy Reconnaissance! 🎯
