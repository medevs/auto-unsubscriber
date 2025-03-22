"""
Auto Email Unsubscriber

This script automatically finds and clicks unsubscribe links from emails in your Gmail inbox.
It searches for emails containing "unsubscribe" text, extracts the unsubscribe links,
and attempts to visit each link to unsubscribe from the mailing lists.

Required Environment Variables:
    EMAIL: Your Gmail address
    PASSWORD: Your Gmail app password (NOT your regular password)

Note: Gmail requires an app password for this script to work.
      Get an app password at: https://myaccount.google.com/apppasswords
      (You need 2-Step Verification enabled first)

Dependencies:
    - python-dotenv
    - imaplib (standard library)
    - email (standard library)
    - beautifulsoup4
    - requests
    - tldextract
    - csv (standard library)
"""

from dotenv import load_dotenv
import imaplib
import email
import os
import sys
from bs4 import BeautifulSoup
import requests
import time
import tldextract
import csv

# Load environment variables from .env file
load_dotenv()

# Get email credentials from environment variables
username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

def check_env_variables():
    """
    Check if required environment variables are set.
    
    Returns:
        bool: True if all required variables are set, False otherwise
    """
    if not username:
        print("ERROR: EMAIL environment variable is not set in .env file")
        return False
    if not password:
        print("ERROR: PASSWORD environment variable is not set in .env file")
        return False
    return True

def connect_to_mail():
    """
    Establish a connection to Gmail using IMAP.
    
    Returns:
        imaplib.IMAP4_SSL: An authenticated IMAP connection object or None if connection fails
    """
    try:
        print(f"Connecting to Gmail as {username}...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("inbox")
        print("Successfully connected to Gmail")
        return mail
    except imaplib.IMAP4.error as e:
        error_msg = str(e)
        if "Application-specific password required" in error_msg:
            print("\nERROR: Gmail requires an app password for this script.")
            print("1. Enable 2-Step Verification: https://myaccount.google.com/security")
            print("2. Generate an app password: https://myaccount.google.com/apppasswords")
            print("3. Update your .env file with the new app password")
        else:
            print(f"\nERROR: Failed to connect to Gmail: {error_msg}")
        return None
    except Exception as e:
        print(f"\nERROR: Unexpected error connecting to Gmail: {str(e)}")
        return None

def extract_links_from_html(html_content):
    """
    Parse HTML content and extract unsubscribe links.
    
    Args:
        html_content (str): HTML content of the email
        
    Returns:
        list: List of unsubscribe URLs found in the HTML content
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        links = [link["href"] for link in soup.find_all("a", href=True) if "unsubscribe" in link["href"].lower()]
        return links
    except Exception as e:
        print(f"Error parsing HTML content: {str(e)}")
        return []

def click_link(link):
    """
    Visit an unsubscribe link and report the result.
    
    Args:
        link (str): URL to visit for unsubscription
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"Visiting: {link}")
        response = requests.get(link, timeout=10)
        if response.status_code == 200:
            print("✓ Successfully visited")
            return True
        else:
            print(f"✗ Failed with status code {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Connection error")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def extract_company_name(url):
    """
    Extract company name from URL domain
    
    Args:
        url (str): URL to extract company name from
        
    Returns:
        str: Company name
    """
    try:
        # Extract domain information
        extracted = tldextract.extract(url)
        
        # Use domain as company name, capitalize first letter
        company = extracted.domain.replace('-', ' ').replace('_', ' ')
        company = company.title()
        
        return company
    except Exception:
        return "Unknown"

def group_links_by_service(links):
    """
    Group unsubscribe links by service domain and select best candidate
    
    Args:
        links (list): List of unsubscribe URLs
        
    Returns:
        dict: Dictionary with domain as key and service info as value
    """
    service_map = {}
    
    for link in links:
        try:
            # Extract root domain using tldextract
            parsed = tldextract.extract(link)
            domain_key = f"{parsed.domain}.{parsed.suffix}"
            
            # Get company name
            company_name = extract_company_name(link)
            
            # Track best candidate per service
            if domain_key not in service_map or \
               len(link) < len(service_map[domain_key]['url']):
                service_map[domain_key] = {
                    'url': link,
                    'company': company_name,
                    'domain': domain_key,
                    'count': 1
                }
            else:
                service_map[domain_key]['count'] += 1
                
        except Exception as e:
            print(f"Error processing {link}: {str(e)}")
    
    print(f"Found {len(service_map)} unique services")
    return service_map

def search_for_email():
    """
    Search Gmail inbox for emails containing unsubscribe links.
    
    Returns:
        dict: Dictionary of unique services with their unsubscribe URLs
    """
    # Connect to Gmail and search for emails containing "unsubscribe"
    mail = connect_to_mail()
    if not mail:
        return {}
    
    try:
        print("Searching for emails with 'unsubscribe' text...")
        _, search_data = mail.search(None, '(BODY "unsubscribe")')
        data = search_data[0].split()
        
        if not data:
            print("No emails found with 'unsubscribe' text")
            mail.logout()
            return {}
            
        print(f"Found {len(data)} emails to process")
        links = []
        
        # Process each email found
        for i, num in enumerate(data):
            try:
                print(f"Processing email {i+1}/{len(data)}...", end="\r")
                _, data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                
                # Handle multipart messages (emails with both HTML and text content)
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/html":
                            try:
                                payload = part.get_payload(decode=True)
                                charset = part.get_content_charset() or 'utf-8'
                                html_content = payload.decode(charset, errors='ignore')
                                links.extend(extract_links_from_html(html_content))
                            except Exception as e:
                                print(f"\nError processing multipart message: {str(e)}")
                                continue
                else:
                    # Handle single part messages
                    content_type = msg.get_content_type()
                    if content_type == "text/html":
                        try:
                            payload = msg.get_payload(decode=True)
                            charset = msg.get_content_charset() or 'utf-8'
                            content = payload.decode(charset, errors='ignore')
                            links.extend(extract_links_from_html(content))
                        except Exception as e:
                            print(f"\nError processing single part message: {str(e)}")
                            continue
            except Exception as e:
                print(f"\nError processing email: {str(e)}")
                continue
        
        print("\nEmail processing complete")
        mail.logout()
        
        # Remove duplicates and group by service
        return group_links_by_service(list(set(links)))
        
    except Exception as e:
        print(f"Error searching for emails: {str(e)}")
        try:
            mail.logout()
        except:
            pass
        return {}

def save_links(service_map):
    """
    Save the found unsubscribe links to text and CSV files.
    
    Args:
        service_map (dict): Dictionary of services with their unsubscribe URLs
    """
    if not service_map:
        print("No links to save")
        return
    
    # Extract list of links for text file
    links = [service_info['url'] for service_info in service_map.values()]
        
    # Save to text file
    try:
        with open("unsubscribe_links.txt", "w") as f:
            f.write("\n".join(links))
        print(f"Saved {len(links)} links to unsubscribe_links.txt")
    except Exception as e:
        print(f"Error saving links to text file: {str(e)}")
    
    # Save to CSV file with company names
    try:
        # Use semicolon delimiter and add BOM for Excel compatibility
        with open("unsubscribe_services.csv", "w", newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['company', 'domain', 'url', 'emails_found']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            
            writer.writeheader()
            for service_info in service_map.values():
                writer.writerow({
                    'company': service_info['company'],
                    'domain': service_info['domain'],
                    'url': service_info['url'],
                    'emails_found': service_info['count']
                })
        print(f"Saved {len(service_map)} services to unsubscribe_services.csv")
    except Exception as e:
        print(f"Error saving to CSV file: {str(e)}")

# Main execution
if __name__ == "__main__":
    print("=" * 50)
    print("Auto Email Unsubscriber")
    print("=" * 50)
    
    # Check if environment variables are set
    if not check_env_variables():
        print("\nPlease set the required environment variables in the .env file:")
        print("EMAIL=your.email@gmail.com")
        print("PASSWORD=your-app-password")
        print("\nNote: Gmail requires an app password, not your regular password.")
        print("Get an app password at: https://myaccount.google.com/apppasswords")
        sys.exit(1)
    
    # Find all unsubscribe links
    service_map = search_for_email()
    
    if service_map:
        print("\nVisiting unsubscribe links...")
        # Visit each unsubscribe link
        success_count = 0
        for i, (domain, service_info) in enumerate(service_map.items()):
            print(f"\n[{i+1}/{len(service_map)}] {service_info['company']}", end=" ")
            if click_link(service_info['url']):
                success_count += 1
            # Add a small delay between requests to avoid being blocked
            if i < len(service_map) - 1:
                time.sleep(1)
        
        # Save links for reference
        print("\nSaving links for reference...")
        save_links(service_map)
        
        print(f"\nUnsubscribe process complete! Successfully visited {success_count}/{len(service_map)} links.")
    else:
        print("\nNo unsubscribe links found. Process complete.")