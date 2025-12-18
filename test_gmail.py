import os
from pathlib import Path
from dotenv import load_dotenv
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Gmail API scopes
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.send']
TOKEN_FILE = Path("token.json")
gmail_service = None

def initialize_gmail():
    """Initialize Gmail API"""
    global gmail_service
    
    try:
        creds = None
        
        # Load existing token
        if TOKEN_FILE.exists():
            print("Found existing token.json file")
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), GMAIL_SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Token expired, refreshing...")
                creds.refresh(Request())
            else:
                # Check if credentials.json exists
                if not Path("credentials.json").exists():
                    print("❌ ERROR: credentials.json not found!")
                    print("\nTo enable Gmail:")
                    print("1. Go to https://console.cloud.google.com/")
                    print("2. Create a project and enable Gmail API")
                    print("3. Create OAuth 2.0 credentials (Desktop app)")
                    print("4. Download and save as 'credentials.json' in this folder")
                    return False
                
                print("Starting OAuth flow...")
                print("Browser should open for authentication...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', GMAIL_SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            print("Saving token for future use...")
            with TOKEN_FILE.open('w') as token:
                token.write(creds.to_json())
        
        gmail_service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail API initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Gmail initialization error: {e}")
        return False


def send_email(to, subject, body):
    """Send an email via Gmail"""
    try:
        if not gmail_service:
            print("Gmail is not configured. Please run initialize_gmail() first.")
            return False
        
        print(f"\nPreparing email...")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_body = {'raw': raw}
        
        print("\nSending email...")
        result = gmail_service.users().messages().send(
            userId="me", body=message_body).execute()
        
        print(f"✅ Email sent successfully! Message ID: {result['id']}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False


def test_gmail():
    """Test Gmail functionality"""
    print("="*60)
    print("GMAIL API TEST")
    print("="*60)
    
    # Initialize
    if not initialize_gmail():
        print("\n❌ Gmail initialization failed")
        return
    
    print("\n" + "="*60)
    print("Gmail is ready!")
    print("="*60)
    
    # Ask if user wants to send a test email
    print("\nWould you like to send a test email?")
    print("Enter the recipient email (or press Enter to skip):")
    recipient = input("> ").strip()
    
    if recipient:
        print("\nEnter subject (or press Enter for default):")
        subject = input("> ").strip() or "Test Email from JARVIS"
        
        print("\nEnter message body (or press Enter for default):")
        body = input("> ").strip() or "This is a test email sent from JARVIS AI Assistant!"
        
        send_email(recipient, subject, body)
    else:
        print("\nSkipping test email. Gmail is configured and ready to use!")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    load_dotenv()
    test_gmail()