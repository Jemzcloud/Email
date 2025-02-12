import re

def is_phishing_email(email_content):
    # Common phishing indicators
    suspicious_keywords = [
        "urgent", "verify", "account", "password", "login", "bank", "paypal",
        "security", "update", "suspended", "limited", "immediately"
    ]
    
    suspicious_domains = [
        "freegiftcards.com", "claimprize.net", "secureupdate.org"
    ]
    
    # Check for suspicious keywords
    for keyword in suspicious_keywords:
        if re.search(fr'\b{keyword}\b', email_content, re.IGNORECASE):
            print(f"Suspicious keyword found: {keyword}")
            return True
    
    # Check for suspicious links
    links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', email_content)
    for link in links:
        for domain in suspicious_domains:
            if domain in link:
                print(f"Suspicious link found: {link}")
                return True
    
    # Check for mismatched sender and links
    sender_match = re.search(r'From:.*<.*@(.*)>', email_content)
    if sender_match:
        sender_domain = sender_match.group(1)
        for link in links:
            if sender_domain not in link:
                print(f"Mismatch between sender domain and link domain: {sender_domain} vs {link}")
                return True
    
    # If no suspicious indicators found
    print("No phishing indicators detected.")
    return False

# Example email content
email_content = """
From: support@yourbank.com
Subject: Urgent: Verify Your Account

Dear Customer,

We have detected unusual activity on your account. Please verify your login details immediately by clicking the link below:

http://secureupdate.org/login

Thank you,
Your Bank Team
"""

# Check if the email is phishing
if is_phishing_email(email_content):
    print("This email is likely a phishing attempt.")
else:
    print("This email seems safe.")
