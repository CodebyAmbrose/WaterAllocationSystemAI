<template>
  <div class="bg-white rounded-lg shadow p-4 md:p-6">
    <h2 class="text-xl font-bold text-gray-900 mb-3 md:mb-4">Upload Water Consumption Data</h2>
    <p class="text-sm text-gray-600 mb-4 md:mb-6">
      Upload a CSV or JSON file with water consumption data to generate predictions using AI.
      The prediction will be submitted to the blockchain for stakeholder approval.
    </p>

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

export default {
  name: 'FileUpload',
  data() {
    return {
      selectedFile: null,
      fileName: '',
      isUploading: false,
      isDragging: false,
      error: null,
      apiBaseUrl: 'http://localhost:8000'  // Change this to your backend API URL
    };
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileSelection(event) {
      const file = event.target.files[0];
      if (file) {
        this.validateAndSetFile(file);
      }
    },
    handleFileDrop(event) {
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
      if (!this.selectedFile) {
        return;
      }

      this.isUploading = true;
      this.error = null;

      const formData = new FormData();
      formData.append('file', this.selectedFile);

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