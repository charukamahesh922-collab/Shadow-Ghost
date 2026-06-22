#!/usr/bin/env python3
"""
Port Scanning Module
Service detection, banner grabbing
"""

import socket
import threading
from concurrent.futures import ThreadPoolExecutor

class PortScanner:
    """Port scanning and service detection"""
    
    def __init__(self, target, timeout=5):
        self.target = target
        self.timeout = timeout
        self.common_ports = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            111: 'RPC',
            135: 'RPC',
            139: 'NetBIOS',
            143: 'IMAP',
            443: 'HTTPS',
            445: 'SMB',
            993: 'IMAPS',
            995: 'POP3S',
            1723: 'PPTP',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            5900: 'VNC',
            6379: 'Redis',
            8080: 'HTTP-Alt',
            8443: 'HTTPS-Alt',
            27017: 'MongoDB'
        }
    
    def scan(self, ports=None):
        """Scan for open ports"""
        if ports is None:
            ports = list(self.common_ports.keys())
        
        open_ports = {}
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                result = sock.connect_ex((self.target, port))
                if result == 0:
                    # Get service banner
                    service = self.common_ports.get(port, 'Unknown')
                    banner = self._grab_banner(sock, port)
                    open_ports[port] = {
                        'service': service,
                        'banner': banner
                    }
                sock.close()
            except:
                pass
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(scan_port, ports)
        
        return open_ports
    
    def _grab_banner(self, sock, port):
        """Attempt to grab service banner"""
        try:
            # Send HTTP request for web ports
            if port in [80, 443, 8080, 8443]:
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                return sock.recv(1024).decode('utf-8', errors='ignore')
            else:
                return "Banner not available"
        except:
            return "Banner not available"
