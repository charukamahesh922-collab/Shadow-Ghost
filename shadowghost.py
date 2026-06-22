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
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import requests
from colorama import init, Fore, Style

# ============================================
# AUTO-UPDATE SYSTEM - Runs before anything else
# ============================================

def auto_update():
    """Automatically check and apply updates from GitHub"""
    try:
        # Check if we should skip update
        if '--no-update' in sys.argv or '-nu' in sys.argv:
            return
        
        print(f"{Fore.CYAN}[*] 🔄 Checking for updates...{Style.RESET_ALL}")
        
        # Get the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Check if git is available
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
        except:
            print(f"{Fore.YELLOW}[!] Git not found. Skipping auto-update.{Style.RESET_ALL}")
            return
        
        # Check if this is a git repository
        if not os.path.exists(os.path.join(script_dir, '.git')):
            print(f"{Fore.YELLOW}[!] Not a git repository. Initializing...{Style.RESET_ALL}")
            subprocess.run(['git', 'init'], capture_output=True)
            subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/charukamahesh922-collab/Shadow-Ghost.git'], capture_output=True)
        
        # Fetch latest changes
        subprocess.run(['git', 'fetch', 'origin'], capture_output=True)
        
        # Get current and latest commit
        current = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        latest = subprocess.run(['git', 'rev-parse', 'origin/main'], capture_output=True, text=True).stdout.strip()
        
        # If no origin/main, try origin/master
        if not latest:
            latest = subprocess.run(['git', 'rev-parse', 'origin/master'], capture_output=True, text=True).stdout.strip()
        
        # Check if update is available
        if current and latest and current != latest:
            print(f"{Fore.YELLOW}[!] ⬆️  Updates available!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[*] Current: {current[:8]}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[*] Latest:  {latest[:8]}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[*] 🔄 Auto-updating...{Style.RESET_ALL}")
            
            # Backup config files
            if os.path.exists('config/default.conf'):
                subprocess.run(['cp', 'config/default.conf', '/tmp/shadowghost_config.conf'])
            
            # Backup custom wordlists
            if os.path.exists('wordlists/custom.txt'):
                subprocess.run(['cp', 'wordlists/custom.txt', '/tmp/shadowghost_custom.txt'])
            
            # Pull latest changes
            result = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True)
            if result.returncode != 0:
                # Try master branch
                result = subprocess.run(['git', 'pull', 'origin', 'master'], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Restore config files
                if os.path.exists('/tmp/shadowghost_config.conf'):
                    os.makedirs('config', exist_ok=True)
                    subprocess.run(['cp', '/tmp/shadowghost_config.conf', 'config/default.conf'])
                    os.remove('/tmp/shadowghost_config.conf')
                
                if os.path.exists('/tmp/shadowghost_custom.txt'):
                    os.makedirs('wordlists', exist_ok=True)
                    subprocess.run(['cp', '/tmp/shadowghost_custom.txt', 'wordlists/custom.txt'])
                    os.remove('/tmp/shadowghost_custom.txt')
                
                # Update dependencies
                if os.path.exists('requirements.txt'):
                    try:
                        subprocess.run(['pip', 'install', '-r', 'requirements.txt', '--upgrade'], capture_output=True)
                    except:
                        pass
                
                print(f"{Fore.GREEN}[✓] ✅ Update completed successfully!{Style.RESET_ALL}")
                print(f"{Fore.GREEN}[✓] 🔄 Restarting with new version...{Style.RESET_ALL}")
                print()
                
                # Restart the script with the same arguments
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print(f"{Fore.RED}[X] ❌ Update failed. Continuing with current version.{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}[✓] ✅ Already up to date!{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"{Fore.RED}[X] Auto-update error: {str(e)}{Style.RESET_ALL}")

# ============================================
# RUN AUTO-UPDATE
# ============================================

auto_update()

# ============================================
# MAIN TOOL
# ============================================

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
    """Main reconnaissance engine"""
    
    def __init__(self, target, threads=30, timeout=10, verbose=False, output=None):
        self.target = self._normalize_target(target)
        self.domain = self._extract_domain(self.target)
        self.threads = threads
        self.timeout = timeout
        self.verbose = verbose
        self.output = output or f"reports/{self.domain}_report"
        self.start_time = datetime.now()
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
        print(f"{Fore.CYAN}[+] 🔍 Starting reconnaissance...\n")
        
        try:
            self._phase_dns_recon()
            self._phase_port_scan()
            self._phase_web_tech()
            self._phase_hosting()
            self._phase_osint()
            self._phase_vulnerability()
            self._phase_discovery()
            
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
        except Exception as e:
            self.logger.error(f"Vulnerability scan failed: {str(e)}")
    
    def _phase_discovery(self):
        print(f"{Fore.CYAN}[+] 📂 Phase 7: Directory Discovery")
        try:
            result = self.modules['web'].discover_directories()
            self.results['directories'] = result.get('directories', [])
        except Exception as e:
            self.logger.error(f"Discovery failed: {str(e)}")
    
    def _generate_reports(self):
        print(f"{Fore.CYAN}[+] 📊 Generating reports...")
        
        json_file = f"{self.output}.json"
        html_file = f"{self.output}.html"
        md_file = f"{self.output}.md"
        
        self.report_gen.generate_json(self.results, json_file)
        self.report_gen.generate_html(self.results, html_file)
        self.report_gen.generate_markdown(self.results, md_file)

def main():
    parser = argparse.ArgumentParser(description='ShadowGhost - Advanced Ethical Reconnaissance Tool')
    parser.add_argument('-t', '--target', required=True, help='Target domain or IP address')
    parser.add_argument('-T', '--threads', type=int, default=30, help='Number of threads (default: 30)')
    parser.add_argument('--timeout', type=int, default=10, help='Connection timeout in seconds (default: 10)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-o', '--output', help='Output file prefix')
    parser.add_argument('--no-update', '-nu', action='store_true', help='Skip update check')
    
    args = parser.parse_args()
    
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
