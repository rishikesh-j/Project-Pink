#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check if Go is installed
if ! command_exists go; then
    echo "Go is not installed. Please install Go and run this script again."
    exit 1
fi

# Check if Python 3 is installed
if ! command_exists python3; then
    echo "Python 3 is not installed. Please install Python 3 and run this script again."
    exit 1
fi

# Check if Pip3 is installed
if ! command_exists pip3; then
    echo "Pip3 is not installed. Please install Pip3 and run this script again."
    exit 1
fi

# Check if Docker is installed
if ! command_exists docker; then
    echo "Docker is not installed. Please install Docker and run this script again."
    exit 1
fi

# Check if Docker Compose is installed
if ! command_exists docker compose; then
    echo "Docker Compose is not installed. Please install Docker Compose and run this script again."
    exit 1
fi

# Function to install subfinder
install_subfinder() {
    echo "Installing subfinder..."
    GO111MODULE=on go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest &> /dev/null
}

# Function to install httpx
install_httpx() {
    echo "Installing httpx..."
    GO111MODULE=on go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest &> /dev/null
}

# Function to install nuclei
install_nuclei() {
    echo "Installing nuclei..."
    GO111MODULE=on go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest &> /dev/null
    NUCLEI_TEMPLATES_PATH=~/nuclei-templates
    git clone https://github.com/projectdiscovery/nuclei-templates $NUCLEI_TEMPLATES_PATH &> /dev/null
    git clone https://github.com/rishikesh-j/Nuclei-Templates-Scrapped.git /tmp/nuclei-templates && find /tmp/nuclei-templates/templates -type f -exec cp --parents {} ~/nuclei-templates/extra_templates/ \; && rm -rf /tmp/nuclei-templates
 &> /dev/null
    git clone https://github.com/projectdiscovery/fuzzing-templates ~/fuzzing-templates &> /dev/null
    nuclei -update-templates -update-template-dir $NUCLEI_TEMPLATES_PATH &> /dev/null
}

# Function to install gotator
install_gotator() {
    echo "Installing gotator..."
    GO111MODULE=on go install github.com/Josue87/gotator@latest &> /dev/null
}

# Function to install amass
install_amass() {
    echo "Installing amass..."
    GO111MODULE=on go install github.com/owasp-amass/amass/v4/...@master &> /dev/null
}

# Function to install dnstwist
install_dnstwist() {
    echo "Installing dnstwist..."
    sudo apt install dnstwist &> /dev/null
}

# Function to install trufflehog
install_trufflehog() {
    echo "Installing trufflehog..."
    git clone https://github.com/trufflesecurity/trufflehog.git
    cd trufflehog; go install; cd ../;
    rm -r trufflehog;
}

# Function to install porch-pirate
install_porch-pirate() {
    echo "Installing porch-pirate..."
    sudo pip3 install porch-pirate;
}

# Function to install pip dependency
install_pydependency() {
    echo "Installing Python Dependencies..."
    pip3 install shodan &> /dev/null
    pip3 install pymongo &> /dev/null
}

# Function to install dnsx
install_dnsx() {
    echo "Installing dnsx..."
    GO111MODULE=on go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest &> /dev/null
}

# Function to install masscan
install_masscan() {
    echo "Installing masscan..."
    sudo apt-get install -y masscan &> /dev/null
    sudo setcap cap_net_raw=eip $(which masscan)
}

# Function to install nmap
install_nmap() {
    echo "Installing nmap..."
    sudo apt-get install -y nmap &> /dev/null
}

# Main installation function
install_tools() {
    echo "Starting installation of tools..."

    # Install tools
    install_subfinder
    install_httpx
    install_nuclei
    install_gotator
    install_amass
    install_dnstwist
    install_trufflehog
    install_porch-pirate
    install_pydependency
    install_dnsx
    install_masscan
    install_nmap

    echo "Installation completed."
}

# Run the installation
install_tools
