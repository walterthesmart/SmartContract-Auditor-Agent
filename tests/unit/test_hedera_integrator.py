"""Tests for the Hedera integration module."""

import pytest
from unittest.mock import patch, MagicMock

from src.integrations.hedera.integrator import HederaService


class TestHederaService:
    """Test suite for the HederaService class."""

    @pytest.fixture
    def mock_hedera_client(self):
        """Mock Hedera client for testing."""
        with patch("src.hedera.integrator.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.forName.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def mock_private_key(self):
        """Mock PrivateKey for testing."""
        with patch("src.hedera.integrator.PrivateKey") as mock_key_class:
            mock_key = MagicMock()
            mock_key_class.fromString.return_value = mock_key
            yield mock_key

    @pytest.fixture
    def hedera_service(self, mock_hedera_client, mock_private_key):
        """Create a HederaService instance for testing."""
        with patch.dict("os.environ", {
            "HEDERA_NETWORK": "testnet",
            "HEDERA_OPERATOR_ID": "0.0.12345",
            "HEDERA_OPERATOR_KEY": "test_key"
        }):
            return HederaService()

    def test_init_with_env_vars(self, mock_hedera_client, mock_private_key):
        """Test initialization with environment variables."""
        with patch.dict("os.environ", {
            "HEDERA_NETWORK": "testnet",
            "HEDERA_OPERATOR_ID": "0.0.12345",
            "HEDERA_OPERATOR_KEY": "test_key"
        }):
            service = HederaService()
            
            assert service.network == "testnet"
            assert service.operator_id == "0.0.12345"
            assert service.operator_key == mock_private_key
            assert service.client == mock_hedera_client

    def test_init_with_params(self, mock_hedera_client, mock_private_key):
        """Test initialization with parameters."""
        service = HederaService(
            network="mainnet",
            operator_id="0.0.67890",
            operator_key="custom_key"
        )
        
        assert service.network == "mainnet"
        assert service.operator_id == "0.0.67890"
        assert service.operator_key == mock_private_key

    def test_init_without_operator_id(self, mock_hedera_client, mock_private_key):
        """Test initialization without operator ID."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError):
                HederaService()

    def test_init_without_operator_key(self, mock_hedera_client, mock_private_key):
        """Test initialization without operator key."""
        with patch.dict("os.environ", {"HEDERA_OPERATOR_ID": "0.0.12345"}, clear=True):
            with pytest.raises(ValueError):
                HederaService()

    @patch("src.hedera.integrator.FileCreateTransaction")
    def test_store_pdf_small_file(self, mock_file_create, hedera_service, mock_hedera_client):
        """Test storing a small PDF file."""
        # Mock transaction
        mock_transaction = MagicMock()
        mock_file_create.return_value = mock_transaction
        mock_transaction.setKeys.return_value = mock_transaction
        mock_transaction.setContents.return_value = mock_transaction
        mock_transaction.setMaxTransactionFee.return_value = mock_transaction
        
        # Mock response and receipt
        mock_response = MagicMock()
        mock_transaction.execute.return_value = mock_response
        
        mock_receipt = MagicMock()
        mock_response.getReceipt.return_value = mock_receipt
        
        mock_file_id = MagicMock()
        mock_file_id.toString.return_value = "0.0.12345"
        mock_receipt.fileId = mock_file_id
        
        # Store PDF
        pdf_bytes = b"PDF_CONTENT" * 100  # Less than 1024 bytes
        file_id = hedera_service.store_pdf(pdf_bytes)
        
        # Verify results
        assert file_id == "0.0.12345"
        mock_transaction.setContents.assert_called_once_with(pdf_bytes)
        mock_transaction.execute.assert_called_once_with(mock_hedera_client)
        mock_response.getReceipt.assert_called_once_with(mock_hedera_client)

    @patch("src.hedera.integrator.FileCreateTransaction")
    @patch("src.hedera.integrator.FileAppendTransaction")
    def test_store_pdf_large_file(self, mock_file_append, mock_file_create, hedera_service, mock_hedera_client):
        """Test storing a large PDF file."""
        # Mock create transaction
        mock_create_transaction = MagicMock()
        mock_file_create.return_value = mock_create_transaction
        mock_create_transaction.setKeys.return_value = mock_create_transaction
        mock_create_transaction.setContents.return_value = mock_create_transaction
        mock_create_transaction.setMaxTransactionFee.return_value = mock_create_transaction
        
        # Mock create response and receipt
        mock_create_response = MagicMock()
        mock_create_transaction.execute.return_value = mock_create_response
        
        mock_create_receipt = MagicMock()
        mock_create_response.getReceipt.return_value = mock_create_receipt
        
        mock_file_id = MagicMock()
        mock_file_id.toString.return_value = "0.0.12345"
        mock_create_receipt.fileId = mock_file_id
        
        # Mock append transaction
        mock_append_transaction = MagicMock()
        mock_file_append.return_value = mock_append_transaction
        mock_append_transaction.setFileId.return_value = mock_append_transaction
        mock_append_transaction.setContents.return_value = mock_append_transaction
        mock_append_transaction.setMaxTransactionFee.return_value = mock_append_transaction
        
        # Mock append response and receipt
        mock_append_response = MagicMock()
        mock_append_transaction.execute.return_value = mock_append_response
        
        mock_append_receipt = MagicMock()
        mock_append_response.getReceipt.return_value = mock_append_receipt
        
        # Store PDF
        pdf_bytes = b"PDF_CONTENT" * 1000  # More than 1024 bytes
        file_id = hedera_service.store_pdf(pdf_bytes)
        
        # Verify results
        assert file_id == "0.0.12345"
        mock_create_transaction.setContents.assert_called_once_with(pdf_bytes[:1024])
        mock_create_transaction.execute.assert_called_once_with(mock_hedera_client)
        mock_create_response.getReceipt.assert_called_once_with(mock_hedera_client)
        
        # Verify append calls
        assert mock_file_append.call_count >= 1
        assert mock_append_transaction.setFileId.call_count >= 1
        assert mock_append_transaction.setContents.call_count >= 1
        assert mock_append_transaction.execute.call_count >= 1
        assert mock_append_response.getReceipt.call_count >= 1

    @patch("src.hedera.integrator.FileContentsQuery")
    def test_get_file(self, mock_file_contents_query, hedera_service, mock_hedera_client):
        """Test retrieving a file."""
        # Mock query
        mock_query = MagicMock()
        mock_file_contents_query.return_value = mock_query
        mock_query.setFileId.return_value = mock_query
        
        # Mock response
        mock_query.execute.return_value = b"FILE_CONTENTS"
        
        # Get file
        contents = hedera_service.get_file("0.0.12345")
        
        # Verify results
        assert contents == b"FILE_CONTENTS"
        mock_query.setFileId.assert_called_once()
        mock_query.execute.assert_called_once_with(mock_hedera_client)

    @patch("src.hedera.integrator.TokenCreateTransaction")
    @patch("src.hedera.integrator.TokenMintTransaction")
    @patch("json.dumps")
    def test_mint_audit_nft(self, mock_json_dumps, mock_token_mint, mock_token_create, hedera_service, mock_hedera_client, mock_private_key):
        """Test minting an audit NFT."""
        # Mock JSON dumps
        mock_json_dumps.return_value = '{"key": "value"}'
        
        # Mock create transaction
        mock_create_transaction = MagicMock()
        mock_token_create.return_value = mock_create_transaction
        mock_create_transaction.setTokenName.return_value = mock_create_transaction
        mock_create_transaction.setTokenSymbol.return_value = mock_create_transaction
        mock_create_transaction.setTokenType.return_value = mock_create_transaction
        mock_create_transaction.setSupplyType.return_value = mock_create_transaction
        mock_create_transaction.setMaxSupply.return_value = mock_create_transaction
        mock_create_transaction.setTreasuryAccountId.return_value = mock_create_transaction
        mock_create_transaction.setAdminKey.return_value = mock_create_transaction
        mock_create_transaction.setSupplyKey.return_value = mock_create_transaction
        mock_create_transaction.setMaxTransactionFee.return_value = mock_create_transaction
        mock_create_transaction.freezeWith.return_value = mock_create_transaction
        mock_create_transaction.sign.return_value = mock_create_transaction
        
        # Mock create response and receipt
        mock_create_response = MagicMock()
        mock_create_transaction.execute.return_value = mock_create_response
        
        mock_create_receipt = MagicMock()
        mock_create_response.getReceipt.return_value = mock_create_receipt
        
        mock_token_id = MagicMock()
        mock_token_id.toString.return_value = "0.0.67890"
        mock_create_receipt.tokenId = mock_token_id
        
        # Mock mint transaction
        mock_mint_transaction = MagicMock()
        mock_token_mint.return_value = mock_mint_transaction
        mock_mint_transaction.setTokenId.return_value = mock_mint_transaction
        mock_mint_transaction.addMetadata.return_value = mock_mint_transaction
        mock_mint_transaction.freezeWith.return_value = mock_mint_transaction
        mock_mint_transaction.sign.return_value = mock_mint_transaction
        
        # Mock mint response and receipt
        mock_mint_response = MagicMock()
        mock_mint_transaction.execute.return_value = mock_mint_response
        
        mock_mint_receipt = MagicMock()
        mock_mint_response.getReceipt.return_value = mock_mint_receipt
        
        # Mint NFT
        metadata = {"key": "value"}
        token_id = hedera_service.mint_audit_nft(metadata)
        
        # Verify results
        assert token_id == "0.0.67890"
        mock_create_transaction.execute.assert_called_once_with(mock_hedera_client)
        mock_create_response.getReceipt.assert_called_once_with(mock_hedera_client)
        
        mock_mint_transaction.setTokenId.assert_called_once_with("0.0.67890")
        mock_mint_transaction.addMetadata.assert_called_once()
        mock_mint_transaction.execute.assert_called_once_with(mock_hedera_client)
        mock_mint_response.getReceipt.assert_called_once_with(mock_hedera_client)

    @patch("src.hedera.integrator.TokenAssociateTransaction")
    def test_associate_token(self, mock_token_associate, hedera_service, mock_hedera_client, mock_private_key):
        """Test associating a token with an account."""
        # Mock transaction
        mock_transaction = MagicMock()
        mock_token_associate.return_value = mock_transaction
        mock_transaction.setAccountId.return_value = mock_transaction
        mock_transaction.setTokenIds.return_value = mock_transaction
        mock_transaction.freezeWith.return_value = mock_transaction
        mock_transaction.sign.return_value = mock_transaction
        
        # Mock response and receipt
        mock_response = MagicMock()
        mock_transaction.execute.return_value = mock_response
        
        mock_receipt = MagicMock()
        mock_response.getReceipt.return_value = mock_receipt
        
        mock_status = MagicMock()
        mock_status.toString.return_value = "SUCCESS"
        mock_receipt.status = mock_status
        
        # Associate token
        status = hedera_service.associate_token("0.0.12345", "0.0.67890")
        
        # Verify results
        assert status == "SUCCESS"
        mock_transaction.setAccountId.assert_called_once()
        mock_transaction.setTokenIds.assert_called_once_with(["0.0.67890"])
        mock_transaction.execute.assert_called_once_with(mock_hedera_client)
        mock_response.getReceipt.assert_called_once_with(mock_hedera_client)
