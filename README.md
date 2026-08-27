# DEV-786: Automation Script – Domain/SSL Certificate Checker

## Overview
This repository contains a standalone Python automation script designed to verify the validity of domain/SSL certificates. It connects directly to the specified domain(s), retrieves the peer certificate, and performs essential checks to ensure service continuity and security compliance. 

The script reports the remaining time until expiration and important metadata such as the issuer, domain name, and exact expiry date.

## Features
- **Zero Dependencies:** Built entirely using Python 3's standard library (`socket`, `ssl`, `datetime`, `argparse`, `csv`).
- **Comprehensive Verification:** Distinguishes between valid and invalid certificates, and safely catches hostname mismatches, DNS failures, and expired chains.
- **Detailed Reporting:** Calculates the exact number of days remaining before expiration.
- **Bulk Processing:** Accepts a file containing multiple domains for bulk checking.
- **CSV Export:** Option to write formatted results into a CSV file for automated monitoring and integrations.

## Prerequisites
- Python 3.7+ (Windows, macOS, or Linux)
- *Optional:* VirtualBox and Vagrant (if using the local Vagrant testing environment).

## Usage

### 1. Single or Multiple Domains via CLI
Test individual domains directly from the command line:
```bash
python check_ssl.py google.com expired.badssl.com
```

### 2. Bulk Processing via File
If you have a file named `domains.txt` with one domain per line:
```bash
python check_ssl.py -f domains.txt -o results.csv
```
*This will display a well-formatted table in the terminal and save the output to `results.csv`.*

## Local Testing Environment (Vagrant)
A lightweight Vagrant environment is included to test the script consistently across environments.

1. **Spin up the VM:**
   ```bash
   vagrant up
   ```
2. **SSH into the VM:**
   ```bash
   vagrant ssh
   ```
3. **Run the script:**
   ```bash
   cd /vagrant
   python3 check_ssl.py -f domains.txt -o results_vm.csv
   ```

## Directory Structure
- `check_ssl.py`: Core automation script for SSL verification.
- `domains.txt`: Sample list of popular domains for testing purposes.
- `Vagrantfile`: Configuration for the local testing Ubuntu VM.
- `Screenshots/`: Contains visual documentation of the script executing on Windows PowerShell and inside the Vagrant VM.
