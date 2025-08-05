// check_hedera_account.js - Check Hedera account status and balance
const { 
  Client, 
  AccountBalanceQuery,
  PrivateKey,
  Hbar
} = require("@hashgraph/sdk");
require('dotenv').config({ path: './config/.env' });

async function checkAccount() {
  try {
    console.log("🔍 Checking Hedera Account Status");
    console.log("=" * 50);
    
    // Get environment variables
    const operatorId = process.env.HEDERA_OPERATOR_ID;
    const operatorKey = process.env.HEDERA_OPERATOR_KEY;
    const network = process.env.HEDERA_NETWORK || 'testnet';
    
    if (!operatorId || !operatorKey) {
      throw new Error("Missing HEDERA_OPERATOR_ID or HEDERA_OPERATOR_KEY in .env file");
    }
    
    console.log(`📋 Account ID: ${operatorId}`);
    console.log(`🌐 Network: ${network}`);
    console.log(`🔑 Private Key: ${operatorKey.substring(0, 8)}...`);
    
    // Initialize client with longer timeout
    const client = Client.forTestnet();
    client.setOperator(operatorId, PrivateKey.fromStringECDSA(operatorKey));
    
    // Set request timeout to 30 seconds
    client.setRequestTimeout(30000);
    
    console.log("\n🔗 Testing connection to Hedera network...");
    
    // Check account balance
    const balanceQuery = new AccountBalanceQuery()
      .setAccountId(operatorId);
    
    console.log("💰 Querying account balance...");
    const balance = await balanceQuery.execute(client);
    
    console.log("\n✅ Connection successful!");
    console.log(`💰 Account Balance: ${balance.hbars.toString()}`);
    console.log(`🪙 Token Balances: ${balance.tokens.size} tokens`);
    
    // Check if balance is sufficient for deployment
    const hbarBalance = balance.hbars.toTinybars();
    const requiredBalance = Hbar.fromHbars(50).toTinybars(); // 50 HBAR minimum
    
    if (hbarBalance.gte(requiredBalance)) {
      console.log("✅ Sufficient balance for contract deployment");
    } else {
      console.log("⚠️  Low balance - consider adding more HBAR for deployment");
      console.log(`   Required: ~50 HBAR, Current: ${balance.hbars.toString()}`);
    }
    
    // Test a simple transaction (account info query)
    console.log("\n🧪 Testing transaction capability...");
    
    try {
      const accountInfo = await client.getAccountInfo(operatorId);
      console.log("✅ Transaction test successful");
      console.log(`📊 Account Key: ${accountInfo.key.toString().substring(0, 20)}...`);
    } catch (error) {
      console.log("❌ Transaction test failed:", error.message);
    }
    
    client.close();
    
    console.log("\n🎯 Account Status: READY for deployment");
    return true;
    
  } catch (error) {
    console.error("\n❌ Account check failed:");
    console.error(`Error: ${error.message}`);
    
    if (error.message.includes("UNKNOWN")) {
      console.log("\n🔧 Troubleshooting suggestions:");
      console.log("1. Check your internet connection");
      console.log("2. Verify firewall settings (allow ports 50211, 50212)");
      console.log("3. Try disabling VPN if using one");
      console.log("4. Check if corporate proxy is blocking gRPC");
      console.log("5. Wait a few minutes and retry");
    }
    
    if (error.message.includes("INVALID_ACCOUNT_ID")) {
      console.log("\n🔧 Account ID issue:");
      console.log("1. Verify HEDERA_OPERATOR_ID format (e.g., 0.0.123456)");
      console.log("2. Ensure account exists on testnet");
    }
    
    if (error.message.includes("INVALID_SIGNATURE")) {
      console.log("\n🔧 Private key issue:");
      console.log("1. Verify HEDERA_OPERATOR_KEY is correct");
      console.log("2. Ensure key matches the account ID");
    }
    
    return false;
  }
}

// Run the check
if (require.main === module) {
  checkAccount()
    .then(success => {
      if (success) {
        console.log("\n🚀 Ready to proceed with deployment!");
        process.exit(0);
      } else {
        console.log("\n🛑 Please fix the issues above before deploying.");
        process.exit(1);
      }
    })
    .catch(error => {
      console.error('Unexpected error:', error);
      process.exit(1);
    });
}

module.exports = { checkAccount };
