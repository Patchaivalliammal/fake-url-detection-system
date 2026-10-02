
import re
import ipaddress
from urllib.parse import urlparse


SUSPICIOUS_KEYWORDS = [
    "login",
    "verify",
    "account",
    "secure",
    "update",
    "banking",
    "password",
    "signin",
    "confirm",
    "wallet"
]


def extract_features(url):

    if not isinstance(url, str) or not url.strip():
        raise ValueError("Please provide a valid URL.")

    url = url.strip()

    # Add scheme if missing
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "http://" + url

    parsed_url = urlparse(url)

    hostname = parsed_url.hostname or ""
    path = parsed_url.path or ""
    query = parsed_url.query or ""

    # Check whether hostname is an IP address
    try:
        ipaddress.ip_address(hostname)
        has_ip = 1
    except ValueError:
        has_ip = 0

    # Count suspicious keywords
    suspicious_count = sum(
        keyword in url.lower()
        for keyword in SUSPICIOUS_KEYWORDS
    )

    # Extract URL features
    features = {
        "url_length": len(url),
        "hostname_length": len(hostname),
        "path_length": len(path),
        "query_length": len(query),
        "dot_count": url.count("."),
        "hyphen_count": url.count("-"),
        "at_count": url.count("@"),
        "question_count": url.count("?"),
        "equal_count": url.count("="),
        "slash_count": url.count("/"),
        "https": 1 if parsed_url.scheme == "https" else 0,
        "has_ip": has_ip,
        "suspicious_keyword_count": suspicious_count,
        "subdomain_count": max(0, len(hostname.split(".")) - 2),
        "has_port": 1 if parsed_url.port else 0,
        "has_shortening_service": 1 if any(
            service in hostname.lower()
            for service in [
                "bit.ly",
                "tinyurl.com",
                "t.co",
                "is.gd",
                "ow.ly"
            ]
        ) else 0
    }

    return features
