import { ethers } from 'ethers';

const CONTRACT_ABI = [
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_id",
				"type": "uint256"
			}
		],
		"name": "approvePrediction",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address[]",
				"name": "_stakeholders",
				"type": "address[]"
			},
			{
				"internalType": "address",
				"name": "_oracle",
				"type": "address"
			},
			{
				"internalType": "uint8",
				"name": "_minApprovalsRequired",
				"type": "uint8"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "predictionId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "address",
				"name": "approver",
				"type": "address"
			}
		],
		"name": "PredictionApproved",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "predictionId",
				"type": "uint256"
			}
		],
		"name": "PredictionFinalized",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "predictionId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "ipfsHash",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "address",
				"name": "submittedBy",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint8",
				"name": "confidenceScore",
				"type": "uint8"
			}
		],
		"name": "PredictionSubmitted",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_ipfsHash",
				"type": "string"
			},
			{
				"internalType": "uint8",
				"name": "_confidenceScore",
				"type": "uint8"
			}
		],
		"name": "submitPrediction",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "approvedBy",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getOracle",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_id",
				"type": "uint256"
			}
		],
		"name": "getPrediction",
		"outputs": [
			{
				"internalType": "string",
				"name": "ipfsHash",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "submittedBy",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			},
			{
				"internalType": "uint8",
				"name": "confidenceScore",
				"type": "uint8"
			},
			{
				"internalType": "uint8",
				"name": "approvals",
				"type": "uint8"
			},
			{
				"internalType": "bool",
				"name": "isFinalized",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getPredictionCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getStakeholders",
		"outputs": [
			{
				"internalType": "address[]",
				"name": "",
				"type": "address[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_addr",
				"type": "address"
			}
		],
		"name": "isStakeholder",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "minApprovalsRequired",
		"outputs": [
			{
				"internalType": "uint8",
				"name": "",
				"type": "uint8"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "oracle",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "predictionCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "stakeholders",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
];

const CONTRACT_ADDRESS = '0x6b282341D709b3c6f6cfdF366Be2d326dDA39Ce4';
const BSC_TESTNET_RPC = 'https://data-seed-prebsc-1-s1.binance.org:8545/';

class ContractService {
  constructor() {
    this.provider = null;
    this.contract = null;
    this.signer = null;
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return true;

    try {
      // For read-only access, always setup a JsonRpcProvider
      this.provider = new ethers.providers.JsonRpcProvider(BSC_TESTNET_RPC);
      
      // Setup the contract with the read-only provider
      this.contract = new ethers.Contract(
        CONTRACT_ADDRESS,
        CONTRACT_ABI,
        this.provider
      );

      // If MetaMask is available, setup web3 provider
      if (typeof window !== 'undefined' && window.ethereum) {
        try {
          // Request account access if needed
          await window.ethereum.request({ method: 'eth_requestAccounts' });
          
          // Setup Web3Provider
          const web3Provider = new ethers.providers.Web3Provider(window.ethereum);
          this.signer = web3Provider.getSigner();
          
          // Update contract with signer
          this.contract = this.contract.connect(this.signer);
          
          // Listen for chain/account changes
          window.ethereum.on('chainChanged', () => {
            window.location.reload();
          });
          window.ethereum.on('accountsChanged', () => {
            window.location.reload();
          });
        } catch (walletError) {
          console.warn('Wallet connection failed or denied by user:', walletError);
          // Continue with read-only provider
        }
      }

      this.initialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize contract service:', error);
      return false;
    }
  }

  async getAccount() {
    if (!this.signer) return null;
    return await this.signer.getAddress();
  }

  async isStakeholder(address) {
    if (!await this.initialize()) return false;
    return await this.contract.isStakeholder(address);
  }

  async getPredictionCount() {
    if (!await this.initialize()) return 0;
    const count = await this.contract.getPredictionCount();
    return count.toNumber();
  }

  async getPrediction(id) {
    if (!await this.initialize()) return null;
    
    const prediction = await this.contract.getPrediction(id);
    
    return {
      id,
      ipfsHash: prediction.ipfsHash,
      submittedBy: prediction.submittedBy,
      timestamp: new Date(prediction.timestamp.toNumber() * 1000),
      confidenceScore: prediction.confidenceScore,
      approvals: prediction.approvals,
      isFinalized: prediction.isFinalized
    };
  }

  async getMultiplePredictions(startId, count) {
    if (!await this.initialize()) return [];
    
    const predictions = [];
    for (let i = startId; i < startId + count; i++) {
      try {
        const prediction = await this.getPrediction(i);
        predictions.push(prediction);
      } catch (error) {
        console.error(`Error fetching prediction ${i}:`, error);
      }
    }
    
    return predictions;
  }

  async getRecentPredictions(count = 5) {
    if (!await this.initialize()) return [];
    
    const totalCount = await this.getPredictionCount();
    const startId = Math.max(0, totalCount - count);
    
    return this.getMultiplePredictions(startId, Math.min(count, totalCount));
  }

  async approvePrediction(id) {
    if (!await this.initialize() || !this.signer) {
      throw new Error('Not connected to wallet or not a stakeholder');
    }
    
    const tx = await this.contract.approvePrediction(id);
    return await tx.wait();
  }

  async getMinApprovalsRequired() {
    if (!await this.initialize()) return 0;
    return await this.contract.minApprovalsRequired();
  }

  async getStakeholders() {
    if (!await this.initialize()) return [];
    return await this.contract.getStakeholders();
  }

  async checkApproval(predictionId, address) {
    if (!await this.initialize()) return false;
    return await this.contract.approvedBy(predictionId, address);
  }
}

export default new ContractService(); 