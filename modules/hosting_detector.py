
#!/usr/bin/env python3
"""
Hosting Detector Module - ShadowGhost
"""

import socket
import requests
from urllib.parse import urlparse

class HostingDetector:
    """Detect hosting provider and infrastructure"""
    
    def __init__(self, target, timeout=10):
        self.target = target
        self.timeout = timeout
        self.domain = urlparse(target).netloc if target.startswith(('http://', 'https://')) else target
        self.results = {}
    
    def analyze(self):
        """Analyze hosting infrastructure"""
        print("[*] Analyzing hosting infrastructure...")
        
        self.results = {
            'ip': None,
            'hosting_provider': 'Unknown',
            'cdn': 'No CDN detected',
            'server_location': 'Unknown',
            'server_type': 'Unknown'
        }
        
        # Get IP
        try:
            self.results['ip'] = socket.gethostbyname(self.domain)
            print(f"[+] IP Address: {self.results['ip']}")
        except:
            pass
        
        # Determine hosting provider
        if self.results['ip']:
            self.results['hosting_provider'] = self._identify_provider(self.results['ip'])
        
        # Check for CDN
        self.results['cdn'] = self._detect_cdn()
        
        # Get server type from response
        self.results['server_type'] = self._get_server_type()
        
        print(f"[+] Hosting Provider: {self.results['hosting_provider']}")
        print(f"[+] CDN: {self.results['cdn']}")
        
        return self.results
    
    def _identify_provider(self, ip):
        """Identify hosting provider by IP"""
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            data = response.json()
            return data.get('isp', 'Unknown')
        except:
            return 'Unknown'
    
    def _detect_cdn(self):
        """Detect CDN usage"""
        try:
            response = requests.get(f"http://{self.domain}", timeout=5)
            headers = response.headers
            
            if 'cf-cache-status' in headers:
                return 'Cloudflare'
            elif 'x-cache' in headers and 'akamai' in headers.get('x-cache', '').lower():
                return 'Akamai'
            elif 'via' in headers and 'fastly' in headers['via'].lower():
                return 'Fastly'
            else:
                return 'No CDN detected'
        except:
            return 'Unknown'
    
    def _get_server_type(self):
        """Get server type from response headers"""
        try:
            response = requests.get(f"http://{self.domain}", timeout=5)
            server = response.headers.get('Server', '')
            if 'nginx' in server.lower():
                return 'Nginx'
            elif 'apache' in server.lower():
                return 'Apache'
            elif 'microsoft' in server.lower() or 'iis' in server.lower():
                return 'IIS'
            else:
                return server or 'Unknown'
        except:
            return 'Unknown'
