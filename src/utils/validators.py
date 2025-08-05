"""Input validation utilities."""

import re
from typing import Dict, Any, List, Optional


def validate_contract_code(code: str) -> Dict[str, Any]:
    """
    Validate smart contract code.
    
    Args:
        code: Contract source code
        
    Returns:
        Validation result with 'valid' boolean and 'errors' list
    """
    errors = []
    
    if not code or not code.strip():
        errors.append("Contract code cannot be empty")
        return {"valid": False, "errors": errors}
    
    # Check for minimum length
    if len(code.strip()) < 10:
        errors.append("Contract code is too short")
    
    # Check for basic Solidity structure
    if not re.search(r'contract\s+\w+', code, re.IGNORECASE):
        errors.append("No contract declaration found")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_hedera_account_id(account_id: str) -> bool:
    """
    Validate Hedera account ID format.
    
    Args:
        account_id: Account ID string (e.g., "0.0.12345")
        
    Returns:
        True if valid, False otherwise
    """
    if not account_id:
        return False
    
    # Hedera account ID format: shard.realm.account
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, account_id))


def validate_hedera_topic_id(topic_id: str) -> bool:
    """
    Validate Hedera topic ID format.
    
    Args:
        topic_id: Topic ID string (e.g., "0.0.12345")
        
    Returns:
        True if valid, False otherwise
    """
    # Same format as account ID
    return validate_hedera_account_id(topic_id)


def validate_contract_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate contract metadata.
    
    Args:
        metadata: Contract metadata dictionary
        
    Returns:
        Validation result with 'valid' boolean and 'errors' list
    """
    errors = []
    required_fields = ["name", "language"]
    
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")
        elif not metadata[field]:
            errors.append(f"Field '{field}' cannot be empty")
    
    # Validate language
    if "language" in metadata:
        valid_languages = ["solidity", "vyper"]
        if metadata["language"].lower() not in valid_languages:
            errors.append(f"Unsupported language: {metadata['language']}")
    
    # Validate name format
    if "name" in metadata and metadata["name"]:
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', metadata["name"]):
            errors.append("Contract name must be a valid identifier")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
