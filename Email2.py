import dns.resolver
import re
import whois
from email import message_from_string

# List of common phishing keywords
PHISHING_KEYWORDS = [
    "urgent", "password", "click here", "update account", "verify", "lottery", 
    "bank", "invoice", "suspended", "limited", "security alert", "confirm your account"
]

# List of suspicious domains (can be expanded)
SUSPICIOUS_DOMAINS = [
    "freegiftcards.com", "claimprize.net", "secureupdate.org", "accountverify.net"
]

def check_spf(domain):
    """Check if the domain has a valid SPF record."""
    try:
        answers = dns.resolver.resolve(f'_spf.{domain}', 'TXT')
        for txt_record in answers:
            if 'v=spf1' in txt_record.to_text():
                return True
    except Exception:
        return False
    return False

def check_dkim(domain, selector="default"):
    """Check if the domain has a valid DKIM record."""
    try:
        dkim_domain = f"{selector}._domainkey.{domain}"
        answers = dns.resolver.resolve(dkim_domain, 'TXT')
        for txt_record in answers:
            if 'v=DKIM1' in txt_record.to_text():
                return True
    except Exception:
        return False
    return False

def check_dmarc(domain):
    """Check if the domain has a valid DMARC record."""
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
    """Check if the domain is legitimate using WHOIS."""
    try:
        domain_info = whois.whois(domain)
        if domain_info.creation_date:
            return True
    except Exception:
        return False
    return False

def extract_domain(email_address):
    """Extract the domain from an email address."""
    return email_address.split('@')[-1]

def check_phishing_keywords(email_body):
    """Check for phishing-related keywords in the email body."""
    for keyword in PHISHING_KEYWORDS:
        if re.search(fr'\b{keyword}\b', email_body, re.IGNORECASE):
            return True
    return False

def check_suspicious_links(email_body, domain):
    """Check for suspicious links in the email body."""
    links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', email_body)
    for link in links:
        if domain not in link:
            for suspicious_domain in SUSPICIOUS_DOMAINS:
                if suspicious_domain in link:
                    return True
    return False

def analyze_email(email_content):
    """Analyze the email for phishing indicators."""
    email_msg = message_from_string(email_content)
    
    # Extract sender email
    sender = email_msg.get("From")
    sender_email = re.findall(r'<([^<>]+)>', sender)[0] if re.findall(r'<([^<>]+)>', sender) else sender
    
    # Extract domain
    domain = extract_domain(sender_email)
    
    # Perform checks
    spf_valid = check_spf(domain)
    dkim_valid = check_dkim(domain)
    dmarc_valid = check_dmarc(domain)
    domain_legit = check_domain_legitimacy(domain)
    
    # Extract email body
    email_body = ""
    if email_msg.is_multipart():
        for part in email_msg.walk():
            if part.get_content_type() == "text/plain":
                email_body += part.get_payload(decode=True).decode(errors="ignore")
    else:
        email_body = email_msg.get_payload(decode=True).decode(errors="ignore")
    
    # Check for phishing keywords and suspicious links
    phishing_detected = check_phishing_keywords(email_body)
    suspicious_links_detected = check_suspicious_links(email_body, domain)
    
    # Print results
    print(f"Sender Email: {sender_email}")
    print(f"Domain: {domain}")
    print(f"SPF Valid: {spf_valid}")
    print(f"DKIM Valid: {dkim_valid}")
    print(f"DMARC Valid: {dmarc_valid}")
    print(f"Domain Legitimacy: {domain_legit}")
    print(f"Phishing Keywords Detected: {phishing_detected}")
    print(f"Suspicious Links Detected: {suspicious_links_detected}")
    
    # Final verdict
    if not spf_valid or not dkim_valid or not dmarc_valid or not domain_legit or phishing_detected or suspicious_links_detected:
        print("\n⚠️ WARNING: This email may be FAKE or PHISHING!")
    else:
        print("\n✅ This email seems legitimate.")

def read_email_from_file(file_path):
    """Read email content from a text file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Example usage
if __name__ == "__main__":
    file_path = "email_sample.txt"  # Replace with your email file path
    email_content = read_email_from_file(file_path)
    analyze_email(email_content)
