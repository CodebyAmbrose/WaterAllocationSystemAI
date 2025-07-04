<template>
  <div>
    <div class="bg-white rounded-lg shadow p-4 md:p-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-4 space-y-2 sm:space-y-0">
        <h2 class="text-xl font-bold text-gray-900">Blockchain Verification</h2>
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 self-start">
          <span class="w-2 h-2 mr-1 bg-green-400 rounded-full"></span>
          Verified
        </span>
      </div>
      
      <div class="space-y-4 md:space-y-5">
        <div class="rounded-lg border border-gray-200 p-3 md:p-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-2 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clip-rule="evenodd" />
            </svg>
            IPFS Hash
          </h3>
          <div class="flex items-start md:items-center bg-gray-50 p-2 md:p-3 rounded-md">
            <div class="font-mono text-xs break-all text-gray-700 pr-2 flex-grow">
              {{ transactionData.ipfsHash }}
            </div>
            <button 
              class="ml-1 text-blue-600 hover:text-blue-800 transition-colors flex-shrink-0" 
              @click="copyToClipboard(transactionData.ipfsHash)"
              title="Copy to clipboard"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
          </div>
          <div class="mt-2 flex space-x-3">
            <button 
              @click="viewPrediction(transactionData.ipfsHash)"
              class="text-blue-600 text-sm flex items-center hover:text-blue-800 transition-colors px-2 py-1 bg-blue-50 rounded hover:bg-blue-100"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              View Prediction
            </button>
            <a 
              :href="`https://gateway.pinata.cloud/ipfs/${transactionData.ipfsHash}`" 
              target="_blank"
              class="text-gray-500 text-sm flex items-center hover:text-gray-700 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              IPFS Gateway
            </a>
          </div>
        </div>

        <div v-if="transactionData.transaction_hash" class="rounded-lg border border-gray-200 p-3 md:p-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-2 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-green-500" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
            </svg>
            Transaction Hash
          </h3>
          <div class="flex items-start md:items-center bg-gray-50 p-2 md:p-3 rounded-md">
            <div class="font-mono text-xs break-all text-gray-700 pr-2 flex-grow">
              {{ transactionData.transaction_hash }}
            </div>
            <button 
              class="ml-1 text-blue-600 hover:text-blue-800 transition-colors flex-shrink-0" 
              @click="copyToClipboard(transactionData.transaction_hash)"
              title="Copy to clipboard"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
          </div>
          <div class="mt-2">
            <a 
              :href="`https://testnet.bscscan.com/tx/${transactionData.transaction_hash}`" 
              target="_blank"
              class="text-blue-600 text-sm flex items-center hover:text-blue-800 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              View on BSC Testnet Explorer
            </a>
          </div>
        </div>

        <div class="rounded-lg border border-gray-200 p-3 md:p-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-indigo-500" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 2a1 1 0 00-1 1v1a1 1 0 002 0V3a1 1 0 00-1-1zM4 4h3a3 3 0 006 0h3a2 2 0 012 2v9a2 2 0 01-2 2H4a2 2 0 01-2-2V6a2 2 0 012-2zm2.5 7a1.5 1.5 0 100-3 1.5 1.5 0 000 3zm2.45 4a2.5 2.5 0 10-4.9 0h4.9zM12 9a1 1 0 100 2h3a1 1 0 100-2h-3zm-1 4a1 1 0 011-1h2a1 1 0 110 2h-2a1 1 0 01-1-1z" clip-rule="evenodd" />
            </svg>
            Smart Contract Details
          </h3>
          
          <div class="space-y-3">
            <div class="rounded-md bg-gray-50 p-2 md:p-3">
              <span class="block text-xs text-gray-500 mb-1">Contract Address:</span>
              <div class="flex items-start md:items-center">
                <span class="font-mono text-xs text-gray-700 pr-2 flex-grow break-all">0x6b282341D709b3c6f6cfdF366Be2d326dDA39Ce4</span>
                <button 
                  class="ml-1 text-blue-600 hover:text-blue-800 transition-colors flex-shrink-0" 
                  @click="copyToClipboard('0x6b282341D709b3c6f6cfdF366Be2d326dDA39Ce4')"
                  title="Copy to clipboard"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
              <div class="mt-1">
                <a 
                  href="https://testnet.bscscan.com/address/0x6b282341D709b3c6f6cfdF366Be2d326dDA39Ce4" 
                  target="_blank"
                  class="text-blue-600 text-xs flex items-center hover:text-blue-800 transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  View on BSC Testnet Explorer
                </a>
              </div>
            </div>
            
            <div class="rounded-md bg-gray-50 p-2 md:p-3">
              <span class="block text-xs text-gray-500 mb-1">Oracle Address:</span>
              <div class="flex items-start md:items-center">
                <span class="font-mono text-xs text-gray-700 pr-2 flex-grow break-all">{{ transactionData.oracle_address }}</span>
                <button 
                  class="ml-1 text-blue-600 hover:text-blue-800 transition-colors flex-shrink-0" 
                  @click="copyToClipboard(transactionData.oracle_address)"
                  title="Copy to clipboard"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-5 md:mt-6 bg-blue-50 p-3 md:p-4 rounded-lg border border-blue-100">
        <h3 class="text-sm font-semibold text-blue-800 mb-2 md:mb-3 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          Verification Process
        </h3>
        <ul class="space-y-2 md:space-y-3 text-sm text-blue-700">
          <li class="flex items-start">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Prediction data uploaded to IPFS for permanent, immutable storage</span>
          </li>
          <li class="flex items-start">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Oracle submits IPFS hash to AIPredictionMultisig contract</span>
          </li>
          <li class="flex items-start">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Stakeholders review prediction and approve via multi-signature process</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Prediction Viewer Modal -->
    <PredictionViewer ref="predictionViewer" />
  </div>
</template>

<script>
import PredictionViewer from './PredictionViewer.vue';

export default {
  name: 'BlockchainInfo',
  components: {
    PredictionViewer
  },
  props: {
    transactionData: {
      type: Object,
      required: true
    }
  },
  methods: {
    copyToClipboard(text) {
      navigator.clipboard.writeText(text)
        .then(() => {
          // You could add a toast notification here in a real application
          console.log('Text copied to clipboard');
        })
        .catch(err => {
          console.error('Failed to copy text: ', err);
        });
    },

    async viewPrediction(ipfsHash) {
      try {
        await this.$refs.predictionViewer.viewPrediction(ipfsHash);
      } catch (error) {
        console.error('Error viewing prediction:', error);
      }
    }
  }
};
</script> 