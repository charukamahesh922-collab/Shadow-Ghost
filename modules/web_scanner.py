#!/usr/bin/env python3
"""
Web Scanner Module
Technology detection, directory brute force, parameter discovery
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin

class WebScanner:
    """Web application scanning and fingerprinting"""
    
    def __init__(self, target, timeout=10):
        self.target = target
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def detect_technologies(self):
        """Detect web technologies in use"""
        result = {
            'technologies': [],
            'headers': {},
            'cms': None,
            'frameworks': []
        }
        
        try:
            response = self.session.get(self.target, timeout=self.timeout)
            result['headers'] = dict(response.headers)
            
            # Server header
            if 'Server' in response.headers:
                result['technologies'].append({
                    'name': 'Web Server',
                    'version': response.headers['Server']
                })
            
            # X-Powered-By
            if 'X-Powered-By' in response.headers:
                result['technologies'].append({
                    'name': 'Backend Language',
                    'version': response.headers['X-Powered-By']
                })
            
            # Parse HTML for tech detection
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # CMS Detection
            cms_patterns = {
                'WordPress': ['wp-content', 'wp-includes', 'wp-json'],
                'Drupal': ['Drupal', 'drupal'],
                'Joomla': ['joomla', 'Joomla'],
                'Magento': ['magento', 'Magento'],
                'Shopify': ['shopify', 'Shopify']
            }
            
            for cms, patterns in cms_patterns.items():
                if any(p in response.text.lower() for p in patterns):
                    result['cms'] = cms
                    result['technologies'].append({'name': 'CMS', 'version': cms})
                    break
            
            # JavaScript Framework Detection
            js_frameworks = {
                'jQuery': 'jquery',
                'Angular': 'angular',
                'React': 'react',
                'Vue.js': 'vue',
                'Bootstrap': 'bootstrap'
            }
            
            for framework, pattern in js_frameworks.items():
                if pattern.lower() in response.text.lower():
                    result['frameworks'].append(framework)
                    result['technologies'].append({'name': 'Framework', 'version': framework})
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def discover_directories(self, wordlist=None):
        """Discover directories through brute force"""
        if wordlist is None:
            wordlist = [
                'admin', 'login', 'wp-admin', 'api', 'v1', 'v2',
                'assets', 'css', 'js', 'images', 'img', 'uploads',
                'backup', 'temp', 'tmp', 'test', 'dev', 'staging',
                'docs', 'documentation', 'help', 'info', 'about',
                'contact', 'support', 'blog', 'news', 'shop',
                'cart', 'checkout', 'account', 'profile', 'settings',
                'dashboard', 'panel', 'console', 'manager', 'control',
                'system', 'core', 'lib', 'vendor', 'node_modules'
            ]
        
        discovered = []
        
        def check_dir(dir_name):
            url = urljoin(self.target, f"{dir_name}/")
            try:
                response = self.session.head(url, timeout=3, allow_redirects=False)
                if response.status_code in [200, 301, 302, 403]:
                    return {
                        'path': url,
                        'status': response.status_code,
                        'size': response.headers.get('Content-Length', 'Unknown')
                    }
            except:
                pass
            return None
        
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=30) as executor:
            results = executor.map(check_dir, wordlist)
            discovered = [r for r in results if r]
        
        return {'directories': discovered}
