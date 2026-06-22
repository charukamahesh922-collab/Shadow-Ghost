#!/usr/bin/env python3
"""
Report Generator Module
Generate comprehensive HTML and Markdown reports
"""

import json
from datetime import datetime

class ReportGenerator:
    """Generate detailed reconnaissance reports"""
    
    def generate_html(self, data, filename):
        """Generate HTML report"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>ShadowGhost Report - {data['domain']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #0a0a0a; color: #00ff00; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1a1a1a, #000000); padding: 20px; border: 1px solid #00ff00; }}
        .section {{ background: #1a1a1a; margin: 20px 0; padding: 20px; border: 1px solid #003300; }}
        .vulnerability {{ background: #330000; border: 1px solid #ff0000; padding: 10px; margin: 10px 0; }}
        .finding {{ background: #001a00; border: 1px solid #00ff00; padding: 10px; margin: 10px 0; }}
        .critical {{ color: #ff0000; }}
        .high {{ color: #ff6600; }}
        .medium {{ color: #ffcc00; }}
        .low {{ color: #66ff66; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #003300; padding: 8px; text-align: left; }}
        th {{ background: #002200; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👻 ShadowGhost Reconnaissance Report</h1>
            <p><strong>Target:</strong> {data['target']}</p>
            <p><strong>Domain:</strong> {data['domain']}</p>
            <p><strong>Scan Date:</strong> {data['timestamp']}</p>
            <p><strong>Duration:</strong> {data.get('scan_duration', 0):.2f} seconds</p>
        </div>
        
        <div class="section">
            <h2>🎯 Executive Summary</h2>
            <p>Total Vulnerabilities Found: {len(data.get('vulnerabilities', []))}</p>
            <p>Open Ports: {len(data.get('open_ports', {}))}</p>
            <p>Subdomains Discovered: {len(data.get('subdomains', []))}</p>
            <p>
