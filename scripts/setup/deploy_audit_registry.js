// deploy_audit_registry.js - Deploy AuditRegistry contract to Hedera for MoonScape integration
const { 
  Client, 
  ContractCreateFlow,
  Hbar,
  PrivateKey,
  ContractFunctionParameters,
  FileCreateTransaction,
  FileAppendTransaction,
  ContractCreateTransaction
} = require("@hashgraph/sdk");
require('dotenv').config({ path: './config/.env' });
const fs = require('fs');
const solc = require('solc');
const path = require('path');

async function compileContract() {
  console.log("📝 Compiling AuditRegistry.sol...");
  
  // Read the contract source code
  const contractPath = path.join(__dirname, '../../contracts/AuditRegistry.sol');
  const source = fs.readFileSync(contractPath, 'utf8');
  
  // Read OpenZeppelin dependencies
  const ownable = fs.readFileSync('./node_modules/@openzeppelin/contracts/access/Ownable.sol', 'utf8');
  const ierc721 = fs.readFileSync('./node_modules/@openzeppelin/contracts/token/ERC721/IERC721.sol', 'utf8');
  const reentrancyGuard = fs.readFileSync('./node_modules/@openzeppelin/contracts/utils/ReentrancyGuard.sol', 'utf8');
  const context = fs.readFileSync('./node_modules/@openzeppelin/contracts/utils/Context.sol', 'utf8');
  const ierc165 = fs.readFileSync('./node_modules/@openzeppelin/contracts/utils/introspection/IERC165.sol', 'utf8');
  
  const input = {
    language: 'Solidity',
    sources: {
      'AuditRegistry.sol': { content: source },
      '@openzeppelin/contracts/access/Ownable.sol': { content: ownable },
      '@openzeppelin/contracts/token/ERC721/IERC721.sol': { content: ierc721 },
      '@openzeppelin/contracts/utils/ReentrancyGuard.sol': { content: reentrancyGuard },
      '@openzeppelin/contracts/utils/Context.sol': { content: context },
      '@openzeppelin/contracts/utils/introspection/IERC165.sol': { content: ierc165 }
    },
    settings: {
      outputSelection: {
        '*': {
          '*': ['*']
        }
      }
    }
  };
  
  const output = JSON.parse(solc.compile(JSON.stringify(input)));
  
  if (output.errors) {
    output.errors.forEach(error => {
      if (error.severity === 'error') {
        console.error('❌ Compilation error:', error.formattedMessage);
        throw new Error('Contract compilation failed');
      } else {
        console.warn('⚠️ Compilation warning:', error.formattedMessage);
      }
    });
  }
  
  const contract = output.contracts['AuditRegistry.sol']['AuditRegistry'];
  console.log("✅ Contract compiled successfully!");
  
  return {
    bytecode: contract.evm.bytecode.object,
    abi: contract.abi
  };
}

async function deployContract() {
  try {
    console.log("🚀 Starting AuditRegistry deployment for MoonScape integration...");
    console.log("=" * 70);
    
    // Initialize Hedera client
    const operatorId = process.env.HEDERA_OPERATOR_ID;
    const operatorKey = process.env.HEDERA_OPERATOR_KEY;
    
    if (!operatorId || !operatorKey) {
      throw new Error("Please set HEDERA_OPERATOR_ID and HEDERA_OPERATOR_KEY in your .env file");
    }
    
    const client = Client.forTestnet();
    client.setOperator(operatorId, PrivateKey.fromStringECDSA(operatorKey));
    
    console.log(`📋 Using Hedera account: ${operatorId}`);
    console.log(`🌐 Network: ${process.env.HEDERA_NETWORK || 'testnet'}`);
    
    // Compile the contract
    const { bytecode, abi } = await compileContract();
    
    // Store the contract bytecode on Hedera File Service
    console.log("📁 Storing contract bytecode on Hedera File Service...");
    
    const fileCreateTx = new FileCreateTransaction()
      .setContents(bytecode)
      .setKeys([PrivateKey.fromStringECDSA(operatorKey).publicKey])
      .setMaxTransactionFee(new Hbar(2));
    
    const fileCreateResponse = await fileCreateTx.execute(client);
    const fileCreateReceipt = await fileCreateResponse.getReceipt(client);
    const bytecodeFileId = fileCreateReceipt.fileId;
    
    console.log(`✅ Bytecode stored with File ID: ${bytecodeFileId}`);
    
    // Deploy the contract with constructor parameter (owner address)
    console.log("🔨 Deploying AuditRegistry contract...");
    
    const contractCreateTx = new ContractCreateTransaction()
      .setBytecodeFileId(bytecodeFileId)
      .setGas(1000000)
      .setConstructorParameters(
        new ContractFunctionParameters()
          .addAddress(operatorId) // Set deployer as initial owner
      )
      .setMaxTransactionFee(new Hbar(20));
    
    const contractCreateResponse = await contractCreateTx.execute(client);
    const contractCreateReceipt = await contractCreateResponse.getReceipt(client);
    const contractId = contractCreateReceipt.contractId;
    
    console.log("🎉 AuditRegistry deployed successfully!");
    console.log(`📋 Contract ID: ${contractId}`);
    console.log(`📁 Bytecode File ID: ${bytecodeFileId}`);
    console.log(`👤 Owner: ${operatorId}`);
    
    // Update .env file with the new contract ID
    updateEnvFile(contractId.toString());
    
    // Save ABI for future interactions
    saveABI(abi, contractId.toString());
    
    console.log("\n🌙 MoonScape Integration Setup:");
    console.log(`✅ Contract deployed and ready for MoonScape integration`);
    console.log(`✅ Update your MoonScape configuration with Contract ID: ${contractId}`);
    console.log(`✅ The contract is now available for audit registry operations`);
    
    return contractId.toString();
    
  } catch (error) {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  }
}

function updateEnvFile(contractId) {
  const envPath = './config/.env';
  let envContent = fs.readFileSync(envPath, 'utf8');
  
  if (envContent.includes('AUDIT_REGISTRY_CONTRACT_ID=')) {
    envContent = envContent.replace(
      /AUDIT_REGISTRY_CONTRACT_ID=.*/,
      `AUDIT_REGISTRY_CONTRACT_ID=${contractId}`
    );
  } else {
    envContent += `\n\n# Smart Contract Configuration\nAUDIT_REGISTRY_CONTRACT_ID=${contractId}\n`;
  }
  
  fs.writeFileSync(envPath, envContent);
  console.log(`✅ Updated ${envPath} with contract ID: ${contractId}`);
}

function saveABI(abi, contractId) {
  const abiDir = './contracts/abi';
  if (!fs.existsSync(abiDir)) {
    fs.mkdirSync(abiDir, { recursive: true });
  }
  
  const abiPath = path.join(abiDir, `AuditRegistry_${contractId}.json`);
  fs.writeFileSync(abiPath, JSON.stringify(abi, null, 2));
  console.log(`✅ ABI saved to: ${abiPath}`);
}

// Run deployment
if (require.main === module) {
  deployContract()
    .then(contractId => {
      console.log(`\n🎯 Deployment completed successfully!`);
      console.log(`Contract ID: ${contractId}`);
      process.exit(0);
    })
    .catch(error => {
      console.error('❌ Deployment failed:', error);
      process.exit(1);
    });
}

module.exports = { deployContract, compileContract };
