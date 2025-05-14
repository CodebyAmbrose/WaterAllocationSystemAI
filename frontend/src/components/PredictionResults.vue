<template>
  <div>
    <div class="bg-white rounded-lg shadow p-4 md:p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">AI Prediction Results</h2>
      
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 space-y-3 sm:space-y-0">
        <div class="flex items-center space-x-2">
          <span class="inline-flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </span>
          <div>
            <div class="text-xs text-gray-500 font-medium">Prediction ID</div>
            <div class="text-sm font-semibold truncate max-w-[200px]">{{ prediction.prediction_id }}</div>
          </div>
        </div>
        <div class="flex items-center px-3 py-1.5 rounded-full bg-blue-100 text-blue-800 text-sm font-medium self-start sm:self-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
          Confidence: {{ prediction.confidence_score }}%
        </div>
      </div>
      
      <div v-if="predictionData" class="mb-6 md:mb-8">
        <div class="flex flex-wrap items-center mb-3">
          <h3 class="text-lg font-semibold text-gray-900">Water Allocation by Borough</h3>
          <div class="ml-2 px-2 py-0.5 bg-indigo-100 text-indigo-800 text-xs font-medium rounded-full">Chart</div>
        </div>
        <div class="h-56 sm:h-64 bg-white rounded-lg border border-gray-100">
          <AllocationChart :chartData="chartData" />
        </div>
      </div>
      
      <div v-if="predictionData" class="mt-6 md:mt-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-3 space-y-2 sm:space-y-0">
          <h3 class="text-lg font-semibold text-gray-900">Detailed Allocations</h3>
          <button class="text-sm text-blue-600 hover:text-blue-800 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
            Export
          </button>
        </div>
        <div class="responsive-table-container overflow-hidden rounded-lg border border-gray-200">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Borough</th>
                <th scope="col" class="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Water (HCF)</th>
                <th scope="col" class="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Percentage</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(data, borough) in predictionData.predicted_allocation" :key="borough">
                <td class="px-3 sm:px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ borough }}</div>
                </td>
                <td class="px-3 sm:px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-500">{{ data.consumption_hcf.toLocaleString() }}</div>
                </td>
                <td class="px-3 sm:px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-16 sm:w-full bg-gray-200 rounded-full h-2.5">
                      <div class="bg-blue-600 h-2.5 rounded-full" :style="{ width: `${data.percentage}%` }"></div>
                    </div>
                    <span class="ml-2 text-sm text-gray-500">{{ data.percentage }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div v-if="predictionData && predictionData.metadata" class="mt-6 md:mt-8 p-4 bg-gray-50 rounded-lg border border-gray-100">
        <h3 class="text-sm font-semibold text-gray-600 mb-3">Prediction Metadata</h3>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
          <div class="flex items-start sm:items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
            </svg>
            <div>
              <span class="block text-gray-500">Prediction Date:</span>
              <span class="font-medium">{{ formatDate(predictionData.metadata.prediction_date) }}</span>
            </div>
          </div>
          <div class="flex items-start sm:items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
              <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
            </svg>
            <div>
              <span class="block text-gray-500">Total Consumption:</span>
              <span class="font-medium">{{ predictionData.metadata.total_consumption_hcf.toLocaleString() }} HCF</span>
            </div>
          </div>
          <div class="flex items-start sm:items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
            </svg>
            <div>
              <span class="block text-gray-500">Boroughs:</span>
              <span class="font-medium">{{ predictionData.metadata.number_of_boroughs }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="isLoadingFile" class="flex justify-center items-center space-x-2 mt-6 p-6">
        <svg class="animate-spin h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-gray-700 font-medium">Loading prediction data...</span>
      </div>
      
      <div v-if="predictionError" class="mt-6 p-4 bg-red-100 text-red-800 rounded-lg flex items-start">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        <p>{{ predictionError }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { ref, reactive, onMounted } from 'vue';
import AllocationChart from './AllocationChart.vue';

export default {
  name: 'PredictionResults',
  components: {
    AllocationChart
  },
  props: {
    prediction: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      predictionData: null,
      predictionError: null,
      isLoadingFile: false,
      chartData: {
        labels: [],
        datasets: []
      }
    };
  },
  watch: {
    prediction: {
      immediate: true,
      handler() {
        this.loadPredictionFile();
      }
    }
  },
  methods: {
    async loadPredictionFile() {
      // In a real application, you would fetch the prediction file from IPFS using the ipfsHash
      // For simplicity, we'll simulate loading the data
      this.isLoadingFile = true;
      
      try {
        // Simulate API call to get prediction file (in production, fetch from IPFS)
        // const response = await axios.get(`https://gateway.pinata.cloud/ipfs/${this.prediction.ipfsHash}`);
        
        // For demo purposes, generate sample data
        setTimeout(() => {
          this.predictionData = this.generateSampleData();
          this.prepareChartData();
          this.isLoadingFile = false;
        }, 1000);
        
      } catch (err) {
        console.error('Error loading prediction file:', err);
        this.predictionError = 'Failed to load prediction data';
        this.isLoadingFile = false;
      }
    },
    generateSampleData() {
      // This is sample data for demonstration purposes
      // In a real application, this would come from the IPFS file
      return {
        prediction_id: this.prediction.prediction_id,
        timestamp: new Date().toISOString(),
        predicted_allocation: {
          'Manhattan': { consumption_hcf: 12500, percentage: 25.0 },
          'Brooklyn': { consumption_hcf: 15000, percentage: 30.0 },
          'Queens': { consumption_hcf: 10000, percentage: 20.0 },
          'Bronx': { consumption_hcf: 7500, percentage: 15.0 },
          'Staten Island': { consumption_hcf: 5000, percentage: 10.0 }
        },
        confidence_score: this.prediction.confidence_score,
        metadata: {
          prediction_date: new Date().toISOString(),
          total_consumption_hcf: 50000,
          number_of_boroughs: 5
        }
      };
    },
    prepareChartData() {
      const boroughs = Object.keys(this.predictionData.predicted_allocation);
      const percentages = boroughs.map(borough => this.predictionData.predicted_allocation[borough].percentage);
      const consumption = boroughs.map(borough => this.predictionData.predicted_allocation[borough].consumption_hcf);
      
      // Random colors for each borough
      const backgroundColors = [
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 99, 132, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(153, 102, 255, 0.6)',
        'rgba(255, 205, 86, 0.6)',
        'rgba(201, 203, 207, 0.6)'
      ];
      
      this.chartData = {
        labels: boroughs,
        datasets: [
          {
            label: 'Water Allocation (%)',
            data: percentages,
            backgroundColor: backgroundColors.slice(0, boroughs.length)
          }
        ]
      };
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
};
</script> 