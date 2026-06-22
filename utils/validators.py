
#!/usr/bin/env python3
"""
Input validation utilities for ShadowGhost
"""

import re
import socket
from urllib.parse import urlparse

class Validators:
    """Validate input and target data"""
    
    @staticmethod
    def validate_url(url):
        """Validate if the URL is properly formatted"""
        if not url:
            return False, "URL is empty"
        
        if not url.startswith(('http://', 'https://')):
            url = f"http://{url}"
        
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False, "Invalid domain"
            return True, url
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def validate_ip(ip):
        """Validate if the string is a valid IP address"""
        try:
            socket.inet_aton(ip)
            return True
        except:
            return False
    
    @staticmethod
    def validate_domain(domain):
        """Validate if the string is a valid domain"""
        pattern = re.compile(
            r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
            r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
        )
        return bool(pattern.match(domain))
    
    @staticmethod
    def sanitize_input(input_string):
        """Sanitize input to prevent injection"""
        # Remove dangerous characters
        dangerous = [';', '&', '|', '`', '$', '(', ')', '<', '>']
        for char in dangerous:
            input_string = input_string.replace(char, '')
        return input_string.strip()
    
    @staticmethod
    def validate_port(port):
        """Validate if port is valid (1-65535)"""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except:
            return False
    
    @staticmethod
    def validate_threads(threads):
        """Validate thread count"""
        try:
            thread_num = int(threads)
            return 1 <= thread_num <= 1000
        except:
            return False
    
    @staticmethod
    def validate_timeout(timeout):
        """Validate timeout value"""
        try:
            timeout_num = int(timeout)
            return 1 <= timeout_num <= 60
        except:
            return False
