<script>
import DashboardLayout from './components/Layout/DashboardLayout.vue';
import FileUpload from './components/FileUpload.vue';
import PredictionResults from './components/PredictionResults.vue';
import BlockchainInfo from './components/BlockchainInfo.vue';
import StakeholderDashboard from './components/StakeholderDashboard.vue';
import PredictionHistory from './components/PredictionHistory.vue';
import WaterAnalytics from './components/WaterAnalytics.vue';
import ReportsModal from './components/ReportsModal.vue';

export default {
  name: 'App',
  components: {
    DashboardLayout,
    FileUpload,
    PredictionResults,
    BlockchainInfo,
    StakeholderDashboard,
    PredictionHistory,
    WaterAnalytics,
    ReportsModal
  },
  data() {
    return {
      prediction: null,
      activeTab: 'dashboard', // 'dashboard', 'predict', 'approve', 'history', 'analytics', 'settings'
      dashboardStats: {
        total_predictions: 0,
        approved_predictions: 0,
        accuracy: 96
      },
      eventSource: null,
      isConnected: false,
      recentActivities: [],
      timeUpdateInterval: null,
      showReportsModal: false
    };
  },
  methods: {
    handlePrediction(predictionData) {
      this.prediction = predictionData;
    },
    setActiveTab(tab) {
      this.activeTab = tab;
    },
    connectToSSE() {
      // Disconnect existing connection
      if (this.eventSource) {
        this.eventSource.close();
      }
      
      try {
        this.eventSource = new EventSource('http://localhost:8000/stats/stream');
        
        this.eventSource.onopen = () => {
          this.isConnected = true;
          console.log('SSE connection established');
        };
        
        this.eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('SSE data received:', data);
            
            if (data.type === 'stats_update') {
              this.dashboardStats = data.stats;
              console.log('Dashboard stats updated');
            } else if (data.type === 'analytics_update') {
              this.$emit('analytics-updated', data.analytics);
              console.log('Analytics data updated');
            } else if (data.type === 'activity_update') {
              this.recentActivities = data.activities;
              this.updateActivityTimes(); // Update times immediately for new activities
              console.log('Activities updated:', data.activities.length, 'activities');
            } else if (data.type === 'heartbeat') {
              console.log('Heartbeat received - connection alive');
            }
          } catch (error) {
            console.error('Error parsing SSE data:', error, event.data);
          }
        };
        
        this.eventSource.onerror = (event) => {
          console.error('SSE connection error:', event);
          this.isConnected = false;
        };
        
      } catch (error) {
        console.error('Error connecting to SSE:', error);
        this.isConnected = false;
      }
    },
    disconnectSSE() {
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
        this.isConnected = false;
      }
    },
    getActivityColor(type, severity) {
      // Color mapping based on activity type and severity
      const colorMap = {
        'prediction': {
          'success': 'bg-blue-500',
          'info': 'bg-blue-400',
          'warning': 'bg-yellow-500',
          'error': 'bg-red-500'
        },
        'approval': {
          'success': 'bg-green-500',
          'info': 'bg-green-400',
          'warning': 'bg-yellow-500',
          'error': 'bg-red-500'
        },
        'system': {
          'success': 'bg-gray-500',
          'info': 'bg-gray-400',
          'warning': 'bg-orange-500',
          'error': 'bg-red-600'
        },
        'blockchain': {
          'success': 'bg-indigo-500',
          'info': 'bg-indigo-400',
          'warning': 'bg-purple-500',
          'error': 'bg-red-500'
        }
      };
      
      return colorMap[type]?.[severity] || 'bg-gray-400';
    },
    getActivityIconStyle(type, severity) {
      // Map activity types to background colors for icons
      const styleMap = {
        'prediction': {
          'success': 'bg-blue-50 border-blue-200',
          'info': 'bg-blue-50 border-blue-200',
          'warning': 'bg-yellow-50 border-yellow-200',
          'error': 'bg-red-50 border-red-200'
        },
        'approval': {
          'success': 'bg-green-50 border-green-200',
          'info': 'bg-green-50 border-green-200',
          'warning': 'bg-yellow-50 border-yellow-200',
          'error': 'bg-red-50 border-red-200'
        },
        'system': {
          'success': 'bg-gray-50 border-gray-200',
          'info': 'bg-gray-50 border-gray-200',
          'warning': 'bg-orange-50 border-orange-200',
          'error': 'bg-red-50 border-red-200'
        },
        'blockchain': {
          'success': 'bg-indigo-50 border-indigo-200',
          'info': 'bg-indigo-50 border-indigo-200',
          'warning': 'bg-purple-50 border-purple-200',
          'error': 'bg-red-50 border-red-200'
        }
      };
      
      return styleMap[type]?.[severity] || 'bg-gray-50 border-gray-200';
    },
    getActivityBadgeStyle(type) {
      // Map activity types to badge styles
      const badgeMap = {
        'prediction': 'bg-blue-100 text-blue-800 border border-blue-200',
        'approval': 'bg-green-100 text-green-800 border border-green-200',
        'system': 'bg-gray-100 text-gray-800 border border-gray-200',
        'blockchain': 'bg-indigo-100 text-indigo-800 border border-indigo-200'
      };
      
      return badgeMap[type] || 'bg-gray-100 text-gray-800 border border-gray-200';
    },
    getActivityTypeLabel(type) {
      // Map activity types to display labels
      const labelMap = {
        'prediction': 'Prediction',
        'approval': 'Approval',
        'system': 'System',
        'blockchain': 'Blockchain'
      };
      
      return labelMap[type] || type.charAt(0).toUpperCase() + type.slice(1);
    },
    formatActivityTimestamp(timestamp) {
      try {
        const date = new Date(timestamp);
        return date.toLocaleString('en-US', {
          month: 'numeric',
          day: 'numeric',
          year: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          second: '2-digit',
          hour12: true
        });
      } catch (error) {
        return 'Invalid date';
      }
    },
    async loadRecentActivities() {
      try {
        const response = await fetch('http://localhost:8000/activities?limit=20');
        const data = await response.json();
        if (data.status === 'success') {
          this.recentActivities = data.activities;
          this.updateActivityTimes(); // Calculate dynamic times immediately
          console.log('Loaded', data.activities.length, 'recent activities');
        }
      } catch (error) {
        console.error('Error loading recent activities:', error);
      }
    },
    calculateTimeAgo(rawTimestamp) {
      try {
        const timestamp = new Date(rawTimestamp);
        const now = new Date();
        const diffMs = now - timestamp;
        const diffSeconds = Math.floor(diffMs / 1000);
        const diffMinutes = Math.floor(diffSeconds / 60);
        const diffHours = Math.floor(diffMinutes / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffDays > 0) {
          return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        } else if (diffHours > 0) {
          return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        } else if (diffMinutes > 0) {
          return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
        } else {
          return 'Just now';
        }
      } catch (error) {
        return 'Unknown';
      }
    },
    updateActivityTimes() {
      // Update the dynamic time for all activities
      this.recentActivities.forEach(activity => {
        if (activity.raw_timestamp) {
          activity.dynamic_time_ago = this.calculateTimeAgo(activity.raw_timestamp);
        }
      });
    },
    startTimeUpdates() {
      // Update times immediately
      this.updateActivityTimes();
      // Set up interval to update every minute (60000ms)
      this.timeUpdateInterval = setInterval(() => {
        this.updateActivityTimes();
      }, 60000);
    },
    stopTimeUpdates() {
      if (this.timeUpdateInterval) {
        clearInterval(this.timeUpdateInterval);
        this.timeUpdateInterval = null;
      }
    },
    async loadDashboardStats() {
      try {
        const response = await fetch('http://localhost:8000/stats');
        const data = await response.json();
        if (data.status === 'success') {
          this.dashboardStats = data.stats;
          console.log('Loaded dashboard stats:', data.stats);
        } else {
          // Handle old format if status field is missing
          this.dashboardStats = data;
          console.log('Loaded dashboard stats (fallback):', data);
        }
      } catch (error) {
        console.error('Error loading dashboard stats:', error);
      }
    },
    handleApprovalUpdate(updatedStats) {
      // Update dashboard stats when approval happens via blockchain interface
      this.dashboardStats = updatedStats;
      console.log('Dashboard stats updated from blockchain approval:', updatedStats);
    },
    async testApproval() {
      try {
        const response = await fetch('http://localhost:8000/stats/approve', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            prediction_id: 'test_' + Date.now(),
            finalized: true
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log('Test approval successful:', data);
          // Stats will be updated automatically via SSE, but we can also update locally
          if (data.finalized && data.stats) {
            this.dashboardStats = data.stats;
          }
        } else {
          console.error('Test approval failed:', response.statusText);
        }
      } catch (error) {
        console.error('Error during test approval:', error);
      }
    },
    openReportsModal() {
      this.showReportsModal = true;
    },
    closeReportsModal() {
      this.showReportsModal = false;
    }
  },
  mounted() {
    this.connectToSSE();
    this.loadDashboardStats();
    this.loadRecentActivities();
    this.startTimeUpdates();
  },
  beforeUnmount() {
    // Clean up SSE connection when component unmounts
    this.disconnectSSE();
    this.stopTimeUpdates();
  }
};
</script>

<template>
  <DashboardLayout :activeTab="activeTab" @change-tab="setActiveTab">
    <!-- Dashboard Tab -->
    <div v-if="activeTab === 'dashboard'" class="space-y-8">
      <!-- Welcome Banner -->
      <div class="relative bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-800 rounded-2xl shadow-2xl p-8 text-white overflow-hidden">
        <!-- Background Pattern -->
        <div class="absolute inset-0 opacity-10">
          <svg class="w-full h-full" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
            <defs>
              <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                <path d="M 10 0 L 0 0 0 10" fill="none" stroke="white" stroke-width="0.5"/>
              </pattern>
            </defs>
            <rect width="100" height="100" fill="url(#grid)" />
          </svg>
        </div>
        
        <!-- Floating Elements -->
        <div class="absolute -top-4 -right-4 w-24 h-24 bg-white bg-opacity-5 rounded-full blur-xl"></div>
        <div class="absolute -bottom-8 -left-8 w-32 h-32 bg-blue-300 bg-opacity-10 rounded-full blur-2xl"></div>
        
        <div class="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <div class="flex items-center mb-3">
              <div class="w-10 h-10 bg-white bg-opacity-20 rounded-xl backdrop-blur-sm flex items-center justify-center mr-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
            <h1 class="text-3xl md:text-4xl font-bold mb-3 bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent">
              Welcome to BIWMS
            </h1>
            <p class="text-blue-100 text-lg font-medium">Blockchain Integrated Water Management System</p>
            <p class="text-blue-200 text-sm mt-2 opacity-90">Real-time predictions • Multi-signature approval • Decentralized data</p>
          </div>
          <div class="mt-6 md:mt-0 flex items-center space-x-4">
            <div class="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl px-4 py-2 border border-white border-opacity-20">
              <div class="flex items-center">
                                 <div class="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
                <span class="text-white text-sm font-medium">System Active</span>
              </div>
            </div>
            <button @click="openReportsModal" class="bg-white bg-opacity-20 backdrop-blur-sm border border-white border-opacity-30 text-white hover:bg-opacity-30 px-6 py-3 rounded-xl shadow-lg font-medium transition-all duration-300 hover:scale-105 hover:shadow-xl">
              <div class="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              View Reports
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- Main Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
        <!-- Predictions Card -->
        <div class="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 overflow-hidden border border-gray-100 hover:border-blue-200 hover:-translate-y-1">
          <!-- Gradient Border Effect -->
          <div class="absolute inset-0 bg-gradient-to-br from-blue-500 via-blue-600 to-indigo-600 opacity-0 group-hover:opacity-5 transition-opacity duration-500"></div>
          
          <!-- Main Content -->
          <div class="relative p-6 border-b border-gray-50">
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <div class="flex items-center mb-2">
                  <p class="text-sm font-medium text-gray-500 uppercase tracking-wider">Predictions</p>
                                     <div class="ml-2 w-2 h-2 bg-blue-400 rounded-full"></div>
                </div>
                                 <h3 class="text-3xl font-bold text-gray-900">{{ dashboardStats.total_predictions }}</h3>
              </div>
              <div class="bg-gradient-to-br from-blue-100 to-blue-200 p-4 rounded-2xl shadow-inner group-hover:scale-105 transition-transform duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
          </div>
          <div class="px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600 font-medium">AI Predictions Generated</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
        </div>
        
        <!-- Approved Card -->
        <div class="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 overflow-hidden border border-gray-100 hover:border-green-200 hover:-translate-y-1">
          <!-- Gradient Border Effect -->
          <div class="absolute inset-0 bg-gradient-to-br from-green-500 via-green-600 to-emerald-600 opacity-0 group-hover:opacity-5 transition-opacity duration-500"></div>
          
          <!-- Main Content -->
          <div class="relative p-6 border-b border-gray-50">
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <div class="flex items-center mb-2">
                  <p class="text-sm font-medium text-gray-500 uppercase tracking-wider">Approved</p>
                                     <div class="ml-2 w-2 h-2 bg-green-400 rounded-full"></div>
                </div>
                                 <h3 class="text-3xl font-bold text-gray-900">{{ dashboardStats.approved_predictions }}</h3>
              </div>
              <div class="bg-gradient-to-br from-green-100 to-green-200 p-4 rounded-2xl shadow-inner group-hover:scale-105 transition-transform duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
          <div class="px-6 py-4 bg-gradient-to-r from-green-50 to-emerald-50">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600 font-medium">Multi-Sig Approved</span>
              <div class="flex items-center">
                <span class="text-green-600 text-xs font-medium mr-1">2/2 Required</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Accuracy Card -->
        <div class="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 overflow-hidden border border-gray-100 hover:border-purple-200 hover:-translate-y-1">
          <!-- Gradient Border Effect -->
          <div class="absolute inset-0 bg-gradient-to-br from-purple-500 via-indigo-600 to-blue-600 opacity-0 group-hover:opacity-5 transition-opacity duration-500"></div>
          
          <!-- Main Content -->
          <div class="relative p-6 border-b border-gray-50">
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <div class="flex items-center mb-2">
                  <p class="text-sm font-medium text-gray-500 uppercase tracking-wider">Accuracy</p>
                                     <div class="ml-2 w-2 h-2 bg-purple-400 rounded-full"></div>
                </div>
                <h3 class="text-3xl font-bold text-gray-900 mb-1">{{ dashboardStats.accuracy }}%</h3>
                <div class="flex items-center">
                  <div class="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                    <div class="bg-gradient-to-r from-purple-500 to-indigo-600 h-2 rounded-full transition-all duration-1000" 
                         :style="{ width: dashboardStats.accuracy + '%' }"></div>
                  </div>
                  <span class="text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded-full font-medium">
                    High Performance
                  </span>
                </div>
              </div>
              <div class="bg-gradient-to-br from-purple-100 to-indigo-200 p-4 rounded-2xl shadow-inner group-hover:scale-105 transition-transform duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
          </div>
          <div class="px-6 py-4 bg-gradient-to-r from-purple-50 to-indigo-50">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600 font-medium">Neural Network</span>
              <div class="flex items-center">
                <span class="text-purple-600 text-xs font-medium mr-1">AI Model</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recent Activity -->
      <div class="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
        <!-- Header -->
        <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-8 py-6 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <div class="flex items-center">
              <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h2 class="text-xl font-bold text-gray-900 flex items-center">
                  Recent Activity
                  <span v-if="recentActivities.length > 0" class="ml-3 inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border border-green-200">
                    <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    Live Updates
                  </span>
                </h2>
                <p class="text-sm text-gray-500 mt-1">Real-time system events and transactions</p>
              </div>
            </div>

          </div>
        </div>
        
        <!-- Activity List -->
        <div class="p-8">
          <div v-if="recentActivities.length === 0" class="text-center py-12">
            <div class="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-900 mb-2">No recent activity</h3>
            <p class="text-gray-500 text-sm mb-1">Activity will appear here when predictions are generated</p>
            <p class="text-gray-400 text-xs">Connect your wallet and upload data to get started</p>
          </div>
          
          <div v-else class="space-y-4">
            <div v-for="(activity, index) in recentActivities.slice(0, 10)" :key="activity.timestamp" 
                 class="group relative border border-gray-100 rounded-xl p-4 hover:border-blue-200 hover:shadow-md transition-all duration-300 hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50">
              
              <!-- Timeline connector -->
              <div v-if="index < recentActivities.slice(0, 10).length - 1" 
                   class="absolute left-6 top-12 w-px h-6 bg-gradient-to-b from-gray-200 to-transparent"></div>
              
              <div class="flex items-start">
                <!-- Activity Icon -->
                <div class="flex-shrink-0 mt-0.5">
                  <div class="w-8 h-8 rounded-xl flex items-center justify-center shadow-sm border border-gray-200"
                       :class="getActivityIconStyle(activity.type, activity.severity)">
                    <div class="w-3 h-3 rounded-full" 
                         :class="getActivityColor(activity.type, activity.severity)"></div>
                  </div>
                </div>
                
                <!-- Activity Content -->
                <div class="ml-4 flex-1 min-w-0">
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <p class="text-sm font-semibold text-gray-900 group-hover:text-blue-900 transition-colors">
                        {{ activity.title }}
                      </p>
                      <p v-if="activity.description" class="text-sm text-gray-600 mt-1 leading-relaxed">
                        {{ activity.description }}
                      </p>
                    </div>
                    <div class="ml-4 flex-shrink-0">
                      <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium"
                            :class="getActivityBadgeStyle(activity.type)">
                        {{ getActivityTypeLabel(activity.type) }}
                      </span>
                    </div>
                  </div>
                  <div class="mt-2 flex items-center text-xs text-gray-500">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {{ formatActivityTimestamp(activity.timestamp) }}
                  </div>
                </div>
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
      <StakeholderDashboard @approval-updated="handleApprovalUpdate" />
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

    <!-- Reports Modal -->
    <ReportsModal :showModal="showReportsModal" @close="closeReportsModal" />
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
