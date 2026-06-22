#!/usr/bin/env python3
"""
Cloud Service Scanner - ShadowGhost
Detects cloud providers, SaaS, and third-party services
"""

import requests
import dns.resolver
import re
from urllib.parse import urlparse

class CloudScanner:
    """Detect cloud providers and third-party services"""
    
    def __init__(self, target, timeout=10):
        self.target = target
        self.timeout = timeout
        self.domain = urlparse(target).netloc if target.startswith(('http://', 'https://')) else target
    
    def scan(self):
        """Scan for cloud services"""
        print("[*] Scanning for cloud services...")
        
        results = {
            'cloud_provider': None,
            'cdn_provider': None,
            'saas_services': [],
            'email_provider': None,
            'dns_provider': None
        }
        
        # Check cloud providers
        results['cloud_provider'] = self._detect_cloud_provider()
        
        # Check CDN
        results['cdn_provider'] = self._detect_cdn()
        
        # Check DNS provider
        results['dns_provider'] = self._detect_dns_provider()
        
        # Check email provider
        results['email_provider'] = self._detect_email_provider()
        
        # Check SaaS services
        results['saas_services'] = self._detect_saas()
        
        return results
    
    def _detect_cloud_provider(self):
        """Detect cloud hosting provider"""
        try:
            response = requests.get(f"http://{self.domain}", timeout=self.timeout)
            headers = response.headers
            server = headers.get('Server', '').lower()
            
            cloud_patterns = {
                'AWS': ['aws', 'amazon', 'ec2', 's3', 'cloudfront'],
                'Azure': ['azure', 'microsoft', 'windows.net'],
                'GCP': ['google', 'cloud.google', 'gcp'],
                'DigitalOcean': ['digitalocean'],
                'Linode': ['linode'],
                'Vultr': ['vultr'],
                'Heroku': ['heroku'],
                'Netlify': ['netlify'],
                'Vercel': ['vercel']
            }
            
            # Check IP
            import socket
            try:
                ip = socket.gethostbyname(self.domain)
                # Query ipinfo.io for provider
                ip_info = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
                data = ip_info.json()
                org = data.get('org', '').lower()
                
                for provider, patterns in cloud_patterns.items():
                    for pattern in patterns:
                        if pattern in server or pattern in org:
                            return provider
            except:
                pass
            
            return 'Unknown'
        except:
            return 'Unknown'
    
    def _detect_cdn(self):
        """Detect CDN provider"""
        try:
            response = requests.get(f"http://{self.domain}", timeout=self.timeout)
            headers = response.headers
            
            cdn_headers = {
                'Cloudflare': ['cf-cache-status', 'cf-ray'],
                'Akamai': ['x-akamai-transformed', 'akamai'],
                'Fastly': ['x-cache', 'fastly'],
                'CloudFront': ['x-amz-cf-id', 'cloudfront'],
                'StackPath': ['x-sp-request-id'],
                'KeyCDN': ['x-keycdn-cache']
            }
            
            for provider, headers_list in cdn_headers.items():
                for header in headers_list:
                    if header in headers:
                        return provider
            
            return 'No CDN detected'
        except:
            return 'Unknown'
    
    def _detect_dns_provider(self):
        """Detect DNS provider"""
        try:
            ns_records = dns.resolver.resolve(self.domain, 'NS')
            for ns in ns_records:
                ns_str = str(ns).lower()
                dns_providers = {
                    'Cloudflare': ['cloudflare'],
                    'AWS Route53': ['awsdns', 'amazon'],
                    'Google Cloud DNS': ['google'],
                    'Azure DNS': ['azure'],
                    'GoDaddy': ['godaddy'],
                    'Namecheap': ['namecheap'],
                    'DigitalOcean': ['digitalocean']
                }
                
                for provider, patterns in dns_providers.items():
                    for pattern in patterns:
                        if pattern in ns_str:
                            return provider
            return 'Unknown'
        except:
            return 'Unknown'
    
    def _detect_email_provider(self):
        """Detect email service provider"""
        try:
            mx_records = dns.resolver.resolve(self.domain, 'MX')
            for mx in mx_records:
                mx_str = str(mx).lower()
                email_providers = {
                    'Google Workspace': ['google', 'gmail'],
                    'Microsoft 365': ['microsoft', 'office365', 'outlook'],
                    'Zoho': ['zoho'],
                    'ProtonMail': ['proton'],
                    'FastMail': ['fastmail']
                }
                
                for provider, patterns in email_providers.items():
                    for pattern in patterns:
                        if pattern in mx_str:
                            return provider
            return 'Unknown'
        except:
            return 'Unknown'
    
    def _detect_saas(self):
        """Detect SaaS services in use"""
        saas_services = []
        
        # Check for common SaaS providers via headers or content
        try:
            response = requests.get(f"http://{self.domain}", timeout=self.timeout)
            text = response.text.lower()
            
            saas_patterns = {
                'Shopify': ['shopify'],
                'WordPress.com': ['wordpress.com'],
                'Wix': ['wix.com'],
                'Squarespace': ['squarespace'],
                'HubSpot': ['hubspot'],
                'Salesforce': ['salesforce'],
                'Zendesk': ['zendesk'],
                'Intercom': ['intercom'],
                'Mailchimp': ['mailchimp'],
                'Stripe': ['stripe.js', 'stripe.com'],
                'PayPal': ['paypal'],
                'Discord': ['discord'],
                'Slack': ['slack']
            }
            
            for service, patterns in saas_patterns.items():
                for pattern in patterns:
                    if pattern in text:
                        saas_services.append(service)
                        break
        except:
            pass
        
        return list(set(saas_services))
