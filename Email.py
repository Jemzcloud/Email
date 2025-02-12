import dns.resolver
import re
import tldextract
import whois
from email import message_from_string
from email.header import decode_header

# Phishing keywords commonly used in fake emails
PHISHING_KEYWORDS = [
    "urgent", "password", "click here", "update account", 
    "verify", "lottery", "bank", "invoice", "win", "free", "confirm"
]

def check_spf(domain):
    """Check if the domain has a valid SPF record"""
    try:
        answers = dns.resolver.resolve(f'_spf.{domain}', 'TXT')
        for txt_record in answers:
            if 'v=spf1' in txt_record.to_text():
                return True
    except Exception:
        return False
    return False

def check_dkim(domain):
    """Check if the domain has a valid DKIM record"""
    try:
        dkim_selector = "default"  # This might change per provider
        dkim_domain = f"{dkim_selector}._domainkey.{domain}"
        answers = dns.resolver.resolve(dkim_domain, 'TXT')
        for txt_record in answers:
            if 'v=DKIM1' in txt_record.to_text():
                return True
    except Exception:
        return False
    return False

def check_dmarc(domain):
    """Check if the domain has a valid DMARC record"""
    try:
        dmarc_domain = f"_dmarc.{domain}"
        answers = dns.resolver.resolve(dmarc_domain, 'TXT')
        for txt_record in answers:
            if 'v=DMARC1' in txt_record.to_text():
                return True
    except Exception:
        return False
    return False

def check_domain_legitimacy(domain):
    """Check if the domain is newly registered or suspicious"""
    try:
        domain_info = whois.whois(domain)
        if domain_info.creation_date:
            return True  # If creation_date exists, it's a legitimate domain
    except Exception:
        return False  # WHOIS lookup failed (possibly a new/suspicious domain)
    return False

def extract_domain(email_address):
    """Extract domain from email address"""
    return email_address.split('@')[-1]

def check_phishing_keywords(email_body):
    """Check for phishing-related words in the email body"""
    for keyword in PHISHING_KEYWORDS:
        if keyword.lower() in email_body.lower():
            return True
    return False

def analyze_email(email_content):
    """Analyze an email and detect if it is suspicious"""
    email_msg = message_from_string(email_content)
    
    # Extract sender email
    sender = email_msg.get("From")
    if sender:
        sender_email = re.findall(r'<([^<>]+)>', sender)
        sender_email = sender_email[0] if sender_email else sender
    else:
        sender_email = "Unknown"

    # Extract domain
    domain = extract_domain(sender_email)

    # Check SPF, DKIM, DMARC
    spf_valid = check_spf(domain)
    dkim_valid = check_dkim(domain)
    dmarc_valid = check_dmarc(domain)
    
    # Check domain legitimacy
    domain_legit = check_domain_legitimacy(domain)

    # Extract email body
    email_body = ""
    if email_msg.is_multipart():
        for part in email_msg.walk():
            if part.get_content_type() == "text/plain":
                email_body += part.get_payload(decode=True).decode(errors="ignore")
    else:
        email_body = email_msg.get_payload(decode=True).decode(errors="ignore")

    # Check for phishing keywords
    phishing_detected = check_phishing_keywords(email_body)

    # Final verdict
    print(f"Sender Email: {sender_email}")
    print(f"SPF Valid: {spf_valid}")
    print(f"DKIM Valid: {dkim_valid}")
    print(f"DMARC Valid: {dmarc_valid}")
    print(f"Domain Legitimacy: {domain_legit}")
    print(f"Phishing Keywords Detected: {phishing_detected}")

    if not spf_valid or not dkim_valid or not dmarc_valid or not domain_legit or phishing_detected:
        print("\n⚠️ WARNING: This email may be FAKE or PHISHING!")
    else:
        print("\n✅ This email seems legitimate.")

# Example usage:
email_sample = """From: "Bank Support" <support@secure-bank.com>
Subject: Urgent! Verify Your Account Now

Dear customer,

We noticed unusual activity on your bank account. Please click here to verify your information immediately or your account will be suspended.

Best regards,
Bank Support Team"""

# Analyze the email
analyze_email(email_sample)
