#!/usr/bin/env python3
"""
ShadowGhost - Advanced Ethical Reconnaissance Tool
"For those who climb where others can't"
Author: charukamahesh922-collab
License: MIT
"""

import argparse
import sys
import os
import json
import time
import threading
import subprocess
import ipaddress
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import requests
from colorama import init, Fore, Style
from urllib.parse import urlparse, urljoin

# ============================================
# AUTO-UPDATE SYSTEM
# ============================================

def auto_update():
    """Automatically check and apply updates from GitHub"""
    try:
        if '--no-update' in sys.argv or '-nu' in sys.argv:
            return
        
        print(f"{Fore.CYAN}[*] 🔄 Checking for updates...{Style.RESET_ALL}")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
        except:
            print(f"{Fore.YELLOW}[!] Git not found. Skipping auto-update.{Style.RESET_ALL}")
            return
        
        if not os.path.exists(os.path.join(script_dir, '.git')):
            print(f"{Fore.YELLOW}[!] Not a git repository. Initializing...{Style.RESET_ALL}")
            subprocess.run(['git', 'init'], capture_output=True)
            subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/charukamahesh922-collab/Shadow-Ghost.git'], capture_output=True)
        
        subprocess.run(['git', 'fetch', 'origin'], capture_output=True)
        
        current = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        latest = subprocess.run(['git', 'rev-parse', 'origin/main'], capture_output=True, text=True).stdout.strip()
        
        if not latest:
            latest = subprocess.run(['git', 'rev-parse', 'origin/master'], capture_output=True, text=True).stdout.strip()
        
        if current and latest and current != latest:
            print(f"{Fore.YELLOW}[!] ⬆️  Updates available!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[*] Current: {current[:8]}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[*] Latest:  {latest[:8]}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[*] 🔄 Auto-updating...{Style.RESET_ALL}")
            
            if os.path.exists('config/default.conf'):
                subprocess.run(['cp', 'config/default.conf', '/tmp/shadowghost_config.conf'])
            
            if os.path.exists('wordlists/custom.txt'):
                subprocess.run(['cp', 'wordlists/custom.txt', '/tmp/shadowghost_custom.txt'])
            
            result = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True)
            if result.returncode != 0:
                result = subprocess.run(['git', 'pull', 'origin', 'master'], capture_output=True, text=True)
            
            if result.returncode == 0:
                if os.path.exists('/tmp/shadowghost_config.conf'):
                    os.makedirs('config', exist_ok=True)
                    subprocess.run(['cp', '/tmp/shadowghost_config.conf', 'config/default.conf'])
                    os.remove('/tmp/shadowghost_config.conf')
                
                if os.path.exists('/tmp/shadowghost_custom.txt'):
                    os.makedirs('wordlists', exist_ok=True)
                    subprocess.run(['cp', '/tmp/shadowghost_custom.txt', 'wordlists/custom.txt'])
                    os.remove('/tmp/shadowghost_custom.txt')
                
                if os.path.exists('requirements.txt'):
                    try:
                        subprocess.run(['pip', 'install', '-r', 'requirements.txt', '--upgrade'], capture_output=True)
                    except:
                        pass
                
                print(f"{Fore.GREEN}[✓] ✅ Update completed successfully!{Style.RESET_ALL}")
                print(f"{Fore.GREEN}[✓] 🔄 Restarting with new version...{Style.RESET_ALL}")
                print()
                
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print(f"{Fore.RED}[X] ❌ Update failed. Continuing with current version.{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}[✓] ✅ Already up to date!{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"{Fore.RED}[X] Auto-update error: {str(e)}{Style.RESET_ALL}")

auto_update()

# ============================================
# IMPORTS
# ============================================

from modules.dns_recon import DNSRecon
from modules.port_scanner import PortScanner
from modules.web_scanner import WebScanner
from modules.hosting_detector import HostingDetector
from modules.osint import OSINTGatherer
from modules.vulnerability_scanner import VulnerabilityScanner
from modules.report_generator import ReportGenerator
from utils.logger import Logger
from utils.color import Colors

init(autoreset=True)

# ============================================
# ADDITIONAL FEATURES
# ============================================

def scan_subnet(ip, cidr=24):
    """Scan an entire subnet"""
    network = ipaddress.ip_network(f"{ip}/{cidr}", strict=False)
    hosts = []
    for ip in network.hosts():
        hosts.append(str(ip))
    return hosts

def extract_emails(text):
    """Extract email addresses from text"""
    import re
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, text)

def extract_urls(text):
    """Extract URLs from text"""
    import re
    pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(pattern, text)

def check_security_headers(url):
    """Check security headers"""
    headers = {
        'Strict-Transport-Security': 'HSTS',
        'Content-Security-Policy': 'CSP',
        'X-Frame-Options': 'Clickjacking Protection',
        'X-Content-Type-Options': 'MIME Sniffing Protection',
        'X-XSS-Protection': 'XSS Protection',
        'Referrer-Policy': 'Referrer Policy',
        'Feature-Policy': 'Feature Policy',
        'Permissions-Policy': 'Permissions Policy'
    }
    
    try:
        response = requests.get(url, timeout=10)
        results = {}
        for header, name in headers.items():
            results[name] = header in response.headers
        return results
    except:
        return {'Error': 'Could not retrieve headers'}

def test_rate_limiting(url):
    """Test for rate limiting"""
    try:
        times = []
        for i in range(50):
            start = time.time()
            response = requests.get(url, timeout=5)
            times.append(time.time() - start)
            if i % 10 == 0:
                print(f"[*] Request {i+1}: {response.status_code} - {times[-1]:.2f}s")
        avg_time = sum(times) / len(times)
        return avg_time
    except:
        return None

def get_page_links(url):
    """Extract all links from a page"""
    from bs4 import BeautifulSoup
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                links.append(urljoin(url, href))
        return links
    except:
        return []

def check_common_vulnerabilities(url):
    """Check for common vulnerabilities"""
    vulnerabilities = []
    
    # Check for default pages
    default_pages = ['admin', 'login', 'wp-admin', 'phpmyadmin', 'cpanel', 
                    'webmail', 'config', 'backup', 'test', 'temp']
    
    print("[*] Checking default pages...")
    for page in default_pages:
        try:
            test_url = urljoin(url, page)
            response = requests.get(test_url, timeout=5)
            if response.status_code in [200, 301, 302, 403]:
                vulnerabilities.append({
                    'type': 'Default Page',
                    'url': test_url,
                    'status': response.status_code
                })
                print(f"[!] Found: {page} (Status: {response.status_code})")
        except:
            pass
    
    # Check for directory listing
    print("[*] Checking for directory listing...")
    dirs = ['uploads/', 'images/', 'files/', 'assets/', 'media/']
    for dir_path in dirs:
        try:
            test_url = urljoin(url, dir_path)
            response = requests.get(test_url, timeout=5)
            if 'Index of' in response.text and '/p' in response.text:
                vulnerabilities.append({
                    'type': 'Directory Listing',
                    'url': test_url
                })
                print(f"[!] Found directory listing: {dir_path}")
        except:
            pass
    
    return vulnerabilities

# ============================================
# MAIN CLASS
# ============================================

class ShadowGhost:
    """Main reconnaissance engine"""
    
    def __init__(self, target, threads=30, timeout=10, verbose=False, output=None,
                 scan_type='full', aggressive=False, no_ports=False, no_dirs=False,
                 subnet=None, email_extract=False, url_extract=False, rate_test=False):
        self.target = self._normalize_target(target)
        self.domain = self._extract_domain(self.target)
        self.threads = threads
        self.timeout = timeout
        self.verbose = verbose
        self.output = output or f"reports/{self.domain}_report"
        self.scan_type = scan_type
        self.aggressive = aggressive
        self.no_ports = no_ports
        self.no_dirs = no_dirs
        self.subnet = subnet
        self.email_extract = email_extract
        self.url_extract = url_extract
        self.rate_test = rate_test
        self.start_time = datetime.now()
        self.logger = Logger(verbose)
        
        # Results storage
        self.results = {
            'target': self.target,
            'domain': self.domain,
            'timestamp': self.start_time.isoformat(),
            'scan_type': self.scan_type,
            'scan_duration': 0,
            'findings': {},
            'vulnerabilities': [],
            'technologies': [],
            'endpoints': [],
            'security_headers': {},
            'ssl_info': {},
            'dns_records': {},
            'open_ports': {},
            'subdomains': [],
            'directories': [],
            'hosting_info': {},
            'osint_data': {},
            'emails': [],
            'urls': [],
            'links': [],
            'rate_limit': None
        }
        
        # Initialize modules
        self.modules = {
            'dns': DNSRecon(self.domain, timeout),
            'ports': PortScanner(self.domain, timeout),
            'web': WebScanner(self.target, timeout),
            'hosting': HostingDetector(self.target, timeout),
            'osint': OSINTGatherer(self.domain, timeout),
            'vuln': VulnerabilityScanner(self.target, timeout)
        }
        
        self.report_gen = ReportGenerator()
        self._print_banner()
    
    def _normalize_target(self, target):
        target = target.strip()
        if not target.startswith(('http://', 'https://')):
            target = f'http://{target}'
        return target
    
    def _extract_domain(self, target):
        from urllib.parse import urlparse
        return urlparse(target).netloc
    
    def _print_banner(self):
        banner = f"""
{Fore.RED}@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*.-%@@@@@@@@@@=.=@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#:@@@...-@@%=-.#..=#@@+. .#@@++@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@*@@@@@@@@@@@@@@@@@@@@@@@@:@@:.+@..%@%@@@@*@=%@*@*@@@@#@+.*%..@@.@@@@@@@@@@@@@@@@@@@@@@@@=@@@@@@
@@@@@@@%:@@@@@@@@@@@@@@@@@@-@:.@.+@@@@@@%%@%@@@%.....@@@%=#@@@@@@@.@..@%@@@@@@@@@@@@@@@@@@.+*@@@@@@@
@@@@@@@@-+.-@@@@@@@@@@@@:@.:#:@%.=@*@+@@@@*@+@@:+@-@@@*@@@%@@@@@@@:.@@:*.@#@@@@@@@@@@@@@.-%@@@@@@@@@
@@@@@@@@@#*-::@@@@@@@%@*.@:@@@:.%@.@@@-@=##@@@*=#@@=*@@@%#=*@@@%@.@.@@*@@-:.@.@@@@@@@%::+@@@@@@@@@@@
@@@@@@@@@@@@*=+:.:=.@:-:=@@@@@@@#.#@*@..@+..=@@@@@@@@@+..-@-.%@@##.@*@*@@@@:::...:..-==%-@@@@@@@@@@@
@@@@@@@@@@@@*@%#=+#*#--:..:..%.::@.@.+@@@@@+@@@@%@@@@@@@@@@@@#.%.@=:..*....::=--=*@@@@%@@@@@@@@@@@@@
@@@@@@@@@@@@@@@=@@@@%@@@+*-=.=.::..:+@@@@@@@@=*@@@@@#=#@@@@@@@@::.--:=-::+@+#+@@@@@*@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@:@.@@@*+@@@%#*##+:-.:+-+*@@@@@@@@::@.:.=@+@@@@@==:-.:-=+@@@%@@@@-@@@+-@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@:#.@%@@@@-@@#%@@%=@%::=:+:**@@#@.@@@@@@@@@@@::.#:-::=%%%@@+%@@.@@@+%@*.@.@@@@@@@@@@@@@
@@@@@@@@@@@-@.%@@@#@+@@.%.%@@@@%@@*---..#*-@@@@@@@@@@@@@@:**.::.+*@@%@@@@*.@@@@+@#@@.-#@@@@@@@@@@@@@
@@@@@@@@@@.@.:@+@@@@%#.@%-@.@@@@@#@%:#:.%-**:@@@@@@@@@#:*#:%.-#+%@:@@@@@.:%.%@%#@@*@@#@:@@@@@@@@@@@@
@@@@@@@@@:@..@@#@*@:@#.@=#.**.@@@@@@%+-*=:=#%#@@@@@@@@***-:-:%#%@@@@@@..@=%@@:.@%@@@@*@@.@@@@@@@@@@@
@@@@@@@@.@..=@%#@@@:*@@@@.#+%%..@@@@@##=+.#@@@@@@@@@@@@@@::%=@@=@@@#+-@@@-#@@@.-@@@@+@@*#.@@@@@@@@@@
@@@@@@@:@..@@@@=@#.:@@@@@@*-@@@:-.@@@@@*=:@-+#@-@+++*@*-#-:#%@*@@+@@-%=+..@@@@@=%@@@@=@@@@=@@@@@@@@@
@@@@@@@@.+@+@@%@*.:@@@@@@@=-:@*@=.@=@%@#==@+%@-@%%=-%*@%+@-@@@@%@@.#@-@:%@@*@@@@+#@@@%@%@:-@-@@@@@@@
@@@@@@@-@@@-@#@*-*@@@@@@:+@-#@:#@%.=@@@@%%#*@-@=%@:+=:*%*@%-@*@%::@@+:@.-@#@@@@@@:-@*%@@@%..@*@@@@@@
@@@@@-@..*@*@#@@@#@@@#@@@@@%:*+=#@#:+@@*##+-.-%%@@@@%%*@+#.%@@@=.@@%:%+:@@@@@@@@@@..*@@@@*%@:@@@@@@@
@@@@@@.@@@@@@-#..@@@*@@@@#@@..@.#@@@@@+@-@%:%%%:.@@:@+%-@%@+%*@%@@*.=++%@@=@@@@@@@@@@@:@@@@..@=@@@@@
@@@@%@..@@@#@@@@@@@#*@@@@@@@@%%@.*@@@@=@@@+==+*@-@=@@@%=+=@@#@@@@@=:@..@@@@#@@@%@@@..*@@+@*@@+#@@@@@
@@@@:@%%@@#@@#..@@@@@@@%@@@@@..%@=-*%@@*--..-%%@@+@@:%*-..::@@*#+.@@#@@@@@@*@@@@%@@@@@@%@@#@:.@@@@@@
@@@@%.%@@@#@@+.-@**.#.+@..@@@@#%#%%@+@@%*+@=:.=%%@@@#=.:%**@+@@*@#@%..@@@#..@...=@@@-+=@*@@=..@#@@@@
@@@@@..@*@.@#@=@=@@@%@..@@@@@@+..#+*%@@@%..@*--*#==*-++@#.-%#@%@@@@@*@@*@.@@:-@@@@@@.=@@=:@%*:@:@@@@
@@@@@.*@@...@@=@@@@@=@-@@@@%@@.*@%*.@@@-@=##@@@+#:=%*@@@##@@*@@@@.@..@@@@@@@.@@@@@@@=@-@..@-@-@.@@@@
@@@@@..*@:%.@**@@@@@%@%@@@@@..#@@#-@@%@+..:=@@%*+.:-#@@#:..:@@#@+%@@*.:@@@@@#@@@@%@@..@%+**@*=@.@@@@
@@@@@.-#@@=%@@:=@@#@@@-@@@.%*@-@@@===#@@@%%%+@*-...=-@%%%%#@@@#:%%%%@#+.+%@@@@@@@@@@..%@*%+%-:@:@@@@
@@@@@.%@=@@=+*..@@%@@@@@.*+=#@@@@%++*@*@@@*-+@@=:..:*@*.++@@@@*=#+*%@@@*+.**@@@@@@@@*#@@#@@@..@#@@@@
@@@@:@%%@@%@@+==@@@@@@.:%=#@@:**@+%@%=@@#@%+=%@*...:@@*+#@@%:##%#@@@+-@%@*@-%-@@@@@%#@==@@@@:.@@@@@@
@@@@*@..@@@*@@@#%@@% .@--@*@#%.%@@@@*+.@@+@@*#@-...--%%*@@@@-%@*@@@@:@+*.@@-%-%.@@@..#@@@@@%@=%@@@@@
@@@@@@.#%%*=@@#.*@:.*-@@@*+%@@@@@@@@@-@@*%%%+@*:...::+@@@@=@@%**@@@@@@@@#=@:@-*%-.@@@@@@+*@..@.@@@@@
@@@@@.@-.@%%%@@*+.-@%%@@@@@@@@@%%@%@@*#@@@@@@-@:..:.%:*@@=@+#@*@@@%%%@@@@@@@@@@@-%..@@@##@%@.@@@@@@@
@@@@@@@.@@@@@.%....................#@@-=@@@@%::%@%@@=.-@@@@-@@@@#:....................@@@%..@.@@@@@@
@@@@@@:@..@...........::-=*%@@@@@@@@@#@@@-*@%-..:@*:..#@@@%=@@@@@@@@@:@@%*=-::..........-.@-@@@@@@@@
@@@@@@@%#.@@@@@+@@..@@@=@@@@@*@@@@@@@@@%*@-%@@@@@@@@@@@@@=+*+#@@@@@@@@@@@@@@@@@@%*%%@@%@@-:#%@@@@@@@
@@@@@@@@@.@@@@%@%@+..@@@@@@@@@@-@@@@@@@#+--#@@+.....-@@@@@@%#@@*@@:@@@+@@@@@@@@%+%@@*@@@:.@:@@@@@@@@
@@@@@@@@@@.@%@*+@@@+.:@@@@@@@@@.@:%:+@@@%%::%@@@@@@@@@%@+:+@%@@.-.#..*@@-@@@@*@%@@@@+%@..@:@@@@@@@@@
@@@@@@@@@@@.@+@@*@@@@+@=@@@@@*@@@@@:@@@@#@%+.+%%%@@@@@@@*@@@@@@:@@.@@@*@@@@@.:@=@@*@@@:.@.@@@@@@@@@@
@@@@@@@@@@@@=+.@@%@@*%@..@@=@@@@@@@+@@@@@@%@@@@**#%#@.@*@@%@@@@@@@@.@@@=@@#%.@#@@@@@@%.@.@@@@@@@@@@@
@@@@@@@@@@@@#@.-%@@%@@@*@-.@@@@@@@@@@.@@@@@:%%@@*:*+#%@@@@@@@@@*@+@@@@@@@-.*#@@@@@@:@.@*@@@@@@@@@@@@
@@@@@@@@@@@@@:@.@:@@#@@*@@@-.@@@@@@@@@@@@@#.+@@#%=@@@@@+@@@@@%@+@@@@@@-#.@@@=@@@@%-.@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@.%@@%@@**@@@.@.@@@@@@@@@@@@#*@@@@#%%#=:@@@@*@@@@@@#:-#@@+@-@@@@.*.@.@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@+@#..@@@@@@@@+#@.%.=@@@@@@@@:.-@#@@@%=@@@@@@@@@@.*.%*@@@@@@+@@.@.@#@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@:@*.%*%@%@@@.@@:@@.*+.*@@@@#@=@@.@+.@@@@@:.@.:@%.@@@%@@%%@.@.@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@-@@.@.@#=@@@.@:@@#*@@+.:%@..==@#@@@+..#@%+@#@=*.@-@#@+#.:@%@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@%@=.@.@@%@.@=@@@=@@@@@%@@#=#..@%@@*@@@@#@@#%@:@:-+.@@.@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@+@@*.%#:@@@@@#@@@++@@@..@##@@@#@@=@*@@@@@*.@..@@=@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@=@@=.=@.:@@@@@@@#%@##..@@@@+@@@##.#@..@@@.@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:@@@#..:@@+...+:.*%-..:%@=..-@@@#-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@=:@@@@@@@@@+:@@@@@@@@+.%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-=@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

{Fore.CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗
{Fore.CYAN}║                                                                               ║
{Fore.CYAN}║  {Fore.MAGENTA}✦ ShadowGhost - Advanced Ethical Reconnaissance Tool ✦{Fore.CYAN}                 ║
{Fore.CYAN}║  {Fore.WHITE}Target: {self.target}{Fore.CYAN}                                                  ║
{Fore.CYAN}║  {Fore.WHITE}Scan Type: {self.scan_type.upper()}{Fore.CYAN}                                                 ║
{Fore.CYAN}║  {Fore.WHITE}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Fore.CYAN}                          ║
{Fore.CYAN}║  {Fore.WHITE}Threads: {self.threads}{Fore.CYAN}                                                        ║
{Fore.CYAN}╚═══════════════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
        print(banner)
        print(f"{Fore.RED}╔═══════════════════════════════════════════════════════════════════════════════╗")
        print(f"{Fore.RED}║ {Fore.YELLOW}⚠ LEGAL DISCLAIMER: Use only on systems you own or have permission{Fore.RED} ║")
        print(f"{Fore.RED}║ {Fore.YELLOW}⚠ Unauthorized use is illegal. The author assumes no liability{Fore.RED}    ║")
        print(f"{Fore.RED}╚═══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    def run(self):
        print(f"{Fore.CYAN}[+] 👻 ShadowGhost Rising...")
        print(f"{Fore.CYAN}[+] 🎯 Target Locked: {self.target}")
        print(f"{Fore.CYAN}[+] ⚡ Threads: {self.threads}")
        print(f"{Fore.CYAN}[+] ⏱️  Timeout: {self.timeout}s")
        print(f"{Fore.CYAN}[+] 📋 Scan Type: {self.scan_type.upper()}")
        print(f"{Fore.CYAN}[+] 🔍 Starting reconnaissance...\n")
        
        try:
            # DNS Recon
            self._phase_dns_recon()
            
            # Port Scan (skip if no-ports)
            if not self.no_ports:
                self._phase_port_scan()
            else:
                print(f"{Fore.YELLOW}[!] Skipping port scan (--no-ports){Style.RESET_ALL}")
            
            # Web Technologies
            self._phase_web_tech()
            
            # Hosting Analysis
            self._phase_hosting()
            
            # OSINT
            self._phase_osint()
            
            # Vulnerability Scan
            self._phase_vulnerability()
            
            # Directory Discovery (skip if no-dirs)
            if not self.no_dirs:
                self._phase_discovery()
            else:
                print(f"{Fore.YELLOW}[!] Skipping directory discovery (--no-dirs){Style.RESET_ALL}")
            
            # Extra Features
            if self.email_extract:
                self._extract_emails()
            
            if self.url_extract:
                self._extract_urls()
            
            if self.rate_test:
                self._test_rate_limiting()
            
            # Aggressive mode - extra checks
            if self.aggressive:
                self._aggressive_scan()
            
            duration = (datetime.now() - self.start_time).total_seconds()
            self.results['scan_duration'] = duration
            self._generate_reports()
            
            print(f"\n{Fore.GREEN}[+] ✅ Scan completed in {duration:.2f} seconds!")
            print(f"{Fore.GREEN}[+] 📊 Results saved to: {self.output}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Scan interrupted by user")
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Scan failed: {str(e)}")
            sys.exit(1)
    
    def _phase_dns_recon(self):
        print(f"{Fore.CYAN}[+] 🌐 Phase 1: DNS Reconnaissance")
        try:
            result = self.modules['dns'].run()
            self.results['dns_records'] = result
            self.results['subdomains'] = result.get('subdomains', [])
        except Exception as e:
            self.logger.error(f"DNS recon failed: {str(e)}")
    
    def _phase_port_scan(self):
        print(f"{Fore.CYAN}[+] 🔌 Phase 2: Port Scanning")
        try:
            result = self.modules['ports'].scan()
            self.results['open_ports'] = result
        except Exception as e:
            self.logger.error(f"Port scan failed: {str(e)}")
    
    def _phase_web_tech(self):
        print(f"{Fore.CYAN}[+] 🖥️  Phase 3: Technology Detection")
        try:
            result = self.modules['web'].detect_technologies()
            self.results['technologies'] = result.get('technologies', [])
            self.results['security_headers'] = result.get('headers', {})
        except Exception as e:
            self.logger.error(f"Tech detection failed: {str(e)}")
    
    def _phase_hosting(self):
        print(f"{Fore.CYAN}[+] 🏢 Phase 4: Hosting Analysis")
        try:
            result = self.modules['hosting'].analyze()
            self.results['hosting_info'] = result
        except Exception as e:
            self.logger.error(f"Hosting analysis failed: {str(e)}")
    
    def _phase_osint(self):
        print(f"{Fore.CYAN}[+] 🔍 Phase 5: OSINT Gathering")
        try:
            result = self.modules['osint'].gather()
            self.results['osint_data'] = result
        except Exception as e:
            self.logger.error(f"OSINT gathering failed: {str(e)}")
    
    def _phase_vulnerability(self):
        print(f"{Fore.CYAN}[+] 🛡️  Phase 6: Vulnerability Assessment")
        try:
            result = self.modules['vuln'].scan()
            self.results['vulnerabilities'] = result.get('vulnerabilities', [])
            self.results['endpoints'] = result.get('endpoints', [])
            
            # Additional vulnerability checks
            extra_vulns = check_common_vulnerabilities(self.target)
            self.results['vulnerabilities'].extend(extra_vulns)
        except Exception as e:
            self.logger.error(f"Vulnerability scan failed: {str(e)}")
    
    def _phase_discovery(self):
        print(f"{Fore.CYAN}[+] 📂 Phase 7: Directory Discovery")
        try:
            result = self.modules['web'].discover_directories()
            self.results['directories'] = result.get('directories', [])
        except Exception as e:
            self.logger.error(f"Discovery failed: {str(e)}")
    
    def _extract_emails(self):
        print(f"{Fore.CYAN}[+] 📧 Extracting emails from page...")
        try:
            response = requests.get(self.target, timeout=10)
            emails = extract_emails(response.text)
            self.results['emails'] = list(set(emails))
            print(f"[+] Found {len(self.results['emails'])} unique emails")
        except Exception as e:
            self.logger.error(f"Email extraction failed: {str(e)}")
    
    def _extract_urls(self):
        print(f"{Fore.CYAN}[+] 🔗 Extracting URLs from page...")
        try:
            links = get_page_links(self.target)
            self.results['links'] = links
            print(f"[+] Found {len(links)} links")
        except Exception as e:
            self.logger.error(f"URL extraction failed: {str(e)}")
    
    def _test_rate_limiting(self):
        print(f"{Fore.CYAN}[+] ⏱️  Testing rate limiting...")
        try:
            avg_time = test_rate_limiting(self.target)
            self.results['rate_limit'] = avg_time
            print(f"[+] Average response time: {avg_time:.2f}s")
        except Exception as e:
            self.logger.error(f"Rate testing failed: {str(e)}")
    
    def _aggressive_scan(self):
        """Aggressive scan mode - extra checks"""
        print(f"{Fore.CYAN}[+] 🚀 Aggressive mode enabled - Extra checks...{Style.RESET_ALL}")
        
        # Check security headers
        print("[*] Checking security headers...")
        headers = check_security_headers(self.target)
        self.results['security_headers_detailed'] = headers
        
        # Check for sensitive files
        sensitive_files = ['.git/config', '.env', '.htaccess', 'robots.txt', 
                          'sitemap.xml', 'crossdomain.xml', '.well-known/']
        
        print("[*] Checking for sensitive files...")
        sensitive_found = []
        for file_path in sensitive_files:
            try:
                test_url = urljoin(self.target, file_path)
                response = requests.get(test_url, timeout=5)
                if response.status_code == 200:
                    sensitive_found.append({'file': file_path, 'url': test_url})
                    print(f"[!] Found: {file_path}")
            except:
                pass
        
        self.results['sensitive_files'] = sensitive_found
        
        # SSL/TLS check
        print("[*] Checking SSL/TLS...")
        try:
            import ssl
            import socket
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    self.results['ssl_detailed'] = {
                        'subject': cert.get('subject', []),
                        'issuer': cert.get('issuer', []),
                        'not_before': cert.get('notBefore', ''),
                        'not_after': cert.get('notAfter', '')
                    }
        except:
            self.results['ssl_detailed'] = {'error': 'No SSL/TLS'}
    
    def _generate_reports(self):
        print(f"{Fore.CYAN}[+] 📊 Generating reports...")
        
        json_file = f"{self.output}.json"
        html_file = f"{self.output}.html"
        md_file = f"{self.output}.md"
        txt_file = f"{self.output}.txt"
        
        self.report_gen.generate_json(self.results, json_file)
        self.report_gen.generate_html(self.results, html_file)
        self.report_gen.generate_markdown(self.results, md_file)
        self.report_gen.generate_txt(self.results, txt_file)

def main():
    parser = argparse.ArgumentParser(
        description='ShadowGhost - Advanced Ethical Reconnaissance Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  shadowghost -t example.com                    # Full scan
  shadowghost -t example.com --quick            # Quick scan (no ports, no dirs)
  shadowghost -t example.com --aggressive       # Aggressive scan
  shadowghost -t example.com --email-extract    # Extract emails
  shadowghost -t example.com --rate-test        # Test rate limiting
  shadowghost -t example.com --no-ports         # Skip port scanning
  shadowghost -t example.com --no-dirs          # Skip directory discovery
  shadowghost -t example.com -T 50              # Use 50 threads
  shadowghost -t example.com -v -o custom_name  # Verbose with custom output
        """
    )
    
    # Basic options
    parser.add_argument('-t', '--target', required=True, help='Target domain or IP address')
    parser.add_argument('-T', '--threads', type=int, default=30, help='Number of threads (default: 30)')
    parser.add_argument('--timeout', type=int, default=10, help='Connection timeout in seconds (default: 10)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-o', '--output', help='Output file prefix')
    parser.add_argument('--no-update', '-nu', action='store_true', help='Skip update check')
    
    # Scan types
    scan_group = parser.add_mutually_exclusive_group()
    scan_group.add_argument('--quick', action='store_true', help='Quick scan (skip ports and dirs)')
    scan_group.add_argument('--aggressive', action='store_true', help='Aggressive scan with extra checks')
    scan_group.add_argument('--full', action='store_true', help='Full scan (default)')
    
    # Skip options
    parser.add_argument('--no-ports', action='store_true', help='Skip port scanning')
    parser.add_argument('--no-dirs', action='store_true', help='Skip directory discovery')
    
    # Extra features
    parser.add_argument('--email-extract', '-e', action='store_true', help='Extract emails from pages')
    parser.add_argument('--url-extract', '-u', action='store_true', help='Extract all URLs/links from pages')
    parser.add_argument('--rate-test', '-r', action='store_true', help='Test rate limiting')
    parser.add_argument('--subnet', help='Scan subnet (e.g., 192.168.1.0/24)')
    
    args = parser.parse_args()
    
    # Determine scan type
    if args.quick:
        scan_type = 'quick'
        args.no_ports = True
        args.no_dirs = True
    elif args.aggressive:
        scan_type = 'aggressive'
    else:
        scan_type = 'full'
    
    ghost = ShadowGhost(
        target=args.target,
        threads=args.threads,
        timeout=args.timeout,
        verbose=args.verbose,
        output=args.output,
        scan_type=scan_type,
        aggressive=args.aggressive,
        no_ports=args.no_ports,
        no_dirs=args.no_dirs,
        email_extract=args.email_extract,
        url_extract=args.url_extract,
        rate_test=args.rate_test
    )
    ghost.run()

if __name__ == '__main__':
    main()
