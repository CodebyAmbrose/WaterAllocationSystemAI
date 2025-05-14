<template>
  <div class="card">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-bold">Prediction History</h2>
      <div class="flex space-x-2">
        <button @click="refreshHistory" class="text-primary hover:text-blue-700 flex items-center text-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center my-8">
      <svg class="animate-spin h-6 w-6 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="ml-2">Loading prediction history...</span>
    </div>

    <div v-else-if="predictions.length === 0" class="text-center py-6 bg-gray-50 rounded-lg">
      <p class="text-gray-500">No historical predictions found</p>
    </div>

    <div v-else>
      <!-- Prediction Timeline -->
      <div class="relative">
        <div class="absolute h-full w-0.5 bg-gray-200 left-5 top-0"></div>
        
        <div v-for="prediction in predictions" :key="prediction.id" class="mb-8 relative pl-14">
          <!-- Timeline Dot -->
          <div 
            class="absolute left-0 bg-white border-4 rounded-full h-10 w-10 flex items-center justify-center"
            :class="{
              'border-green-500': prediction.isFinalized,
              'border-yellow-500': !prediction.isFinalized
            }"
          >
            <span class="text-sm font-semibold">{{ prediction.id }}</span>
          </div>
          
          <!-- Prediction Card -->
          <div 
            class="border rounded-lg p-4 transition-all"
            :class="{
              'border-green-200 bg-green-50': prediction.isFinalized,
              'border-yellow-200 bg-yellow-50': !prediction.isFinalized
            }"
          >
            <div class="flex justify-between items-start">
              <div>
                <div class="flex items-center">
                  <h4 class="font-medium text-gray-900">Prediction #{{ prediction.id }}</h4>
                  <span
                    v-if="prediction.isFinalized"
                    class="ml-2 bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded"
                  >
                    Approved
                  </span>
                  <span 
                    v-else 
                    class="ml-2 bg-yellow-100 text-yellow-800 text-xs font-medium px-2.5 py-0.5 rounded"
                  >
                    Pending Approval
                  </span>
                </div>
                <p class="text-sm text-gray-500 mt-1">
                  {{ formatDate(prediction.timestamp) }}
                </p>
              </div>
              <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                Confidence: {{ prediction.confidenceScore }}%
              </span>
            </div>
            
            <div class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span class="text-xs text-gray-500">IPFS Hash:</span>
                <div class="flex items-center">
                  <span class="text-xs font-mono truncate">{{ prediction.ipfsHash }}</span>
                  <a 
                    :href="`https://gateway.pinata.cloud/ipfs/${prediction.ipfsHash}`" 
                    target="_blank"
                    class="ml-1 text-primary hover:text-blue-700"
                    title="View on IPFS"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </div>
              <div>
                <span class="text-xs text-gray-500">Oracle:</span>
                <div class="flex items-center">
                  <span class="text-xs font-mono truncate">{{ shortenAddress(prediction.submittedBy) }}</span>
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
              <span class="text-xs text-gray-500">Approvals ({{ prediction.approvals }}/{{ minApprovalsRequired }}):</span>
              <div class="flex items-center mt-1">
                <div class="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    class="bg-primary h-2.5 rounded-full" 
                    :style="{ width: `${(prediction.approvals / minApprovalsRequired) * 100}%` }"
                  ></div>
                </div>
              </div>
            </div>
            
            <div class="mt-4 flex justify-end">
              <a 
                :href="`https://testnet.bscscan.com/address/${contractAddress}#readContract`" 
                target="_blank"
                class="text-primary text-xs flex items-center hover:underline"
              >
                View Transaction Details
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>

      <div v-if="error" class="mt-4 p-3 bg-red-100 text-red-800 rounded-lg">
        {{ error }}
      </div>

      <div class="mt-6 flex justify-center">
        <button 
          v-if="hasMorePredictions" 
          @click="loadMorePredictions" 
          class="btn btn-secondary text-sm"
          :disabled="loadingMore"
        >
          <span v-if="loadingMore">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Loading...
          </span>
          <span v-else>Load More</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import contractService from '../services/ContractService';

export default {
  name: 'PredictionHistory',
  data() {
    return {
      predictions: [],
      loading: true,
      loadingMore: false,
      error: null,
      currentPage: 0,
      pageSize: 5,
      totalPredictions: 0,
      minApprovalsRequired: 0,
      contractAddress: '0x6b282341D709b3c6f6cfdF366Be2d326dDA39Ce4'
    };
  },
  computed: {
    hasMorePredictions() {
      return this.predictions.length < this.totalPredictions;
    }
  },
  async mounted() {
    try {
      await this.loadPredictionHistory();
    } catch (error) {
      console.error('Error in mounting PredictionHistory:', error);
      this.error = 'Failed to connect to blockchain. Please refresh the page.';
      this.loading = false;
    }
  },
  methods: {
    async loadPredictionHistory() {
      try {
        this.loading = true;
        this.error = null;
        
        // Initialize contract service
        await contractService.initialize();
        
        // Get total prediction count and minimum approvals required
        this.totalPredictions = await contractService.getPredictionCount();
        this.minApprovalsRequired = await contractService.getMinApprovalsRequired();
        
        // Load the first page of predictions (most recent ones)
        const startId = Math.max(0, this.totalPredictions - this.pageSize);
        const count = Math.min(this.pageSize, this.totalPredictions);
        
        this.predictions = await contractService.getMultiplePredictions(startId, count);
        this.currentPage = 1;
      } catch (error) {
        console.error('Error loading prediction history:', error);
        this.error = 'Failed to load prediction history. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    async loadMorePredictions() {
      try {
        this.loadingMore = true;
        
        const startId = Math.max(0, this.totalPredictions - ((this.currentPage + 1) * this.pageSize));
        const count = Math.min(this.pageSize, startId + 1);
        
        if (startId < 0 || count <= 0) {
          return;
        }
        
        const morePredictions = await contractService.getMultiplePredictions(startId, count);
        this.predictions = [...this.predictions, ...morePredictions];
        this.currentPage++;
      } catch (error) {
        console.error('Error loading more predictions:', error);
        this.error = 'Failed to load more predictions. Please try again.';
      } finally {
        this.loadingMore = false;
      }
    },
    
    async refreshHistory() {
      this.currentPage = 0;
      this.predictions = [];
      await this.loadPredictionHistory();
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
    
    shortenAddress(address) {
      if (!address) return '';
      return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
    }
  }
};
</script> 