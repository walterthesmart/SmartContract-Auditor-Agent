"""LLM processor for vulnerability analysis and code fix generation."""

import os
from typing import Dict, List, Optional

from groq import Groq
from langgraph.graph import END, StateGraph


class LLMProcessor:
    """
    Processes vulnerabilities using LLM to generate explanations, fixes, and test cases.
    Uses LangGraph for workflow orchestration.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the LLM processor.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: LLM model to use (defaults to GROQ_MODEL env var)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key not provided and GROQ_API_KEY env var not set")
        
        self.model = model or os.getenv("GROQ_MODEL", "llama3-70b-8192")
        self.client = Groq(api_key=self.api_key)
        self.workflow = self._create_workflow()
    
    def process_vulnerabilities(
        self, vulnerabilities: List[Dict], contract_code: str
    ) -> List[Dict]:
        """
        Process vulnerabilities using LLM to generate explanations, fixes, and test cases.
        
        Args:
            vulnerabilities: List of vulnerability dictionaries
            contract_code: The source code of the contract
            
        Returns:
            Enhanced vulnerabilities with explanations, fixes, and test cases
        """
        if not vulnerabilities:
            return []
        
        # Initialize state
        initial_state = {
            "vulnerabilities": vulnerabilities,
            "contract_code": contract_code,
            "explanations": [],
            "fixes": [],
            "test_cases": [],
            "processed_results": []
        }
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        
        return final_state["processed_results"]
    
    def _create_workflow(self) -> StateGraph:
        """
        Create LangGraph workflow for vulnerability processing.
        
        Returns:
            StateGraph instance
        """
        # Define the workflow
        workflow = StateGraph(self._state_dict)
        
        # Add nodes
        workflow.add_node("explain", self._generate_explanations)
        workflow.add_node("fix", self._generate_fixes)
        workflow.add_node("test", self._generate_test_cases)
        workflow.add_node("compile", self._compile_results)
        
        # Define edges
        workflow.set_entry_point("explain")
        workflow.add_edge("explain", "fix")
        workflow.add_edge("fix", "test")
        workflow.add_edge("test", "compile")
        workflow.add_edge("compile", END)
        
        return workflow.compile()
    
    def _generate_explanations(self, state: Dict) -> Dict:
        """
        Generate explanations for vulnerabilities.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with explanations
        """
        explanations = []
        
        for vuln in state["vulnerabilities"]:
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
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=512
            )
            
            explanations.append({
                "id": vuln['id'],
                "explanation": response.choices[0].message.content
            })
        
        state["explanations"] = explanations
        return state
    
    def _generate_fixes(self, state: Dict) -> Dict:
        """
        Generate code fixes for vulnerabilities.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with fixes
        """
        fixes = []
        
        for vuln in state["vulnerabilities"]:
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
            - Specifically address Hedera-specific considerations if applicable
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1024
            )
            
            fixes.append({
                "id": vuln['id'],
                "fixed_code": response.choices[0].message.content
            })
        
        state["fixes"] = fixes
        return state
    
    def _generate_test_cases(self, state: Dict) -> Dict:
        """
        Generate test cases for vulnerabilities.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with test cases
        """
        test_cases = []
        
        for vuln in state["vulnerabilities"]:
            prompt = f"""
            Generate a Solidity test case for this vulnerability using Hardhat:
            
            Vulnerability ID: {vuln['id']}
            Description: {vuln['description']}
            
            Requirements:
            - Test should verify vulnerability exists in original code
            - Test should verify fix resolves vulnerability
            - Use Hardhat testing framework
            - Include setup and assertions
            - Consider Hedera-specific testing requirements if applicable
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=1024
            )
            
            test_cases.append({
                "id": vuln['id'],
                "test_case": response.choices[0].message.content
            })
        
        state["test_cases"] = test_cases
        return state
    
    def _compile_results(self, state: Dict) -> Dict:
        """
        Compile all results into a single structure.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with processed results
        """
        processed_results = []
        
        # Map explanations, fixes, and test cases to vulnerabilities
        for vuln in state["vulnerabilities"]:
            vuln_id = vuln["id"]
            
            # Find matching explanation
            explanation = next(
                (e["explanation"] for e in state["explanations"] if e["id"] == vuln_id),
                None
            )
            
            # Find matching fix
            fixed_code = next(
                (f["fixed_code"] for f in state["fixes"] if f["id"] == vuln_id),
                None
            )
            
            # Find matching test case
            test_case = next(
                (t["test_case"] for t in state["test_cases"] if t["id"] == vuln_id),
                None
            )
            
            # Create enhanced vulnerability
            enhanced_vuln = {
                **vuln,
                "explanation": explanation,
                "fixed_code": fixed_code,
                "test_case": test_case
            }
            
            processed_results.append(enhanced_vuln)
        
        state["processed_results"] = processed_results
        return state
    
    @staticmethod
    def _state_dict(vulnerabilities=None, contract_code="", explanations=None,
                   fixes=None, test_cases=None, processed_results=None):
        """
        Create a state dictionary for the workflow.
        
        Returns:
            State dictionary
        """
        return {
            "vulnerabilities": vulnerabilities or [],
            "contract_code": contract_code,
            "explanations": explanations or [],
            "fixes": fixes or [],
            "test_cases": test_cases or [],
            "processed_results": processed_results or []
        }
