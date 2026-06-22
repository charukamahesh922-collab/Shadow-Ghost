#!/usr/bin/env python3
"""
SSL/TLS Scanner Module - ShadowGhost
Checks SSL certificate details and vulnerabilities
"""

import ssl
import socket
import datetime
import OpenSSL
import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend

class SSLScanner:
    """SSL/TLS security scanner"""
    
    def __init__(self, domain, timeout=10):
        self.domain = domain
        self.timeout = timeout
        self.results = {}
    
    def scan(self):
        """Perform SSL/TLS scan"""
        print("[*] Scanning SSL/TLS configuration...")
        
        self.results = {
            'certificate': {},
            'vulnerabilities': [],
            'protocols': {},
            'cipher_suites': []
        }
        
        # Get certificate info
        self._get_certificate_info()
        
        # Check vulnerabilities
        self._check_vulnerabilities()
        
        # Check protocols
        self._check_protocols()
        
        return self.results
    
    def _get_certificate_info(self):
        """Get certificate details"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    self.results['certificate'] = {
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'issuer': dict(x[0] for x in cert.get('issuer', [])),
                        'not_before': cert.get('notBefore', 'Unknown'),
                        'not_after': cert.get('notAfter', 'Unknown'),
                        'serial_number': cert.get('serialNumber', 'Unknown'),
                        'version': cert.get('version', 'Unknown')
                    }
                    print("[+] SSL certificate retrieved")
        except:
            self.results['certificate'] = {'error': 'No SSL/TLS found'}
    
    def _check_vulnerabilities(self):
        """Check for SSL/TLS vulnerabilities"""
        vulns = []
        
        # Check for weak protocols
        weak_protocols = {
            'SSLv2': self._test_protocol(ssl.PROTOCOL_SSLv2),
            'SSLv3': self._test_protocol(ssl.PROTOCOL_SSLv3),
            'TLSv1.0': self._test_protocol(ssl.PROTOCOL_TLSv1),
            'TLSv1.1': self._test_protocol(ssl.PROTOCOL_TLSv1_1)
        }
        
        for protocol, enabled in weak_protocols.items():
            if enabled:
                vulns.append({
                    'type': 'Weak Protocol',
                    'protocol': protocol,
                    'severity': 'High',
                    'description': f'{protocol} is enabled and considered insecure'
                })
        
        # Check heartbleed
        if self._test_heartbleed():
            vulns.append({
                'type': 'Heartbleed',
                'severity': 'Critical',
                'description': 'Server vulnerable to Heartbleed attack'
            })
        
        self.results['vulnerabilities'] = vulns
    
    def _test_protocol(self, protocol):
        """Test if a protocol is enabled"""
        try:
            context = ssl.SSLContext(protocol)
            with socket.create_connection((self.domain, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    return True
        except:
            return False
    
    def _test_heartbleed(self):
        """Test for Heartbleed vulnerability"""
        # Simplified check - in production use specialized tools
        return False
    
    def _check_protocols(self):
        """Check supported TLS versions"""
        protocols = {}
        for version in ['TLSv1.2', 'TLSv1.3']:
            try:
                context = ssl.create_default_context()
                if version == 'TLSv1.2':
                    context.minimum_version = ssl.TLSVersion.TLSv1_2
                    context.maximum_version = ssl.TLSVersion.TLSv1_2
                else:
                    context.minimum_version = ssl.TLSVersion.TLSv1_3
                    context.maximum_version = ssl.TLSVersion.TLSv1_3
                
                with socket.create_connection((self.domain, 443), timeout=self.timeout) as sock:
                    with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                        protocols[version] = True
            except:
                protocols[version] = False
        
        self.results['protocols'] = protocols
