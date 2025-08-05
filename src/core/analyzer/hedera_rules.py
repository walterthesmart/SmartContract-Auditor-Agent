"""
Custom Slither detectors for Hedera-specific vulnerabilities.

This module extends Slither's detection capabilities with rules specific to Hedera smart contracts.
"""

from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.core.declarations import Function, Contract
from slither.utils.output import Output


class UnsafeTokenAssociation(AbstractDetector):
    """
    Detector for unsafe token association patterns in Hedera smart contracts.
    
    Hedera requires explicit token association before an account can receive tokens.
    This detector identifies contracts that might be interacting with tokens without
    proper association checks.
    """
    
    ARGUMENT = "hedera-unsafe-token-association"
    HELP = "Unsafe token association patterns"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.MEDIUM
    
    WIKI = "https://docs.hedera.com/hedera/sdks-and-apis/sdks/token-service/associate-tokens-to-an-account"
    WIKI_TITLE = "Unsafe Token Association"
    WIKI_DESCRIPTION = "Contracts that transfer tokens without checking association status may fail."
    WIKI_EXPLOIT_SCENARIO = """
```solidity
contract TokenSender {
    function sendToken(address token, address recipient, uint256 amount) external {
        // No check if recipient has associated the token
        IERC20(token).transfer(recipient, amount);
    }
}
```
The transfer will fail if the recipient hasn't associated the token, potentially causing funds to be lost.
"""
    WIKI_RECOMMENDATION = """
Check if the account has associated the token before transferring:
```solidity
function sendToken(address token, address recipient, uint256 amount) external {
    require(isTokenAssociated(token, recipient), "Token not associated");
    IERC20(token).transfer(recipient, amount);
}

function isTokenAssociated(address token, address account) internal view returns (bool) {
    // Implement association check
    // For example, call a precompiled contract or use try/catch
    return true; // Placeholder
}
```
"""
    
    def _detect(self):
        results = []
        
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                # Skip if function is a constructor or private/internal
                if function.is_constructor or function.visibility in ["private", "internal"]:
                    continue
                
                # Look for token transfer patterns
                if self._has_token_transfer(function) and not self._has_association_check(function):
                    info = [
                        "Token transfer without association check in ",
                        function,
                        ":\n"
                    ]
                    
                    # Add relevant statements
                    for node in function.nodes:
                        if "transfer" in str(node) or "transferFrom" in str(node):
                            info += ["\t- ", node, "\n"]
                    
                    res = self.generate_result(info)
                    results.append(res)
        
        return results
    
    def _has_token_transfer(self, function):
        """Check if function contains token transfer operations."""
        for node in function.nodes:
            # Look for common transfer function calls
            if "transfer(" in str(node) or "transferFrom(" in str(node) or "send(" in str(node):
                return True
        return False
    
    def _has_association_check(self, function):
        """Check if function verifies token association."""
        # This is a simplified check - in a real implementation, you would
        # use more sophisticated analysis to detect association checks
        for node in function.nodes:
            if "associate" in str(node).lower() or "isAssociated" in str(node).lower():
                return True
        return False


class UnsafeHbarHandling(AbstractDetector):
    """
    Detector for unsafe HBAR handling in payable functions.
    
    Identifies payable functions that don't validate the HBAR amount received,
    which could lead to unexpected behavior.
    """
    
    ARGUMENT = "hedera-unsafe-hbar-handling"
    HELP = "Unsafe HBAR handling in payable functions"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.HIGH
    
    WIKI = "https://docs.hedera.com/hedera/sdks-and-apis/sdks/cryptocurrency/transfer-hbar"
    WIKI_TITLE = "Unsafe HBAR Handling"
    WIKI_DESCRIPTION = "Payable functions without HBAR amount validation."
    WIKI_EXPLOIT_SCENARIO = """
```solidity
contract HbarReceiver {
    mapping(address => uint256) public balances;
    
    function deposit() public payable {
        // No validation on msg.value
        balances[msg.sender] += msg.value;
    }
}
```
Users could accidentally send 0 HBAR or an excessive amount.
"""
    WIKI_RECOMMENDATION = """
Add validation to ensure the HBAR amount is within expected ranges:
```solidity
function deposit() public payable {
    require(msg.value > 0, "Amount must be positive");
    require(msg.value <= maxDepositAmount, "Amount exceeds maximum");
    balances[msg.sender] += msg.value;
}
```
"""
    
    def _detect(self):
        results = []
        
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                # Only check payable functions
                if not function.payable:
                    continue
                
                # Check if function validates msg.value
                if not self._has_value_validation(function):
                    info = [
                        "Payable function without HBAR amount validation in ",
                        function,
                        ":\n"
                    ]
                    
                    # Add function definition
                    info += ["\t- Function: ", function, "\n"]
                    
                    res = self.generate_result(info)
                    results.append(res)
        
        return results
    
    def _has_value_validation(self, function):
        """Check if function validates msg.value."""
        for node in function.nodes:
            # Look for conditions involving msg.value
            if "msg.value" in str(node) and ("require" in str(node) or "assert" in str(node) or "if" in str(node)):
                return True
        return False


class HederaGasLimitVulnerability(AbstractDetector):
    """
    Detector for potential gas limit issues specific to Hedera.
    
    Hedera has different gas mechanics than Ethereum, and loops without
    proper bounds can cause transactions to fail.
    """
    
    ARGUMENT = "hedera-gas-limit"
    HELP = "Potential gas limit issues on Hedera"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.MEDIUM
    
    WIKI = "https://docs.hedera.com/hedera/networks/mainnet/fees"
    WIKI_TITLE = "Hedera Gas Limit Issues"
    WIKI_DESCRIPTION = "Contracts with unbounded loops may hit gas limits on Hedera."
    WIKI_EXPLOIT_SCENARIO = """
```solidity
contract ArrayProcessor {
    function processArray(uint256[] memory data) public {
        for (uint i = 0; i < data.length; i++) {
            // Complex processing
            // No upper bound on array size
        }
    }
}
```
If called with a large array, this function may exceed Hedera's gas limits.
"""
    WIKI_RECOMMENDATION = """
Add bounds to loops and array operations:
```solidity
uint256 constant MAX_ARRAY_LENGTH = 100;

function processArray(uint256[] memory data) public {
    require(data.length <= MAX_ARRAY_LENGTH, "Array too large");
    for (uint i = 0; i < data.length; i++) {
        // Processing
    }
}
```
"""
    
    def _detect(self):
        results = []
        
        for contract in self.compilation_unit.contracts_derived:
            for function in contract.functions:
                # Skip if function is a constructor or private/internal
                if function.is_constructor or function.visibility in ["private", "internal"]:
                    continue
                
                # Check for unbounded loops
                if self._has_unbounded_loop(function):
                    info = [
                        "Potentially unbounded loop in ",
                        function,
                        " which may exceed Hedera gas limits:\n"
                    ]
                    
                    # Add relevant statements
                    for node in function.nodes:
                        if "for" in str(node) or "while" in str(node):
                            info += ["\t- ", node, "\n"]
                    
                    res = self.generate_result(info)
                    results.append(res)
        
        return results
    
    def _has_unbounded_loop(self, function):
        """Check if function contains potentially unbounded loops."""
        for node in function.nodes:
            # Look for loops
            if "for" in str(node) or "while" in str(node):
                # Check if there's an array length involved without a bound check
                if ".length" in str(node) and not self._has_array_length_check(function):
                    return True
                # Check for while loops without clear bounds
                if "while" in str(node) and not self._has_iteration_limit(function):
                    return True
        return False
    
    def _has_array_length_check(self, function):
        """Check if function validates array length."""
        for node in function.nodes:
            if ".length" in str(node) and "require" in str(node) and "<=" in str(node):
                return True
        return False
    
    def _has_iteration_limit(self, function):
        """Check if function has iteration limits."""
        # This is a simplified check - in a real implementation, you would
        # use more sophisticated analysis
        for node in function.nodes:
            if "limit" in str(node).lower() or "max" in str(node).lower() and "iteration" in str(node).lower():
                return True
        return False
