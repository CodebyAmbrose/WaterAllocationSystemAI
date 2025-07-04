<template>
  <div class="prediction-viewer">
    <!-- Modal Overlay -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
      <div class="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-2xl bg-white" @click.stop>
        <!-- Modal Header -->
        <div class="flex justify-between items-center pb-6 border-b border-gray-200">
          <div>
            <h3 class="text-2xl font-bold text-gray-900">Prediction Details</h3>
            <p class="text-sm text-gray-500 mt-1">AI-Generated Water Allocation Forecast</p>
          </div>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg p-2 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="py-12 text-center">
          <svg class="animate-spin h-12 w-12 text-blue-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="text-gray-600 mt-4">Loading prediction data...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="py-12 text-center">
          <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <h4 class="text-lg font-medium text-gray-900 mb-2">Failed to Load Prediction</h4>
          <p class="text-gray-600">{{ error }}</p>
        </div>

        <!-- Prediction Content -->
        <div v-else-if="prediction" class="py-6">
          <!-- Summary Cards -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <!-- Confidence Score -->
            <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-blue-600">Confidence Score</p>
                  <p class="text-3xl font-bold text-blue-900 mt-1">{{ prediction.confidence_score }}%</p>
                </div>
                <div class="bg-blue-100 p-3 rounded-xl">
                  <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
              </div>
              <div class="mt-4">
                <div class="bg-blue-200 rounded-full h-2">
                  <div class="bg-blue-600 h-2 rounded-full transition-all duration-1000" :style="{ width: prediction.confidence_score + '%' }"></div>
                </div>
              </div>
            </div>

            <!-- Total Consumption -->
            <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-green-600">Total Consumption</p>
                  <p class="text-2xl font-bold text-green-900 mt-1">
                    {{ formatNumber(prediction.metadata?.total_consumption_hcf) }}
                  </p>
                  <p class="text-xs text-green-700">HCF (Hundred Cubic Feet)</p>
                </div>
                <div class="bg-green-100 p-3 rounded-xl">
                  <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                  </svg>
                </div>
              </div>
            </div>

            <!-- Boroughs -->
            <div class="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl p-6 border border-purple-200">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-purple-600">Boroughs Analyzed</p>
                  <p class="text-3xl font-bold text-purple-900 mt-1">{{ prediction.metadata?.number_of_boroughs || 0 }}</p>
                </div>
                <div class="bg-purple-100 p-3 rounded-xl">
                  <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- Borough Allocations -->
          <div class="bg-white rounded-xl border border-gray-200 overflow-hidden mb-8">
            <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
              <h4 class="text-lg font-semibold text-gray-900">Borough Water Allocations</h4>
              <p class="text-sm text-gray-600 mt-1">Predicted consumption by New York City borough</p>
            </div>
            
            <div class="p-6">
              <div class="space-y-4">
                <div v-for="(allocation, borough) in prediction.predicted_allocation" :key="borough" 
                     class="border border-gray-100 rounded-xl p-4 hover:bg-gray-50 transition-colors">
                  <div class="flex justify-between items-center mb-3">
                    <div class="flex items-center">
                      <div class="w-3 h-3 rounded-full mr-3" :class="getBoroughColor(borough)"></div>
                      <span class="font-semibold text-gray-900">{{ borough }}</span>
                    </div>
                    <div class="text-right">
                      <span class="text-lg font-bold text-gray-900">{{ allocation.percentage }}%</span>
                      <p class="text-sm text-gray-600">{{ formatNumber(allocation.consumption_hcf) }} HCF</p>
                    </div>
                  </div>
                  
                  <!-- Progress Bar -->
                  <div class="bg-gray-200 rounded-full h-3">
                    <div 
                      class="h-3 rounded-full transition-all duration-1000" 
                      :class="getBoroughProgressColor(borough)"
                      :style="{ width: allocation.percentage + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Metadata -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Prediction Info -->
            <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
              <h4 class="text-lg font-semibold text-gray-900 mb-4">Prediction Information</h4>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-gray-600">Prediction ID:</span>
                  <span class="font-mono text-sm text-gray-900">{{ prediction.prediction_id?.substring(0, 8) }}...</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Generated:</span>
                  <span class="text-gray-900">{{ formatDate(prediction.timestamp) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Source File:</span>
                  <span class="text-gray-900">{{ prediction.metadata?.source_file || 'N/A' }}</span>
                </div>
              </div>
            </div>

            <!-- File Info -->
            <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
              <h4 class="text-lg font-semibold text-gray-900 mb-4">File Information</h4>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-gray-600">Filename:</span>
                  <span class="font-mono text-sm text-gray-900">{{ prediction.file_info?.filename }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">File Size:</span>
                  <span class="text-gray-900">{{ formatBytes(prediction.file_info?.file_size) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Created:</span>
                  <span class="text-gray-900">{{ formatDate(prediction.file_info?.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="flex justify-end pt-6 border-t border-gray-200">
          <button @click="closeModal" class="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PredictionViewer',
  data() {
    return {
      showModal: false,
      loading: false,
      error: null,
      prediction: null
    };
  },
  methods: {
    async viewPrediction(predictionId) {
      this.showModal = true;
      this.loading = true;
      this.error = null;
      this.prediction = null;

      try {
        console.log('Fetching prediction:', predictionId);
        const response = await fetch(`http://localhost:8000/prediction/${predictionId}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch prediction: ${response.statusText}`);
        }

        const data = await response.json();
        
        if (data.status === 'success') {
          this.prediction = data.prediction;
          console.log('Prediction loaded:', this.prediction);
        } else {
          throw new Error('Invalid response format');
        }
      } catch (err) {
        console.error('Error fetching prediction:', err);
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },

    closeModal() {
      this.showModal = false;
      this.prediction = null;
      this.error = null;
    },

    getBoroughColor(borough) {
      const colors = {
        'BRONX': 'bg-blue-500',
        'BROOKLYN': 'bg-green-500',
        'MANHATTAN': 'bg-purple-500',
        'QUEENS': 'bg-orange-500'
      };
      return colors[borough] || 'bg-gray-500';
    },

    getBoroughProgressColor(borough) {
      const colors = {
        'BRONX': 'bg-blue-500',
        'BROOKLYN': 'bg-green-500',
        'MANHATTAN': 'bg-purple-500',
        'QUEENS': 'bg-orange-500'
      };
      return colors[borough] || 'bg-gray-500';
    },

    formatNumber(num) {
      if (!num) return '0';
      return num.toLocaleString('en-US', { 
        minimumFractionDigits: 0,
        maximumFractionDigits: 2 
      });
    },

    formatBytes(bytes) {
      if (!bytes) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch {
        return 'Invalid date';
      }
    }
  }
};
</script>

<style scoped>
.prediction-viewer {
  /* Component-specific styles can go here */
}

/* Smooth transitions for progress bars */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style> 