#!/bin/bash

# Function to install Go
install_go() {
  echo "[*] Installing Go..."
  wget -q -O - https://git.io/vQhTU | bash
  export PATH=$HOME/.go/bin:$PATH
  source ~/.bashrc
}

# Function to install Amass
install_amass() {
  echo "[*] Installing Amass..."
  if ! command -v go &> /dev/null; then
    install_go
  fi
  go install -v github.com/owasp-amass/amass/v3/...@master
  sudo cp ~/go/bin/amass /usr/local/bin/
}

# Function to install Subfinder
install_subfinder() {
  echo "[*] Installing Subfinder..."
  if ! command -v go &> /dev/null; then
    install_go
  fi
  go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
  sudo cp ~/go/bin/subfinder /usr/local/bin/
}

# Function to install Nuclei
install_nuclei() {
  echo "[*] Installing Nuclei..."
  if ! command -v go &> /dev/null; then
    install_go
  fi
  go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
  sudo cp ~/go/bin/nuclei /usr/local/bin/

  # Setting up Nuclei templates
  NUCLEI_TEMPLATES_PATH="${HOME}/nuclei-templates"
  git clone https://github.com/projectdiscovery/nuclei-templates ${NUCLEI_TEMPLATES_PATH}
  git clone https://github.com/geeknik/the-nuclei-templates.git ${NUCLEI_TEMPLATES_PATH}/extra_templates
  git clone https://github.com/projectdiscovery/fuzzing-templates ${HOME}/fuzzing-templates

  nuclei -update-templates -update-template-dir ${NUCLEI_TEMPLATES_PATH}
}

# Main function
main() {
  # Update and install prerequisites
  echo "[*] Updating package list and installing prerequisites..."
  sudo apt-get update
  sudo apt-get install -y git python3 python3-pip

  # Install tools
  install_amass
  install_subfinder
  install_nuclei

  echo "[*] Installation complete."
}

# Execute main function
main
