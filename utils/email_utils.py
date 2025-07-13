import dns.resolver

def domain_has_mx(email):
    domain = email.split('@')[1]
    try:
        records = dns.resolver.resolve(domain, rdtype='MX')
        return len(records) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
        return False
