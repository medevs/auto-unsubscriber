# Auto Email Unsubscriber

An automated tool to help you unsubscribe from unwanted email subscriptions by automatically finding and visiting unsubscribe links in your Gmail inbox.

## Features

- 📧 Automatically connects to your Gmail account
- 🔍 Searches for emails containing unsubscribe links
- 🔗 Extracts unsubscribe links from HTML emails
- 🚀 Automatically visits unsubscribe links
- 🔄 Groups links by service/company to prevent duplicates
- 📊 Exports company names and links to CSV file
- 📝 Saves all found links to text file for reference
- ✅ Shows success/failure statistics for unsubscribe attempts

## Prerequisites

- Python 3.6 or higher
- Gmail account
- Gmail App Password (if 2FA is enabled)
- Required Python packages:
  - python-dotenv
  - beautifulsoup4
  - requests
  - tldextract

## Installation

1. Clone the repository:
```bash
git clone https://github.com/medevs/auto-unsubscriber.git
cd auto-unsubscriber
```

2. Install required dependencies:
```bash
pip install python-dotenv beautifulsoup4 requests tldextract
```

## Configuration

1. Create a `.env` file in the project root directory
2. Add your Gmail credentials:
```
EMAIL="your.email@gmail.com"
PASSWORD="your-app-password"
```

**Important**: You must use an App Password, not your regular Gmail password. Gmail requires this for security reasons.

To generate an App Password:
1. Enable 2-Step Verification: https://myaccount.google.com/security
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the generated password in your `.env` file

## Usage

Run the script:
```bash
python main.py
```

The script will:
1. Connect to your Gmail account
2. Search for emails containing unsubscribe links
3. Group links by service/company domain
4. Visit one unsubscribe link per service
5. Save results to both text and CSV files

## Output Files

The script generates two output files:

1. `unsubscribe_links.txt`: Contains all discovered unsubscribe links (one per line)
2. `unsubscribe_services.csv`: Contains structured data with:
   - Company name (extracted from domain)
   - Domain
   - Unsubscribe URL
   - Number of emails found from that service

## Console Output

The script provides detailed console output:
- Connection status to Gmail
- Number of emails found and processed
- Number of unique services identified
- Progress of visiting each unsubscribe link
- Success/failure status for each link
- Summary statistics after completion

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements.

## License

This project is open source and available under the MIT License.

## Disclaimer

Use this tool responsibly. Make sure you have the right to access the Gmail account you're using with this script. The author is not responsible for any misuse of this tool.