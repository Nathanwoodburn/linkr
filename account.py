import secrets
import db
import dns.resolver
import os
import dotenv

dotenv.load_dotenv()
avatars = {}

def add_user(domain,token):
    db.add_token(token,domain)

def get_user(token):
    return db.get_token(token)

def remove_user(token):
    db.delete_token(token)

def generate_token(length=32):
    token = secrets.token_hex(length // 2)
    return token

def get_avatar(domain):
    global avatars
    if domain in avatars:
        return avatars[domain]
    else:
        avatars[domain] = lookup_avatar(domain)
        return avatars[domain]
    
def lookup_avatar(domain):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [os.getenv("DNS_SERVER")]
    resolver.port = int(os.getenv("DNS_SERVER_PORT"))
    try:
        # Query the DNS record
        response = resolver.resolve(domain, "TXT")
        for record in response:
            # If starts with profile avatar=
            record = record.to_text().replace('"','')
            if record.startswith("profile avatar="):
                # Return the URL
                return record.replace("profile avatar=","")


    except dns.resolver.NXDOMAIN:
        return "assets/img/favicon-32x32.png"
    except dns.exception.DNSException as e:
        return "assets/img/favicon-32x32.png"


    
    return "assets/img/favicon-32x32.png"