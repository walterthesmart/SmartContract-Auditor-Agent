#!/usr/bin/env python3
"""
Create a Hedera Consensus Service (HCS) topic for HCS-10 OpenConvAI integration.
Uses the existing Hedera testnet account credentials from the .env file.
"""

import os
from dotenv import load_dotenv
from hedera import (
    Client, 
    TopicCreateTransaction,
    Hbar,
    PrivateKey
)

def create_hcs_topic():
    # Load environment variables from .env file
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    load_dotenv(os.path.join(project_root, "config", ".env"))
    
    # Get Hedera credentials from environment variables
    operator_id = os.getenv("HEDERA_OPERATOR_ID")
    operator_key = os.getenv("HEDERA_OPERATOR_KEY")
    
    if not operator_id or not operator_key:
        print("Error: Hedera credentials not found in .env file")
        return None
    
    print(f"Using Hedera account: {operator_id}")
    
    # Initialize Hedera client for testnet
    client = Client.forTestnet()
    
    # Remove '0x' prefix if present in the private key
    if operator_key.startswith("0x"):
        operator_key = operator_key[2:]
    
    # Set the operator account ID and private key
    private_key = PrivateKey.fromString(operator_key)
    
    # Parse the account ID string into an AccountId object
    from hedera import AccountId
    account_parts = operator_id.split('.')
    if len(account_parts) == 3:
        shard, realm, account_num = map(int, account_parts)
        account_id = AccountId(shard, realm, account_num)
    else:
        print(f"Error: Invalid account ID format: {operator_id}")
        return None
        
    client.setOperator(account_id, private_key)
    
    # Set a maximum transaction fee
    client.setMaxTransactionFee(Hbar(10))
    
    print("Creating HCS topic for HederaAuditAI...")
    
    # Create a new topic
    transaction = (TopicCreateTransaction()
        .setTopicMemo("HederaAuditAI Registry Topic")
        .setSubmitKey(private_key.getPublicKey())
        .freezeWith(client)
    )
    
    # Sign the transaction with the operator key
    signed_txn = transaction.sign(private_key)
    
    # Submit the transaction to the Hedera network
    txn_response = signed_txn.execute(client)
    
    # Get the receipt to ensure successful execution and get the topic ID
    receipt = txn_response.getReceipt(client)
    topic_id = receipt.topicId
    
    # Convert the topic ID to a string
    topic_id_str = str(topic_id)
    
    print(f"Topic created successfully!")
    print(f"Topic ID: {topic_id_str}")
    print("\nUpdate your .env file with:")
    print(f"HCS10_REGISTRY_TOPIC_ID={topic_id_str}")
    
    return topic_id

if __name__ == "__main__":
    create_hcs_topic()
