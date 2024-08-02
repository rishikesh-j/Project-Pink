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
    git clone https://github.com/geeknik/the-nuclei-templates.git $NUCLEI_TEMPLATES_PATH/extra_templates &> /dev/null
    git clone https://github.com/projectdiscovery/fuzzing-templates ~/fuzzing-templates &> /dev/null
    nuclei -update-templates -update-template-dir $NUCLEI_TEMPLATES_PATH &> /dev/null
}

# Function to install gotator
install_gotator() {
    echo "Installing gotator..."
    GO111MODULE=on go install github.com/Josue87/gotator@latest &> /dev/null
    wget -O Recon/permutations_list.txt https://gist.githubusercontent.com/six2dez/ffc2b14d283e8f8eff6ac83e20a3c4b4/raw/8f9fa10e35ddc5f3ef4496b72da5c5cad3f230bf/permutations_list.txt &> /dev/null
}

# Function to install amass
install_amass() {
    echo "Installing amass..."
    GO111MODULE=on go install github.com/owasp-amass/amass/v4/...@master &> /dev/null
}

# Function to install dnstwist
install_masscan() {
    echo "Installing dnstwist..."
    sudo apt install dnstwist &> /dev/null
}

# Function to install trufflehog
install_masscan() {
    echo "Installing trufflehog..."
    git clone https://github.com/trufflesecurity/trufflehog.git
    cd trufflehog; go install; cd ../;
    rm -r trufflehog;
}

# Function to install porch-pirate
install_masscan() {
    echo "Installing porch-pirate..."
    sudo pip3 install porch-pirate;
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

# Function to clone additional nuclei template repositories
clone_additional_templates() {
    echo "Cloning additional nuclei templates..."
    EXTRA_TEMPLATES_PATH=~/nuclei-templates/extra_templates
    REPOS=(
        "https://github.com/pikpikcu/nuclei-templates"
        "https://github.com/esetal/nuclei-bb-templates"
        "https://github.com/ARPSyndicate/kenzer-templates"
        "https://github.com/medbsq/ncl"
        "https://github.com/notnotnotveg/nuclei-custom-templates"
        "https://github.com/clarkvoss/Nuclei-Templates"
        "https://github.com/z3bd/nuclei-templates"
        "https://github.com/peanuth8r/Nuclei_Templates"
        "https://github.com/thebrnwal/Content-Injection-Nuclei-Script"
        "https://github.com/ree4pwn/my-nuclei-templates"
        "https://github.com/im403/nuclei-temp"
        "https://github.com/System00-Security/backflow"
        "https://github.com/geeknik/nuclei-templates-1"
        "https://github.com/geeknik/the-nuclei-templates"
        "https://github.com/optiv/mobile-nuclei-templates"
        "https://github.com/obreinx/nuceli-templates"
        "https://github.com/randomstr1ng/nuclei-sap-templates"
        "https://github.com/CharanRayudu/Custom-Nuclei-Templates"
        "https://github.com/n1f2c3/mytemplates"
        "https://github.com/kabilan1290/templates"
        "https://github.com/smaranchand/nuclei-templates"
        "https://github.com/Saimonkabir/Nuclei-Templates"
        "https://github.com/yavolo/nuclei-templates"
        "https://github.com/sadnansakin/my-nuclei-templates"
        "https://github.com/5cr1pt/templates"
        "https://github.com/rahulkadavil/nuclei-templates"
        "https://github.com/shifa123/detections"
        "https://github.com/daffainfo/my-nuclei-templates"
        "https://github.com/javaongsan/nuclei-templates"
        "https://github.com/AshiqurEmon/nuclei_templates"
        "https://gist.github.com/ResistanceIsUseless/e46848f67706a8aa1205c9d2866bff31"
        "https://github.com/NitinYadav00/My-Nuclei-Templates"
        "https://github.com/sharathkramadas/k8s-nuclei-templates"
        "https://github.com/securitytest3r/nuclei_templates_work"
        "https://github.com/MR-pentestGuy/nuclei-templates"
        "https://github.com/thelabda/nuclei-templates"
        "https://github.com/1in9e/my-nuclei-templates"
        "https://github.com/redteambrasil/nuclei-templates"
        "https://github.com/Saptak9983/Nuclei-Template"
        "https://github.com/Harish4948/Nuclei-Templates"
    )

    mkdir -p $EXTRA_TEMPLATES_PATH
    for repo in "${REPOS[@]}"; do
        repo_name=$(basename "$repo")
        git clone "$repo" "/tmp/$repo_name" &> /dev/null
        find "/tmp/$repo_name" -name "*.yaml" -exec cp {} $EXTRA_TEMPLATES_PATH \;
        rm -rf "/tmp/$repo_name"
    done
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
    install_dnsx
    install_masscan
    install_nmap
#    clone_additional_templates

    echo "Installation completed."
}

# Run the installation
install_tools
