"""Tests for the report generator module."""

import pytest
from unittest.mock import patch, MagicMock

from src.report.generator import ReportGenerator, CodeSnippet


class TestReportGenerator:
    """Test suite for the ReportGenerator class."""

    @pytest.fixture
    def report_generator(self):
        """Create a ReportGenerator instance for testing."""
        return ReportGenerator()

    @pytest.fixture
    def sample_audit_data(self):
        """Sample audit data for testing."""
        return {
            "contract_metadata": {
                "name": "TestContract",
                "language": "solidity",
                "hash": "0x1234567890abcdef"
            },
            "vulnerabilities": [
                {
                    "id": "reentrancy-eth",
                    "title": "Reentrancy",
                    "description": "Reentrancy vulnerability in withdraw function",
                    "severity": "High",
                    "severity_level_value": 3,
                    "line": 13,
                    "code_snippet": "function withdraw(uint256 amount) public {",
                    "explanation": "This function is vulnerable to reentrancy attacks.",
                    "fixed_code": "function withdraw(uint256 amount) public {\n    uint256 amount = balances[msg.sender];\n    balances[msg.sender] = 0;\n    (bool success, ) = msg.sender.call{value: amount}(\"\");\n    require(success, \"Transfer failed\");\n}",
                    "test_case": "function testReentrancy() public {}"
                },
                {
                    "id": "HED-002",
                    "title": "Unsafe HBAR Handling",
                    "description": "Payable function without HBAR amount validation",
                    "severity": "Medium",
                    "severity_level_value": 2,
                    "line": 7,
                    "code_snippet": "function deposit() public payable {",
                    "explanation": "This function accepts HBAR without validation.",
                    "fixed_code": "function deposit() public payable {\n    require(msg.value > 0, \"Amount must be positive\");\n    balances[msg.sender] += msg.value;\n}",
                    "test_case": "function testDeposit() public {}"
                }
            ],
            "audit_score": 75,
            "passed": False
        }

    def test_init(self, report_generator):
        """Test initialization."""
        assert report_generator.logo_path is None
        assert report_generator.styles is not None
        
        # Check custom styles
        assert "Heading1" in report_generator.styles
        assert "Heading2" in report_generator.styles
        assert "Heading3" in report_generator.styles
        assert "Normal" in report_generator.styles
        assert "Code" in report_generator.styles
        assert "Footer" in report_generator.styles

    @patch("src.report.generator.SimpleDocTemplate")
    @patch("src.report.generator.io.BytesIO")
    def test_generate_pdf(self, mock_bytesio, mock_simple_doc, report_generator, sample_audit_data):
        """Test PDF generation."""
        # Mock BytesIO
        mock_buffer = MagicMock()
        mock_bytesio.return_value = mock_buffer
        mock_buffer.getvalue.return_value = b"PDF_BYTES"
        
        # Mock SimpleDocTemplate
        mock_doc = MagicMock()
        mock_simple_doc.return_value = mock_doc
        
        # Generate PDF
        result = report_generator.generate_pdf(sample_audit_data)
        
        # Verify results
        assert result == b"PDF_BYTES"
        assert mock_doc.build.called
        mock_buffer.close.assert_called_once()

    @patch("src.report.generator.Paragraph")
    def test_add_header(self, mock_paragraph, report_generator, sample_audit_data):
        """Test adding header to report."""
        elements = []
        report_generator._add_header(elements, sample_audit_data)
        
        # Verify elements
        assert len(elements) > 0
        assert mock_paragraph.call_count >= 3  # Title, contract name, date

    @patch("src.report.generator.Paragraph")
    @patch("src.report.generator.Table")
    def test_add_summary(self, mock_table, mock_paragraph, report_generator, sample_audit_data):
        """Test adding summary to report."""
        elements = []
        report_generator._add_summary(elements, sample_audit_data)
        
        # Verify elements
        assert len(elements) > 0
        assert mock_paragraph.call_count >= 1
        assert mock_table.call_count >= 1

    @patch("src.report.generator.Paragraph")
    @patch("src.report.generator.Table")
    def test_add_vulnerability_table(self, mock_table, mock_paragraph, report_generator, sample_audit_data):
        """Test adding vulnerability table to report."""
        elements = []
        report_generator._add_vulnerability_table(elements, sample_audit_data)
        
        # Verify elements
        assert len(elements) > 0
        assert mock_paragraph.call_count >= 1
        assert mock_table.call_count >= 1

    @patch("src.report.generator.Paragraph")
    @patch("src.report.generator.PageBreak")
    def test_add_detailed_findings(self, mock_page_break, mock_paragraph, report_generator, sample_audit_data):
        """Test adding detailed findings to report."""
        elements = []
        report_generator._add_detailed_findings(elements, sample_audit_data)
        
        # Verify elements
        assert len(elements) > 0
        assert mock_paragraph.call_count >= len(sample_audit_data["vulnerabilities"]) * 3  # At least 3 paragraphs per vulnerability
        assert mock_page_break.call_count >= len(sample_audit_data["vulnerabilities"]) - 1  # Page break between vulnerabilities

    @patch("src.report.generator.Paragraph")
    def test_add_footer(self, mock_paragraph, report_generator, sample_audit_data):
        """Test adding footer to report."""
        elements = []
        report_generator._add_footer(elements, sample_audit_data)
        
        # Verify elements
        assert len(elements) > 0
        assert mock_paragraph.call_count >= 2  # Footer text and disclaimer


class TestCodeSnippet:
    """Test suite for the CodeSnippet class."""

    def test_init(self):
        """Test initialization."""
        code_snippet = CodeSnippet("function test() {}", width=100, height=50)
        
        assert code_snippet.code_text == "function test() {}"
        assert code_snippet.language == "solidity"
        assert code_snippet.width == 100
        assert code_snippet.height == 50
        
        assert code_snippet.background_color is not None
        assert code_snippet.border_color is not None
        assert code_snippet.text_color is not None
        assert code_snippet.font_name == "Courier"
        assert code_snippet.font_size == 8

    def test_draw(self):
        """Test drawing the code snippet."""
        code_snippet = CodeSnippet("function test() {}\nline 2", width=100, height=50)
        
        # Mock canvas
        mock_canvas = MagicMock()
        code_snippet.canv = mock_canvas
        
        # Draw
        code_snippet.draw()
        
        # Verify canvas calls
        assert mock_canvas.setFillColor.call_count >= 2  # Background and text
        assert mock_canvas.setStrokeColor.call_count >= 1  # Border
        assert mock_canvas.rect.call_count >= 1  # Background rectangle
        assert mock_canvas.setFont.call_count >= 1  # Font
        assert mock_canvas.drawString.call_count >= 2  # Two lines of code
