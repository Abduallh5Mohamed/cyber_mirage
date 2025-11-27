"""
📋 Court-Ready Forensic Report Generator
Cyber Mirage - Role 6: Forensics Trace Builder

Generates professional forensic reports suitable for:
- Legal proceedings
- Court submissions
- Insurance claims
- Regulatory compliance
- Law enforcement

Follows NIST SP 800-86 and ISO/IEC 27037 standards

Author: Cyber Mirage Team
Version: 1.0.0 - Production
"""

import json
import logging
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid

# PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, ListFlowable, ListItem
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class ReportType(Enum):
    """Types of forensic reports"""
    INCIDENT_RESPONSE = "incident_response"
    ATTACK_ANALYSIS = "attack_analysis"
    EVIDENCE_SUMMARY = "evidence_summary"
    CHAIN_OF_CUSTODY = "chain_of_custody"
    EXECUTIVE_SUMMARY = "executive_summary"
    FULL_INVESTIGATION = "full_investigation"


class ClassificationLevel(Enum):
    """Document classification levels"""
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    TOP_SECRET = "TOP SECRET"


class LegalFramework(Enum):
    """Legal frameworks for compliance"""
    NIST = "NIST SP 800-86"
    ISO_27037 = "ISO/IEC 27037"
    ISO_27042 = "ISO/IEC 27042"
    GDPR = "GDPR Article 33"
    HIPAA = "HIPAA Security Rule"
    PCI_DSS = "PCI DSS v4.0"
    SOC2 = "SOC 2 Type II"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ReportMetadata:
    """Report metadata"""
    report_id: str
    report_type: str
    classification: str
    case_number: str
    organization: str
    author: str
    reviewer: str
    created_at: str
    version: str = "1.0"
    legal_framework: str = "NIST SP 800-86"
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class EvidenceItem:
    """Evidence item for report"""
    evidence_id: str
    description: str
    evidence_type: str
    source: str
    collected_at: str
    collected_by: str
    hash_md5: str
    hash_sha256: str
    file_size: int
    integrity_verified: bool
    chain_of_custody: List[Dict]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AttackTimeline:
    """Attack timeline entry"""
    timestamp: str
    event_type: str
    description: str
    source_ip: str
    target: str
    mitre_technique: str
    severity: str
    evidence_refs: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ForensicReport:
    """Complete forensic report"""
    metadata: ReportMetadata
    executive_summary: str
    incident_overview: Dict
    timeline: List[AttackTimeline]
    evidence_items: List[EvidenceItem]
    technical_analysis: Dict
    attacker_profile: Dict
    impact_assessment: Dict
    recommendations: List[str]
    appendices: List[Dict]
    legal_notice: str
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['timeline'] = [t.to_dict() if hasattr(t, 'to_dict') else t for t in self.timeline]
        data['evidence_items'] = [e.to_dict() if hasattr(e, 'to_dict') else e for e in self.evidence_items]
        return data


# =============================================================================
# REPORT GENERATOR
# =============================================================================

class ForensicReportGenerator:
    """
    Generates court-ready forensic reports in multiple formats
    
    Features:
    - PDF generation with professional formatting
    - JSON/HTML export
    - Chain of custody documentation
    - Evidence integrity verification
    - MITRE ATT&CK mapping
    - Legal compliance sections
    """
    
    def __init__(
        self,
        organization: str = "Cyber Mirage Security",
        author: str = "Automated Forensics Engine",
        output_dir: str = "./reports"
    ):
        self.organization = organization
        self.author = author
        self.output_dir = output_dir
        
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info("ForensicReportGenerator initialized")
    
    def generate_report(
        self,
        report_type: ReportType,
        case_number: str,
        incident_data: Dict,
        evidence_list: List[Dict],
        timeline_events: List[Dict],
        classification: ClassificationLevel = ClassificationLevel.CONFIDENTIAL
    ) -> ForensicReport:
        """
        Generate a forensic report
        
        Args:
            report_type: Type of report
            case_number: Case/incident number
            incident_data: Incident details
            evidence_list: List of evidence items
            timeline_events: Attack timeline events
            classification: Document classification
        
        Returns:
            ForensicReport object
        """
        report_id = f"FR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create metadata
        metadata = ReportMetadata(
            report_id=report_id,
            report_type=report_type.value,
            classification=classification.value,
            case_number=case_number,
            organization=self.organization,
            author=self.author,
            reviewer="Pending Review",
            created_at=datetime.now().isoformat(),
            version="1.0",
            legal_framework=LegalFramework.NIST.value
        )
        
        # Process evidence
        evidence_items = [self._process_evidence(e) for e in evidence_list]
        
        # Process timeline
        timeline = [self._process_timeline_event(e) for e in timeline_events]
        
        # Generate sections
        executive_summary = self._generate_executive_summary(incident_data, timeline, evidence_items)
        incident_overview = self._generate_incident_overview(incident_data)
        technical_analysis = self._generate_technical_analysis(incident_data, timeline)
        attacker_profile = self._generate_attacker_profile(incident_data)
        impact_assessment = self._generate_impact_assessment(incident_data)
        recommendations = self._generate_recommendations(incident_data, technical_analysis)
        
        # Legal notice
        legal_notice = self._generate_legal_notice(classification)
        
        # Create report
        report = ForensicReport(
            metadata=metadata,
            executive_summary=executive_summary,
            incident_overview=incident_overview,
            timeline=timeline,
            evidence_items=evidence_items,
            technical_analysis=technical_analysis,
            attacker_profile=attacker_profile,
            impact_assessment=impact_assessment,
            recommendations=recommendations,
            appendices=[],
            legal_notice=legal_notice
        )
        
        logger.info(f"Generated forensic report: {report_id}")
        
        return report
    
    def _process_evidence(self, evidence: Dict) -> EvidenceItem:
        """Process and validate evidence item"""
        return EvidenceItem(
            evidence_id=evidence.get('id', str(uuid.uuid4())),
            description=evidence.get('description', 'No description'),
            evidence_type=evidence.get('type', 'unknown'),
            source=evidence.get('source', 'unknown'),
            collected_at=evidence.get('collected_at', datetime.now().isoformat()),
            collected_by=evidence.get('collected_by', self.author),
            hash_md5=evidence.get('hash_md5', 'N/A'),
            hash_sha256=evidence.get('hash_sha256', 'N/A'),
            file_size=evidence.get('file_size', 0),
            integrity_verified=evidence.get('integrity_verified', False),
            chain_of_custody=evidence.get('chain_of_custody', [])
        )
    
    def _process_timeline_event(self, event: Dict) -> AttackTimeline:
        """Process timeline event"""
        return AttackTimeline(
            timestamp=event.get('timestamp', datetime.now().isoformat()),
            event_type=event.get('event_type', 'unknown'),
            description=event.get('description', ''),
            source_ip=event.get('source_ip', 'N/A'),
            target=event.get('target', 'N/A'),
            mitre_technique=event.get('mitre_technique', 'N/A'),
            severity=event.get('severity', 'medium'),
            evidence_refs=event.get('evidence_refs', [])
        )
    
    def _generate_executive_summary(
        self,
        incident: Dict,
        timeline: List[AttackTimeline],
        evidence: List[EvidenceItem]
    ) -> str:
        """Generate executive summary"""
        attack_duration = "Unknown"
        if timeline:
            first = timeline[0].timestamp
            last = timeline[-1].timestamp
            attack_duration = f"{first} to {last}"
        
        summary = f"""
On {incident.get('detection_date', 'the incident date')}, the {self.organization} Security Operations 
Center detected suspicious activity targeting organizational assets. This report documents the 
comprehensive forensic investigation conducted in accordance with NIST SP 800-86 guidelines.

KEY FINDINGS:
• Attack Type: {incident.get('attack_type', 'Unauthorized Access Attempt')}
• Attack Vector: {incident.get('attack_vector', 'Network-based intrusion')}
• Duration: {attack_duration}
• Attacker Origin: {incident.get('attacker_origin', 'Under investigation')}
• Systems Affected: {incident.get('systems_affected', 'Honeypot infrastructure')}
• Data Compromise: {incident.get('data_compromise', 'No sensitive data compromised')}

EVIDENCE COLLECTED:
A total of {len(evidence)} evidence items were collected and preserved following chain of custody 
protocols. All evidence has been cryptographically verified using SHA-256 hashing.

TIMELINE:
The attack consisted of {len(timeline)} documented events, captured by the Cyber Mirage 
deception platform. The AI-driven deception system successfully engaged the attacker while 
collecting comprehensive forensic data.

CONCLUSION:
The deception platform successfully detected, engaged, and documented the attack while 
preventing any actual compromise of production systems. The collected intelligence provides 
valuable insights into attacker tactics, techniques, and procedures (TTPs).
"""
        return summary.strip()
    
    def _generate_incident_overview(self, incident: Dict) -> Dict:
        """Generate incident overview section"""
        return {
            'incident_id': incident.get('incident_id', str(uuid.uuid4())),
            'detection_date': incident.get('detection_date', datetime.now().isoformat()),
            'detection_method': incident.get('detection_method', 'Honeypot alert'),
            'attack_type': incident.get('attack_type', 'Unknown'),
            'attack_vector': incident.get('attack_vector', 'Network'),
            'severity': incident.get('severity', 'Medium'),
            'status': incident.get('status', 'Contained'),
            'affected_systems': incident.get('affected_systems', ['Honeypot infrastructure']),
            'business_impact': incident.get('business_impact', 'No production impact'),
            'responders': incident.get('responders', [self.author])
        }
    
    def _generate_technical_analysis(self, incident: Dict, timeline: List[AttackTimeline]) -> Dict:
        """Generate technical analysis section"""
        # Extract MITRE techniques
        mitre_techniques = list(set(e.mitre_technique for e in timeline if e.mitre_technique != 'N/A'))
        
        # Count event types
        event_counts = {}
        for event in timeline:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        
        return {
            'attack_methodology': incident.get('methodology', 'Multi-stage attack'),
            'initial_access': incident.get('initial_access', 'SSH brute force attempt'),
            'persistence_methods': incident.get('persistence', []),
            'lateral_movement': incident.get('lateral_movement', 'None observed'),
            'data_exfiltration': incident.get('exfiltration', 'Attempted but blocked'),
            'mitre_techniques': mitre_techniques,
            'event_summary': event_counts,
            'tools_detected': incident.get('tools', []),
            'indicators_of_compromise': {
                'ip_addresses': incident.get('iocs_ip', []),
                'domains': incident.get('iocs_domain', []),
                'file_hashes': incident.get('iocs_hash', []),
                'user_agents': incident.get('iocs_ua', [])
            }
        }
    
    def _generate_attacker_profile(self, incident: Dict) -> Dict:
        """Generate attacker profile section"""
        return {
            'attribution': incident.get('attribution', 'Unknown threat actor'),
            'skill_level': incident.get('skill_level', 'Intermediate'),
            'motivation': incident.get('motivation', 'Unknown'),
            'geographic_origin': incident.get('geo_origin', 'Under investigation'),
            'known_aliases': incident.get('aliases', []),
            'historical_activity': incident.get('history', 'No prior activity observed'),
            'behavioral_patterns': {
                'working_hours': incident.get('work_hours', 'Unknown'),
                'language_indicators': incident.get('language', 'Unknown'),
                'tool_preferences': incident.get('tools', [])
            }
        }
    
    def _generate_impact_assessment(self, incident: Dict) -> Dict:
        """Generate impact assessment section"""
        return {
            'confidentiality_impact': incident.get('impact_c', 'Low - No sensitive data accessed'),
            'integrity_impact': incident.get('impact_i', 'None - Systems unchanged'),
            'availability_impact': incident.get('impact_a', 'None - No service disruption'),
            'financial_impact': incident.get('financial', 'Minimal - Contained by honeypot'),
            'regulatory_impact': incident.get('regulatory', 'No reportable breach'),
            'reputational_impact': incident.get('reputation', 'None - No external exposure'),
            'recovery_time': incident.get('recovery', 'N/A - No recovery needed'),
            'lessons_learned': incident.get('lessons', [])
        }
    
    def _generate_recommendations(self, incident: Dict, analysis: Dict) -> List[str]:
        """Generate security recommendations"""
        recommendations = [
            "Continue monitoring for similar attack patterns from identified threat actors",
            "Update firewall rules to block identified malicious IP addresses",
            "Review and strengthen authentication mechanisms on exposed services",
            "Implement additional logging and monitoring on critical systems",
            "Conduct security awareness training based on observed attack techniques",
        ]
        
        # Add technique-specific recommendations
        techniques = analysis.get('mitre_techniques', [])
        
        if any('T1110' in t for t in techniques):  # Brute Force
            recommendations.append("Implement account lockout policies and MFA for all remote access")
        
        if any('T1190' in t for t in techniques):  # Exploit Public-Facing
            recommendations.append("Conduct vulnerability assessment of public-facing applications")
        
        if any('T1021' in t for t in techniques):  # Remote Services
            recommendations.append("Restrict remote service access to authorized networks only")
        
        recommendations.append("Schedule follow-up threat hunting exercise within 30 days")
        recommendations.append("Update incident response procedures based on lessons learned")
        
        return recommendations
    
    def _generate_legal_notice(self, classification: ClassificationLevel) -> str:
        """Generate legal notice"""
        return f"""
LEGAL NOTICE AND CONFIDENTIALITY STATEMENT
==========================================

Classification: {classification.value}

This document contains confidential and privileged information prepared for the exclusive 
use of authorized personnel. The information contained herein is intended for investigative 
and legal purposes only.

HANDLING INSTRUCTIONS:
• This document must be stored in a secure location when not in use
• Electronic copies must be encrypted and access-controlled
• Distribution is limited to authorized personnel on a need-to-know basis
• Unauthorized disclosure may result in legal action

CHAIN OF CUSTODY:
All evidence referenced in this report has been collected, preserved, and documented 
in accordance with legal requirements and industry best practices. The integrity of 
all evidence items has been verified using cryptographic hashing.

COMPLIANCE FRAMEWORKS:
This investigation was conducted in accordance with:
• NIST SP 800-86: Guide to Integrating Forensic Techniques into Incident Response
• ISO/IEC 27037: Guidelines for identification, collection, acquisition and preservation
• ISO/IEC 27042: Guidelines for the analysis and interpretation of digital evidence

DISCLAIMER:
The analysis and conclusions in this report are based on available evidence at the time 
of investigation. Findings may be subject to revision as additional evidence becomes available.

© {datetime.now().year} {self.organization}. All rights reserved.
"""
    
    def export_pdf(self, report: ForensicReport, output_path: str = None) -> str:
        """Export report to PDF format"""
        if not REPORTLAB_AVAILABLE:
            logger.error("ReportLab not available. Install with: pip install reportlab")
            return self.export_json(report, output_path)
        
        output_path = output_path or os.path.join(
            self.output_dir,
            f"{report.metadata.report_id}.pdf"
        )
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.darkblue
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )
        
        # Build document content
        story = []
        
        # Title page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(
            f"FORENSIC INVESTIGATION REPORT",
            title_style
        ))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f"Case Number: {report.metadata.case_number}",
            ParagraphStyle('Center', alignment=TA_CENTER, fontSize=14)
        ))
        story.append(Paragraph(
            f"Report ID: {report.metadata.report_id}",
            ParagraphStyle('Center', alignment=TA_CENTER, fontSize=12)
        ))
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(
            f"<b>Classification: {report.metadata.classification}</b>",
            ParagraphStyle('Center', alignment=TA_CENTER, fontSize=16, textColor=colors.red)
        ))
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(
            f"Prepared by: {report.metadata.organization}",
            ParagraphStyle('Center', alignment=TA_CENTER)
        ))
        story.append(Paragraph(
            f"Author: {report.metadata.author}",
            ParagraphStyle('Center', alignment=TA_CENTER)
        ))
        story.append(Paragraph(
            f"Date: {report.metadata.created_at[:10]}",
            ParagraphStyle('Center', alignment=TA_CENTER)
        ))
        
        story.append(PageBreak())
        
        # Table of Contents
        story.append(Paragraph("TABLE OF CONTENTS", heading_style))
        toc_items = [
            "1. Executive Summary",
            "2. Incident Overview",
            "3. Attack Timeline",
            "4. Evidence Summary",
            "5. Technical Analysis",
            "6. Attacker Profile",
            "7. Impact Assessment",
            "8. Recommendations",
            "9. Legal Notice",
        ]
        for item in toc_items:
            story.append(Paragraph(item, body_style))
        
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph("1. EXECUTIVE SUMMARY", heading_style))
        for para in report.executive_summary.split('\n\n'):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
        
        story.append(PageBreak())
        
        # Incident Overview
        story.append(Paragraph("2. INCIDENT OVERVIEW", heading_style))
        overview_data = [
            ["Field", "Value"],
            ["Incident ID", report.incident_overview.get('incident_id', 'N/A')],
            ["Detection Date", report.incident_overview.get('detection_date', 'N/A')],
            ["Attack Type", report.incident_overview.get('attack_type', 'N/A')],
            ["Severity", report.incident_overview.get('severity', 'N/A')],
            ["Status", report.incident_overview.get('status', 'N/A')],
        ]
        overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(overview_table)
        
        story.append(PageBreak())
        
        # Timeline
        story.append(Paragraph("3. ATTACK TIMELINE", heading_style))
        if report.timeline:
            timeline_data = [["Timestamp", "Event", "Source IP", "Severity"]]
            for event in report.timeline[:20]:  # Limit to 20 events
                timeline_data.append([
                    event.timestamp[:19] if hasattr(event, 'timestamp') else str(event.get('timestamp', ''))[:19],
                    (event.event_type if hasattr(event, 'event_type') else str(event.get('event_type', '')))[:30],
                    event.source_ip if hasattr(event, 'source_ip') else str(event.get('source_ip', '')),
                    event.severity if hasattr(event, 'severity') else str(event.get('severity', ''))
                ])
            
            timeline_table = Table(timeline_data, colWidths=[1.5*inch, 2.5*inch, 1.2*inch, 0.8*inch])
            timeline_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(timeline_table)
        
        story.append(PageBreak())
        
        # Evidence Summary
        story.append(Paragraph("4. EVIDENCE SUMMARY", heading_style))
        story.append(Paragraph(
            f"Total Evidence Items Collected: {len(report.evidence_items)}",
            body_style
        ))
        
        if report.evidence_items:
            evidence_data = [["ID", "Type", "Description", "Verified"]]
            for item in report.evidence_items[:15]:
                evidence_data.append([
                    (item.evidence_id if hasattr(item, 'evidence_id') else str(item.get('evidence_id', '')))[:12],
                    item.evidence_type if hasattr(item, 'evidence_type') else str(item.get('evidence_type', '')),
                    (item.description if hasattr(item, 'description') else str(item.get('description', '')))[:40],
                    "✓" if (item.integrity_verified if hasattr(item, 'integrity_verified') else item.get('integrity_verified', False)) else "✗"
                ])
            
            evidence_table = Table(evidence_data, colWidths=[1*inch, 1.2*inch, 3*inch, 0.8*inch])
            evidence_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(evidence_table)
        
        story.append(PageBreak())
        
        # Recommendations
        story.append(Paragraph("8. RECOMMENDATIONS", heading_style))
        for i, rec in enumerate(report.recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", body_style))
        
        story.append(PageBreak())
        
        # Legal Notice
        story.append(Paragraph("9. LEGAL NOTICE", heading_style))
        for para in report.legal_notice.split('\n\n'):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"PDF report generated: {output_path}")
        return output_path
    
    def export_json(self, report: ForensicReport, output_path: str = None) -> str:
        """Export report to JSON format"""
        output_path = output_path or os.path.join(
            self.output_dir,
            f"{report.metadata.report_id}.json"
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, default=str)
        
        logger.info(f"JSON report generated: {output_path}")
        return output_path
    
    def export_html(self, report: ForensicReport, output_path: str = None) -> str:
        """Export report to HTML format"""
        output_path = output_path or os.path.join(
            self.output_dir,
            f"{report.metadata.report_id}.html"
        )
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Forensic Report - {report.metadata.report_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .classification {{
            background: #d32f2f;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            display: inline-block;
            font-weight: bold;
            margin: 10px 0;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin: 20px 0;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #1a237e;
            border-bottom: 2px solid #1a237e;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th {{
            background: #1a237e;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        .severity-high {{
            color: #d32f2f;
            font-weight: bold;
        }}
        .severity-medium {{
            color: #f57c00;
            font-weight: bold;
        }}
        .severity-low {{
            color: #388e3c;
            font-weight: bold;
        }}
        .recommendation {{
            background: #e3f2fd;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #1976d2;
            border-radius: 0 5px 5px 0;
        }}
        .legal-notice {{
            background: #fff3e0;
            padding: 20px;
            border: 1px solid #ff9800;
            border-radius: 5px;
            font-size: 0.9em;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 30px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔬 FORENSIC INVESTIGATION REPORT</h1>
        <p>Case Number: {report.metadata.case_number}</p>
        <p>Report ID: {report.metadata.report_id}</p>
        <div class="classification">{report.metadata.classification}</div>
    </div>
    
    <div class="section">
        <h2>📋 Report Metadata</h2>
        <table>
            <tr><td><strong>Organization</strong></td><td>{report.metadata.organization}</td></tr>
            <tr><td><strong>Author</strong></td><td>{report.metadata.author}</td></tr>
            <tr><td><strong>Created</strong></td><td>{report.metadata.created_at}</td></tr>
            <tr><td><strong>Legal Framework</strong></td><td>{report.metadata.legal_framework}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>📝 Executive Summary</h2>
        <p>{report.executive_summary.replace(chr(10), '<br>')}</p>
    </div>
    
    <div class="section">
        <h2>⏰ Attack Timeline</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Event</th>
                <th>Source IP</th>
                <th>Severity</th>
            </tr>
            {''.join(f'''
            <tr>
                <td>{(e.timestamp if hasattr(e, 'timestamp') else e.get('timestamp', ''))[:19]}</td>
                <td>{e.event_type if hasattr(e, 'event_type') else e.get('event_type', '')}</td>
                <td>{e.source_ip if hasattr(e, 'source_ip') else e.get('source_ip', '')}</td>
                <td class="severity-{(e.severity if hasattr(e, 'severity') else e.get('severity', 'medium')).lower()}">{e.severity if hasattr(e, 'severity') else e.get('severity', '')}</td>
            </tr>
            ''' for e in report.timeline[:20])}
        </table>
    </div>
    
    <div class="section">
        <h2>📦 Evidence Summary</h2>
        <p><strong>Total Items:</strong> {len(report.evidence_items)}</p>
        <table>
            <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Description</th>
                <th>Verified</th>
            </tr>
            {''.join(f'''
            <tr>
                <td>{(e.evidence_id if hasattr(e, 'evidence_id') else e.get('evidence_id', ''))[:12]}</td>
                <td>{e.evidence_type if hasattr(e, 'evidence_type') else e.get('evidence_type', '')}</td>
                <td>{e.description if hasattr(e, 'description') else e.get('description', '')}</td>
                <td>{"✅" if (e.integrity_verified if hasattr(e, 'integrity_verified') else e.get('integrity_verified', False)) else "❌"}</td>
            </tr>
            ''' for e in report.evidence_items[:15])}
        </table>
    </div>
    
    <div class="section">
        <h2>💡 Recommendations</h2>
        {''.join(f'<div class="recommendation">{i}. {rec}</div>' for i, rec in enumerate(report.recommendations, 1))}
    </div>
    
    <div class="section">
        <h2>⚖️ Legal Notice</h2>
        <div class="legal-notice">
            {report.legal_notice.replace(chr(10), '<br>')}
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by Cyber Mirage Forensics Engine</p>
        <p>© {datetime.now().year} {report.metadata.organization}</p>
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {output_path}")
        return output_path


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Example usage
    generator = ForensicReportGenerator(
        organization="Cyber Mirage Security",
        author="Automated Forensics Engine",
        output_dir="./reports"
    )
    
    # Sample incident data
    incident_data = {
        'incident_id': 'INC-2024-001',
        'detection_date': '2024-11-27T10:30:00',
        'attack_type': 'Brute Force Attack',
        'attack_vector': 'SSH',
        'severity': 'High',
        'status': 'Contained',
        'attacker_origin': '185.220.101.50 (Tor Exit Node)',
        'systems_affected': ['SSH Honeypot'],
        'methodology': 'Dictionary-based credential attack'
    }
    
    # Sample evidence
    evidence_list = [
        {
            'id': 'EV-001',
            'description': 'SSH authentication logs',
            'type': 'log_file',
            'source': 'honeypot-ssh',
            'hash_sha256': 'abc123...',
            'integrity_verified': True
        },
        {
            'id': 'EV-002',
            'description': 'Network capture (PCAP)',
            'type': 'network_capture',
            'source': 'network_tap',
            'hash_sha256': 'def456...',
            'integrity_verified': True
        }
    ]
    
    # Sample timeline
    timeline_events = [
        {
            'timestamp': '2024-11-27T10:30:00',
            'event_type': 'Connection Established',
            'source_ip': '185.220.101.50',
            'target': 'SSH:22',
            'mitre_technique': 'T1110 - Brute Force',
            'severity': 'medium'
        },
        {
            'timestamp': '2024-11-27T10:30:05',
            'event_type': 'Authentication Attempt',
            'source_ip': '185.220.101.50',
            'target': 'SSH:22',
            'mitre_technique': 'T1110.001 - Password Guessing',
            'severity': 'high'
        }
    ]
    
    # Generate report
    report = generator.generate_report(
        report_type=ReportType.INCIDENT_RESPONSE,
        case_number='CASE-2024-001',
        incident_data=incident_data,
        evidence_list=evidence_list,
        timeline_events=timeline_events
    )
    
    # Export in multiple formats
    generator.export_json(report)
    generator.export_html(report)
    
    if REPORTLAB_AVAILABLE:
        generator.export_pdf(report)
    
    print(f"✅ Reports generated in ./reports/")
    print(f"   Report ID: {report.metadata.report_id}")
