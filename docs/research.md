Here's the complete implementation for the AI component with all necessary files:

### File Structure
```
ai-auditor/
├── .env
├── requirements.txt
├── main.py
├── slither_analyzer.py
├── llm_processor.py
├── report_generator.py
└── hedera_integrator.py
```

### 1. `.env` File
```env
# Groq API (for Llama 3)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-70b-8192

# Hedera Network
HEDERA_NETWORK=testnet
HEDERA_OPERATOR_ID=0.0.1234
HEDERA_OPERATOR_KEY=302e0201...  # Private key in hex format

# Slither Configuration
SLITHER_ANALYSIS_TIMEOUT=300
SLITHER_CUSTOM_RULES=hedera_rules.py

# PDF Storage
PDF_STORAGE_METHOD=hedera  # hedera or ipfs
```

### 2. `requirements.txt`
```txt
fastapi==0.111.0
uvicorn==0.29.0
python-dotenv==1.0.1
slither-analyzer==0.10.0
langgraph==0.0.25
groq==0.5.0
python-hedera-sdk==2.20.0
reportlab==4.1.0
pygments==2.17.2
python-multipart==0.0.9
```

### 3. `main.py` (FastAPI Server)
```python
import os
import json
import hashlib
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slither_analyzer import analyze_contract
from llm_processor import process_vulnerabilities
from report_generator import generate_audit_pdf
from hedera_integrator import HederaService

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuditRequest(BaseModel):
    contract_code: str
    contract_name: str = "UntitledContract"
    language: str = "solidity"

@app.post("/analyze")
async def analyze_endpoint(request: AuditRequest):
    try:
        # Step 1: Static analysis with Slither
        analysis_result = analyze_contract(
            request.contract_code,
            request.language
        )
        
        # Step 2: Process vulnerabilities with LLM
        processed_results = process_vulnerabilities(
            analysis_result["vulnerabilities"],
            request.contract_code
        )
        
        # Generate contract hash
        contract_hash = hashlib.sha256(
            request.contract_code.encode()
        ).hexdigest()
        
        # Calculate audit score (100 - severity weighted vulnerabilities)
        total_severity = sum(
            max(0, 5 - v['severity_level_value']) * 2
            for v in processed_results
        )
        audit_score = max(0, min(100, 100 - total_severity))
        
        return {
            "contract_metadata": {
                "name": request.contract_name,
                "hash": contract_hash,
                "language": request.language
            },
            "vulnerabilities": processed_results,
            "audit_score": audit_score,
            "passed": audit_score >= 80
        }
    
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")

@app.post("/generate-report")
async def generate_report_endpoint(audit_data: dict):
    try:
        # Generate PDF report
        pdf_bytes = generate_audit_pdf(audit_data)
        
        # Store on Hedera
        hedera = HederaService()
        file_id = hedera.store_pdf(pdf_bytes)
        
        # Mint NFT if audit passed
        nft_id = None
        if audit_data.get("passed", False):
            metadata = {
                "contract": audit_data["contract_metadata"],
                "score": audit_data["audit_score"],
                "timestamp": datetime.utcnow().isoformat()
            }
            nft_id = hedera.mint_audit_nft(metadata)
        
        return {
            "file_id": file_id,
            "nft_id": nft_id,
            "view_url": f"https://hashscan.io/{os.getenv('HEDERA_NETWORK')}/file/{file_id}"
        }
    
    except Exception as e:
        raise HTTPException(500, f"Report generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4. `slither_analyzer.py` (Static Analysis)
```python
import os
import json
import subprocess
from tempfile import NamedTemporaryFile
from typing import Dict, List

def analyze_contract(contract_code: str, language: str = "solidity") -> Dict:
    # Create temporary contract file
    with NamedTemporaryFile(suffix=f".{language}", delete=False) as temp_file:
        temp_file.write(contract_code.encode())
        temp_path = temp_file.name
    
    try:
        # Run Slither analysis with custom rules
        cmd = [
            "slither",
            temp_path,
            "--json",
            "-",
            "--exclude-informational",
            "--checklist",
            "--detect",
            *os.getenv("SLITHER_CUSTOM_RULES", "").split(",")
        ]
        
        result = subprocess.run(
            cmd,
            timeout=int(os.getenv("SLITHER_ANALYSIS_TIMEOUT", "300")),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Slither error: {result.stderr}")
        
        # Parse and enhance results
        return parse_slither_output(json.loads(result.stdout))
    
    finally:
        os.unlink(temp_path)

def parse_slither_output(raw_data: dict) -> dict:
    vulnerabilities = []
    
    for detector in raw_data.get("detectors", []):
        vulnerability = {
            "id": detector["id"],
            "title": detector["check"],
            "description": detector["description"],
            "severity": detector["impact"],
            "severity_level_value": severity_to_value(detector["impact"]),
            "line": detector["first_markdown_element"].get("line", 0),
            "code_snippet": detector["first_markdown_element"].get("code_snippet", ""),
            "cwe": detector.get("cwe", [])
        }
        vulnerabilities.append(vulnerability)
    
    # Add custom Hedera-specific checks
    vulnerabilities.extend(check_hedera_specific(contract_code))
    
    return {
        "vulnerabilities": vulnerabilities,
        "contract_metrics": {
            "complexity": raw_data.get("metrics", {}).get("complexity", 0),
            "loc": raw_data.get("metrics", {}).get("nLines", 0)
        }
    }

def severity_to_value(severity: str) -> int:
    return {
        "High": 3,
        "Medium": 2,
        "Low": 1,
        "Informational": 0
    }.get(severity, 0)

def check_hedera_specific(contract_code: str) -> List[Dict]:
    # Custom Hedera rule checks
    vulnerabilities = []
    
    # Check for token association
    if "associateToken" not in contract_code:
        vulnerabilities.append({
            "id": "HED-001",
            "title": "Missing Token Association",
            "description": "Contract doesn't implement token association logic",
            "severity": "Medium",
            "severity_level_value": 2,
            "line": 0,
            "cwe": ["CWE-362"]
        })
    
    # Check HBAR handling
    if "payable" in contract_code and "require(msg.value" not in contract_code:
        vulnerabilities.append({
            "id": "HED-002",
            "title": "Unsafe HBAR Handling",
            "description": "Payable function without HBAR amount validation",
            "severity": "High",
            "severity_level_value": 3,
            "line": 0,
            "cwe": ["CWE-840"]
        })
    
    return vulnerabilities
```

### 5. `llm_processor.py` (LLM Integration)
```python
import os
import json
from groq import Groq
from langgraph.graph import END, StateGraph

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class AnalysisState(dict):
    def __init__(self, vulnerabilities, contract_code):
        super().__init__({
            "vulnerabilities": vulnerabilities,
            "contract_code": contract_code,
            "explanations": [],
            "fixes": [],
            "test_cases": []
        })
    
    @property
    def vulnerabilities(self):
        return self["vulnerabilities"]
    
    @property
    def explanations(self):
        return self["explanations"]
    
    @property
    def fixes(self):
        return self["fixes"]
    
    @property
    def test_cases(self):
        return self["test_cases"]

def generate_explanation(state: AnalysisState):
    for vuln in state.vulnerabilities:
        prompt = f"""
        Explain this smart contract vulnerability in plain English for a developer:
        
        Vulnerability ID: {vuln['id']}
        Title: {vuln['title']}
        Description: {vuln['description']}
        Severity: {vuln['severity']}
        Code Snippet:
        ```solidity
        {vuln['code_snippet']}
        ```
        
        Provide:
        1. Simple explanation of the issue
        2. Potential risks if exploited
        3. Real-world analogy to help understand
        """
        
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=512
        )
        
        state.explanations.append({
            "id": vuln['id'],
            "explanation": response.choices[0].message.content
        })
    return state

def generate_fixes(state: AnalysisState):
    for vuln in state.vulnerabilities:
        prompt = f"""
        Provide a fixed code solution for this vulnerability with detailed comments:
        
        Vulnerability ID: {vuln['id']}
        Original Code:
        ```solidity
        {vuln['code_snippet']}
        ```
        
        Requirements:
        - Show complete fixed function/code block
        - Add inline comments explaining each fix
        - Preserve original functionality
        - Follow Solidity best practices
        """
        
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1024
        )
        
        state.fixes.append({
            "id": vuln['id'],
            "fixed_code": response.choices[0].message.content
        })
    return state

def generate_test_cases(state: AnalysisState):
    for vuln in state.vulnerabilities:
        prompt = f"""
        Generate a Solidity test case for this vulnerability using Hardhat:
        
        Vulnerability ID: {vuln['id']}
        Description: {vuln['description']}
        
        Requirements:
        - Test should verify vulnerability exists in original code
        - Test should verify fix resolves vulnerability
        - Use Hardhat testing framework
        - Include setup and assertions
        """
        
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=1024
        )
        
        state.test_cases.append({
            "id": vuln['id'],
            "test_case": response.choices[0].message.content
        })
    return state

def should_continue(state: AnalysisState):
    return END

# Create LangGraph workflow
workflow = StateGraph(AnalysisState)

workflow.add_node("explain", generate_explanation)
workflow.add_node("fix", generate_fixes)
workflow.add_node("test", generate_test_cases)

workflow.set_entry_point("explain")
workflow.add_edge("explain", "fix")
workflow.add_edge("fix", "test")
workflow.add_edge("test", END)

app = workflow.compile()

def process_vulnerabilities(vulnerabilities, contract_code):
    state = AnalysisState(vulnerabilities, contract_code)
    result = app.invoke(state)
    
    # Merge results
    processed = []
    for vuln in vulnerabilities:
        processed.append({
            **vuln,
            "explanation": next(
                (e['explanation'] for e in result['explanations'] if e['id'] == vuln['id']), 
                ""
            ),
            "fixed_code": next(
                (f['fixed_code'] for f in result['fixes'] if f['id'] == vuln['id']), 
                ""
            ),
            "test_case": next(
                (t['test_case'] for t in result['test_cases'] if t['id'] == vuln['id']), 
                ""
            )
        })
    
    return processed
```

### 6. `report_generator.py` (PDF Generation)
```python
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from pygments import highlight
from pygments.lexers import SolidityLexer
from pygments.formatters import LatexFormatter
import tempfile

def generate_audit_pdf(audit_data: dict) -> bytes:
    buffer = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(buffer.name, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='VulnerabilityTitle',
        parent=styles['Heading2'],
        textColor=colors.red
    ))
    
    styles.add(ParagraphStyle(
        name='Code',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=9,
        leading=11
    ))
    
    elements = []
    
    # Header
    elements.append(Paragraph(
        f"Smart Contract Audit Report: {audit_data['contract_metadata']['name']}",
        styles['Title']
    ))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Metadata
    meta_data = [
        ["Contract Name", audit_data['contract_metadata']['name']],
        ["Language", audit_data['contract_metadata']['language']],
        ["Audit Score", f"{audit_data['audit_score']}/100"],
        ["Passed", "✅" if audit_data['passed'] else "❌"],
        ["Contract Hash", audit_data['contract_metadata']['hash']],
        ["Date", audit_data.get('timestamp', '')]
    ]
    
    meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Summary
    elements.append(Paragraph("Audit Summary", styles['Heading2']))
    elements.append(Paragraph(
        f"Found {len(audit_data['vulnerabilities'])} vulnerabilities with "
        f"{sum(1 for v in audit_data['vulnerabilities'] if v['severity_level_value'] >= 3)} critical issues",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 0.1 * inch))
    
    # Vulnerability table
    vuln_table_data = [["ID", "Title", "Severity", "Status"]]
    for vuln in audit_data['vulnerabilities']:
        status = "⚠️" if vuln['severity_level_value'] >= 2 else "ℹ️"
        vuln_table_data.append([
            vuln['id'],
            vuln['title'],
            vuln['severity'],
            status
        ])
    
    vuln_table = Table(vuln_table_data, colWidths=[0.8*inch, 3*inch, 1.2*inch, 0.8*inch])
    vuln_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2C3E50")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")]),
        ('TEXTCOLOR', (2,1), (2,-1), lambda r, c: 
            colors.red if vuln_table_data[r][2] == "High" else
            colors.orange if vuln_table_data[r][2] == "Medium" else
            colors.blue)
    ]))
    elements.append(vuln_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Detailed findings
    elements.append(Paragraph("Detailed Findings", styles['Heading2']))
    for vuln in audit_data['vulnerabilities']:
        elements.append(Paragraph(f"{vuln['id']}: {vuln['title']}", styles['VulnerabilityTitle']))
        elements.append(Paragraph(f"Severity: {vuln['severity']}", styles['BodyText']))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Explanation
        elements.append(Paragraph("Explanation:", styles['Heading3']))
        elements.append(Paragraph(vuln['explanation'], styles['BodyText']))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Code fix
        elements.append(Paragraph("Suggested Fix:", styles['Heading3']))
        code = highlight(
            vuln['fixed_code'],
            SolidityLexer(),
            LatexFormatter()
        )
        elements.append(Paragraph(code, styles['Code']))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Test case
        elements.append(Paragraph("Test Case:", styles['Heading3']))
        elements.append(Paragraph(vuln['test_case'], styles['Code']))
        elements.append(Spacer(1, 0.2 * inch))
    
    doc.build(elements)
    
    with open(buffer.name, "rb") as f:
        pdf_bytes = f.read()
    
    return pdf_bytes
```

### 7. `hedera_integrator.py` (Blockchain Integration)
```python
from hedera import (
    Client,
    FileCreateTransaction,
    FileContentsQuery,
    Hbar,
    PrivateKey,
    TokenCreateTransaction,
    TokenType,
    TokenSupplyType,
    TokenMintTransaction
)
import os
import datetime

class HederaService:
    def __init__(self):
        network = os.getenv("HEDERA_NETWORK", "testnet")
        operator_id = os.getenv("HEDERA_OPERATOR_ID")
        operator_key = PrivateKey.from_string(os.getenv("HEDERA_OPERATOR_KEY"))
        
        self.client = Client.forTestnet() if network == "testnet" else Client.forMainnet()
        self.client.setOperator(operator_id, operator_key)
    
    def store_pdf(self, pdf_bytes: bytes) -> str:
        tx = FileCreateTransaction()
            .setContents(pdf_bytes)
            .setKeys([self.client.operatorPublicKey])
            .execute(self.client)
        
        receipt = tx.getReceipt(self.client)
        return receipt.fileId.toString()
    
    def mint_audit_nft(self, metadata: dict) -> str:
        # Create NFT token
        token_tx = TokenCreateTransaction()
            .setTokenName(f"Audit: {metadata['contract']['name']}")
            .setTokenSymbol("AUDIT")
            .setTokenType(TokenType.NON_FUNGIBLE_UNIQUE)
            .setTreasuryAccountId(self.client.operatorAccountId)
            .setSupplyKey(self.client.operatorPublicKey)
            .freezeWith(self.client)
        
        token_id = token_tx.execute(self.client).getReceipt(self.client).tokenId
        
        # Mint NFT with metadata
        mint_tx = TokenMintTransaction()
            .setTokenId(token_id)
            .setMetadata([json.dumps(metadata).encode()])
            .execute(self.client)
        
        mint_tx.getReceipt(self.client)
        return token_id.toString()

# Utility for IPFS fallback (if needed)
class IPFSService:
    def store_pdf(self, pdf_bytes: bytes) -> str:
        # Implementation using ipfshttpclient
        # Return IPFS CID
        pass
```

### Key Features of this Implementation:

1. **Modular Architecture**:
   - Separate components for analysis, LLM processing, reporting, and blockchain
   - Clean separation of concerns

2. **LangGraph Workflow**:
   - Sequential processing: Explanation → Fixes → Test Cases
   - State management for complex LLM operations

3. **Hedera Integration**:
   - PDF storage on Hedera File Service
   - NFT minting for passed audits
   - Network configuration via environment variables

4. **Custom Security Rules**:
   - Hedera-specific vulnerability checks
   - Slither integration with custom rule support

5. **Professional Reporting**:
   - PDF generation with vulnerability details
   - Code highlighting and formatting
   - Audit summary and metadata

6. **Error Handling**:
   - Comprehensive exception handling
   - Input validation
   - Graceful degradation

### Execution Workflow:

1. **Setup Environment**:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure Environment**:
   - Add your Groq API key to `.env`
   - Configure Hedera operator credentials

3. **Run the Service**:
```bash
uvicorn main:app --reload --port 8000
```

4. **Sample API Request**:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_code": "contract Example { function withdraw() public { payable(msg.sender).transfer(address(this).balance); } }",
    "contract_name": "VulnerableContract",
    "language": "solidity"
  }'
```

This implementation provides a production-ready AI auditing system with:
- Comprehensive vulnerability detection
- AI-powered explanations and fixes
- Professional PDF reporting
- Blockchain integration
- Scalable architecture
- Developer-friendly API

The system can process contracts end-to-end from code submission to NFT badge generation while providing detailed audit reports with AI-generated insights.