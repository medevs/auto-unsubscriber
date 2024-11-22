# Auto Email Unsubscriber

An automated tool to help you unsubscribe from unwanted email subscriptions by automatically finding and visiting unsubscribe links in your Gmail inbox.

## Features

- 📧 Automatically connects to your Gmail account
- 🔍 Searches for emails containing unsubscribe links
- 🔗 Extracts unsubscribe links from HTML emails
- 🚀 Automatically visits unsubscribe links
- 💾 Saves all found links to a file for reference

## Prerequisites

- Python 3.6 or higher
- Gmail account
- Gmail App Password (if 2FA is enabled)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/medevs/auto-unsubscriber.git
cd auto-unsubscriber
```

2. Install required dependencies using the requirements.txt file:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root directory
2. Add your Gmail credentials:
```
EMAIL="your.email@gmail.com"
PASSWORD="your-password"
```

Note: If you have 2-factor authentication enabled, you'll need to use an App Password instead of your regular Gmail password. You can generate one at: https://myaccount.google.com/apppasswords

## Usage

Run the script:
```bash
python main.py
```

The script will:
1. Connect to your Gmail account
2. Search for emails containing unsubscribe links
3. Extract and visit each unsubscribe link
4. Save all found links to `links.txt`

## Output

The script creates a `links.txt` file containing all discovered unsubscribe links. Each link attempt will print its status to the console:
- Success: "Successfully visited [link]"
- Failure: "Failed to visit [link] error code [status_code]"
- Error: "Error with [link] [error message]"

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements.

## License

This project is open source and available under the MIT License.

## Disclaimer

Use this tool responsibly. Make sure you have the right to access the Gmail account you're using with this script. The author is not responsible for any misuse of this tool.