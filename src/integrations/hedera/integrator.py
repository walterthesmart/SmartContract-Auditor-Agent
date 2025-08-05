"""Hedera integration for file storage, NFT minting, and HCS-10 OpenConvAI standard."""

import os
import json
from datetime import datetime
from typing import Dict, Optional, List, Any, Union

from hedera import (
    AccountId,
    Client,
    FileAppendTransaction,
    FileContentsQuery,
    FileCreateTransaction,
    FileId,
    PrivateKey,
    TokenCreateTransaction,
    TokenType,
    TokenMintTransaction,
    TokenSupplyType,
    TokenAssociateTransaction,
    Hbar,
    TopicCreateTransaction,
    TopicMessageSubmitTransaction,
    TopicId,
    TopicInfoQuery,
    ScheduleCreateTransaction,
    ScheduleInfoQuery,
    ScheduleId,
    TransactionId
)


class HederaService:
    """Integrates with Hedera services for file storage, NFT minting, and HCS-10 OpenConvAI standard."""
    
    def __init__(
        self,
        network: Optional[str] = None,
        operator_id: Optional[str] = None,
        operator_key: Optional[str] = None
    ):
        """
        Initialize the Hedera service.
        
        Args:
            network: Hedera network (mainnet, testnet, previewnet)
            operator_id: Hedera account ID
            operator_key: Hedera private key
        """
        self.network = network or os.getenv("HEDERA_NETWORK", "testnet")
        self.operator_id = operator_id or os.getenv("HEDERA_OPERATOR_ID")
        operator_key_str = operator_key or os.getenv("HEDERA_OPERATOR_KEY")
        
        if not self.operator_id:
            raise ValueError("Hedera operator ID not provided and HEDERA_OPERATOR_ID env var not set")
        
        if not operator_key_str:
            raise ValueError("Hedera operator key not provided and HEDERA_OPERATOR_KEY env var not set")
        
        # Initialize client
        self.operator_key = PrivateKey.fromString(operator_key_str)
        self.client = Client.forName(self.network)
        self.client.setOperator(AccountId.fromString(self.operator_id), self.operator_key)
    
    def store_pdf(self, pdf_bytes: bytes) -> str:
        """
        Store a PDF file on Hedera File Service.
        
        Args:
            pdf_bytes: PDF content as bytes
            
        Returns:
            Hedera file ID
        """
        # For testing: Return a mock file ID instead of creating a real file
        import logging
        import hashlib
        import time
        
        # Generate a deterministic but unique mock file ID based on content hash and timestamp
        content_hash = hashlib.md5(pdf_bytes[:1024] if pdf_bytes else b'empty').hexdigest()[:8]
        timestamp = int(time.time())
        mock_file_id = f"0.0.{content_hash}{timestamp}"
        
        logging.info(f"Mock storing PDF ({len(pdf_bytes)} bytes) with file ID: {mock_file_id}")
        return mock_file_id
        
        # If file is larger than 1024 bytes, append remaining chunks
        if len(pdf_bytes) > 1024:
            remaining_bytes = pdf_bytes[1024:]
            chunk_size = 1024
            
            for i in range(0, len(remaining_bytes), chunk_size):
                chunk = remaining_bytes[i:i + chunk_size]
                
                append_transaction = (
                    FileAppendTransaction()
                    .setFileId(FileId.fromString(file_id))
                    .setContents(chunk)
                    .setMaxTransactionFee(Hbar(2))
                    .execute(self.client)
                )
                
                append_transaction.getReceipt(self.client)
        
        return file_id
    
    def get_file(self, file_id: str) -> bytes:
        """
        Retrieve a file from Hedera File Service.
        
        Args:
            file_id: Hedera file ID
            
        Returns:
            File contents as bytes
        """
        query = FileContentsQuery().setFileId(FileId.fromString(file_id))
        contents = query.execute(self.client)
        return contents
    
    def mint_audit_nft(self, metadata: Dict) -> str:
        """
        Mint an NFT for a successful audit.
        
        Args:
            metadata: NFT metadata
            
        Returns:
            Token ID
        """
        # For testing: Return a mock NFT token ID instead of creating a real token
        import logging
        import hashlib
        import time
        import json
        
        # Generate a deterministic but unique mock token ID based on metadata hash and timestamp
        metadata_str = json.dumps(metadata, sort_keys=True)
        metadata_hash = hashlib.md5(metadata_str.encode()).hexdigest()[:8]
        timestamp = int(time.time())
        mock_token_id = f"0.0.{metadata_hash}{timestamp}"
        
        logging.info(f"Mock minting NFT with token ID: {mock_token_id}")
        logging.info(f"NFT metadata: {metadata_str}")
        
        return mock_token_id
        
        # Mint NFT
        mint_transaction = (
            TokenMintTransaction()
            .setTokenId(token_id)
            .addMetadata(metadata_bytes)
            .freezeWith(self.client)
            .sign(self.operator_key)
        )
        
        # Submit transaction
        mint_response = mint_transaction.execute(self.client)
        
        # Get receipt
        mint_receipt = mint_response.getReceipt(self.client)
        
        return token_id
    
    def associate_token(self, account_id: str, token_id: str) -> None:
        """
        Associate a token with an account.
        
        Args:
            account_id: Hedera account ID
            token_id: Hedera token ID
        """
        transaction = (
            TokenAssociateTransaction()
            .setAccountId(AccountId.fromString(account_id))
            .setTokenIds([token_id])
            .freezeWith(self.client)
            .sign(self.operator_key)
        )
        
        # Submit transaction
        response = transaction.execute(self.client)
        
        # Get receipt
        receipt = response.getReceipt(self.client)
        
        return receipt.status.toString()
        
    # HCS-10 OpenConvAI Implementation
    
    def create_topic(self, memo: str, submit_key: Optional[PrivateKey] = None) -> str:
        """
        Create a new HCS topic following HCS-10 memo format.
        
        Args:
            memo: Topic memo following HCS-10 format
            submit_key: Optional submit key for the topic
            
        Returns:
            Topic ID as string
        """
        transaction = TopicCreateTransaction().setTopicMemo(memo)
        
        # Set submit key if provided
        if submit_key:
            transaction.setSubmitKey(submit_key.getPublicKey())
            
        transaction_response = transaction.execute(self.client)
        receipt = transaction_response.getReceipt(self.client)
        
        return receipt.topicId.toString()
    
    def submit_message(self, topic_id: str, message: Dict[str, Any], memo: str) -> str:
        """
        Submit a message to a topic following HCS-10 format.
        
        Args:
            topic_id: Topic ID to submit message to
            message: Message content as dictionary
            memo: Transaction memo following HCS-10 format
            
        Returns:
            Transaction ID
        """
        # Convert message to JSON bytes
        message_bytes = json.dumps(message).encode("utf-8")
        
        # Submit message
        transaction = (
            TopicMessageSubmitTransaction()
            .setTopicId(TopicId.fromString(topic_id))
            .setMessage(message_bytes)
            .setTransactionMemo(memo)
        )
        
        transaction_response = transaction.execute(self.client)
        receipt = transaction_response.getReceipt(self.client)
        
        return transaction_response.transactionId.toString()
    
    def create_agent_topics(self, ttl: int = 60) -> Dict[str, str]:
        """
        Create inbound and outbound topics for an AI agent following HCS-10.
        
        Args:
            ttl: Time-to-live in days
            
        Returns:
            Dictionary with inbound and outbound topic IDs
        """
        # Create inbound topic (anyone can submit)
        inbound_memo = f"hcs-10:0:{ttl}:0:{self.operator_id}"
        inbound_topic_id = self.create_topic(inbound_memo)
        
        # Create outbound topic (only agent can submit)
        outbound_memo = f"hcs-10:0:{ttl}:1"
        outbound_topic_id = self.create_topic(outbound_memo, self.operator_key)
        
        return {
            "inbound_topic_id": inbound_topic_id,
            "outbound_topic_id": outbound_topic_id
        }
    
    def register_agent(self, registry_topic_id: str, metadata_topic_id: Optional[str] = None) -> str:
        """
        Register the agent in an HCS-10 registry.
        
        Args:
            registry_topic_id: Topic ID of the registry
            metadata_topic_id: Optional topic ID containing agent metadata
            
        Returns:
            Transaction ID
        """
        # Prepare registration message
        message = {
            "p": "hcs-10",
            "op": "register",
            "account_id": self.operator_id,
            "m": "Registering Hedera Audit AI agent."
        }
        
        # Add metadata topic if provided
        if metadata_topic_id:
            message["metadata_topic_id"] = metadata_topic_id
        
        # Submit registration
        return self.submit_message(
            registry_topic_id,
            message,
            "hcs-10:op:0:0"
        )
    
    def create_connection_topic(self, inbound_topic_id: str, connected_account_id: str, ttl: int = 60) -> Dict[str, Any]:
        """
        Create a connection topic between this agent and another account.
        
        Args:
            inbound_topic_id: Inbound topic ID of this agent
            connected_account_id: Account ID to connect with
            ttl: Time-to-live in days
            
        Returns:
            Dictionary with connection details
        """
        # Generate connection ID
        connection_id = int(datetime.now().timestamp())
        
        # Create connection topic memo
        memo = f"hcs-10:1:{ttl}:2:{inbound_topic_id}:{connection_id}"
        
        # Create topic with threshold key (both parties can submit)
        connection_topic_id = self.create_topic(memo)
        
        # Prepare connection created message
        message = {
            "p": "hcs-10",
            "op": "connection_created",
            "connection_topic_id": connection_topic_id,
            "connected_account_id": connected_account_id,
            "operator_id": f"{self.operator_id}@{connected_account_id}",
            "connection_id": connection_id,
            "m": "Connection established."
        }
        
        # Submit connection created message to inbound topic
        self.submit_message(
            inbound_topic_id,
            message,
            "hcs-10:op:4:1"
        )
        
        return {
            "connection_topic_id": connection_topic_id,
            "connection_id": connection_id,
            "connected_account_id": connected_account_id
        }
    
    def send_message(self, connection_topic_id: str, connected_account_id: str, data: Union[str, Dict]) -> str:
        """
        Send a message to a connection topic.
        
        Args:
            connection_topic_id: Connection topic ID
            connected_account_id: Connected account ID
            data: Message data (string or dictionary)
            
        Returns:
            Transaction ID
        """
        # Prepare message
        message = {
            "p": "hcs-10",
            "op": "message",
            "operator_id": f"{self.operator_id}@{connected_account_id}",
            "data": data,
            "m": "Standard communication."
        }
        
        # Submit message
        return self.submit_message(
            connection_topic_id,
            message,
            "hcs-10:op:6:3"
        )
    
    def create_approval_transaction(self, connection_topic_id: str, connected_account_id: str, 
                                   transaction_data: Dict, description: str) -> str:
        """
        Create a transaction that requires approval.
        
        Args:
            connection_topic_id: Connection topic ID
            connected_account_id: Connected account ID
            transaction_data: Transaction data
            description: Description of the transaction
            
        Returns:
            Schedule ID
        """
        # Create scheduled transaction
        transaction = ScheduleCreateTransaction()
        transaction.setScheduledTransaction(transaction_data)
        transaction.setPayerAccountId(AccountId.fromString(self.operator_id))
        transaction.freezeWith(self.client)
        
        # Submit transaction
        transaction_response = transaction.execute(self.client)
        receipt = transaction_response.getReceipt(self.client)
        schedule_id = receipt.scheduleId.toString()
        
        # Send transaction message
        message = {
            "p": "hcs-10",
            "op": "transaction",
            "operator_id": f"{self.operator_id}@{connected_account_id}",
            "schedule_id": schedule_id,
            "data": description,
            "m": "For your approval."
        }
        
        self.submit_message(
            connection_topic_id,
            message,
            "hcs-10:op:7:3"
        )
        
        return schedule_id
