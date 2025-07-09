#!/usr/bin/env node

/**
 * Oracle Submission Script for AIPredictionMultisig Contract
 * 
 * This script serves as an oracle interface for submitting water consumption 
 * prediction data to the AIPredictionMultisig smart contract on Binance Smart Chain Testnet.
 * It validates inputs, establishes secure blockchain connections, and executes 
 * contract transactions with comprehensive error handling and logging.
 * 
 * Features:
 * - Multi-RPC endpoint failover for enhanced reliability
 * - Input validation and sanitization
 * - Comprehensive error handling and logging
 * - Gas price optimization for cost-effective transactions
 * - Transaction timeout management
 * - Oracle address verification
 * 
 * @author Water Allocation System AI Team
 * @version 1.0.0
 * @requires ethers ^5.0.0
 * @requires dotenv
 * 
 * Usage: node oracle_submit.js <ipfsHash> <confidenceScore>
 * 
 * Environment Variables Required:
 * - SMART_CONTRACT_ADDRESS: The deployed contract address
 * - ORACLE_PRIVATE_KEY: Private key for oracle wallet (optional for simulation)
 * - ORACLE_ADDRESS: Expected oracle address for verification
 * - RPC_URL: Primary RPC endpoint (optional, has fallbacks)
 */

// Import required modules for blockchain interaction and environment configuration
require('dotenv').config();
const ethers = require('ethers');

/**
 * Parse and validate command line arguments
 * The script expects exactly two arguments: IPFS hash and confidence score
 */
const ipfsHash = process.argv[2];
const confidenceScore = parseInt(process.argv[3]);

/**
 * Input validation for IPFS hash parameter
 * IPFS hash is required for storing prediction data off-chain
 */
if (!ipfsHash) {
    console.error('Error: IPFS hash is required');
    console.error('Usage: node oracle_submit.js <ipfsHash> <confidenceScore>');
    process.exit(1);
}

/**
 * Input validation for confidence score parameter
 * Confidence score must be an integer between 0-100 representing prediction accuracy
 */
if (isNaN(confidenceScore) || confidenceScore < 0 || confidenceScore > 100) {
    console.error('Error: Confidence score must be a number between 0 and 100');
    console.error('Usage: node oracle_submit.js <ipfsHash> <confidenceScore>');
    process.exit(1);
}

/**
 * Smart Contract ABI (Application Binary Interface)
 * Defines the interface for the submitPrediction function in the AIPredictionMultisig contract
 * 
 * Function signature: submitPrediction(string memory _ipfsHash, uint8 _confidenceScore)
 * Returns: uint256 (transaction/prediction ID)
 */
const contractABI = [
    "function submitPrediction(string memory _ipfsHash, uint8 _confidenceScore) external returns (uint256)"
];

/**
 * Environment variable configuration
 * These variables must be set in the .env file for proper operation
 */
const CONTRACT_ADDRESS = process.env.SMART_CONTRACT_ADDRESS;
const PRIVATE_KEY = process.env.ORACLE_PRIVATE_KEY;
const ORACLE_ADDRESS = process.env.ORACLE_ADDRESS;

/**
 * Binance Smart Chain Testnet RPC endpoints
 * Ordered by reliability and response time for optimal performance
 * The system will attempt connections in parallel for the first three,
 * then sequentially for remaining endpoints if needed
 */
const RPC_URLS = [
    "https://bsc-testnet.publicnode.com",                                          // Primary: Public node with high uptime
    process.env.RPC_URL || "https://data-seed-prebsc-1-s1.binance.org:8545/",    // Secondary: Official Binance endpoint
    "https://endpoints.omniatech.io/v1/bsc/testnet/public",                       // Tertiary: Omniatech public endpoint
    "https://data-seed-prebsc-1-s1.bnbchain.org:8545",                          // Backup: BNB Chain official
    "https://bsc-testnet.nodereal.io/v1/e9a36765eb8a40b9bd12e680a1fd2bc5",      // Backup: NodeReal service
    "https://bsctestapi.terminet.io/rpc",                                        // Backup: Terminet service
    "https://bsc-testnet-rpc.publicnode.com"                                     // Backup: Alternative public node
];

/**
 * Validate required environment variables
 * The smart contract address is mandatory for any operation
 */
if (!CONTRACT_ADDRESS) {
    console.error('Error: SMART_CONTRACT_ADDRESS environment variable is required');
    console.error('Please add it to your .env file');
    process.exit(1);
}

/**
 * Test RPC endpoint connectivity and performance
 * 
 * This function attempts to establish a connection to a given RPC endpoint
 * and validates it by fetching the current block number. It includes timeout
 * handling to prevent hanging on unresponsive endpoints.
 * 
 * @param {string} rpcUrl - The RPC endpoint URL to test
 * @returns {Promise<Object>} Connection result with provider instance or error details
 */
async function testRPCConnection(rpcUrl) {
    try {
        // Create JsonRpcProvider with BSC Testnet configuration
        const provider = new ethers.providers.JsonRpcProvider(rpcUrl, {
            chainId: 97,                    // BSC Testnet chain ID
            name: 'bsc-testnet',           // Network name for ethers.js
            timeout: 15000                 // Connection timeout in milliseconds
        });
        
        /**
         * Test connection reliability by fetching current block number
         * Uses Promise.race to implement a custom timeout shorter than provider timeout
         * This ensures responsive failover to backup RPC endpoints
         */
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
 * Main function to submit prediction data to the AIPredictionMultisig contract
 * 
 * This function orchestrates the entire submission process including:
 * - RPC endpoint selection and failover
 * - Wallet creation and balance verification
 * - Gas price optimization
 * - Transaction submission with timeout handling
 * - Comprehensive error reporting and recovery suggestions
 */
async function submitToContract() {
    try {
        // Log submission parameters for audit trail
        console.log(`Submitting prediction to AIPredictionMultisig contract:`);
        console.log(`- Network: Binance Smart Chain Testnet (Chain ID: 97)`);
        console.log(`- Smart Contract: ${CONTRACT_ADDRESS}`);
        console.log(`- Oracle Address: ${ORACLE_ADDRESS}`);
        console.log(`- IPFS Hash: ${ipfsHash}`);
        console.log(`- Confidence Score: ${confidenceScore}`);
        
        /**
         * Simulation mode for testing without private key
         * Allows validation of all parameters and logic without actual blockchain interaction
         */
        if (!PRIVATE_KEY) {
            console.log('No private key found in environment variables. Simulating submission...');
            console.log('SUCCESS: Prediction data submitted to contract (SIMULATION)');
            process.exit(0);
        }

        /**
         * Parallel RPC connection testing for optimal performance
         * Tests the first three RPC endpoints simultaneously to minimize connection time
         * This approach significantly reduces latency compared to sequential testing
         */
        console.log('Testing RPC connections...');
        const connectionPromises = RPC_URLS.slice(0, 3).map(url => 
            testRPCConnection(url).then(result => ({ url, ...result }))
        );
        
        const results = await Promise.allSettled(connectionPromises);
        let provider = null;
        let selectedRpcUrl = null;
        
        /**
         * Select the first successful connection from parallel tests
         * This ensures we use the fastest responding endpoint
         */
        for (const result of results) {
            if (result.status === 'fulfilled' && result.value.success) {
                provider = result.value.provider;
                selectedRpcUrl = result.value.url;
                console.log(`Successfully connected to ${selectedRpcUrl}`);
                break;
            }
        }
        
        /**
         * Fallback to sequential testing of remaining RPC endpoints
         * If parallel connections failed, try remaining endpoints one by one
         * This provides comprehensive failover coverage
         */
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

        /**
         * Comprehensive RPC failure handling
         * If all endpoints fail, provide clear error message and exit
         */
        if (!provider) {
            throw new Error(`Could not connect to any BSC Testnet nodes. All RPC endpoints are unavailable.`);
        }
        
        /**
         * Wallet creation and initialization
         * Creates an ethers.js wallet instance using the provided private key
         * The wallet is connected to the selected provider for transaction signing
         */
        console.log(`Creating wallet with private key: ${PRIVATE_KEY.substring(0, 6)}...`);
        const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
        console.log(`Wallet created. Address: ${wallet.address}`);
        
        /**
         * Wallet balance verification with timeout protection
         * Ensures the wallet has sufficient BNB for transaction fees
         * Uses timeout to prevent hanging on slow network responses
         */
        console.log(`Checking wallet balance...`);
        const balance = await Promise.race([
            provider.getBalance(wallet.address),
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Balance check timeout')), 10000)
            )
        ]);
        console.log(`Wallet balance: ${ethers.utils.formatEther(balance)} BNB`);
        
        /**
         * Oracle address verification for security
         * Compares the wallet address with the expected oracle address
         * Warns if there's a mismatch that could cause contract rejections
         */
        const walletAddress = wallet.address;
        if (ORACLE_ADDRESS && walletAddress.toLowerCase() !== ORACLE_ADDRESS.toLowerCase()) {
            console.warn(`WARNING: Wallet address ${walletAddress} does not match ORACLE_ADDRESS ${ORACLE_ADDRESS}`);
            console.warn('This might cause transaction failures if the contract expects a specific oracle address');
        }
        
        /**
         * Smart contract instance creation
         * Creates an ethers.js contract instance for interaction with the deployed contract
         * Uses the ABI to define available functions and their signatures
         */
        console.log(`Creating contract instance at ${CONTRACT_ADDRESS}...`);
        const contract = new ethers.Contract(CONTRACT_ADDRESS, contractABI, wallet);
        
        /**
         * Dynamic gas price calculation with fallback
         * Retrieves current network gas price and applies 20% premium for faster processing
         * Falls back to a safe default if gas price retrieval fails
         */
        let gasPrice;
        try {
            gasPrice = await Promise.race([
                provider.getGasPrice(),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Gas price timeout')), 5000)
                )
            ]);
            // Add 20% premium to gas price for faster transaction processing
            gasPrice = gasPrice.mul(120).div(100);
        } catch (error) {
            console.log('Using fallback gas price due to timeout');
            gasPrice = ethers.utils.parseUnits('10', 'gwei'); // Conservative fallback gas price
        }
        
        /**
         * Contract transaction submission with comprehensive configuration
         * Submits the prediction data to the smart contract with optimized parameters:
         * - Increased gas limit to prevent out-of-gas errors
         * - Optimized gas price for timely execution
         * - Timeout protection to prevent hanging transactions
         */
        console.log(`Preparing transaction with gas price: ${ethers.utils.formatUnits(gasPrice, 'gwei')} gwei`);
        const tx = await Promise.race([
            contract.submitPrediction(
                ipfsHash,
                confidenceScore,
                {
                    gasLimit: 300000,          // Conservative gas limit for complex operations
                    gasPrice: gasPrice         // Optimized gas price for network conditions
                }
            ),
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Transaction submission timeout')), 20000)
            )
        ]);
        
        /**
         * Transaction success logging and tracking
         * Provides comprehensive information for monitoring and debugging
         */
        console.log(`Transaction submitted: ${tx.hash}`);
        console.log(`Using RPC: ${selectedRpcUrl}`);
        console.log(`View on BSC Testnet Explorer: https://testnet.bscscan.com/tx/${tx.hash}`);
        
        /**
         * Asynchronous transaction processing
         * Returns immediately after submission without waiting for confirmation
         * This allows the oracle to submit multiple predictions efficiently
         */
        console.log(`Transaction submitted successfully - processing asynchronously`);
        console.log(`SUCCESS: Transaction submitted: ${tx.hash}`);
        
        console.log('SUCCESS: Prediction submitted successfully');
        
        /**
         * Clean resource cleanup and graceful exit
         * Properly closes provider connections to prevent resource leaks
         */
        if (provider && provider.destroy) {
            provider.destroy();
        }
        process.exit(0);
        
    } catch (error) {
        /**
         * Comprehensive error handling and user guidance
         * Provides specific error messages and recovery suggestions
         * based on the type of error encountered
         */
        console.error(`ERROR: Failed to submit to contract: ${error.message}`);
        
        // Provide context-specific error guidance
        if (error.message.includes('timeout') || error.message.includes('ETIMEDOUT')) {
            console.error('Network timeout - BSC testnet nodes may be experiencing high load');
            console.error('Consider retrying in a few minutes or check your internet connection');
        } else if (error.message.includes('insufficient funds')) {
            console.error('Insufficient BNB balance for transaction fees');
            console.error('Please ensure your wallet has enough BNB for gas fees');
        } else if (error.message.includes('nonce')) {
            console.error('Transaction nonce issue - try again in a few seconds');
            console.error('This usually resolves automatically with retry');
        } else if (error.message.includes('reverted')) {
            console.error('Smart contract transaction reverted');
            console.error('Check if oracle address is authorized and parameters are valid');
        }
        
        process.exit(1);
    }
}

/**
 * Script execution entry point
 * Handles any unhandled errors and ensures clean exit
 */
submitToContract().catch(error => {
    console.error(`Unhandled error: ${error.message}`);
    process.exit(1);
}); 