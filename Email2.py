import dns.resolver
import re
import tldextract
import whois
from email import message_from_string
from email.header import decode_header

PHISHING_KEYWORDS = ["urgent", "password", "click here", "update account", "verify", "lottery", "bank", "invoice"]

def check_spf(domain):
    try:
        answers = dns.resolver.resolve(f'_spf.{domain}', 'TXT')
        for txt_record in answers:
            if 'v=spf1' in txt_record.to_text():
                return True
    except Exception:
        return False
    return False

def check_dkim(domain):
    try:
        dkim_selector = "default"
        dkim_domain = f"{dkim_selector}._domainkey.{domain}"
        answers = dns.resolver.resolve(dkim_domain, 'TXT')
        for txt_record in answers:
            if 'v=DKIM1' in txt_record.to_text():
                return True
    except Exception:
        return False
    return False

def check_dmarc(domain):
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
    try:
        domain_info = whois.whois(domain)
        if domain_info.creation_date:
            return True
    except Exception:
        return False
    return False

def extract_domain(email_address):
    return email_address.split('@')[-1]

def check_phishing_keywords(email_body):
    for keyword in PHISHING_KEYWORDS:
        if keyword.lower() in email_body.lower():
            return True
    return False

def analyze_email(email_content):
    email_msg = message_from_string(email_content)
    
    sender = email_msg.get("From")
    if sender:
        sender_email = re.findall(r'<([^<>]+)>', sender)
        sender_email = sender_email[0] if sender_email else sender
    else:
        sender_email = "Unknown"

    domain = extract_domain(sender_email)

    spf_valid = check_spf(domain)
    dkim_valid = check_dkim(domain)
    dmarc_valid = check_dmarc(domain)
    domain_legit = check_domain_legitimacy(domain)

    email_body = ""
    if email_msg.is_multipart():
        for part in email_msg.walk():
            if part.get_content_type() == "text/plain":
                email_body += part.get_payload(decode=True).decode(errors="ignore")
    else:
        email_body = email_msg.get_payload(decode=True).decode(errors="ignore")

    phishing_detected = check_phishing_keywords(email_body)

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

def read_email_from_file(file_path):
    """Read email content from a text file"""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Example usage:
if __name__ == "__main__":
    file_path = "email_sample.txt"  # Change this to the actual file path
    email_content = read_email_from_file(file_path)
    analyze_email(email_content)
