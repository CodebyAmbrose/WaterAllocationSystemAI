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

// Get environment variables
const CONTRACT_ADDRESS = process.env.SMART_CONTRACT_ADDRESS;
const PRIVATE_KEY = process.env.ORACLE_PRIVATE_KEY;
const ORACLE_ADDRESS = process.env.ORACLE_ADDRESS;

// Multiple RPC URLs to try if the first one fails
const RPC_URLS = [
    // This endpoint worked successfully in testing:
    process.env.RPC_URL || "https://data-seed-prebsc-1-s1.binance.org:8545/",
    "https://data-seed-prebsc-1-s1.bnbchain.org:8545",
    "https://data-seed-prebsc-2-s1.bnbchain.org:8545",
    "https://data-seed-prebsc-2-s1.binance.org:8545/",
    "https://data-seed-prebsc-1-s2.binance.org:8545/",
    "https://endpoints.omniatech.io/v1/bsc/testnet/public",
    "https://bsc-testnet.publicnode.com"
];

if (!CONTRACT_ADDRESS) {
    console.error('Error: SMART_CONTRACT_ADDRESS environment variable is required');
    console.error('Please add it to your .env file');
    process.exit(1);
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
            return;
        }

        // Try connecting with different RPC URLs
        let provider = null;
        let connectionSuccess = false;
        let connectionError = null;

        // Try each RPC URL until one works
        for (const rpcUrl of RPC_URLS) {
            try {
                console.log(`Trying to connect to RPC: ${rpcUrl.substring(0, 30)}...`);
                provider = new ethers.providers.JsonRpcProvider(rpcUrl, {
                    chainId: 97,
                    name: 'bsc-testnet',
                    timeout: 30000 // 30 second timeout
                });
                
                // Test the connection by getting block number
                await provider.getBlockNumber();
                console.log(`Successfully connected to ${rpcUrl.substring(0, 30)}...`);
                connectionSuccess = true;
                break; // Exit loop if successful
            } catch (error) {
                console.log(`Failed to connect to ${rpcUrl.substring(0, 30)}...: ${error.message}`);
                connectionError = error;
            }
        }

        if (!connectionSuccess) {
            throw new Error(`Could not connect to any BSC Testnet nodes. Last error: ${connectionError.message}`);
        }
        
        // Create wallet with better error logging
        console.log(`Creating wallet with private key: ${PRIVATE_KEY.substring(0, 6)}...`);
        console.log(`Provider network: ${JSON.stringify(provider.network)}`);
        const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
        console.log(`Wallet created. Address: ${wallet.address}`);
        console.log(`Checking wallet balance...`);
        
        // Get wallet balance
        const balance = await provider.getBalance(wallet.address);
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
        
        // Submit the prediction to the contract
        console.log(`Preparing transaction...`);
        const tx = await contract.submitPrediction(
            ipfsHash,
            confidenceScore, // Contract expects uint8 (0-255)
            {
                gasLimit: 500000 // Explicit gas limit for BSC
            }
        );
        
        console.log(`Transaction submitted: ${tx.hash}`);
        console.log(`View on BSC Testnet Explorer: https://testnet.bscscan.com/tx/${tx.hash}`);
        
        // Wait for transaction confirmation (BSC is faster, so fewer confirmations needed)
        console.log(`Waiting for transaction confirmation...`);
        const receipt = await tx.wait(1); // Wait for 1 confirmation
        console.log(`Transaction confirmed in block ${receipt.blockNumber}`);
        
        // Try to parse prediction ID from logs (if events are emitted)
        let predictionId = null;
        try {
            // Look for PredictionSubmitted event (simplified parsing)
            for (const log of receipt.logs) {
                const event = contract.interface.parseLog(log);
                if (event && event.name === "PredictionSubmitted") {
                    predictionId = event.args.predictionId.toString();
                    break;
                }
            }
        } catch (error) {
            console.log("Could not parse prediction ID from logs");
        }
        
        if (predictionId !== null) {
            console.log(`SUCCESS: Prediction submitted with ID: ${predictionId}`);
        } else {
            console.log('SUCCESS: Prediction submitted successfully');
        }
        
    } catch (error) {
        console.error(`ERROR: Failed to submit to contract: ${error.message}`);
        process.exit(1);
    }
}

// Execute the submission
submitToContract().catch(error => {
    console.error(`Unhandled error: ${error.message}`);
    process.exit(1);
}); 