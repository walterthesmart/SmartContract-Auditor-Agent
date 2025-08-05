"""PDF report generator for audit results."""

import datetime
import io
import tempfile
from typing import Dict, List, Optional, Union

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Paragraph, 
    SimpleDocTemplate, 
    Spacer, 
    Table, 
    TableStyle, 
    Image, 
    PageBreak
)
from reportlab.lib.units import inch
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


class CodeSnippet(Flowable):
    """Custom flowable for code snippets with syntax highlighting."""
    
    def __init__(self, code_text, language="solidity", width=None, height=None):
        """
        Initialize the code snippet.
        
        Args:
            code_text: The code text to display
            language: The programming language (for syntax highlighting)
            width: Width of the snippet
            height: Height of the snippet
        """
        Flowable.__init__(self)
        self.code_text = code_text
        self.language = language
        self.width = width
        self.height = height
        
        # Default styles
        self.background_color = colors.whitesmoke
        self.border_color = colors.lightgrey
        self.text_color = colors.black
        self.font_name = "Courier"
        self.font_size = 8
        
    def draw(self):
        """Draw the code snippet on the canvas."""
        # Draw background
        self.canv.setFillColor(self.background_color)
        self.canv.setStrokeColor(self.border_color)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=1)
        
        # Draw text
        self.canv.setFillColor(self.text_color)
        self.canv.setFont(self.font_name, self.font_size)
        
        # Split text into lines
        lines = self.code_text.split('\n')
        y = self.height - 15  # Start from top with padding
        
        for line in lines:
            # Handle indentation
            indent = len(line) - len(line.lstrip())
            indented_line = ' ' * indent + line.lstrip()
            
            self.canv.drawString(10, y, indented_line)
            y -= 12  # Line spacing
            
            if y < 10:  # Stop if we run out of space
                break


class ReportGenerator:
    """Generates PDF audit reports for smart contracts."""
    
    def __init__(self, logo_path: Optional[str] = None):
        """
        Initialize the report generator.
        
        Args:
            logo_path: Path to logo image for the report header
        """
        self.logo_path = logo_path
        self.styles = getSampleStyleSheet()
        
        # Create custom styles with unique names to avoid conflicts
        self.styles.add(
            ParagraphStyle(
                name='CustomHeading1',
                parent=self.styles['Heading1'],
                fontSize=18,
                spaceAfter=12
            )
        )
        self.styles.add(
            ParagraphStyle(
                name='CustomHeading2',
                parent=self.styles['Heading2'],
                fontSize=14,
                spaceAfter=10
            )
        )
        self.styles.add(
            ParagraphStyle(
                name='CustomHeading3',
                parent=self.styles['Heading3'],
                fontSize=12,
                spaceAfter=8
            )
        )
        self.styles.add(
            ParagraphStyle(
                name='CustomNormal',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=6
            )
        )
        self.styles.add(
            ParagraphStyle(
                name='CustomCode',
                parent=self.styles['Code'],
                fontName='Courier',
                fontSize=8,
                spaceAfter=8
            )
        )
        self.styles.add(
            ParagraphStyle(
                name='CustomFooter',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey
            )
        )
    
    def generate_pdf(self, audit_data: Dict) -> bytes:
        """
        Generate a PDF report from audit data.
        
        Args:
            audit_data: Dictionary containing audit results
            
        Returns:
            PDF report as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build the document
        elements = []
        
        # Add header
        self._add_header(elements, audit_data)
        
        # Add summary
        self._add_summary(elements, audit_data)
        
        # Add vulnerability table
        self._add_vulnerability_table(elements, audit_data)
        
        # Add detailed findings
        self._add_detailed_findings(elements, audit_data)
        
        # Add footer
        self._add_footer(elements, audit_data)
        
        # Build the PDF
        doc.build(elements)
        
        # Get the PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _add_header(self, elements: List, audit_data: Dict) -> None:
        """
        Add header to the report.
        
        Args:
            elements: List of elements to add to
            audit_data: Dictionary containing audit results
        """
        # Add logo if available
        if self.logo_path:
            elements.append(Image(self.logo_path, width=2*inch, height=0.5*inch))
        
        # Add title
        contract_name = audit_data.get("contract_metadata", {}).get("name", "Unnamed Contract")
        elements.append(Paragraph(f"Smart Contract Audit Report", self.styles["CustomHeading1"]))
        elements.append(Paragraph(f"{contract_name}", self.styles["CustomHeading2"]))
        
        # Add date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        elements.append(Paragraph(f"Audit Date: {current_date}", self.styles["CustomNormal"]))
        elements.append(Spacer(1, 0.25*inch))
    
    def _add_summary(self, elements: List, audit_data: Dict) -> None:
        """
        Add summary to the report.
        
        Args:
            elements: List of elements to add to
            audit_data: Dictionary containing audit results
        """
        elements.append(Paragraph("Audit Summary", self.styles["CustomHeading2"]))
        
        # Calculate statistics
        vulnerabilities = audit_data.get("vulnerabilities", [])
        total_vulns = len(vulnerabilities)
        high_vulns = sum(1 for v in vulnerabilities if v.get("severity_level_value", 0) == 3)
        medium_vulns = sum(1 for v in vulnerabilities if v.get("severity_level_value", 0) == 2)
        low_vulns = sum(1 for v in vulnerabilities if v.get("severity_level_value", 0) == 1)
        
        # Add audit score
        audit_score = audit_data.get("audit_score", 0)
        passed = audit_data.get("passed", False)
        status = "PASSED" if passed else "FAILED"
        status_color = colors.green if passed else colors.red
        
        # Create summary table
        summary_data = [
            ["Audit Score", "Status", "High Severity", "Medium Severity", "Low Severity"],
            [
                f"{audit_score}/100",
                status,
                str(high_vulns),
                str(medium_vulns),
                str(low_vulns)
            ]
        ]
        
        summary_table = Table(summary_data, colWidths=[1.0*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.0*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (1, 1), (1, 1), status_color if passed else colors.lightcoral),
            ('TEXTCOLOR', (1, 1), (1, 1), colors.white if passed else colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add contract metadata
        contract_metadata = audit_data.get("contract_metadata", {})
        elements.append(Paragraph("Contract Information", self.styles["CustomHeading3"]))
        
        metadata_text = [
            f"<b>Name:</b> {contract_metadata.get('name', 'N/A')}",
            f"<b>Language:</b> {contract_metadata.get('language', 'Solidity')}",
            f"<b>Hash:</b> {contract_metadata.get('hash', 'N/A')}"
        ]
        
        for text in metadata_text:
            elements.append(Paragraph(text, self.styles["CustomNormal"]))
        
        elements.append(Spacer(1, 0.25*inch))
    
    def _add_vulnerability_table(self, elements: List, audit_data: Dict) -> None:
        """
        Add vulnerability table to the report.
        
        Args:
            elements: List of elements to add to
            audit_data: Dictionary containing audit results
        """
        elements.append(Paragraph("Vulnerability Summary", self.styles["CustomHeading2"]))
        
        vulnerabilities = audit_data.get("vulnerabilities", [])
        if not vulnerabilities:
            elements.append(Paragraph("No vulnerabilities found.", self.styles["CustomNormal"]))
            elements.append(Spacer(1, 0.25*inch))
            return
        
        # Create table data
        table_data = [
            ["ID", "Title", "Severity", "Location"]
        ]
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "Unknown")
            severity_color = {
                "High": colors.red,
                "Medium": colors.orange,
                "Low": colors.yellow,
                "Informational": colors.lightblue
            }.get(severity, colors.white)
            
            table_data.append([
                vuln.get("id", "N/A"),
                vuln.get("title", "Unknown"),
                severity,
                f"Line {vuln.get('line', 0)}"
            ])
        
        # Create table
        vuln_table = Table(table_data, colWidths=[0.75*inch, 3.0*inch, 1.0*inch, 1.0*inch])
        
        # Style the table
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        
        # Add severity color coding
        for i, row in enumerate(table_data[1:], 1):
            severity = row[2]
            severity_color = {
                "High": colors.lightcoral,
                "Medium": colors.lightsalmon,
                "Low": colors.lightgoldenrodyellow,
                "Informational": colors.lightblue
            }.get(severity, colors.white)
            
            table_style.add('BACKGROUND', (2, i), (2, i), severity_color)
        
        vuln_table.setStyle(table_style)
        elements.append(vuln_table)
        elements.append(Spacer(1, 0.25*inch))
    
    def _add_detailed_findings(self, elements: List, audit_data: Dict) -> None:
        """
        Add detailed findings to the report.
        
        Args:
            elements: List of elements to add to
            audit_data: Dictionary containing audit results
        """
        elements.append(Paragraph("Detailed Findings", self.styles["CustomHeading2"]))
        
        vulnerabilities = audit_data.get("vulnerabilities", [])
        if not vulnerabilities:
            return
        
        for i, vuln in enumerate(vulnerabilities):
            # Add page break for all but the first vulnerability
            if i > 0:
                elements.append(PageBreak())
            
            # Add vulnerability header
            vuln_id = vuln.get("id", "N/A")
            vuln_title = vuln.get("title", "Unknown")
            elements.append(Paragraph(f"{vuln_id}: {vuln_title}", self.styles["CustomHeading3"]))
            
            # Add description
            elements.append(Paragraph("<b>Description:</b>", self.styles["CustomNormal"]))
            elements.append(Paragraph(vuln.get("description", "No description available."), self.styles["CustomNormal"]))
            elements.append(Spacer(1, 0.1*inch))
            
            # Add explanation if available
            if "explanation" in vuln and vuln["explanation"]:
                elements.append(Paragraph("<b>Explanation:</b>", self.styles["CustomNormal"]))
                elements.append(Paragraph(vuln["explanation"], self.styles["CustomNormal"]))
                elements.append(Spacer(1, 0.1*inch))
            
            # Add code snippet if available
            if "code_snippet" in vuln and vuln["code_snippet"]:
                elements.append(Paragraph("<b>Vulnerable Code:</b>", self.styles["CustomNormal"]))
                elements.append(Paragraph(f"<pre>{vuln['code_snippet']}</pre>", self.styles["CustomCode"]))
                elements.append(Spacer(1, 0.1*inch))
            
            # Add fixed code if available
            if "fixed_code" in vuln and vuln["fixed_code"]:
                elements.append(Paragraph("<b>Suggested Fix:</b>", self.styles["CustomNormal"]))
                elements.append(Paragraph(f"<pre>{vuln['fixed_code']}</pre>", self.styles["CustomCode"]))
                elements.append(Spacer(1, 0.1*inch))
            
            # Add test case if available
            if "test_case" in vuln and vuln["test_case"]:
                elements.append(Paragraph("<b>Test Case:</b>", self.styles["CustomNormal"]))
                elements.append(Paragraph(f"<pre>{vuln['test_case']}</pre>", self.styles["CustomCode"]))
                elements.append(Spacer(1, 0.1*inch))
            
            elements.append(Spacer(1, 0.25*inch))
    
    def _add_footer(self, elements: List, audit_data: Dict) -> None:
        """
        Add footer to the report.
        
        Args:
            elements: List of elements to add to
            audit_data: Dictionary containing audit results
        """
        elements.append(Spacer(1, 0.5*inch))
        
        # Add timestamp and contract hash
        contract_hash = audit_data.get("contract_metadata", {}).get("hash", "N/A")
        timestamp = datetime.datetime.now().isoformat()
        
        footer_text = (
            f"Audit Timestamp: {timestamp} | "
            f"Contract Hash: {contract_hash} | "
            "Generated by Hedera Audit AI"
        )
        
        elements.append(Paragraph(footer_text, self.styles["CustomFooter"]))
        
        # Add disclaimer
        disclaimer = (
            "DISCLAIMER: This report is provided on an 'as is' basis. "
            "While every effort has been made to ensure accuracy, "
            "no guarantee is made that the report is error-free or that all vulnerabilities have been identified. "
            "Always conduct thorough testing before deploying smart contracts to production."
        )
        
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(disclaimer, self.styles["CustomFooter"]))
