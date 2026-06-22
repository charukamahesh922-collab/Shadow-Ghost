
#!/usr/bin/env python3
"""
DNS Reconnaissance Module - ShadowGhost
"""

import dns.resolver
import socket
import whois
from concurrent.futures import ThreadPoolExecutor

class DNSRecon:
    """DNS reconnaissance and subdomain enumeration"""
    
    def __init__(self, domain, timeout=10):
        self.domain = domain
        self.timeout = timeout
        self.results = {
            'records': {},
            'subdomains': [],
            'whois': {},
            'zone_transfer': False
        }
    
    def run(self):
        """Execute all DNS reconnaissance techniques"""
        print("[*] Starting DNS reconnaissance...")
        
        # Enumerate DNS records
        self._enumerate_records()
        
        # Brute force subdomains
        self._brute_force_subdomains()
        
        # Get WHOIS info
        self._get_whois()
        
        return self.results
    
    def _enumerate_records(self):
        """Enumerate all DNS record types"""
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SRV']
        
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(self.domain, rtype)
                self.results['records'][rtype] = [str(r) for r in answers]
                print(f"[+] Found {len(self.results['records'][rtype])} {rtype} records")
            except:
                self.results['records'][rtype] = []
    
    def _brute_force_subdomains(self):
        """Brute force subdomains using common wordlist"""
        common_subdomains = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp',
            'pop', 'ns1', 'webdisk', 'ns2', 'cpanel', 'whm',
            'autodiscover', 'autoconfig', 'm', 'imap', 'test',
            'ns', 'blog', 'pop3', 'dev', 'www2', 'admin',
            'forum', 'news', 'vpn', 'ns3', 'mail2', 'new',
            'mysql', 'old', 'lists', 'support', 'mobile',
            'mx', 'static', 'docs', 'beta', 'shop', 'sql',
            'secure', 'demo', 'cp', 'calendar', 'wiki',
            'web', 'media', 'email', 'images', 'img',
            'download', 'api', 'app', 'staging', 'test'
        ]
        
        found_subdomains = []
        
        def check_subdomain(sub):
            full_domain = f"{sub}.{self.domain}"
            try:
                socket.gethostbyname(full_domain)
                return full_domain
            except:
                return None
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(check_subdomain, common_subdomains)
            found_subdomains = [r for r in results if r]
        
        self.results['subdomains'] = found_subdomains
        print(f"[+] Found {len(found_subdomains)} subdomains")
    
    def _get_whois(self):
        """Get WHOIS information"""
        try:
            w = whois.whois(self.domain)
            self.results['whois'] = {
                'registrar': str(w.registrar) if w.registrar else 'Unknown',
                'creation_date': str(w.creation_date) if w.creation_date else 'Unknown',
                'expiration_date': str(w.expiration_date) if w.expiration_date else 'Unknown',
                'name_servers': w.name_servers if w.name_servers else []
            }
            print("[+] WHOIS information retrieved")
        except Exception as e:
            print(f"[-] WHOIS lookup failed: {e}")
            self.results['whois'] = {}

