"""
Module 5 Automated Reporting Engine
Generates and delivers automated reports for IRAQAF platform
"""

import json
import logging
import smtplib
import schedule
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import requests

# PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie

# Template engine
from jinja2 import Template, Environment, FileSystemLoader

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Automated report generation system"""
    
    def __init__(self, config_file: str = "config/reporting.json"):
        self.config_file = Path(config_file)
        self.reports_dir = Path("reports/generated")
        self.templates_dir = Path("templates/reports")
        
        # Create directories
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
        
        # Hub URLs for data collection
        self.hub_urls = {
            "l1": "http://localhost:8504",
            "l2": "http://localhost:8502", 
            "l3_fairness": "http://localhost:8506",
            "l4": "http://localhost:5000",
            "soqm": "http://localhost:8503",
            "uqo": "http://localhost:8507",
            "cae": "http://localhost:8508"
        }
    
    def _load_config(self) -> Dict:
        """Load reporting configuration"""
        default_config = {
            "daily_report": {
                "enabled": True,
                "time": "08:00",
                "recipients": ["ops@company.com"],
                "format": "pdf",
                "include_charts": True
            },
            "weekly_report": {
                "enabled": True,
                "day": "monday",
                "time": "09:00",
                "recipients": ["qa@company.com", "management@company.com"],
                "format": "pdf",
                "include_trends": True
            },
            "monthly_report": {
                "enabled": True,
                "day": 1,
                "time": "10:00",
                "recipients": ["compliance@company.com", "management@company.com"],
                "format": "pdf",
                "detailed": True
            },
            "quarterly_report": {
                "enabled": True,
                "months": [1, 4, 7, 10],
                "day": 1,
                "time": "11:00",
                "recipients": ["executives@company.com"],
                "format": "pdf",
                "executive_summary": True
            },
            "smtp": {
                "server": "smtp.gmail.com",
                "port": 587,
                "username": "",
                "password": "",
                "use_tls": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                logger.error(f"Error loading reporting config: {e}")
                return default_config
        else:
            # Create default config
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def collect_hub_data(self) -> Dict[str, Any]:
        """Collect data from all hubs"""
        data = {}
        
        for hub_name, base_url in self.hub_urls.items():
            try:
                # Collect key metrics from each hub
                if hub_name == "l1":
                    response = requests.get(f"{base_url}/api/crs", timeout=5)
                    if response.status_code == 200:
                        data[hub_name] = response.json()
                
                elif hub_name == "l2":
                    response = requests.get(f"{base_url}/api/sai", timeout=5)
                    if response.status_code == 200:
                        data[hub_name] = response.json()
                
                elif hub_name == "l3_fairness":
                    response = requests.get(f"{base_url}/api/summary", timeout=5)
                    if response.status_code == 200:
                        data[hub_name] = response.json()
                
                elif hub_name == "l4":
                    response = requests.get(f"{base_url}/api/transparency-score", timeout=5)
                    if response.status_code == 200:
                        data[hub_name] = response.json()
                
                elif hub_name == "soqm":
                    response = requests.get(f"{base_url}/api/status", timeout=5)
                    if response.status_code == 200:
                        data[hub_name] = response.json()
                
                elif hub_name == "uqo":
                    response = requests.get(f"{base_url}/api/qa-overview", timeout=5)
                    if response.status_code == 200:
                        data[hub_name] = response.json()
                
                elif hub_name == "cae":
                    response = requests.get(f"{base_url}/api/internal-cqs", timeout=5)
                    if response.status_code == 200:
                        data[hub_name] = response.json()
            
            except Exception as e:
                logger.warning(f"Could not collect data from {hub_name}: {e}")
                data[hub_name] = {"error": str(e), "status": "offline"}
        
        return data
    
    def generate_daily_report(self) -> str:
        """Generate daily operations report"""
        logger.info("Generating daily operations report")
        
        # Collect current data
        hub_data = self.collect_hub_data()
        
        # Prepare report data
        report_data = {
            "report_type": "Daily Operations Report",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "hub_data": hub_data,
            "summary": self._generate_daily_summary(hub_data)
        }
        
        # Generate PDF
        filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath = self.reports_dir / filename
        
        self._create_pdf_report(report_data, str(filepath), "daily")
        
        return str(filepath)
    
    def generate_weekly_report(self) -> str:
        """Generate weekly QA report"""
        logger.info("Generating weekly QA report")
        
        # Collect data for the past week
        hub_data = self.collect_hub_data()
        
        # Load historical data for trends
        historical_data = self._load_historical_data(days=7)
        
        report_data = {
            "report_type": "Weekly QA Report",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "week_ending": datetime.now().strftime("%Y-%m-%d"),
            "hub_data": hub_data,
            "trends": self._calculate_trends(historical_data),
            "summary": self._generate_weekly_summary(hub_data, historical_data)
        }
        
        filename = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath = self.reports_dir / filename
        
        self._create_pdf_report(report_data, str(filepath), "weekly")
        
        return str(filepath)
    
    def generate_monthly_report(self) -> str:
        """Generate monthly compliance report"""
        logger.info("Generating monthly compliance report")
        
        hub_data = self.collect_hub_data()
        historical_data = self._load_historical_data(days=30)
        
        report_data = {
            "report_type": "Monthly Compliance Report",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "month": datetime.now().strftime("%B %Y"),
            "hub_data": hub_data,
            "compliance_summary": self._generate_compliance_summary(hub_data),
            "trends": self._calculate_trends(historical_data),
            "recommendations": self._generate_recommendations(hub_data)
        }
        
        filename = f"monthly_report_{datetime.now().strftime('%Y%m')}.pdf"
        filepath = self.reports_dir / filename
        
        self._create_pdf_report(report_data, str(filepath), "monthly")
        
        return str(filepath)
    
    def generate_quarterly_report(self) -> str:
        """Generate quarterly executive report"""
        logger.info("Generating quarterly executive report")
        
        hub_data = self.collect_hub_data()
        historical_data = self._load_historical_data(days=90)
        
        report_data = {
            "report_type": "Quarterly Executive Report",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "quarter": f"Q{((datetime.now().month-1)//3)+1} {datetime.now().year}",
            "executive_summary": self._generate_executive_summary(hub_data, historical_data),
            "key_metrics": self._extract_key_metrics(hub_data),
            "risk_assessment": self._generate_risk_assessment(hub_data),
            "strategic_recommendations": self._generate_strategic_recommendations(hub_data)
        }
        
        filename = f"quarterly_report_Q{((datetime.now().month-1)//3)+1}_{datetime.now().year}.pdf"
        filepath = self.reports_dir / filename
        
        self._create_pdf_report(report_data, str(filepath), "quarterly")
        
        return str(filepath)
    
    def _create_pdf_report(self, data: Dict, filepath: str, report_type: str):
        """Create PDF report using ReportLab"""
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50')
        )
        story.append(Paragraph(data["report_type"], title_style))
        story.append(Spacer(1, 12))
        
        # Generated timestamp
        story.append(Paragraph(f"Generated: {data['generated_at']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        if report_type == "daily":
            self._add_daily_content(story, data, styles)
        elif report_type == "weekly":
            self._add_weekly_content(story, data, styles)
        elif report_type == "monthly":
            self._add_monthly_content(story, data, styles)
        elif report_type == "quarterly":
            self._add_quarterly_content(story, data, styles)
        
        # Build PDF
        doc.build(story)
        logger.info(f"PDF report created: {filepath}")
    
    def _add_daily_content(self, story: List, data: Dict, styles):
        """Add daily report content"""
        # Hub Status Summary
        story.append(Paragraph("Hub Status Summary", styles['Heading2']))
        
        hub_status_data = [["Hub", "Status", "Key Metric", "Value"]]
        for hub_name, hub_info in data["hub_data"].items():
            if "error" in hub_info:
                status = "Offline"
                metric = "N/A"
                value = "N/A"
            else:
                status = "Online"
                # Extract key metric based on hub
                if hub_name == "l1" and "crs" in hub_info:
                    metric = "CRS"
                    value = f"{hub_info['crs']:.1f}%"
                elif hub_name == "l2" and "sai" in hub_info:
                    metric = "SAI"
                    value = f"{hub_info['sai']:.1f}%"
                elif hub_name == "uqo" and "cqs" in hub_info:
                    metric = "CQS"
                    value = f"{hub_info['cqs']:.1f}%"
                else:
                    metric = "Status"
                    value = "OK"
            
            hub_status_data.append([hub_name.upper(), status, metric, value])
        
        table = Table(hub_status_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Summary
        if "summary" in data:
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            story.append(Paragraph(data["summary"], styles['Normal']))
    
    def _generate_daily_summary(self, hub_data: Dict) -> str:
        """Generate daily summary text"""
        online_hubs = sum(1 for hub in hub_data.values() if "error" not in hub)
        total_hubs = len(hub_data)
        
        summary = f"System Status: {online_hubs}/{total_hubs} hubs online. "
        
        # Add key metrics if available
        if "uqo" in hub_data and "cqs" in hub_data["uqo"]:
            cqs = hub_data["uqo"]["cqs"]
            summary += f"Overall CQS: {cqs:.1f}%. "
            
            if cqs >= 80:
                summary += "System performance is excellent."
            elif cqs >= 70:
                summary += "System performance is good."
            elif cqs >= 60:
                summary += "System performance needs attention."
            else:
                summary += "System performance requires immediate action."
        
        return summary
    
    def _load_historical_data(self, days: int) -> List[Dict]:
        """Load historical QA data"""
        try:
            history_file = Path("qa_history/qa_history.jsonl")
            if not history_file.exists():
                return []
            
            cutoff_date = datetime.now() - timedelta(days=days)
            historical_data = []
            
            with open(history_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        entry_date = datetime.fromisoformat(entry["timestamp"])
                        if entry_date >= cutoff_date:
                            historical_data.append(entry)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
            
            return historical_data
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            return []
    
    def send_report(self, filepath: str, recipients: List[str], subject: str):
        """Send report via email"""
        if not self.config["smtp"]["username"] or not self.config["smtp"]["password"]:
            logger.warning("SMTP credentials not configured, skipping email delivery")
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config["smtp"]["username"]
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject
            
            # Add body
            body = f"Please find the attached {subject.lower()}."
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachment
            with open(filepath, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {Path(filepath).name}'
            )
            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.config["smtp"]["server"], self.config["smtp"]["port"])
            if self.config["smtp"]["use_tls"]:
                server.starttls()
            server.login(self.config["smtp"]["username"], self.config["smtp"]["password"])
            server.sendmail(self.config["smtp"]["username"], recipients, msg.as_string())
            server.quit()
            
            logger.info(f"Report sent to {recipients}")
        
        except Exception as e:
            logger.error(f"Error sending report: {e}")
    
    def _calculate_trends(self, historical_data: List[Dict]) -> Dict:
        """Calculate trends from historical data"""
        if len(historical_data) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate CQS trend
        cqs_values = [entry.get("cqs", 0) for entry in historical_data if "cqs" in entry]
        if len(cqs_values) >= 2:
            trend = "improving" if cqs_values[-1] > cqs_values[0] else "declining"
            change = cqs_values[-1] - cqs_values[0]
            return {
                "cqs_trend": trend,
                "cqs_change": change,
                "data_points": len(cqs_values)
            }
        
        return {"trend": "no_data"}
    
    def start_scheduler(self):
        """Start the automated reporting scheduler"""
        # Schedule daily reports
        if self.config["daily_report"]["enabled"]:
            schedule.every().day.at(self.config["daily_report"]["time"]).do(
                self._run_daily_report
            )
        
        # Schedule weekly reports
        if self.config["weekly_report"]["enabled"]:
            getattr(schedule.every(), self.config["weekly_report"]["day"]).at(
                self.config["weekly_report"]["time"]
            ).do(self._run_weekly_report)
        
        # Schedule monthly reports
        if self.config["monthly_report"]["enabled"]:
            schedule.every().month.do(self._run_monthly_report)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Automated reporting scheduler started")
    
    def _run_daily_report(self):
        """Run daily report generation and delivery"""
        try:
            filepath = self.generate_daily_report()
            if self.config["daily_report"]["recipients"]:
                self.send_report(
                    filepath,
                    self.config["daily_report"]["recipients"],
                    f"IRAQAF Daily Operations Report - {datetime.now().strftime('%Y-%m-%d')}"
                )
        except Exception as e:
            logger.error(f"Error in daily report generation: {e}")
    
    def _run_weekly_report(self):
        """Run weekly report generation and delivery"""
        try:
            filepath = self.generate_weekly_report()
            if self.config["weekly_report"]["recipients"]:
                self.send_report(
                    filepath,
                    self.config["weekly_report"]["recipients"],
                    f"IRAQAF Weekly QA Report - Week ending {datetime.now().strftime('%Y-%m-%d')}"
                )
        except Exception as e:
            logger.error(f"Error in weekly report generation: {e}")
    
    def _run_monthly_report(self):
        """Run monthly report generation and delivery"""
        try:
            filepath = self.generate_monthly_report()
            if self.config["monthly_report"]["recipients"]:
                self.send_report(
                    filepath,
                    self.config["monthly_report"]["recipients"],
                    f"IRAQAF Monthly Compliance Report - {datetime.now().strftime('%B %Y')}"
                )
        except Exception as e:
            logger.error(f"Error in monthly report generation: {e}")

# Global report generator instance
report_generator = ReportGenerator()

def get_report_generator() -> ReportGenerator:
    """Get the global report generator instance"""
    return report_generator

if __name__ == "__main__":
    # Test report generation
    generator = ReportGenerator()
    
    print("Testing daily report generation...")
    filepath = generator.generate_daily_report()
    print(f"Daily report generated: {filepath}")
    
    print("Testing data collection...")
    data = generator.collect_hub_data()
    print(f"Collected data from {len(data)} hubs")
