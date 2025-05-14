<template>
  <div class="ipfs-metadata-viewer bg-white rounded-lg shadow p-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900">IPFS Metadata</h3>
      <div class="flex items-center space-x-2">
        <a 
          v-if="ipfsCid" 
          :href="gatewayUrl" 
          target="_blank" 
          class="text-blue-600 hover:text-blue-800 text-sm flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          View on IPFS
        </a>
      </div>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="py-8 flex justify-center items-center">
      <div class="w-8 h-8 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="bg-red-50 p-4 rounded border border-red-100">
      <div class="flex">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-sm text-red-600">{{ error }}</p>
      </div>
    </div>
    
    <!-- Empty state -->
    <div v-else-if="!ipfsCid" class="py-8 text-center">
      <p class="text-gray-500">No IPFS content identifier provided</p>
    </div>
    
    <!-- Content -->
    <div v-else-if="ipfsData" class="space-y-4">
      <!-- Metadata summary -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="(section, sectionIndex) in getMetadataSections()" :key="sectionIndex" class="bg-gray-50 p-4 rounded">
          <h4 class="font-medium text-gray-700 mb-2">{{ section.title }}</h4>
          <div class="space-y-2">
            <div v-for="(item, itemIndex) in section.items" :key="itemIndex" class="flex justify-between">
              <span class="text-sm text-gray-600">{{ item.label }}:</span>
              <span class="text-sm font-medium text-gray-800">{{ item.value }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Raw JSON data -->
      <div class="mt-4">
        <div class="flex items-center justify-between mb-2">
          <h4 class="font-medium text-gray-700">Raw JSON Data</h4>
          <button 
            @click="showRawData = !showRawData" 
            class="text-sm text-blue-600 hover:text-blue-800"
          >
            {{ showRawData ? 'Hide' : 'Show' }}
          </button>
        </div>
        <pre v-if="showRawData" class="bg-gray-50 p-4 rounded overflow-auto text-xs text-gray-800">{{ JSON.stringify(ipfsData, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import { fetchFromIPFS, getIPFSGatewayUrl } from '../services/ipfsService';

export default {
  name: 'IPFSMetadataViewer',
  props: {
    ipfsCid: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      ipfsData: null,
      loading: false,
      error: null,
      showRawData: false
    };
  },
  computed: {
    gatewayUrl() {
      return getIPFSGatewayUrl(this.ipfsCid);
    }
  },
  watch: {
    ipfsCid: {
      immediate: true,
      handler(newCid) {
        if (newCid) {
          this.fetchData();
        } else {
          this.resetData();
        }
      }
    }
  },
  methods: {
    async fetchData() {
      if (!this.ipfsCid) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        this.ipfsData = await fetchFromIPFS(this.ipfsCid);
      } catch (err) {
        console.error('Error fetching IPFS data:', err);
        this.error = `Failed to fetch data: ${err.message}`;
        this.ipfsData = null;
      } finally {
        this.loading = false;
      }
    },
    
    resetData() {
      this.ipfsData = null;
      this.loading = false;
      this.error = null;
    },
    
    getMetadataSections() {
      if (!this.ipfsData) return [];
      
      // Organize metadata into sections for display
      // This can be customized based on your specific metadata structure
      const sections = [
        {
          title: 'Prediction Information',
          items: []
        },
        {
          title: 'Water Allocation Details',
          items: []
        }
      ];
      
      // Example of how to extract data from your metadata
      // Adjust according to your actual data structure
      if (this.ipfsData.timestamp) {
        sections[0].items.push({
          label: 'Timestamp',
          value: new Date(this.ipfsData.timestamp).toLocaleString()
        });
      }
      
      if (this.ipfsData.predictionId) {
        sections[0].items.push({
          label: 'Prediction ID',
          value: this.ipfsData.predictionId
        });
      }
      
      if (this.ipfsData.confidence) {
        sections[0].items.push({
          label: 'Confidence',
          value: `${this.ipfsData.confidence}%`
        });
      }
      
      // If there are borough allocations, display them
      if (this.ipfsData.boroughs && Array.isArray(this.ipfsData.boroughs)) {
        this.ipfsData.boroughs.forEach(borough => {
          if (borough.name && borough.allocation) {
            sections[1].items.push({
              label: borough.name,
              value: `${borough.allocation} MG`
            });
          }
        });
      }
      
      return sections;
    }
  }
};
</script>

<style scoped>
.ipfs-metadata-viewer {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style> 