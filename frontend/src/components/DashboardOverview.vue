<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- System Efficiency Card -->
    <div class="card">
      <SystemEfficiencyDisplay 
        v-if="latestEfficiencyData"
        :efficiency-data="latestEfficiencyData" 
      />
      <div v-else class="flex justify-center items-center h-48">
        <p class="text-gray-500">No efficiency data available</p>
      </div>
    </div>

    <!-- Recent Activity Card -->
    <div class="card">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Recent Activity</h3>
        <router-link 
          to="/prediction-history" 
          class="text-primary hover:text-primary-dark text-sm flex items-center"
        >
          View All
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
        </router-link>
      </div>

      <div v-if="loading" class="flex justify-center items-center h-48">
        <svg class="animate-spin h-6 w-6 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="ml-2">Loading recent activity...</span>
      </div>

      <div v-else-if="recentPredictions.length === 0" class="text-center py-6">
        <p class="text-gray-500">No recent predictions</p>
      </div>

      <div v-else class="space-y-4">
        <div 
          v-for="prediction in recentPredictions" 
          :key="prediction.id"
          class="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <div class="flex-1">
            <div class="flex items-center">
              <span class="font-medium text-gray-900">Prediction #{{ prediction.id }}</span>
              <span 
                :class="prediction.isFinalized ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'"
                class="ml-2 text-xs px-2 py-0.5 rounded-full"
              >
                {{ prediction.isFinalized ? 'Finalized' : 'Pending' }}
              </span>
            </div>
            <p class="text-sm text-gray-500 mt-1">{{ formatDate(prediction.timestamp) }}</p>
          </div>
          
          <div class="text-right">
            <div class="text-sm font-medium text-gray-900">
              Confidence: {{ prediction.confidenceScore }}%
            </div>
            <div class="text-xs text-gray-500 mt-1">
              {{ prediction.approvals }}/{{ minApprovalsRequired }} Approvals
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import SystemEfficiencyDisplay from './SystemEfficiencyDisplay.vue';
import contractService from '../services/ContractService';
import { generateEfficiencyReport } from '../services/efficiencyService';

export default {
  name: 'DashboardOverview',
  components: {
    SystemEfficiencyDisplay
  },
  setup() {
    const loading = ref(true);
    const recentPredictions = ref([]);
    const latestEfficiencyData = ref(null);
    const minApprovalsRequired = ref(0);

    const loadDashboardData = async () => {
      try {
        loading.value = true;
        
        // Initialize contract service
        await contractService.initialize();
        
        // Get recent predictions
        const totalPredictions = await contractService.getPredictionCount();
        minApprovalsRequired.value = await contractService.getMinApprovalsRequired();
        
        // Get last 5 predictions
        const startId = Math.max(0, totalPredictions - 5);
        const count = Math.min(5, totalPredictions);
        recentPredictions.value = await contractService.getMultiplePredictions(startId, count);
        
        // Generate efficiency data from most recent prediction
        if (recentPredictions.value.length > 0) {
          const latestPrediction = recentPredictions.value[0];
          // Sample data for demonstration - replace with actual data in production
          const sampleData = {
            actualUsed: 48000,
            totalAllocated: 50000,
            waterDelivered: 49000,
            waterInput: 52000,
            predicted_allocation: latestPrediction.allocations || {
              'Manhattan': { percentage: 25 },
              'Brooklyn': { percentage: 30 },
              'Queens': { percentage: 20 },
              'Bronx': { percentage: 15 },
              'Staten Island': { percentage: 10 }
            }
          };
          latestEfficiencyData.value = generateEfficiencyReport(sampleData);
        }
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        loading.value = false;
      }
    };

    onMounted(loadDashboardData);

    return {
      loading,
      recentPredictions,
      latestEfficiencyData,
      minApprovalsRequired,
      formatDate: (timestamp) => {
        return new Date(timestamp).toLocaleString();
      }
    };
  }
};
</script> 