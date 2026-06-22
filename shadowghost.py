#!/usr/bin/env python3
"""
ShadowGhost - Advanced Reconnaissance Tool
"For those who climb where others can't"
Author: Security Researcher
Purpose: Ethical information gathering for authorized testing
License: Educational Use Only
"""

import argparse
import sys
import os
import time
import json
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from colorama import init, Fore, Style, Back
from urllib.parse import urlparse, urljoin
import socket
import ssl
import whois
import dns.resolver

# Import modules
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

class ShadowGhost:
    """Main reconnaissance engine - The Ghost that sees all"""
    
    def __init__(self, target, threads=30, timeout=10, verbose=False, output=None):
        """
        Initialize ShadowGhost
        
        How ShadowGhost Works:
        1. Validates and normalizes target input
        2. Initializes all reconnaissance modules
        3. Manages thread pool for concurrent scanning
        4. Aggregates results from all modules
        5. Generates comprehensive reports
        """
        self.target = self._normalize_target(target)
        self.domain = urlparse(self.target).netloc
        self.threads = threads
        self.timeout = timeout
        self.verbose = verbose
        self.output = output
        self.start_time = datetime.now()
        self.lock = threading.Lock()
        
        # Initialize logger
        self.logger = Logger(verbose)
        
        # Results storage
        self.results = {
            'target': self.target,
            'domain': self.domain,
            'timestamp': self.start_time.isoformat(),
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
            'parameters': [],
            'hosting_info': {},
            'osint_data': {}
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
        
        # Report generator
        self.report_gen = ReportGenerator()
        
        self._print_banner()
    
    def _normalize_target(self, target):
        """Normalize target URL format"""
        target = target.strip()
        if not target.startswith(('http://', 'https://')):
            target = f'http://{target}'
        return target
    
    def _print_banner(self):
        """Display the legendary ShadowGhost banner"""
        banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗
{Fore.CYAN}║                                                                               ║
{Fore.CYAN}║  {Fore.YELLOW}███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗  ██╗  ██████╗ ███████╗{Fore.CYAN}║
{Fore.CYAN}║  {Fore.YELLOW}██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║  ██║ ██╔════╝ ██╔════╝{Fore.CYAN}║
{Fore.CYAN}║  {Fore.YELLOW}███████╗███████║███████║██║  ██║██║   ██║███████║ ███████╗ █████╗  {Fore.CYAN}║
{Fore.CYAN}║  {Fore.YELLOW}╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██╔══██║ ██╔═══██╗██╔══╝  {Fore.CYAN}║
{Fore.CYAN}║  {Fore.YELLOW}███████║██║  ██║██║  ██║██████╔╝╚██████╔╝██║  ██║ ╚██████╔╝███████╗{Fore.CYAN}║
{Fore.CYAN}║  {Fore.YELLOW}╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝  ╚═════╝ ╚══════╝{Fore.CYAN}║
{Fore.CYAN}║                                                                               ║
{Fore.CYAN}║  {Fore.MAGENTA}✦ Advanced Ethical Reconnaissance Tool ✦{Fore.CYAN}                           ║
{Fore.CYAN}║  {Fore.WHITE}Target: {self.target}{Fore.CYAN}                                                  ║
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
        """Execute all reconnaissance phases"""
        print(f"{Fore.CYAN}[+] 👻 ShadowGhost Rising...")
        print(f"{Fore.CYAN}[+] 🎯 Target Locked: {self.target}")
        print(f"{Fore.CYAN}[+] ⚡ Threads: {self.threads}")
        print(f"{Fore.CYAN}[+] ⏱️  Timeout: {self.timeout}s")
        print(f"{Fore.CYAN}[+] 🔍 Starting reconnaissance...\n")
        
        try:
            # Phase 1: DNS Reconnaissance
            self._phase_dns_recon()
            
            # Phase 2: Port Scanning
            self._phase_port_scan()
            
            # Phase 3: Web Technology Detection
            self._phase_web_tech()
            
            # Phase 4: Hosting & Infrastructure
            self._phase_hosting()
            
            # Phase 5: OSINT Gathering
            self._phase_osint()
            
            # Phase 6: Vulnerability Assessment
            self._phase_vulnerability()
            
            # Phase 7: Directory & Endpoint Discovery
            self._phase_discovery()
            
            # Calculate scan duration
            duration = (datetime.now() - self.start_time).total_seconds()
            self.results['scan_duration'] = duration
            
            # Generate reports
            self._generate_reports()
            
            print(f"\n{Fore.GREEN}[+] ✅ Scan completed in {duration:.2f} seconds!")
            print(f"{Fore.GREEN}[+] 📊 Results saved to: {self.output or 'report.json'}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Scan interrupted by user")
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Scan failed: {str(e)}")
            sys.exit(1)
    
    def _phase_dns_recon(self):
        """Phase 1: DNS Reconnaissance"""
        print(f"{Fore.CYAN}[+] 🌐 Phase 1: DNS Reconnaissance")
        self.logger.info("Starting DNS reconnaissance...")
        
        try:
            with ThreadPoolExecutor(max_workers=10) as executor:
                future = executor.submit(self.modules['dns'].run)
                result = future.result(timeout=60)
                self.results['dns_records'] = result
                self.results['subdomains'] = result.get('subdomains', [])
                self.logger.success(f"Found {len(self.results['subdomains'])} subdomains")
                print(f"{Fore.GREEN}[+] Found {len(result.get('records', {}))} DNS record types")
        except Exception as e:
            self.logger.error(f"DNS recon failed: {str(e)}")
    
    def _phase_port_scan(self):
        """Phase 2: Port Scanning"""
        print(f"{Fore.CYAN}[+] 🔌 Phase 2: Port Scanning")
        self.logger.info("Scanning for open ports...")
        
        try:
            result = self.modules['ports'].scan()
            self.results['open_ports'] = result
            print(f"{Fore.GREEN}[+] Found {len(result)} open ports")
        except Exception as e:
            self.logger.error(f"Port scan failed: {str(e)}")
    
    def _phase_web_tech(self):
        """Phase 3: Web Technology Detection"""
        print(f"{Fore.CYAN}[+] 🖥️  Phase 3: Technology Detection")
        self.logger.info("Detecting web technologies...")
        
        try:
            result = self.modules['web'].detect_technologies()
            self.results['technologies'] = result.get('technologies', [])
            self.results['security_headers'] = result.get('headers', {})
            self.logger.success(f"Detected {len(self.results['technologies'])} technologies")
        except Exception as e:
            self.logger.error(f"Tech detection failed: {str(e)}")
    
    def _phase_hosting(self):
        """Phase 4: Hosting & Infrastructure"""
        print(f"{Fore.CYAN}[+] 🏢 Phase 4: Hosting Analysis")
        self.logger.info("Analyzing hosting infrastructure...")
        
        try:
            result = self.modules['hosting'].analyze()
            self.results['hosting_info'] = result
            self.logger.success(f"Hosting provider: {result.get('provider', 'Unknown')}")
        except Exception as e:
            self.logger.error(f"Hosting analysis failed: {str(e)}")
    
    def _phase_osint(self):
        """Phase 5: OSINT Gathering"""
        print(f"{Fore.CYAN}[+] 🔍 Phase 5: OSINT Gathering")
        self.logger.info("Gathering OSINT data...")
        
        try:
            result = self.modules['osint'].gather()
            self.results['osint_data'] = result
            self.logger.success("OSINT data collected")
        except Exception as e:
            self.logger.error(f"OSINT gathering failed: {str(e)}")
    
    def _phase_vulnerability(self):
        """Phase 6: Vulnerability Assessment"""
        print(f"{Fore.CYAN}[+] 🛡️  Phase 6: Vulnerability Assessment")
        self.logger.info("Scanning for vulnerabilities...")
        
        try:
            result = self.modules['vuln'].scan()
            self.results['vulnerabilities'] = result.get('vulnerabilities', [])
            self.results['endpoints'] = result.get('endpoints', [])
            self.logger.warning(f"Found {len(self.results['vulnerabilities'])} potential vulnerabilities")
        except Exception as e:
            self.logger.error(f"Vulnerability scan failed: {str(e)}")
    
    def _phase_discovery(self):
        """Phase 7: Directory & Endpoint Discovery"""
        print(f"{Fore.CYAN}[+] 📂 Phase 7: Directory Discovery")
        self.logger.info("Discovering directories and endpoints...")
        
        try:
            result = self.modules['web'].discover_directories()
            self.results['directories'] = result.get('directories', [])
            self.results['parameters'] = result.get('parameters', [])
            print(f"{Fore.GREEN}[+] Found {len(self.results['directories'])} directories")
        except Exception as e:
            self.logger.error(f"Discovery failed: {str(e)}")
    
    def _generate_reports(self):
        """Generate comprehensive reports"""
        print(f"{Fore.CYAN}[+] 📊 Generating reports...")
        
        # Save JSON report
        json_file = self.output or f"{self.domain}_report_{int(time.time())}.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Generate HTML report
        html_file = json_file.replace('.json', '.html')
        self.report_gen.generate_html(self.results, html_file)
        
        # Generate Markdown report
        md_file = json_file.replace('.json', '.md')
        self.report_gen.generate_markdown(self.results, md_file)
        
        self.logger.success(f"Reports generated: {json_file}, {html_file}, {md_file}")

def main():
    parser = argparse.ArgumentParser(
        description='ShadowGhost - Advanced Ethical Reconnaissance Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  shadowghost -t example.com
  shadowghost -t https://example.com -t 50 -o scan_report
  shadowghost -t 192.168.1.1 -v -t 100
        """
    )
    
    parser.add_argument('-t', '--target', required=True,
                       help='Target domain or IP address')
    parser.add_argument('-T', '--threads', type=int, default=30,
                       help='Number of threads (default: 30)')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Connection timeout in seconds (default: 10)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-o', '--output', 
                       help='Output file prefix (default: domain_timestamp)')
    
    args = parser.parse_args()
    
    # Initialize and run ShadowGhost
    ghost = ShadowGhost(
        target=args.target,
        threads=args.threads,
        timeout=args.timeout,
        verbose=args.verbose,
        output=args.output
    )
    
    ghost.run()

if __name__ == '__main__':
    main()
