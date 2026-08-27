import socket
import ssl
import datetime
import argparse
import csv
import sys
from urllib.parse import urlparse

def check_ssl_cert(domain, port=443, timeout=5):
    """
    Checks the SSL certificate of a domain and returns its validity, expiry date, and issuer.
    """
    context = ssl.create_default_context()
    
    result = {
        'domain': domain,
        'is_valid': False,
        'days_remaining': 0,
        'expiry_date': '',
        'issuer': '',
        'error': ''
    }
    
    try:
        with socket.create_connection((domain, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                not_after_str = cert.get('notAfter')
                # Parse the expiry date format: 'Aug 25 23:59:59 2026 GMT'
                expiry_date = datetime.datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
                
                # Calculate remaining days
                current_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                days_remaining = (expiry_date - current_time).days
                
                # Get the issuer organization or common name
                issuer_dict = dict(x[0] for x in cert.get('issuer', []))
                issuer = issuer_dict.get('organizationName', issuer_dict.get('commonName', 'Unknown'))
                
                result['is_valid'] = days_remaining > 0
                result['days_remaining'] = days_remaining
                result['expiry_date'] = expiry_date.strftime('%Y-%m-%d %H:%M:%S')
                result['issuer'] = issuer
                
    except ssl.SSLCertVerificationError as e:
        result['error'] = f'Verification Error: {e.verify_message}'
    except socket.timeout:
        result['error'] = 'Connection timed out'
    except socket.gaierror:
        result['error'] = 'DNS resolution failed'
    except Exception as e:
        result['error'] = str(e)
        
    return result

def main():
    parser = argparse.ArgumentParser(description="Automated Domain/SSL Certificate Checker")
    parser.add_argument("domains", nargs='*', help="List of domains to check (e.g., google.com)")
    parser.add_argument("-f", "--file", help="File containing a list of domains (one per line)")
    parser.add_argument("-o", "--output", help="Optional path to output the results as a CSV file")
    
    args = parser.parse_args()
    
    domains_to_check = []
    
    # Add domains from arguments
    if args.domains:
        domains_to_check.extend(args.domains)
        
    # Add domains from file
    if args.file:
        try:
            with open(args.file, 'r') as f:
                domains_to_check.extend([line.strip() for line in f if line.strip()])
        except Exception as e:
            print(f"Error reading file {args.file}: {e}")
            sys.exit(1)
            
    if not domains_to_check:
        print("Error: Please provide domains to check via arguments or a file.")
        parser.print_help()
        sys.exit(1)
        
    results = []
    
    # Print the table header
    header_format = "{:<30} | {:<10} | {:<10} | {:<20} | {}"
    print(header_format.format('Domain', 'Status', 'Days Left', 'Expiry Date', 'Issuer/Error'))
    print("-" * 105)
    
    for url in domains_to_check:
        # Clean up the domain (in case the user accidentally inputs http:// or paths)
        domain = urlparse(url).netloc if url.startswith('http') else url.split('/')[0]
        
        res = check_ssl_cert(domain)
        results.append(res)
        
        # Formatting for the terminal display
        status = "VALID" if res['is_valid'] else "INVALID"
        if res['error']:
            status = "ERROR"
            
        days = str(res['days_remaining']) if not res['error'] else "-"
        expiry = res['expiry_date'] if res['expiry_date'] else "N/A"
        
        # Combine issuer and error into a single column for readability
        issuer_or_error = res['issuer'] if res['issuer'] else res['error']
        
        print(header_format.format(domain[:30], status, days, expiry, issuer_or_error[:40]))
        
    # Handle CSV export
    if args.output:
        keys = ['domain', 'is_valid', 'days_remaining', 'expiry_date', 'issuer', 'error']
        try:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)
            print(f"\n[+] Results successfully saved to {args.output}")
        except Exception as e:
            print(f"\n[-] Error writing to CSV: {e}")

if __name__ == '__main__':
    main()
