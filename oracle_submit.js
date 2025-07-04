#!/usr/bin/env node

/**
 * Oracle Submission Script for AIPredictionMultisig Contract
 * 
 * This script submits water consumption prediction data to the AIPredictionMultisig contract.
 * It takes an IPFS hash and confidence score as inputs and calls the submitPrediction function.
 * 
 * Usage: node oracle_submit.js <ipfsHash> <confidenceScore>
 */

// Import required modules
require('dotenv').config();
const ethers = require('ethers');

// Get command line arguments
const ipfsHash = process.argv[2];
const confidenceScore = parseInt(process.argv[3]);

// Validate inputs
if (!ipfsHash) {
    console.error('Error: IPFS hash is required');
    console.error('Usage: node oracle_submit.js <ipfsHash> <confidenceScore>');
    process.exit(1);
}

if (isNaN(confidenceScore) || confidenceScore < 0 || confidenceScore > 100) {
    console.error('Error: Confidence score must be a number between 0 and 100');
    console.error('Usage: node oracle_submit.js <ipfsHash> <confidenceScore>');
    process.exit(1);
}

// ABI for the submitPrediction function in the AIPredictionMultisig contract
const contractABI = [
    "function submitPrediction(string memory _ipfsHash, uint8 _confidenceScore) external returns (uint256)"
];

// environment variables
const CONTRACT_ADDRESS = process.env.SMART_CONTRACT_ADDRESS;
const PRIVATE_KEY = process.env.ORACLE_PRIVATE_KEY;
const ORACLE_ADDRESS = process.env.ORACLE_ADDRESS;

// Optimized RPC URLs (fastest first)
const RPC_URLS = [
    "https://bsc-testnet.publicnode.com", // 
    process.env.RPC_URL || "https://data-seed-prebsc-1-s1.binance.org:8545/",
    "https://endpoints.omniatech.io/v1/bsc/testnet/public",
    "https://data-seed-prebsc-1-s1.bnbchain.org:8545",
    "https://bsc-testnet.nodereal.io/v1/e9a36765eb8a40b9bd12e680a1fd2bc5",
    "https://bsctestapi.terminet.io/rpc",
    "https://bsc-testnet-rpc.publicnode.com"
];

if (!CONTRACT_ADDRESS) {
    console.error('Error: SMART_CONTRACT_ADDRESS environment variable is required');
    console.error('Please add it to your .env file');
    process.exit(1);
}

/**
 * Test RPC connection with timeout
 */
async function testRPCConnection(rpcUrl) {
    try {
        const provider = new ethers.providers.JsonRpcProvider(rpcUrl, {
            chainId: 97,
            name: 'bsc-testnet',
            timeout: 15000 // Optimized to 15 second timeout
        });
        
        // Test the connection with a simple call
        const blockNumber = await Promise.race([
            provider.getBlockNumber(),
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Connection timeout')), 10000)
            )
        ]);
        
        return { provider, success: true, blockNumber };
    } catch (error) {
        return { provider: null, success: false, error: error.message };
    }
}

/**
 * Submit prediction data to the AIPredictionMultisig contract
 */
async function submitToContract() {
    try {
        console.log(`Submitting prediction to AIPredictionMultisig contract:`);
        console.log(`- Network: Binance Smart Chain Testnet (Chain ID: 97)`);
        console.log(`- Smart Contract: ${CONTRACT_ADDRESS}`);
        console.log(`- Oracle Address: ${ORACLE_ADDRESS}`);
        console.log(`- IPFS Hash: ${ipfsHash}`);
        console.log(`- Confidence Score: ${confidenceScore}`);
        
        // If no private key is provided, simulate submission and exit
        if (!PRIVATE_KEY) {
            console.log('No private key found in environment variables. Simulating submission...');
            console.log('SUCCESS: Prediction data submitted to contract (SIMULATION)');
            process.exit(0);
        }

        // Try connecting with different RPC URLs (test multiple in parallel)
        console.log('Testing RPC connections...');
        const connectionPromises = RPC_URLS.slice(0, 3).map(url => // Test first 3 in parallel
            testRPCConnection(url).then(result => ({ url, ...result }))
        );
        
        const results = await Promise.allSettled(connectionPromises);
        let provider = null;
        let selectedRpcUrl = null;
        
        // Find the first successful connection
        for (const result of results) {
            if (result.status === 'fulfilled' && result.value.success) {
                provider = result.value.provider;
                selectedRpcUrl = result.value.url;
                console.log(`Successfully connected to ${selectedRpcUrl}`);
                break;
            }
        }
        
        // If parallel connections failed, try remaining RPCs sequentially
        if (!provider) {
            console.log('Parallel connections failed, trying remaining RPCs...');
            for (const rpcUrl of RPC_URLS.slice(3)) {
                console.log(`Trying to connect to RPC: ${rpcUrl.substring(0, 40)}...`);
                const result = await testRPCConnection(rpcUrl);
                if (result.success) {
                    provider = result.provider;
                    selectedRpcUrl = rpcUrl;
                    console.log(`Successfully connected to ${rpcUrl.substring(0, 40)}...`);
                    break;
                }
                console.log(`Failed to connect to ${rpcUrl.substring(0, 40)}...: ${result.error}`);
            }
        }

        if (!provider) {
            throw new Error(`Could not connect to any BSC Testnet nodes. All RPC endpoints are unavailable.`);
        }
        
        // Create wallet with better error logging
        console.log(`Creating wallet with private key: ${PRIVATE_KEY.substring(0, 6)}...`);
        const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
        console.log(`Wallet created. Address: ${wallet.address}`);
        
        // Get wallet balance with timeout
        console.log(`Checking wallet balance...`);
        const balance = await Promise.race([
            provider.getBalance(wallet.address),
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Balance check timeout')), 10000)
            )
        ]);
        console.log(`Wallet balance: ${ethers.utils.formatEther(balance)} BNB`);
        
        // Verify we're using the correct oracle address
        const walletAddress = wallet.address;
        if (ORACLE_ADDRESS && walletAddress.toLowerCase() !== ORACLE_ADDRESS.toLowerCase()) {
            console.warn(`WARNING: Wallet address ${walletAddress} does not match ORACLE_ADDRESS ${ORACLE_ADDRESS}`);
            console.warn('This might cause transaction failures if the contract expects a specific oracle address');
        }
        
        // Create contract instance
        console.log(`Creating contract instance at ${CONTRACT_ADDRESS}...`);
        const contract = new ethers.Contract(CONTRACT_ADDRESS, contractABI, wallet);
        
        // Get current gas price with fallback
        let gasPrice;
        try {
            gasPrice = await Promise.race([
                provider.getGasPrice(),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Gas price timeout')), 5000)
                )
            ]);
            // Addde 20% to gas price for faster processing
            gasPrice = gasPrice.mul(120).div(100);
        } catch (error) {
            console.log('Using fallback gas price due to timeout');
            gasPrice = ethers.utils.parseUnits('10', 'gwei'); // Fallback gas price
        }
        
        // Submit the prediction to the contract with increased timeout
        console.log(`Preparing transaction with gas price: ${ethers.utils.formatUnits(gasPrice, 'gwei')} gwei`);
        const tx = await Promise.race([
            contract.submitPrediction(
                ipfsHash,
                confidenceScore,
                {
                    gasLimit: 300000, // Increased gas limit
                    gasPrice: gasPrice
                }
            ),
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Transaction submission timeout')), 20000)
            )
        ]);
        
        console.log(`Transaction submitted: ${tx.hash}`);
        console.log(`Using RPC: ${selectedRpcUrl}`);
        console.log(`View on BSC Testnet Explorer: https://testnet.bscscan.com/tx/${tx.hash}`);
        
        // Return immediately without waiting for confirmation (async processing)
        console.log(`Transaction submitted successfully - processing asynchronously`);
        console.log(`SUCCESS: Transaction submitted: ${tx.hash}`);
        
        console.log('SUCCESS: Prediction submitted successfully');
        
        // Close provider connections and exit cleanly
        if (provider && provider.destroy) {
            provider.destroy();
        }
        process.exit(0);
        
    } catch (error) {
        console.error(`ERROR: Failed to submit to contract: ${error.message}`);
        
        // Provide more specific error information
        if (error.message.includes('timeout') || error.message.includes('ETIMEDOUT')) {
            console.error('Network timeout - BSC testnet nodes may be experiencing high load');
            console.error('Consider retrying in a few minutes or check your internet connection');
        } else if (error.message.includes('insufficient funds')) {
            console.error('Insufficient BNB balance for transaction fees');
        } else if (error.message.includes('nonce')) {
            console.error('Transaction nonce issue - try again in a few seconds');
        }
        
        process.exit(1);
    }
}

// Execute the submission
submitToContract().catch(error => {
    console.error(`Unhandled error: ${error.message}`);
    process.exit(1);
}); 