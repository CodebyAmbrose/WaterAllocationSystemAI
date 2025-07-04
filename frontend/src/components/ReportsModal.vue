<template>
  <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
    <div class="relative top-10 mx-auto p-5 border w-11/12 max-w-6xl shadow-lg rounded-2xl bg-white" @click.stop>
      <!-- Modal Header -->
      <div class="flex justify-between items-center pb-6 border-b border-gray-200">
        <div>
          <h3 class="text-2xl font-bold text-gray-900">BIWMS System Reports</h3>
          <p class="text-sm text-gray-500 mt-1">Comprehensive water management and blockchain analytics</p>
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
        <p class="text-gray-600 mt-4">Loading system reports...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="py-12 text-center">
        <div class="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
          <svg class="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <h4 class="text-red-800 font-semibold mb-2">Error Loading Reports</h4>
          <p class="text-red-600 text-sm">{{ error }}</p>
          <button @click="loadReports" class="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors">
            Retry
          </button>
        </div>
      </div>

      <!-- Report Content -->
      <div v-else class="mt-6 max-h-96 overflow-y-auto">
        <!-- Report Summary -->
        <div v-if="reportData" class="space-y-6">
          <!-- Report Metadata -->
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-lg font-semibold text-blue-900">{{ reportData.report_metadata?.report_type }}</h4>
                <p class="text-sm text-blue-700">{{ reportData.report_metadata?.report_period }}</p>
              </div>
              <div class="text-right">
                <p class="text-xs text-blue-600">Generated</p>
                <p class="text-sm font-medium text-blue-900">{{ formatDate(reportData.report_metadata?.generated_at) }}</p>
              </div>
            </div>
          </div>

          <!-- Overview Cards -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
              <div class="flex items-center">
                <div class="bg-blue-500 p-2 rounded-lg">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm font-medium text-blue-600">Total Predictions</p>
                  <p class="text-2xl font-bold text-blue-900">{{ reportData.prediction_analytics?.current_stats?.total_predictions || 0 }}</p>
                </div>
              </div>
            </div>

            <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
              <div class="flex items-center">
                <div class="bg-green-500 p-2 rounded-lg">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm font-medium text-green-600">Approved</p>
                  <p class="text-2xl font-bold text-green-900">{{ reportData.prediction_analytics?.current_stats?.approved_predictions || 0 }}</p>
                </div>
              </div>
            </div>

            <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
              <div class="flex items-center">
                <div class="bg-purple-500 p-2 rounded-lg">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm font-medium text-purple-600">Accuracy</p>
                  <p class="text-2xl font-bold text-purple-900">{{ formatAccuracy(reportData.prediction_analytics?.current_stats?.accuracy) }}%</p>
                </div>
              </div>
            </div>

            <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 border border-orange-200">
              <div class="flex items-center">
                <div class="bg-orange-500 p-2 rounded-lg">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm font-medium text-orange-600">Active Boroughs</p>
                  <p class="text-2xl font-bold text-orange-900">{{ reportData.water_allocation?.total_boroughs_active || 0 }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Water Allocation Analysis -->
          <div v-if="reportData.water_allocation?.borough_trends?.length > 0" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
              <h4 class="text-lg font-semibold text-gray-900">Water Allocation by Borough</h4>
              <p class="text-sm text-gray-600 mt-1">Average consumption trends over the last 30 days</p>
            </div>
            
            <div class="p-6">
              <div class="space-y-4">
                <div v-for="trend in reportData.water_allocation.borough_trends" :key="trend.borough" 
                     class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div class="flex items-center">
                    <div class="w-3 h-3 rounded-full mr-3" :class="getBoroughColor(trend.borough)"></div>
                    <div>
                      <span class="font-medium text-gray-900">{{ trend.borough }}</span>
                      <p class="text-xs text-gray-500">{{ trend.data_points }} data points</p>
                    </div>
                  </div>
                  <div class="text-right">
                    <p class="text-lg font-bold text-gray-900">{{ formatNumber(trend.avg_consumption) }}</p>
                    <p class="text-xs text-gray-500">HCF avg</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Predictions -->
          <div v-if="reportData.prediction_analytics?.recent_predictions?.length > 0" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
              <h4 class="text-lg font-semibold text-gray-900">Recent Predictions</h4>
              <p class="text-sm text-gray-600 mt-1">Latest AI-generated water allocation predictions</p>
            </div>
            
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Consumption</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Boroughs</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(prediction, index) in reportData.prediction_analytics.recent_predictions.slice(0, 5)" :key="index" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ formatDate(prediction.timestamp) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                            :class="getConfidenceClass(prediction.confidence_score)">
                        {{ formatAccuracy(prediction.confidence_score) }}%
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ formatNumber(prediction.total_consumption) }} HCF
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ prediction.boroughs?.join(', ') || 'N/A' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- System Utilization -->
          <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
              <h4 class="text-lg font-semibold text-gray-900">System Utilization</h4>
              <p class="text-sm text-gray-600 mt-1">Activity summary for the last 30 days</p>
            </div>
            
            <div class="p-6">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center">
                  <p class="text-2xl font-bold text-blue-600">{{ reportData.system_utilization?.predictions_generated || 0 }}</p>
                  <p class="text-sm text-gray-600">Predictions</p>
                </div>
                <div class="text-center">
                  <p class="text-2xl font-bold text-green-600">{{ reportData.system_utilization?.approvals_processed || 0 }}</p>
                  <p class="text-sm text-gray-600">Approvals</p>
                </div>
                <div class="text-center">
                  <p class="text-2xl font-bold text-purple-600">{{ reportData.system_utilization?.blockchain_transactions || 0 }}</p>
                  <p class="text-sm text-gray-600">Blockchain Txs</p>
                </div>
                <div class="text-center">
                  <p class="text-2xl font-bold text-orange-600">{{ reportData.system_utilization?.total_activities || 0 }}</p>
                  <p class="text-sm text-gray-600">Total Activities</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Blockchain Status -->
          <div class="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-6">
            <h4 class="text-lg font-semibold text-indigo-900 mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
              </svg>
              Blockchain Integration Status
            </h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-indigo-600 mb-1">Network</p>
                <p class="font-medium text-indigo-900">{{ reportData.blockchain_status?.network }}</p>
              </div>
              <div>
                <p class="text-sm text-indigo-600 mb-1">Approval Rate</p>
                <p class="font-medium text-indigo-900">{{ reportData.blockchain_status?.approval_rate }}%</p>
              </div>
              <div class="md:col-span-2">
                <p class="text-sm text-indigo-600 mb-1">Contract Address</p>
                <p class="font-mono text-xs text-indigo-900 bg-indigo-100 p-2 rounded">{{ reportData.blockchain_status?.contract_address }}</p>
              </div>
            </div>
          </div>

          <!-- Recommendations -->
          <div v-if="reportData.recommendations?.length > 0" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <h4 class="text-lg font-semibold text-yellow-800 mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
              </svg>
              System Recommendations
            </h4>
            
            <ul class="space-y-2">
              <li v-for="rec in reportData.recommendations" :key="rec" 
                  class="text-sm text-yellow-700 flex items-start">
                <span class="text-yellow-600 mr-2">•</span>
                <span>{{ rec }}</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- No Data State -->
        <div v-else class="text-center py-12">
          <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <h4 class="text-lg font-medium text-gray-900 mb-2">No System Data Available</h4>
          <p class="text-gray-500">Generate predictions and upload data to see comprehensive reports</p>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="flex justify-between items-center pt-6 border-t border-gray-200 mt-6">
        <button @click="loadReports" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          Refresh Reports
        </button>
        <button @click="closeModal" class="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ReportsModal',
  props: {
    showModal: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      loading: false,
      error: null,
      reportData: null
    };
  },
  watch: {
    showModal(newVal) {
      if (newVal) {
        this.loadReports();
      }
    }
  },
  methods: {
    async loadReports() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await fetch('http://localhost:8000/reports');
        if (!response.ok) {
          throw new Error(`Failed to fetch reports: ${response.statusText}`);
        }
        
        const data = await response.json();
        if (data.status === 'success') {
          this.reportData = data.report;
        } else {
          throw new Error(data.message || 'Invalid response format');
        }
      } catch (err) {
        console.error('Error loading reports:', err);
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
    
    closeModal() {
      this.$emit('close');
    },
    
    getBoroughColor(borough) {
      const colors = {
        'BRONX': 'bg-blue-500',
        'BROOKLYN': 'bg-green-500',
        'MANHATTAN': 'bg-purple-500',
        'QUEENS': 'bg-orange-500',
        'STATEN ISLAND': 'bg-red-500'
      };
      return colors[borough?.toUpperCase()] || 'bg-gray-500';
    },
    
    getConfidenceClass(confidence) {
      if (!confidence) return 'bg-gray-100 text-gray-800';
      if (confidence >= 95) return 'bg-green-100 text-green-800';
      if (confidence >= 90) return 'bg-blue-100 text-blue-800';
      if (confidence >= 80) return 'bg-yellow-100 text-yellow-800';
      return 'bg-red-100 text-red-800';
    },
    
    formatNumber(num) {
      if (!num) return '0';
      return num.toLocaleString('en-US', { 
        minimumFractionDigits: 0,
        maximumFractionDigits: 2 
      });
    },
    
    formatAccuracy(accuracy) {
      if (!accuracy) return '0';
      return accuracy.toFixed(1);
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
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
/* Custom scrollbar for the modal content */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style> 