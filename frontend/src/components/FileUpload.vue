<template>
  <div class="bg-white rounded-lg shadow p-4 md:p-6">
    <h2 class="text-xl font-bold text-gray-900 mb-3 md:mb-4">Upload Water Consumption Data</h2>
    <p class="text-sm text-gray-600 mb-4 md:mb-6">
      Upload a CSV or JSON file with water consumption data to generate predictions using AI.
      The prediction will be submitted to the blockchain for stakeholder approval.
    </p>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <svg class="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="ml-3 text-gray-600">Verifying stakeholder access...</span>
    </div>

    <!-- Not Connected to Wallet -->
    <div v-else-if="!account" class="text-center py-12 bg-yellow-50 rounded-lg border border-yellow-200">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-yellow-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
      <h3 class="text-lg font-medium text-yellow-800 mb-2">Wallet Connection Required</h3>
      <p class="text-sm text-yellow-700 mb-6 max-w-md mx-auto">
        You must connect your wallet and verify stakeholder status to upload data and generate predictions.
      </p>
      <button 
        @click="connectWallet"
        class="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors duration-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Connect Wallet
      </button>
    </div>

    <!-- Not a Stakeholder -->
    <div v-else-if="!isStakeholder" class="text-center py-12 bg-red-50 rounded-lg border border-red-200">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-red-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728" />
      </svg>
      <h3 class="text-lg font-medium text-red-800 mb-2">Access Restricted</h3>
      <p class="text-sm text-red-700 mb-4 max-w-md mx-auto">
        Your wallet address is not registered as a stakeholder in the system. Only approved stakeholders can upload data and generate predictions.
      </p>
      <div class="text-xs text-red-600 bg-red-100 rounded-lg p-3 max-w-md mx-auto mb-4">
        <strong>Connected Address:</strong> {{ shortenAddress(account) }}
      </div>
      <button 
        @click="connectWallet"
        class="inline-flex items-center px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition-colors duration-200"
      >
        Try Different Wallet
      </button>
    </div>

    <!-- Stakeholder Authenticated - Normal Upload Interface -->
    <div v-else>
      <!-- Stakeholder Status Banner -->
      <div class="mb-6 p-3 bg-green-50 rounded-lg border border-green-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-sm font-medium text-green-800">Verified Stakeholder</span>
          </div>
          <span class="text-xs text-green-700 bg-green-100 px-2 py-1 rounded">{{ shortenAddress(account) }}</span>
        </div>
      </div>

      <!-- File Upload Area -->
      <div class="mb-4 md:mb-6">
        <div 
          class="border-2 border-dashed border-gray-300 rounded-lg p-4 md:p-8 text-center cursor-pointer transition-all duration-200 hover:border-blue-500 hover:bg-blue-50"
          @click="triggerFileInput"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleFileDrop"
          :class="{ 'border-blue-500 bg-blue-50': isDragging }"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 md:h-12 md:w-12 mx-auto text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p class="mt-3 md:mt-4 text-sm font-medium text-gray-900">
            {{ fileName || 'Drop your file here, or click to select' }}
          </p>
          <p class="mt-1 md:mt-2 text-xs text-gray-500">
            CSV or JSON files only (max. 10MB)
          </p>
        </div>
        <input 
          ref="fileInput" 
          type="file" 
          class="hidden" 
          accept=".csv,.json"
          @change="handleFileSelection" 
        />
      </div>

      <!-- Upload Controls -->
      <div class="flex flex-col sm:flex-row sm:justify-between space-y-3 sm:space-y-0">
        <button 
          class="w-full sm:w-auto px-4 py-2 bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200 flex items-center justify-center"
          @click="uploadFile"
          :disabled="!selectedFile || isUploading"
          :class="{ 'opacity-50 cursor-not-allowed': !selectedFile || isUploading }"
        >
          <span v-if="isUploading">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing...
          </span>
          <span v-else>Generate Prediction</span>
        </button>
        <button 
          class="w-full sm:w-auto px-4 py-2 bg-gray-200 text-gray-700 rounded-md shadow-sm hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200"
          @click="resetForm"
          :disabled="!selectedFile || isUploading"
          :class="{ 'opacity-50 cursor-not-allowed': !selectedFile || isUploading }"
        >
          Clear
        </button>
      </div>
    </div>

    <div v-if="error" class="mt-4 md:mt-6 p-3 md:p-4 bg-red-100 text-red-800 rounded-lg flex items-start">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      <p class="text-sm">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import contractService from '../services/ContractService';

export default {
  name: 'FileUpload',
  data() {
    return {
      // Authentication state
      loading: true,
      account: null,
      isStakeholder: false,
      
      // File upload state  
      selectedFile: null,
      fileName: '',
      isUploading: false,
      isDragging: false,
      error: null,
      apiBaseUrl: 'http://localhost:8000'
    };
  },
  async mounted() {
    await this.checkStakeholderAccess();
  },
  methods: {
    async connectWallet() {
      try {
        this.loading = true;
        this.error = null;
        
        // Initialize the contract service which will connect to MetaMask
        await contractService.initialize();
        await this.checkStakeholderAccess();
      } catch (error) {
        console.error('Failed to connect wallet:', error);
        this.error = 'Failed to connect wallet. Make sure MetaMask is installed and unlocked.';
        this.loading = false;
      }
    },

    async checkStakeholderAccess() {
      try {
        this.loading = true;
        this.error = null;
        
        // Get connected account
        this.account = await contractService.getAccount();
        
        if (this.account) {
          // Check if connected account is a stakeholder
          this.isStakeholder = await contractService.isStakeholder(this.account);
          console.log(`Account ${this.account} stakeholder status: ${this.isStakeholder}`);
        }
      } catch (error) {
        console.error('Error checking stakeholder access:', error);
        this.error = 'Failed to verify stakeholder status. Please try again.';
      } finally {
        this.loading = false;
      }
    },

    shortenAddress(address) {
      if (!address) return '';
      return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
    },

    triggerFileInput() {
      if (!this.isStakeholder) return;
      this.$refs.fileInput.click();
    },
    
    handleFileSelection(event) {
      if (!this.isStakeholder) return;
      const file = event.target.files[0];
      if (file) {
        this.validateAndSetFile(file);
      }
    },
    
    handleFileDrop(event) {
      if (!this.isStakeholder) return;
      this.isDragging = false;
      const file = event.dataTransfer.files[0];
      if (file) {
        this.validateAndSetFile(file);
      }
    },
    
    validateAndSetFile(file) {
      // Check file type
      const allowedTypes = ['.csv', '.json'];
      const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
      
      if (!allowedTypes.includes(fileExtension)) {
        this.error = 'Only CSV or JSON files are allowed';
        return;
      }

      // Check file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        this.error = 'File size should not exceed 10MB';
        return;
      }

      this.selectedFile = file;
      this.fileName = file.name;
      this.error = null;
    },
    
    async uploadFile() {
      if (!this.selectedFile || !this.isStakeholder) {
        console.log('Upload blocked: File selected:', !!this.selectedFile, 'Is stakeholder:', this.isStakeholder);
        return;
      }

      console.log('🚀 Starting upload with stakeholder address:', this.account);
      this.isUploading = true;
      this.error = null;

      const formData = new FormData();
      formData.append('file', this.selectedFile);
      // Include stakeholder address for backend verification
      formData.append('stakeholder_address', this.account);
      
      console.log('📦 FormData prepared with stakeholder_address:', this.account);

      try {
        const response = await axios.post(`${this.apiBaseUrl}/predict`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        // Emit the prediction data to the parent component
        this.$emit('prediction-received', response.data);
        
      } catch (err) {
        console.error('Upload error:', err);
        this.error = err.response?.data?.detail || 'An error occurred during file upload';
        
        // If unauthorized, re-check stakeholder status
        if (err.response?.status === 403) {
          await this.checkStakeholderAccess();
        }
      } finally {
        this.isUploading = false;
      }
    },
    
    resetForm() {
      this.selectedFile = null;
      this.fileName = '';
      this.error = null;
      this.$refs.fileInput.value = '';
    }
  }
};
</script> 