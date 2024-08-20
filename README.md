# Project Pink

![Project Pink](https://your-image-url-here)

## Summary

**Project Pink** is an all-in-one automation tool designed for comprehensive reconnaissance, subdomain enumeration, vulnerability scanning, and data extraction. It leverages a multitude of techniques including OSINT, web scraping, Google Dorks, and GitHub Dorks, ensuring that no stone is left unturned during your security assessments.

Project Pink is built to support a modular architecture, enabling easy integration with other tools and services. This makes it ideal for both individual security researchers and large teams looking to streamline their workflows.

## 📔 Table of Contents

- [Installation](#installation)
  - [Using a PC/VPS/VM](#using-a-pcvpsvm)
- [Usage](#usage)
  - [TARGET OPTIONS](#target-options)
  - [MODE OPTIONS](#mode-options)
  - [GENERAL OPTIONS](#general-options)
  - [Example Usage](#example-usage)
- [Modules](#modules)
  - [GitHub Leaks](#github-leaks)
  - [Google Dorks](#google-dorks)
  - [Network Scanning](#network-scanning)
  - [Phishing](#phishing)
  - [Postman Leaks](#postman-leaks)
  - [Shodan](#shodan)
  - [Subdomain Enumeration](#subdomain-enumeration)
  - [Vulnerability Scanning](#vulnerability-scanning)
- [Features](#features)
- [How to Contribute](#how-to-contribute)
- [License](#license)

## Installation

### Using a PC/VPS/VM

> **Prerequisites:** Ensure that Go, Python3, pip3, Docker, and Docker Compose are installed and paths are correctly set.

Clone the repository and run the installation script:

```bash
git clone https://github.com/rishikesh-j/Project-Pink.git
cd Project-Pink/
./install.sh
```

## Usage

### TARGET OPTIONS

| Flag | Description |
|------|-------------|
| -t   | Single target domain (e.g., example.com) |
| -o   | Organization name (required) |
| -l   | File containing a list of target domains |
| -g   | GitHub organization name |
| -s   | Only run Shodan module |

### Example Usage

To perform a full recon on a single target:

```bash
./project-pink.sh -t example.com -o "Example Org"
```

To perform recon on a list of targets:

```bash
./project-pink.sh -l targets.txt -o "Example Org"
```

To perform a Shodan scan only:

```bash
./project-pink.sh -o "Example Org" -s
```

## Modules

### GitHub Leaks

- **Tool Used:** trufflehog
- **Description:** Identifies sensitive information in GitHub repositories.

### Google Dorks

- **Tool Used:** Custom Google Dorking
- **Description:** Automates Google Dorks search for exposed information.

### Network Scanning

- **Tools Used:** dnsx, masscan, nmap
- **Description:** DNS enumeration and port scanning.

### Phishing

- **Tool Used:** dnstwist
- **Description:** Scans for phishing domains and permutations.

### Postman Leaks

- **Tool Used:** porch-pirate
- **Description:** Extracts exposed information from Postman workspaces.

### Shodan

- **Tool Used:** Shodan API
- **Description:** Performs Shodan searches to identify exposed services and devices.

### Subdomain Enumeration

- **Tools Used:** subfinder, gotator, httpx
- **Description:** Enumerates and verifies subdomains using multiple methods.

### Vulnerability Scanning

- **Tool Used:** nuclei
- **Description:** Scans for known vulnerabilities using predefined templates.

## Features

- Modular design for easy integration and customization.
- Automatic saving of results to MongoDB for analysis.
- Extensive use of multi-threading for faster execution.
- Supports detailed configuration for various modules.

## How to Contribute

We welcome contributions from the community! Please read our [contributing guide](CONTRIBUTING.md) for more information.

## License

Project Pink is released under the MIT License. See [LICENSE](LICENSE) for more information.
