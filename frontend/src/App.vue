<script>
import DashboardLayout from './components/Layout/DashboardLayout.vue';
import FileUpload from './components/FileUpload.vue';
import PredictionResults from './components/PredictionResults.vue';
import BlockchainInfo from './components/BlockchainInfo.vue';
import StakeholderDashboard from './components/StakeholderDashboard.vue';
import PredictionHistory from './components/PredictionHistory.vue';
import WaterAnalytics from './components/WaterAnalytics.vue';

export default {
  name: 'App',
  components: {
    DashboardLayout,
    FileUpload,
    PredictionResults,
    BlockchainInfo,
    StakeholderDashboard,
    PredictionHistory,
    WaterAnalytics
  },
  data() {
    return {
      prediction: null,
      activeTab: 'dashboard' // 'dashboard', 'predict', 'approve', 'history', 'analytics', 'settings'
    };
  },
  methods: {
    handlePrediction(predictionData) {
      this.prediction = predictionData;
    },
    setActiveTab(tab) {
      this.activeTab = tab;
    }
  }
};
</script>

<template>
  <DashboardLayout :activeTab="activeTab" @change-tab="setActiveTab">
    <!-- Dashboard Tab -->
    <div v-if="activeTab === 'dashboard'" class="space-y-6">
      <!-- Welcome Banner -->
      <div class="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl shadow-lg p-6 text-white">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 class="text-2xl font-bold mb-2">Welcome to WaterAlloc</h1>
            <p class="text-blue-100">An AI-powered water allocation system with blockchain verification</p>
          </div>
          <div class="mt-4 md:mt-0">
            <button class="bg-white text-blue-700 hover:bg-blue-50 px-5 py-2 rounded-lg shadow font-medium transition-colors">
              View Reports
            </button>
          </div>
        </div>
      </div>

      <!-- Main Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
        <!-- Predictions Card -->
        <div class="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
          <div class="p-5 border-b border-gray-100">
            <div class="flex justify-between items-center">
              <div>
                <p class="text-sm text-gray-500">Predictions</p>
                <h3 class="text-2xl font-bold text-gray-800">42</h3>
              </div>
              <div class="bg-blue-100 p-3 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
          </div>
          <div class="px-5 py-3 bg-gray-50">
            <div class="flex items-center text-sm">
              <span class="text-gray-500">Predictions Generated</span>
            </div>
          </div>
        </div>
        
        <!-- Approved Card -->
        <div class="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
          <div class="p-5 border-b border-gray-100">
            <div class="flex justify-between items-center">
              <div>
                <p class="text-sm text-gray-500">Approved</p>
                <h3 class="text-2xl font-bold text-gray-800">28</h3>
              </div>
              <div class="bg-green-100 p-3 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
          <div class="px-5 py-3 bg-gray-50">
            <div class="flex items-center text-sm">
              <span class="text-gray-500">Approved Allocations</span>
            </div>
          </div>
        </div>
        
        <!-- Accuracy Card -->
        <div class="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
          <div class="p-5 border-b border-gray-100">
            <div class="flex justify-between items-center">
              <div>
                <p class="text-sm text-gray-500">Accuracy</p>
                <h3 class="text-2xl font-bold text-gray-800">99.8%</h3>
              </div>
              <div class="bg-indigo-100 p-3 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
          </div>
          <div class="px-5 py-3 bg-gray-50">
            <div class="flex items-center text-sm">
              <span class="text-gray-500">Prediction Accuracy</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recent Activity -->
      <div class="bg-white rounded-xl shadow-md p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div class="space-y-4">
          <div v-for="i in 5" :key="i" class="border-b border-gray-100 pb-3 last:border-0 last:pb-0">
            <div class="flex items-start">
              <div class="flex-shrink-0 mt-1">
                <span class="inline-block w-2 h-2 rounded-full" :class="i % 2 === 0 ? 'bg-green-500' : 'bg-blue-500'"></span>
              </div>
              <div class="ml-3">
                <p class="text-sm text-gray-900">
                  {{ i % 2 === 0 ? 'Prediction approved by stakeholder' : 'New prediction generated' }}
                </p>
                <p class="text-xs text-gray-500">{{ new Date().toLocaleString() }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Prediction Tab -->
    <div v-if="activeTab === 'predict'" class="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-8">
      <!-- Left Column: Upload and Prediction -->
      <div class="lg:col-span-2 space-y-4 md:space-y-6">
        <FileUpload @prediction-received="handlePrediction" />
        <PredictionResults v-if="prediction" :prediction="prediction" />
      </div>
      
      <!-- Right Column: Blockchain Info -->
      <div class="lg:col-span-1 space-y-4 md:space-y-6">
        <BlockchainInfo v-if="prediction" :transaction-data="prediction" />
      </div>
    </div>

    <!-- Approval Tab -->
    <div v-if="activeTab === 'approve'">
      <StakeholderDashboard />
    </div>

    <!-- History Tab -->
    <div v-if="activeTab === 'history'">
      <PredictionHistory />
    </div>

    <!-- Analytics Tab -->
    <div v-if="activeTab === 'analytics'" class="space-y-4 md:space-y-6">
      <WaterAnalytics />
    </div>

    <!-- Settings Tab -->
    <div v-if="activeTab === 'settings'" class="space-y-4 md:space-y-6">
      <div class="bg-white rounded-lg shadow p-4 md:p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-3 md:mb-4">System Settings</h2>
        <div class="space-y-4">
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">Blockchain Network</label>
            <select class="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
              <option>BSC Testnet</option>
              <option>BSC Mainnet</option>
              <option>Ethereum Testnet</option>
            </select>
          </div>
          
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">Contract Address</label>
            <input type="text" value="0x6b282341D709b3c6f6cfdF366Be2d326dDA39Ce4" class="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
          </div>
          
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">Notifications</label>
            <div class="flex items-center">
              <input type="checkbox" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
              <label class="ml-2 block text-sm text-gray-900">Enable email notifications</label>
            </div>
          </div>
          
          <div class="pt-4">
            <button class="w-full sm:w-auto bg-blue-600 text-white py-2 px-4 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --primary: #2563eb;
  --primary-hover: #1d4ed8;
}

html, body {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

body {
  font-family: 'Inter', sans-serif;
  @apply bg-gray-100;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.text-primary {
  color: var(--primary);
  }

.bg-primary {
  background-color: var(--primary);
}

.border-primary {
  border-color: var(--primary);
  }

/* Add responsive table support */
.responsive-table-container {
  @apply overflow-x-auto -mx-4 sm:mx-0;
}

@media (max-width: 640px) {
  .responsive-table-container table {
    @apply min-w-full;
  }
}
</style>
