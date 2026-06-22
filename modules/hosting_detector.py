#!/usr/bin/env python3
"""
Hosting Detector Module
Identify hosting provider, CDN usage, IP geolocation
"""

import socket
import requests
import json
from urllib.parse import urlparse

class HostingDetector:
    """Detect hosting provider and infrastructure"""
    
    def __init__(self, target, timeout=10):
        self.target = target
        self.timeout = timeout
        self.domain = urlparse(target).netloc
        self.results = {}
    
    def analyze(self):
        """Analyze hosting infrastructure"""
        self.results = {
            'ip': None,
            'hosting_provider': None,
            'cdn': None,
            'server_location': None,
            'server_type': None
        }
        
        # Get IP
        try:
            self.results['ip'] = socket.gethostbyname(self.domain)
        except:
            pass
        
        # Determine hosting provider
        if self.results['ip']:
            self.results['hosting_provider'] = self._identify_provider(self.results['ip'])
        
        # Check for CDN
        self.results['cdn'] = self._detect_cdn()
        
        # Get server type from response
        self.results['server_type'] = self._get_server_type()
        
        return self.results
    
    def _identify_provider(self, ip):
        """Identify hosting provider by IP"""
        try:
            # Use ipinfo.io for IP info
            response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
            data = response.json()
            
            # Check common hosting providers
            hosting_keywords = ['amazon', 'aws', 'azure', 'google', 'cloud',
                              'digitalocean', 'linode', 'vultr', 'heroku',
                              'infinityfree', '000webhost', 'byet', 'hostinger',
                              'godaddy', 'namecheap']
            
            org = data.get('org', '').lower()
            for provider in hosting_keywords:
                if provider in org:
                    return provider.upper()
            
            return org or 'Unknown'
        except:
            return 'Unknown'
    
    def _detect_cdn(self):
        """Detect CDN usage"""
        cdn_headers = ['cf-cache-status', 'x-cache', 'x-cdn', 'x-powered-by']
        
        try:
            response = requests.get(self.target, timeout=5)
            for header in cdn_headers:
                if header in response.headers:
                    if 'cloudflare' in response.headers.get('Server', '').lower():
                        return 'Cloudflare'
                    elif 'akamai' in response.headers.get('Server', '').lower():
                        return 'Akamai'
                    elif 'fastly' in response.headers.get('Via', '').lower():
                        return 'Fastly'
                    elif 'amazon' in response.headers.get('Server', '').lower():
                        return 'AWS CloudFront'
            return 'No CDN detected'
        except:
            return 'Unknown'
    
    def _get_server_type(self):
        """Get server type from response headers"""
        try:
            response = requests.get(self.target, timeout=5)
            server = response.headers.get('Server', '')
            if 'nginx' in server.lower():
                return 'Nginx'
            elif 'apache' in server.lower():
                return 'Apache'
            elif 'microsoft' in server.lower():
                return 'IIS'
            elif 'cloudflare' in server.lower():
                return 'Cloudflare'
            else:
                return server or 'Unknown'
        except:
            return 'Unknown'
