# utils/logger.py
#!/usr/bin/env python3
"""Logging utility for ShadowGhost"""

from colorama import Fore, Style
from datetime import datetime

class Logger:
    def __init__(self, verbose=False):
        self.verbose = verbose
        
    def info(self, msg):
        print(f"{Fore.CYAN}[*] {msg}{Style.RESET_ALL}")
        
    def success(self, msg):
        print(f"{Fore.GREEN}[+] {msg}{Style.RESET_ALL}")
        
    def warning(self, msg):
        print(f"{Fore.YELLOW}[!] {msg}{Style.RESET_ALL}")
        
    def error(self, msg):
        print(f"{Fore.RED}[X] {msg}{Style.RESET_ALL}")
        
    def debug(self, msg):
        if self.verbose:
            print(f"{Fore.MAGENTA}[DEBUG] {msg}{Style.RESET_ALL}")
