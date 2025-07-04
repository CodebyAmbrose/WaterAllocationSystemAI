<template>
  <div class="card">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-bold">Stakeholder Dashboard</h2>
      <div class="flex space-x-2">
        <div v-if="account" class="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
          Connected: {{ shortenAddress(account) }}
        </div>
        <button v-else @click="connectWallet" class="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full hover:bg-blue-200">
          Connect Wallet
        </button>
        <div v-if="isStakeholder" class="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">
          Stakeholder
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center my-8">
      <svg class="animate-spin h-6 w-6 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="ml-2">Loading blockchain data...</span>
    </div>

    <div v-else-if="!account" class="text-center py-8">
      <p class="text-gray-500">Connect your wallet to view and approve predictions</p>
    </div>

    <div v-else-if="!isStakeholder" class="text-center py-8 bg-yellow-50 rounded-lg p-4">
      <p class="text-yellow-700">Your account is not registered as a stakeholder in the contract</p>
      <p class="text-sm text-yellow-600 mt-2">Only approved stakeholders can view and approve predictions</p>
    </div>

    <div v-else>
      <div class="mb-4 p-3 bg-blue-50 rounded-lg">
        <div class="flex justify-between items-center mb-2">
          <h3 class="text-blue-800 font-semibold">Multi-Signature Requirements</h3>
          <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
            {{ minApprovals }} of {{ stakeholders.length }} required
          </span>
        </div>
        <p class="text-sm text-blue-700">
          Each prediction requires approval from at least {{ minApprovals }} stakeholders before it's finalized.
        </p>
      </div>

      <h3 class="text-lg font-semibold mb-4">Predictions Awaiting Approval</h3>
      
      <div v-if="predictions.length === 0" class="text-center py-6 bg-gray-50 rounded-lg">
        <p class="text-gray-500">No predictions found</p>
      </div>
      
      <div v-else class="space-y-4">
        <div 
          v-for="prediction in predictions" 
          :key="prediction.id" 
          class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
          :class="{ 'bg-green-50 border-green-200': prediction.isFinalized }"
        >
          <div class="flex justify-between items-start">
            <div>
              <h4 class="font-medium text-gray-900">Prediction #{{ prediction.id }}</h4>
              <p class="text-sm text-gray-500 mt-1">
                {{ formatDate(prediction.timestamp) }}
              </p>
            </div>
            <div class="flex space-x-2">
              <span
                v-if="prediction.isFinalized"
                class="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded"
              >
                Finalized
              </span>
              <span 
                v-else 
                class="bg-yellow-100 text-yellow-800 text-xs font-medium px-2.5 py-0.5 rounded"
              >
                Pending Approval
              </span>
              <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                Confidence: {{ prediction.confidenceScore }}%
              </span>
            </div>
          </div>
          
          <div class="mt-3 grid grid-cols-2 gap-4">
            <div>
              <span class="text-xs text-gray-500">IPFS Hash:</span>
              <div class="flex items-center">
                <span class="text-xs font-mono truncate">{{ prediction.ipfsHash }}</span>
                <button 
                  @click="viewPrediction(prediction.ipfsHash)"
                  class="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-700 hover:bg-blue-200 rounded transition-colors"
                  title="View Prediction Details"
                >
                  View Details
                </button>
                <a 
                  :href="`https://gateway.pinata.cloud/ipfs/${prediction.ipfsHash}`" 
                  target="_blank"
                  class="ml-1 text-gray-400 hover:text-gray-600"
                  title="View on IPFS"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
            <div>
              <span class="text-xs text-gray-500">Submitted By:</span>
              <div class="flex items-center">
                <span class="text-xs font-mono truncate">{{ prediction.submittedBy }}</span>
                <a 
                  :href="`https://testnet.bscscan.com/address/${prediction.submittedBy}`" 
                  target="_blank"
                  class="ml-1 text-primary hover:text-blue-700"
                  title="View on BSC Testnet Explorer"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
          
          <div class="mt-3">
            <span class="text-xs text-gray-500">Approvals Progress:</span>
            <div class="flex items-center mt-1">
              <div class="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  class="bg-primary h-2.5 rounded-full" 
                  :style="{ width: `${(prediction.approvals / minApprovals) * 100}%` }"
                ></div>
              </div>
              <span class="ml-2 text-xs text-gray-700">{{ prediction.approvals }} / {{ minApprovals }}</span>
            </div>
          </div>
          
          <div class="mt-4 flex justify-between">
            <button 
              v-if="!prediction.isFinalized && !approvalStatus[prediction.id]" 
              @click="approvePrediction(prediction.id)"
              class="btn btn-primary text-sm px-3 py-1"
              :disabled="approvingId === prediction.id"
            >
              <span v-if="approvingId === prediction.id">
                <svg class="animate-spin -ml-1 mr-1 h-4 w-4 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Approving...
              </span>
              <span v-else>Approve Prediction</span>
            </button>
            <span v-else-if="approvalStatus[prediction.id]" class="text-green-600 text-sm flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Already Approved
            </span>
            <div></div>
            <a 
              :href="`https://testnet.bscscan.com/address/${CONTRACT_ADDRESS}#readContract`" 
              target="_blank"
              class="text-primary text-sm flex items-center hover:underline"
            >
              View Contract Details
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>
      </div>

      <div v-if="error" class="mt-4 p-3 bg-red-100 text-red-800 rounded-lg">
        {{ error }}
      </div>
    </div>

    <!-- Prediction Viewer Modal -->
    <PredictionViewer ref="predictionViewer" />
  </div>
</template>

<script>
import contractService from '../services/ContractService';
import PredictionViewer from './PredictionViewer.vue';

const CONTRACT_ADDRESS = '0x6b282341D709b3c6f6cfdF366Be2d326dDA39Ce4';

export default {
  name: 'StakeholderDashboard',
  components: {
    PredictionViewer
  },
  data() {
    return {
      CONTRACT_ADDRESS,
      loading: true,
      error: null,
      account: null,
      isStakeholder: false,
      predictions: [],
      stakeholders: [],
      minApprovals: 0,
      approvingId: null,
      approvalStatus: {},
      refreshInterval: null
    };
  },
  async mounted() {
    try {
      await this.loadBlockchainData();
      // Refresh data every 30 seconds
      this.refreshInterval = setInterval(() => {
        this.refreshData();
      }, 30000);
    } catch (error) {
      console.error('Error in mounting StakeholderDashboard:', error);
      this.error = 'Failed to connect to blockchain. Please refresh the page.';
      this.loading = false;
    }
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  methods: {
    async connectWallet() {
      try {
        this.loading = true;
        // Initialize the contract service which will connect to MetaMask
        await contractService.initialize();
        await this.loadBlockchainData();
      } catch (error) {
        console.error('Failed to connect wallet:', error);
        this.error = 'Failed to connect wallet. Make sure MetaMask is installed and unlocked.';
      } finally {
        this.loading = false;
      }
    },
    
    async loadBlockchainData() {
      try {
        this.loading = true;
        this.error = null;
        
        // Get connected account
        this.account = await contractService.getAccount();
        
        if (this.account) {
          // Check if connected account is a stakeholder
          this.isStakeholder = await contractService.isStakeholder(this.account);
          
          if (this.isStakeholder) {
            // Load stakeholder-specific data
            this.stakeholders = await contractService.getStakeholders();
            this.minApprovals = await contractService.getMinApprovalsRequired();
            this.predictions = await contractService.getRecentPredictions(10);
            
            // Check approval status for each prediction
            for (const prediction of this.predictions) {
              this.approvalStatus[prediction.id] = await contractService.checkApproval(prediction.id, this.account);
            }
          }
        }
      } catch (error) {
        console.error('Error loading blockchain data:', error);
        this.error = 'Failed to load blockchain data. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    async refreshData() {
      try {
        // Update approval statuses and get new predictions
        const predictions = await contractService.getRecentPredictions(10);
        
        // Update approval status for each prediction
        for (const prediction of predictions) {
          if (!this.approvalStatus[prediction.id]) {
            this.approvalStatus[prediction.id] = await contractService.checkApproval(prediction.id, this.account);
          }
        }
        
        this.predictions = predictions;
      } catch (error) {
        console.error('Error refreshing data:', error);
      }
    },
    
    async approvePrediction(id) {
      try {
        this.approvingId = id;
        this.error = null;
        
        const tx = await contractService.approvePrediction(id);
        console.log('Approval transaction:', tx);
        
        // Update approval status
        this.approvalStatus[id] = true;
        
        // Refresh the predictions to get updated approval counts and check finalization
        await this.refreshData();
        
        // Check if this approval finalized the prediction
        const updatedPrediction = this.predictions.find(p => p.id === id);
        if (updatedPrediction && updatedPrediction.isFinalized) {
          // Prediction is now finalized! Update dashboard stats counter via API
          try {
            const response = await fetch('http://localhost:8000/stats/approve', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ 
                prediction_id: id,
                finalized: true
              })
            });
            
            if (response.ok) {
              const data = await response.json();
              console.log('Dashboard stats updated for finalized prediction:', data);
              // Emit event to parent to update dashboard stats in real-time
              this.$emit('approval-updated', data.stats);
            }
          } catch (apiError) {
            console.warn('Failed to update dashboard stats:', apiError);
            // Don't fail the whole approval if dashboard update fails
          }
        } else {
          console.log(`Prediction ${id} approved but not yet finalized (${updatedPrediction?.approvals}/${this.minApprovals} approvals)`);
        }
      } catch (error) {
        console.error('Error approving prediction:', error);
        this.error = 'Failed to approve prediction. ' + error.message;
      } finally {
        this.approvingId = null;
      }
    },
    
    shortenAddress(address) {
      if (!address) return '';
      return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
    },
    
    formatDate(timestamp) {
      if (!timestamp) return '';
      return new Date(timestamp).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    async viewPrediction(ipfsHash) {
      try {
        // For now, we'll use the IPFS hash as identifier
        // The backend will search for predictions containing this hash
        // Or we could map IPFS hashes to prediction filenames
        await this.$refs.predictionViewer.viewPrediction(ipfsHash);
      } catch (error) {
        console.error('Error viewing prediction:', error);
        this.error = 'Failed to load prediction details: ' + error.message;
      }
    }
  }
};
</script> 