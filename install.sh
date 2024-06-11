#!/bin/bash

# Function to install Go
install_go() {
  echo "[*] Installing Go..."
  bash <(curl -sL https://git.io/go-installer) &> /dev/null
}

# Function to install Subfinder
install_subfinder() {
  echo "[*] Installing Subfinder..."
  go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest &> /dev/null
  sudo cp -f ~/go/bin/subfinder /usr/local/bin/
}

# Function to install Nuclei
install_nuclei() {
  echo "[*] Installing Nuclei..."
  go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest &> /dev/null
  sudo cp -f ~/go/bin/nuclei /usr/local/bin/

  # Setting up Nuclei templates
  NUCLEI_TEMPLATES_PATH="${HOME}/nuclei-templates"
  rm -rf ${NUCLEI_TEMPLATES_PATH}  # Remove existing templates
  git clone https://github.com/projectdiscovery/nuclei-templates ${NUCLEI_TEMPLATES_PATH} &> /dev/null
  git clone https://github.com/geeknik/the-nuclei-templates.git ${NUCLEI_TEMPLATES_PATH}/extra_templates &> /dev/null
  git clone https://github.com/projectdiscovery/fuzzing-templates ${HOME}/fuzzing-templates &> /dev/null

  nuclei -update-templates -update-template-dir ${NUCLEI_TEMPLATES_PATH} &> /dev/null
}

# Main function
main() {
  # Update and install prerequisites
  echo "[*] Updating package list and installing prerequisites..."
  sudo apt-get update -y &> /dev/null
  sudo apt-get install -y git python3 python3-pip &> /dev/null

  # Install Go
  install_go

  # Install tools
  install_subfinder
  install_nuclei

  echo "[*] Installation complete."
}

# Execute main function
main
