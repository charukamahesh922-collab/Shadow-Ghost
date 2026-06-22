#!/usr/bin/env python3
"""
WAF Detection Module - ShadowGhost
Detects Web Application Firewalls and security layers
"""

import requests
from urllib.parse import urlparse

class WAFDetector:
    """Detect WAF and security layers"""
    
    def __init__(self, target, timeout=10):
        self.target = target
        self.timeout = timeout
        self.domain = urlparse(target).netloc if target.startswith(('http://', 'https://')) else target
    
    def detect(self):
        """Detect WAF in front of the target"""
        print("[*] Detecting WAF...")
        
        results = {
            'waf_present': False,
            'waf_provider': None,
            'details': {}
        }
        
        # Test with normal request
        try:
            response = requests.get(self.target, timeout=self.timeout)
            normal_headers = response.headers
            
            # Test with malicious payload
            malicious_payloads = [
                "' OR '1'='1",
                "<script>alert(1)</script>",
                "../../etc/passwd",
                "?id=1' UNION SELECT NULL--"
            ]
            
            for payload in malicious_payloads:
                try:
                    test_url = f"{self.target}?test={payload}"
                    waf_response = requests.get(test_url, timeout=self.timeout, 
                                              headers={'User-Agent': payload})
                    
                    # Check for WAF indicators
                    if self._check_waf_indicators(waf_response, normal_headers):
                        results['waf_present'] = True
                        results['waf_provider'] = self._identify_waf(waf_response.headers)
                        break
                except:
                    pass
            
            return results
            
        except:
            return {'waf_present': False, 'waf_provider': None}
    
    def _check_waf_indicators(self, response, normal_headers):
        """Check for WAF indicators in response"""
        # Check status code
        if response.status_code in [403, 406, 503]:
            return True
        
        # Check for WAF headers
        waf_headers = [
            'x-sucuri-id', 'x-sucuri-cache',  # Sucuri
            'cf-cache-status', 'cf-ray',       # Cloudflare
            'x-akamai-transformed',             # Akamai
            'x-cdn',                           # Various CDNs
            'server: cloudflare'               # Cloudflare
        ]
        
        for header in waf_headers:
            if header in response.headers:
                return True
            if header in str(response.headers).lower():
                return True
        
        # Check response body for WAF signatures
        waf_signatures = [
            'cloudflare', 'sucuri', 'akamai', 'incapsula',
            'blocked by', 'security', 'firewall', 'waf'
        ]
        
        body = response.text.lower()
        for sig in waf_signatures:
            if sig in body:
                return True
        
        return False
    
    def _identify_waf(self, headers):
        """Identify which WAF is being used"""
        waf_patterns = {
            'Cloudflare': ['cf-cache-status', 'cf-ray', 'server: cloudflare'],
            'Sucuri': ['x-sucuri-id', 'x-sucuri-cache'],
            'Akamai': ['x-akamai-transformed', 'akamai'],
            'Incapsula': ['x-incapsula-*', 'incapsula'],
            'AWS WAF': ['x-amzn-requestid'],
            'ModSecurity': ['mod_security']
        }
        
        for waf, patterns in waf_patterns.items():
            for pattern in patterns:
                if pattern in str(headers).lower():
                    return waf
        
        return 'Unknown'
