// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title AuditRegistry
 * @dev Contract for registering smart contract audits with HCS-10 OpenConvAI integration
 * This contract allows for:
 * - Registering audits with verification
 * - Linking audit reports to NFTs
 * - Managing audit approvals through HCS-10 messaging
 */
contract AuditRegistry is Ownable, ReentrancyGuard {
    // Struct to store audit information
    struct Audit {
        address contractAddress;
        string contractName;
        uint256 auditScore;
        string reportFileId;
        string nftId;
        uint256 timestamp;
        bool approved;
    }

    // Mapping from contract address to audit
    mapping(address => Audit) public audits;
    
    // Mapping from audit NFT ID to contract address
    mapping(string => address) public auditNFTs;
    
    // Approved auditors
    mapping(address => bool) public approvedAuditors;
    
    // HCS-10 topic IDs
    string public inboundTopicId;
    string public outboundTopicId;
    string public metadataTopicId;
    
    // Events
    event AuditRegistered(address indexed contractAddress, string contractName, uint256 auditScore, string reportFileId, string nftId);
    event AuditApproved(address indexed contractAddress, string nftId);
    event AuditorAdded(address indexed auditor);
    event AuditorRemoved(address indexed auditor);
    event HCS10TopicsSet(string inboundTopicId, string outboundTopicId, string metadataTopicId);

    /**
     * @dev Constructor
     * @param _owner The owner of the contract
     */
    constructor(address _owner) Ownable(_owner) {
        // Initialize contract
    }
    
    /**
     * @dev Set HCS-10 topic IDs
     * @param _inboundTopicId The inbound topic ID
     * @param _outboundTopicId The outbound topic ID
     * @param _metadataTopicId The metadata topic ID
     */
    function setHCS10Topics(
        string memory _inboundTopicId,
        string memory _outboundTopicId,
        string memory _metadataTopicId
    ) external onlyOwner {
        inboundTopicId = _inboundTopicId;
        outboundTopicId = _outboundTopicId;
        metadataTopicId = _metadataTopicId;
        
        emit HCS10TopicsSet(_inboundTopicId, _outboundTopicId, _metadataTopicId);
    }
    
    /**
     * @dev Add an approved auditor
     * @param auditor The address of the auditor to add
     */
    function addAuditor(address auditor) external onlyOwner {
        approvedAuditors[auditor] = true;
        emit AuditorAdded(auditor);
    }
    
    /**
     * @dev Remove an approved auditor
     * @param auditor The address of the auditor to remove
     */
    function removeAuditor(address auditor) external onlyOwner {
        approvedAuditors[auditor] = false;
        emit AuditorRemoved(auditor);
    }
    
    /**
     * @dev Register an audit
     * @param contractAddress The address of the audited contract
     * @param contractName The name of the audited contract
     * @param auditScore The audit score (0-100)
     * @param reportFileId The Hedera file ID of the audit report
     * @param nftId The Hedera token ID of the audit NFT
     */
    function registerAudit(
        address contractAddress,
        string memory contractName,
        uint256 auditScore,
        string memory reportFileId,
        string memory nftId
    ) external nonReentrant {
        // Check that the sender is an approved auditor
        require(approvedAuditors[msg.sender], "Not an approved auditor");
        
        // Check that the audit score is valid
        require(auditScore <= 100, "Audit score must be between 0 and 100");
        
        // Register the audit
        audits[contractAddress] = Audit({
            contractAddress: contractAddress,
            contractName: contractName,
            auditScore: auditScore,
            reportFileId: reportFileId,
            nftId: nftId,
            timestamp: block.timestamp,
            approved: false
        });
        
        // Link the NFT to the contract
        auditNFTs[nftId] = contractAddress;
        
        emit AuditRegistered(contractAddress, contractName, auditScore, reportFileId, nftId);
    }
    
    /**
     * @dev Approve an audit (can be triggered through HCS-10 message)
     * @param contractAddress The address of the audited contract
     */
    function approveAudit(address contractAddress) external onlyOwner {
        // Check that the audit exists
        require(audits[contractAddress].contractAddress == contractAddress, "Audit does not exist");
        
        // Approve the audit
        audits[contractAddress].approved = true;
        
        emit AuditApproved(contractAddress, audits[contractAddress].nftId);
    }
    
    /**
     * @dev Get audit information
     * @param contractAddress The address of the audited contract
     * @return Audit information
     */
    function getAudit(address contractAddress) external view returns (Audit memory) {
        return audits[contractAddress];
    }
    
    /**
     * @dev Get contract address from NFT ID
     * @param nftId The Hedera token ID of the audit NFT
     * @return The address of the audited contract
     */
    function getContractFromNFT(string memory nftId) external view returns (address) {
        return auditNFTs[nftId];
    }
    
    /**
     * @dev Check if a contract has been audited
     * @param contractAddress The address of the contract to check
     * @return Whether the contract has been audited
     */
    function isAudited(address contractAddress) external view returns (bool) {
        return audits[contractAddress].contractAddress == contractAddress;
    }
    
    /**
     * @dev Check if a contract has been approved
     * @param contractAddress The address of the contract to check
     * @return Whether the contract has been approved
     */
    function isApproved(address contractAddress) external view returns (bool) {
        return audits[contractAddress].approved;
    }
}
