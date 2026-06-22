
#!/usr/bin/env python3
"""
OSINT Gathering Module - ShadowGhost
"""

import requests
import json
from urllib.parse import urlparse
import socket

class OSINTGatherer:
    """OSINT data gathering from public sources"""
    
    def __init__(self, domain, timeout=10):
        self.domain = domain
        self.timeout = timeout
        self.results = {}
    
    def gather(self):
        """Gather OSINT data from various sources"""
        print("[*] Gathering OSINT data...")
        
        # Get IP information
        self._get_ip_info()
        
        # Get SSL/TLS info
        self._get_ssl_info()
        
        # Check security headers
        self._check_security_headers()
        
        return self.results
    
    def _get_ip_info(self):
        """Get IP address information"""
        try:
            ip = socket.gethostbyname(self.domain)
            self.results['ip'] = ip
            
            # Try to get geolocation info
            try:
                response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.results['geolocation'] = {
                        'country': data.get('country', 'Unknown'),
                        'city': data.get('city', 'Unknown'),
                        'region': data.get('regionName', 'Unknown'),
                        'isp': data.get('isp', 'Unknown'),
                        'org': data.get('org', 'Unknown')
                    }
                    print(f"[+] IP: {ip} - Location: {data.get('country', 'Unknown')}")
            except:
                pass
        except Exception as e:
            self.results['ip'] = 'Unknown'
    
    def _get_ssl_info(self):
        """Get SSL/TLS certificate information"""
        self.results['ssl'] = {}
        try:
            import ssl
            import socket
            import datetime
            
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    self.results['ssl'] = {
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'issuer': dict(x[0] for x in cert.get('issuer', [])),
                        'not_before': cert.get('notBefore', 'Unknown'),
                        'not_after': cert.get('notAfter', 'Unknown'),
                        'serial_number': cert.get('serialNumber', 'Unknown')
                    }
                    print("[+] SSL/TLS information retrieved")
        except:
            self.results['ssl'] = {'error': 'No SSL/TLS found or connection failed'}
    
    def _check_security_headers(self):
        """Check for security headers"""
        self.results['security_headers'] = {}
        
        try:
            response = requests.get(f"http://{self.domain}", timeout=5)
            headers = response.headers
            
            security_headers = {
                'Strict-Transport-Security': 'HSTS',
                'Content-Security-Policy': 'CSP',
                'X-Frame-Options': 'Clickjacking Protection',
                'X-Content-Type-Options': 'MIME Sniffing Protection',
                'X-XSS-Protection': 'XSS Protection',
                'Referrer-Policy': 'Referrer Policy'
            }
            
            for header, name in security_headers.items():
                if header in headers:
                    self.results['security_headers'][name] = headers[header]
                else:
                    self.results['security_headers'][name] = 'MISSING'
            
            print("[+] Security headers checked")
        except:
            self.results['security_headers'] = {'error': 'Could not retrieve headers'}

