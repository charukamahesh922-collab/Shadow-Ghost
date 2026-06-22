#!/usr/bin/env python3
"""
Report Generator Module - ShadowGhost
Generate comprehensive HTML, JSON, Markdown, and TXT reports
"""

import json
from datetime import datetime

class ReportGenerator:
    """Generate comprehensive reconnaissance reports"""
    
    def generate_html(self, data, filename):
        """Generate HTML report"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>ShadowGhost Report - {data.get('domain', 'Unknown')}</title>
    <style>
        body {{ font-family: 'Courier New', monospace; margin: 20px; background: #0a0a0a; color: #00ff00; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1a1a1a, #000000); padding: 20px; border: 1px solid #00ff00; border-radius: 10px; }}
        .section {{ background: #1a1a1a; margin: 20px 0; padding: 20px; border: 1px solid #003300; border-radius: 10px; }}
        .vulnerability {{ background: #330000; border: 1px solid #ff0000; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .finding {{ background: #001a00; border: 1px solid #00ff00; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .critical {{ color: #ff0000; }}
        .high {{ color: #ff6600; }}
        .medium {{ color: #ffcc00; }}
        .low {{ color: #66ff66; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #003300; padding: 8px; text-align: left; }}
        th {{ background: #002200; }}
        .port-open {{ color: #00ff00; }}
        .port-closed {{ color: #ff0000; }}
        h1, h2, h3 {{ color: #00ff00; }}
        a {{ color: #00ff00; }}
        .footer {{ margin-top: 40px; padding: 20px; background: #1a1a1a; border: 1px solid #003300; border-radius: 10px; text-align: center; }}
        .badge {{ display: inline-block; padding: 3px 10px; border-radius: 3px; font-size: 12px; }}
        .badge-success {{ background: #003300; color: #00ff00; }}
        .badge-danger {{ background: #330000; color: #ff0000; }}
        .badge-warning {{ background: #332200; color: #ffcc00; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👻 ShadowGhost Reconnaissance Report</h1>
            <p><strong>Target:</strong> {data.get('target', 'Unknown')}</p>
            <p><strong>Domain:</strong> {data.get('domain', 'Unknown')}</p>
            <p><strong>Scan Type:</strong> {data.get('scan_type', 'Full')}</p>
            <p><strong>Scan Date:</strong> {data.get('timestamp', 'Unknown')}</p>
            <p><strong>Duration:</strong> {data.get('scan_duration', 0):.2f} seconds</p>
        </div>
        
        <div class="section">
            <h2>🎯 Executive Summary</h2>
            <table>
                <tr><td>Total Vulnerabilities Found:</td><td><span class="badge badge-danger">{len(data.get('vulnerabilities', []))}</span></td></tr>
                <tr><td>Open Ports:</td><td><span class="badge badge-success">{len(data.get('open_ports', {}))}</span></td></tr>
                <tr><td>Subdomains Discovered:</td><td><span class="badge badge-success">{len(data.get('subdomains', []))}</span></td></tr>
                <tr><td>Technologies Detected:</td><td><span class="badge badge-success">{len(data.get('technologies', []))}</span></td></tr>
                <tr><td>Directories Found:</td><td><span class="badge badge-success">{len(data.get('directories', []))}</span></td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>🔌 Open Ports</h2>
            <table>
                <tr><th>Port</th><th>Service</th><th>Banner</th></tr>
                {''.join(f"<tr><td class='port-open'>{port}</td><td>{info.get('service', 'Unknown')}</td><td>{info.get('banner', 'N/A')[:100]}</td></tr>" for port, info in data.get('open_ports', {}).items())}
            </table>
        </div>
        
        <div class="section">
            <h2>🌐 DNS Records</h2>
            <table>
                <tr><th>Record Type</th><th>Values</th></tr>
                {''.join(f"<tr><td>{rtype}</td><td>{', '.join(values[:5])}{'...' if len(values) > 5 else ''}</td></tr>" for rtype, values in data.get('dns_records', {}).get('records', {}).items() if values)}
            </table>
        </div>
        
        <div class="section">
            <h2>🖥️ Technologies Detected</h2>
            <ul>
                {''.join(f"<li>{tech}</li>" for tech in data.get('technologies', []))}
            </ul>
        </div>
        
        <div class="section">
            <h2>⚠️ Vulnerabilities</h2>
            {''.join(f"<div class='vulnerability'><strong>{vuln.get('type', 'Unknown')}</strong><br><span class='critical'>URL: {vuln.get('url', 'N/A')}</span><br>Payload: {vuln.get('payload', 'N/A')}<br>Evidence: {vuln.get('evidence', 'N/A')}</div>" for vuln in data.get('vulnerabilities', [])) if data.get('vulnerabilities') else "<p>No vulnerabilities found.</p>"}
        </div>
        
        <div class="section">
            <h2>🏢 Hosting Information</h2>
            <p><strong>IP:</strong> {data.get('hosting_info', {}).get('ip', 'Unknown')}</p>
            <p><strong>Provider:</strong> {data.get('hosting_info', {}).get('hosting_provider', 'Unknown')}</p>
            <p><strong>CDN:</strong> {data.get('hosting_info', {}).get('cdn', 'Unknown')}</p>
            <p><strong>Server Type:</strong> {data.get('hosting_info', {}).get('server_type', 'Unknown')}</p>
        </div>
        
        <div class="section">
            <h2>📂 Discovered Directories</h2>
            <table>
                <tr><th>Path</th><th>Status</th><th>Size</th></tr>
                {''.join(f"<tr><td>{dir_info.get('path', '')}</td><td>{dir_info.get('status', 'Unknown')}</td><td>{dir_info.get('size', 'Unknown')}</td></tr>" for dir_info in data.get('directories', []))}
            </table>
        </div>
        
        <div class="footer">
            <p>Report generated by ShadowGhost v1.0</p>
            <p style="color: #666; font-size: 12px;">For educational and authorized testing purposes only</p>
        </div>
    </div>
</body>
</html>"""
        
        with open(filename, 'w') as f:
            f.write(html)
        print(f"[+] HTML report saved: {filename}")
    
    def generate_markdown(self, data, filename):
        """Generate Markdown report"""
        md = f"""# 👻 ShadowGhost Reconnaissance Report

## Target Information
- **Target:** {data.get('target', 'Unknown')}
- **Domain:** {data.get('domain', 'Unknown')}
- **Scan Type:** {data.get('scan_type', 'Full')}
- **Scan Date:** {data.get('timestamp', 'Unknown')}
- **Duration:** {data.get('scan_duration', 0):.2f} seconds

## Executive Summary
- **Vulnerabilities:** {len(data.get('vulnerabilities', []))}
- **Open Ports:** {len(data.get('open_ports', {}))}
- **Subdomains:** {len(data.get('subdomains', []))}
- **Technologies:** {len(data.get('technologies', []))}
- **Directories:** {len(data.get('directories', []))}

## Open Ports
| Port | Service | Banner |
|------|---------|--------|
"""
        for port, info in data.get('open_ports', {}).items():
            md += f"| {port} | {info.get('service', 'Unknown')} | {info.get('banner', 'N/A')[:50]} |\n"
        
        md += "\n## DNS Records\n"
        for rtype, values in data.get('dns_records', {}).get('records', {}).items():
            if values:
                md += f"- **{rtype}:** {', '.join(values[:3])}\n"
        
        md += "\n## Technologies Detected\n"
        for tech in data.get('technologies', []):
            md += f"- {tech}\n"
        
        md += "\n## Vulnerabilities Found\n"
        if data.get('vulnerabilities'):
            for vuln in data.get('vulnerabilities', []):
                md += f"""### {vuln.get('type', 'Unknown')}
- **URL:** {vuln.get('url', 'N/A')}
- **Payload:** {vuln.get('payload', 'N/A')}
- **Evidence:** {vuln.get('evidence', 'N/A')}
"""
        else:
            md += "✅ No vulnerabilities found.\n"
        
        md += "\n## Hosting Information\n"
        hosting = data.get('hosting_info', {})
        md += f"- **IP:** {hosting.get('ip', 'Unknown')}\n"
        md += f"- **Provider:** {hosting.get('hosting_provider', 'Unknown')}\n"
        md += f"- **CDN:** {hosting.get('cdn', 'Unknown')}\n"
        md += f"- **Server Type:** {hosting.get('server_type', 'Unknown')}\n"
        
        md += "\n## Discovered Directories\n"
        for dir_info in data.get('directories', []):
            md += f"- {dir_info.get('path', '')} (Status: {dir_info.get('status', 'Unknown')})\n"
        
        md += f"""
---
*Report generated by ShadowGhost v1.0*
*For educational and authorized testing purposes only*
"""
        
        with open(filename, 'w') as f:
            f.write(md)
        print(f"[+] Markdown report saved: {filename}")
    
    def generate_json(self, data, filename):
        """Generate JSON report"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"[+] JSON report saved: {filename}")
    
    def generate_txt(self, data, filename):
        """Generate plain text report"""
        txt = f"""
SHADOWGHOST RECONNAISSANCE REPORT
================================

TARGET INFORMATION
------------------
Target: {data.get('target', 'Unknown')}
Domain: {data.get('domain', 'Unknown')}
Scan Type: {data.get('scan_type', 'Full')}
Scan Date: {data.get('timestamp', 'Unknown')}
Duration: {data.get('scan_duration', 0):.2f} seconds

EXECUTIVE SUMMARY
-----------------
Vulnerabilities Found: {len(data.get('vulnerabilities', []))}
Open Ports: {len(data.get('open_ports', {}))}
Subdomains: {len(data.get('subdomains', []))}
Technologies: {len(data.get('technologies', []))}
Directories: {len(data.get('directories', []))}
Emails Found: {len(data.get('emails', []))}
Links Found: {len(data.get('links', []))}

OPEN PORTS
----------
"""
        for port, info in data.get('open_ports', {}).items():
            txt += f"  {port}: {info.get('service', 'Unknown')} - {info.get('banner', 'N/A')[:50]}\n"
        
        txt += """
VULNERABILITIES
--------------
"""
        if data.get('vulnerabilities'):
            for vuln in data.get('vulnerabilities', []):
                txt += f"  [{vuln.get('type', 'Unknown')}] {vuln.get('url', 'N/A')}\n"
                txt += f"    Payload: {vuln.get('payload', 'N/A')}\n"
                txt += f"    Evidence: {vuln.get('evidence', 'N/A')}\n"
        else:
            txt += "  No vulnerabilities found.\n"
        
        txt += """
TECHNOLOGIES
-----------
"""
        for tech in data.get('technologies', []):
            if isinstance(tech, dict):
                txt += f"  {tech.get('name', 'Unknown')}: {tech.get('version', 'Unknown')}\n"
            else:
                txt += f"  {tech}\n"
        
        txt += """
DNS RECORDS
----------
"""
        for rtype, values in data.get('dns_records', {}).get('records', {}).items():
            if values:
                txt += f"  {rtype}: {', '.join(values[:3])}\n"
        
        txt += """
HOSTING INFORMATION
------------------
"""
        hosting = data.get('hosting_info', {})
        txt += f"  IP: {hosting.get('ip', 'Unknown')}\n"
        txt += f"  Provider: {hosting.get('hosting_provider', 'Unknown')}\n"
        txt += f"  CDN: {hosting.get('cdn', 'Unknown')}\n"
        txt += f"  Server Type: {hosting.get('server_type', 'Unknown')}\n"
        
        if data.get('emails'):
            txt += "\nEMAILS FOUND\n-----------\n"
            for email in data.get('emails', []):
                txt += f"  {email}\n"
        
        if data.get('sensitive_files'):
            txt += "\nSENSITIVE FILES\n--------------\n"
            for file_info in data.get('sensitive_files', []):
                txt += f"  {file_info.get('file', 'Unknown')}: {file_info.get('url', 'N/A')}\n"
        
        if data.get('links'):
            txt += "\nLINKS FOUND\n----------\n"
            for link in data.get('links', [])[:20]:
                txt += f"  {link}\n"
            if len(data.get('links', [])) > 20:
                txt += f"  ... and {len(data.get('links', [])) - 20} more\n"
        
        txt += """
---
Report generated by ShadowGhost v1.0
For educational and authorized testing purposes only
"""
        
        with open(filename, 'w') as f:
            f.write(txt)
        print(f"[+] Text report saved: {filename}")
