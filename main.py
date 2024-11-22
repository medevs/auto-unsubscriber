"""
Auto Email Unsubscriber

This script automatically finds and clicks unsubscribe links from emails in your Gmail inbox.
It searches for emails containing "unsubscribe" text, extracts the unsubscribe links,
and attempts to visit each link to unsubscribe from the mailing lists.

Required Environment Variables:
    EMAIL: Your Gmail address
    PASSWORD: Your Gmail app password or account password

Dependencies:
    - python-dotenv
    - imaplib (standard library)
    - email (standard library)
    - beautifulsoup4
    - requests
"""

from dotenv import load_dotenv
import imaplib
import email
import os
from bs4 import BeautifulSoup
import requests

# Load environment variables from .env file
load_dotenv()

# Get email credentials from environment variables
username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

def connect_to_mail():
    """
    Establish a connection to Gmail using IMAP.
    
    Returns:
        imaplib.IMAP4_SSL: An authenticated IMAP connection object
    """
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")
    return mail

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
    """
    try:
        response = requests.get(link)
        if response.status_code == 200:
            print("Successfully visited", link)
        else:
            print("Failed to visit", link, "error code", response.status_code)
    except Exception as e:
        print("Error with", link, str(e))

def search_for_email():
    """
    Search Gmail inbox for emails containing unsubscribe links.
    
    Returns:
        list: List of unique unsubscribe URLs found in emails
    """
    # Connect to Gmail and search for emails containing "unsubscribe"
    mail = connect_to_mail()
    _, search_data = mail.search(None, '(BODY "unsubscribe")')
    data = search_data[0].split()
    
    links = []
    
    # Process each email found
    for num in data:
        try:
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
                            print(f"Error processing multipart message: {str(e)}")
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
                        print(f"Error processing single part message: {str(e)}")
                        continue
        except Exception as e:
            print(f"Error processing email: {str(e)}")
            continue
    
    mail.logout()
    # Remove duplicates and return
    return list(set(links))

def save_links(links):
    """
    Save the found unsubscribe links to a text file.
    
    Args:
        links (list): List of unsubscribe URLs to save
    """
    with open("links.txt", "w") as f:
        f.write("\n".join(links)) 

# Main execution
if __name__ == "__main__":
    # Find all unsubscribe links
    links = search_for_email()
    
    # Visit each unsubscribe link
    for link in links:
        click_link(link)
    
    # Save links for reference
    save_links(links)