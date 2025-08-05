// deploy_simple_contract.js - Deploy a simple contract to Hedera testnet
const { 
  Client, 
  ContractCreateFlow,
  Hbar,
  PrivateKey,
  ContractFunctionParameters
} = require("@hashgraph/sdk");
require('dotenv').config({ path: './backend/.env' });
const fs = require('fs');

// Very simple storage contract bytecode (pre-compiled)
// This is a basic contract with no constructor parameters
const simpleBytecode = "608060405234801561001057600080fd5b50610150806100206000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c80632e64cec11461003b5780636057361d14610059575b600080fd5b610043610075565b60405161005091906100d9565b60405180910390f35b610073600480360381019061006e919061009d565b61007e565b005b60008054905090565b8060008190555050565b60008135905061009781610103565b92915050565b6000602082840312156100b3576100b26100fe565b5b60006100c184828501610088565b91505092915050565b6100d3816100f4565b82525050565b60006020820190506100ee60008301846100ca565b92915050565b6000819050919050565b600080fd5b61010c816100f4565b811461011757600080fd5b5056fea2646970667358221220404e37f487a89a932dca5e9def0debfc16b3d004946a2f7d5d873c8a05f7965264736f6c63430008070033";

async function deployContract() {
  // Get operator from .env file
  const operatorId = process.env.HEDERA_OPERATOR_ID;
  const operatorKey = process.env.HEDERA_OPERATOR_KEY;

  if (!operatorId || !operatorKey) {
    console.error("Environment variables HEDERA_OPERATOR_ID and HEDERA_OPERATOR_KEY must be present");
    return;
  }

  console.log(`Using Hedera account: ${operatorId}`);

  // Create Hedera client for testnet
  const client = Client.forTestnet();
  
  // Remove '0x' prefix if present
  const privateKeyString = operatorKey.startsWith("0x") ? operatorKey.slice(2) : operatorKey;
  
  // Set the operator with account ID and private key
  client.setOperator(operatorId, privateKeyString);
  client.setMaxTransactionFee(new Hbar(20));

  console.log("Deploying simple contract for testing...");

  try {
    // Create a file on Hedera containing the bytecode
    let contractBytecode = simpleBytecode;
    
    // Create the contract with increased gas limit
    let contractTransaction = await new ContractCreateFlow()
      .setGas(1000000) // Increased from 100000 to 1000000
      .setBytecode(contractBytecode)
      .setAdminKey(PrivateKey.fromString(privateKeyString).publicKey)
      .execute(client);
    
    // Get the receipt
    const receipt = await contractTransaction.getReceipt(client);
    
    // Get the contract ID
    const contractId = receipt.contractId.toString();
    
    console.log(`Contract deployed successfully!`);
    console.log(`Contract ID: ${contractId}`);
    console.log(`\nUpdate your .env file with:`);
    console.log(`AUDIT_REGISTRY_CONTRACT_ID=${contractId}`);
    
    // Update .env file with contract ID
    const envPath = './backend/.env';
    let envContent = fs.readFileSync(envPath, 'utf8');
    
    if (envContent.includes('AUDIT_REGISTRY_CONTRACT_ID=')) {
      // Replace existing value
      envContent = envContent.replace(
        /AUDIT_REGISTRY_CONTRACT_ID=.*/,
        `AUDIT_REGISTRY_CONTRACT_ID=${contractId}`
      );
    } else {
      // Add new entry
      envContent += `\n\n# Smart Contract Configuration\nAUDIT_REGISTRY_CONTRACT_ID=${contractId}\n`;
    }
    
    fs.writeFileSync(envPath, envContent);
    console.log(`Updated ${envPath} with the contract ID`);
    
    return contractId;
  } catch (error) {
    console.error("Error deploying contract:", error);
    process.exit(1);
  }
}

deployContract();
