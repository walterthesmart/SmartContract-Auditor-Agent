"""Slither-based smart contract analyzer."""

import json
import os
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class SlitherAnalyzer:
    """Analyzes smart contracts using Slither with custom Hedera rules."""
    
    def __init__(self, custom_rules_path: Optional[str] = None, timeout: int = 300):
        """
        Initialize the Slither analyzer.
        
        Args:
            custom_rules_path: Path to custom Hedera rules (relative to backend directory)
            timeout: Maximum execution time in seconds
        """
        # Resolve the custom rules path if provided
        if custom_rules_path:
            # Get the project root directory (4 levels up from this file)
            project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            # Resolve the path relative to the project root directory
            self.custom_rules_path = str(project_root / custom_rules_path)
        else:
            self.custom_rules_path = None
            
        self.timeout = timeout
    
    def analyze_contract(self, contract_code: str, language: str = "solidity") -> Dict:
        """
        Analyze a smart contract using Slither.
        
        Args:
            contract_code: The source code of the contract
            language: The language of the contract (solidity or vyper)
            
        Returns:
            Dict containing vulnerabilities and metrics
        """
        import logging
        logging.info(f"Analyzing contract with length {len(contract_code)}")
        
        # Create temporary contract file
        with tempfile.NamedTemporaryFile(suffix=".sol", delete=False) as temp_file:
            temp_file.write(contract_code.encode())
            temp_path = temp_file.name
            logging.info(f"Created temporary file at {temp_path}")
        
        try:
            # Run Slither analysis
            slither_result = self._run_slither(temp_path)
            
            if slither_result is None:
                logging.error("Slither returned None result")
                # Return a default result structure if Slither fails
                return {
                    "vulnerabilities": self._check_hedera_specific(contract_code),
                    "contract_metrics": {
                        "complexity": 5,  # Default value
                        "loc": len(contract_code.splitlines())  # Count lines in the contract
                    }
                }
            
            # Parse and enhance results
            result = self._parse_slither_output(slither_result)
            
            # Add custom Hedera-specific checks
            hedera_checks = self._check_hedera_specific(contract_code)
            if hedera_checks:
                result["vulnerabilities"].extend(hedera_checks)
            
            return result
        
        except Exception as e:
            logging.error(f"Error in analyze_contract: {str(e)}")
            # Return a minimal result structure if an exception occurs
            return {
                "vulnerabilities": [],
                "contract_metrics": {
                    "complexity": 5,
                    "loc": len(contract_code.splitlines())
                }
            }
            
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
    
    def _run_slither(self, file_path: str) -> Dict:
        """
        Run Slither analysis on the contract file.
        
        Args:
            file_path: Path to the contract file
            
        Returns:
            Dict containing Slither output or None if analysis fails
        """
        import logging
        logging.info(f"Running Slither analysis on {file_path}")
        
        try:
            # Build Slither command using the exact format that works from our test
            cmd = [
                "slither", 
                file_path, 
                "--detect", "reentrancy-eth",
                "--json", "-"
            ]
            
            logging.info(f"Executing command: {' '.join(cmd)}")
            
            # Run Slither with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=os.path.dirname(file_path)
            )
            
            logging.info(f"Slither exit code: {result.returncode}")
            logging.info(f"Slither stdout length: {len(result.stdout)}")
            if result.stderr:
                logging.info(f"Slither stderr: {result.stderr}")
            
            # Slither returns high exit codes when vulnerabilities are found (like 255)
            # This is normal behavior, so we only treat very specific errors as failures
            if result.returncode == 127:  # Command not found
                logging.error("Slither command not found")
                return None
            elif result.returncode > 0 and not result.stdout.strip():
                # Only treat as error if there's no output and a non-zero exit code
                logging.error(f"Slither failed with exit code {result.returncode} and no output")
                logging.error(f"Stderr: {result.stderr}")
                return None
            
            # Parse JSON output
            if result.stdout.strip():
                try:
                    slither_output = json.loads(result.stdout)
                    logging.info(f"Successfully parsed Slither JSON output")
                    return slither_output
                except json.JSONDecodeError as e:
                    logging.error(f"Failed to parse Slither JSON output: {e}")
                    logging.error(f"Raw output: {result.stdout[:500]}...")
                    return None
            else:
                logging.warning("Slither produced no output")
                return {"success": True, "results": {"detectors": []}}
                
        except subprocess.TimeoutExpired:
            logging.error(f"Slither analysis timed out after {self.timeout} seconds")
            return None
        except FileNotFoundError:
            logging.error("Slither not found. Please install slither-analyzer: pip install slither-analyzer")
            return None
        except Exception as e:
            logging.error(f"Error running Slither: {str(e)}")
            return None
    
    def _parse_slither_output(self, raw_data: Dict) -> Dict:
        """
        Parse Slither output into a structured format.
        
        Args:
            raw_data: Raw Slither output
            
        Returns:
            Dict containing structured vulnerabilities and metrics
        """
        import logging
        logging.info(f"Parsing Slither output: {raw_data}")
        
        vulnerabilities = []
        
        # Handle our mock data format
        if "success" in raw_data and "results" in raw_data:
            detectors = raw_data.get("results", {}).get("detectors", [])
        else:
            # Handle standard Slither output format
            detectors = raw_data.get("detectors", [])
        
        for detector in detectors:
            # Generate a unique ID for the vulnerability
            vuln_id = f"VULN-{len(vulnerabilities) + 1}"
            
            # Extract elements information
            elements = detector.get("elements", [])
            line = 0
            code_snippet = ""
            
            if elements:
                element = elements[0]
                source_mapping = element.get("source_mapping", {})
                line = source_mapping.get("start", 0)
                code_snippet = f"// In {element.get('name', 'unknown')}\n// Vulnerable code here"
            
            vulnerability = {
                "id": vuln_id,
                "title": detector.get("check", "Unknown"),
                "description": detector.get("description", "No description"),
                "severity": detector.get("impact", "Medium").lower(),
                "severity_level_value": self._severity_to_value(detector.get("impact", "Medium")),
                "location": {
                    "line": line,
                    "column": None,
                    "function": element.get("name") if elements else None
                },
                "code_snippet": code_snippet,
                "cwe": detector.get("cwe", [])
            }
            vulnerabilities.append(vulnerability)
            
        logging.info(f"Found {len(vulnerabilities)} vulnerabilities")
        
        return {
            "vulnerabilities": vulnerabilities,
            "contract_metrics": {
                "complexity": raw_data.get("metrics", {}).get("complexity", 5),  # Default value for mock
                "loc": raw_data.get("metrics", {}).get("nLines", 25)  # Default value for mock
            }
        }
    
    def _severity_to_value(self, severity: str) -> int:
        """
        Convert severity string to numeric value.
        
        Args:
            severity: Severity level string
            
        Returns:
            Integer value representing severity (0-3)
        """
        return {
            "High": 3,
            "Medium": 2,
            "Low": 1,
            "Informational": 0
        }.get(severity, 0)
    
    def _check_hedera_specific(self, contract_code: str) -> List[Dict]:
        """
        Perform Hedera-specific checks.
        
        Args:
            contract_code: The source code of the contract
            
        Returns:
            List of Hedera-specific vulnerabilities
        """
        vulnerabilities = []
        
        # Check for token association
        if "associateToken" not in contract_code and "TokenAssociate" not in contract_code:
            vulnerabilities.append({
                "id": "HED-001",
                "title": "Missing Token Association",
                "description": "Contract doesn't implement token association logic which is required for HTS tokens",
                "severity": "medium",
                "severity_level_value": 2,
                "location": {
                    "line": 0,
                    "column": None,
                    "function": None
                },
                "cwe": ["CWE-362"]
            })
        
        # Check HBAR handling
        if "payable" in contract_code and "require(msg.value" not in contract_code:
            vulnerabilities.append({
                "id": "HED-002",
                "title": "Unsafe HBAR Handling",
                "description": "Payable function without HBAR amount validation could lead to unexpected behavior",
                "severity": "high",
                "severity_level_value": 3,
                "location": {
                    "line": 0,
                    "column": None,
                    "function": None
                },
                "cwe": ["CWE-840"]
            })
        
        # Check for consensus timestamp usage
        if "block.timestamp" in contract_code and "ConsensusTimestamp" not in contract_code:
            vulnerabilities.append({
                "id": "HED-003",
                "title": "Improper Timestamp Usage",
                "description": "Using block.timestamp instead of Hedera's ConsensusTimestamp may lead to inconsistencies",
                "severity": "medium",
                "severity_level_value": 2,
                "location": {
                    "line": 0,
                    "column": None,
                    "function": None
                },
                "cwe": ["CWE-829"]
            })
        
        return vulnerabilities
