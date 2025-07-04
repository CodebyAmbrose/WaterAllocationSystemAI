<template>
  <div class="analytics-container">
    <!-- Infrastructure Analytics Header -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <h2 class="text-xl font-bold text-gray-900">Water System Infrastructure Analytics</h2>
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2">
              <div class="w-3 h-3 rounded-full" :class="systemHealthColor"></div>
              <span class="text-sm font-medium" :class="systemHealthTextColor">
                {{ systemHealthStatus }}
              </span>
            </div>
          </div>
          <span v-if="lastUpdate" class="text-xs text-gray-500">
            Last update: {{ lastUpdate }}
          </span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Actual Water Consumption Trends -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Actual Water Consumption</h3>
          <div class="flex space-x-2">
            <button 
              class="px-3 py-1 text-xs font-medium rounded-full"
              :class="selectedYear === 2025 ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'"
              @click="changeYear(2025)"
            >
              2025
            </button>
            <button 
              class="px-3 py-1 text-xs font-medium rounded-full"
              :class="selectedYear === 2024 ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'"
              @click="changeYear(2024)"
            >
              2024
            </button>
          </div>
        </div>
        <div class="h-64 relative">
          <div v-if="loading.consumptionData" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-70">
            <div class="w-8 h-8 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
          </div>
          <Line :data="consumptionChartData" :options="consumptionChartOptions" />
        </div>
      </div>

      <!-- Borough Water Distribution -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Borough Water Distribution</h3>
          <select 
            class="text-sm border-gray-300 rounded-md"
            v-model="selectedTimeframe"
            @change="changeTimeframe(selectedTimeframe)"
          >
            <option value="current">Current Data</option>
            <option value="monthly">Monthly Average</option>
            <option value="yearly">Yearly Total</option>
          </select>
        </div>
        <div class="h-64 relative">
          <div v-if="loading.boroughData" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-70">
            <div class="w-8 h-8 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
          </div>
          <Bar :data="boroughChartData" :options="boroughChartOptions" />
        </div>
      </div>

      <!-- System Performance -->
      <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">System Performance</h3>
        <div v-if="loading.performanceData" class="flex items-center justify-center py-10">
          <div class="w-8 h-8 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
        </div>
        <div v-else class="grid grid-cols-2 gap-4">
          <div class="bg-gray-50 p-4 rounded-lg">
            <h4 class="text-sm font-medium text-gray-700 mb-2">System Uptime</h4>
            <div class="h-40 relative">
              <Doughnut :data="uptimeChartData" :options="uptimeChartOptions" />
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="text-center">
                  <span class="text-2xl font-bold text-green-600">{{ formattedUptime }}%</span>
                  <div class="text-xs text-gray-500">Uptime</div>
                </div>
              </div>
            </div>
          </div>
          <div class="space-y-4">
            <div v-for="(metric, index) in performanceMetrics" :key="index" class="bg-gray-50 p-3 rounded-lg">
              <div class="flex justify-between items-center mb-1">
                <span class="text-sm font-medium text-gray-700">{{ metric.name }}</span>
                <span class="text-sm font-semibold" :class="metric.valueColor">{{ metric.value }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="h-2 rounded-full" :class="metric.barColor" :style="{ width: `${metric.percentage}%` }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Conservation Effectiveness -->
      <div class="bg-white rounded-lg shadow p-4 col-span-1 lg:col-span-2">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Water Conservation Effectiveness</h3>
        <div class="h-64 relative">
          <div v-if="loading.conservationData" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-70">
            <div class="w-8 h-8 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
          </div>
          <Line :data="conservationChartData" :options="conservationChartOptions" />
        </div>
      </div>


    </div>
  </div>
</template>

<script>
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip, 
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar, Doughnut } from 'vue-chartjs';

ChartJS.register(
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip, 
  Legend,
  Filler
);

export default {
  name: 'WaterAnalytics',
  components: {
    Line,
    Bar,
    Doughnut
  },
  data() {
    return {
      selectedYear: 2025,
      selectedTimeframe: 'current',
      loading: {
        consumptionData: true,
        boroughData: true,
        performanceData: true,
        conservationData: true
      },
      eventSource: null,
      isConnected: false,
      lastUpdate: null,
      systemHealthStatus: 'All Systems Operational',
      systemHealthColor: 'bg-green-400',
      systemHealthTextColor: 'text-green-600',
      
      // Chart data structures
      consumptionChartData: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{ data: [] }]
      },
      consumptionChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            mode: 'index',
            intersect: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              drawBorder: false,
            },
            title: {
              display: true,
              text: 'Consumption (HCF)'
            }
          },
          x: {
            grid: {
              display: false,
            }
          }
        }
      },
      
      boroughChartData: {
        labels: [],
        datasets: [{ data: [] }]
      },
      boroughChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              drawBorder: false,
            },
            title: {
              display: true,
              text: 'Water Volume (HCF)'
            }
          },
          x: {
            grid: {
              display: false,
            }
          }
        }
      },
      
      uptimeChartData: {
        labels: ['Uptime', 'Downtime'],
        datasets: [{ data: [0, 100] }]
      },
      uptimeChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '75%',
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            enabled: false
          }
        }
      },
      
      conservationChartData: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{ data: [] }]
      },
      conservationChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              drawBorder: false,
            },
            title: {
              display: true,
              text: 'Conservation Rate (%)'
            }
          },
          x: {
            grid: {
              display: false,
            }
          }
        }
      },
      
      performanceMetrics: [],
      formattedUptime: 0
    };
  },
  mounted() {
    this.loadAllData().then(() => {
      this.connectToRealTimeAnalytics();
    });
  },
  beforeUnmount() {
    this.disconnectFromRealTime();
  },
  methods: {
    connectToRealTimeAnalytics() {
      if (this.eventSource) {
        this.eventSource.close();
      }

      try {
        this.eventSource = new EventSource('http://localhost:8000/stats/stream');
        
        this.eventSource.onopen = () => {
          console.log('Connected to real-time infrastructure analytics');
          this.isConnected = true;
        };

        this.eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'heartbeat') {
              return; // Don't process heartbeat as data update
            }
            
            if (data.analytics) {
              console.log('🎯 Infrastructure analytics data received');
              this.updateChartsWithRealTimeData(data.analytics);
              this.lastUpdate = new Date().toLocaleTimeString();
            }
          } catch (error) {
            console.error('❌ Error parsing infrastructure analytics:', error);
          }
        };

        this.eventSource.onerror = (error) => {
          console.error('Infrastructure analytics SSE error:', error);
          this.isConnected = false;
          setTimeout(() => {
            if (!this.isConnected) {
              this.connectToRealTimeAnalytics();
            }
          }, 5000);
        };

      } catch (error) {
        console.error('Failed to establish infrastructure analytics SSE connection:', error);
      }
    },

    disconnectFromRealTime() {
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
        this.isConnected = false;
      }
    },

    updateChartsWithRealTimeData(analyticsData) {
      console.log('Updating infrastructure charts with data:', analyticsData);
      
      // Update actual consumption chart
      this.updateConsumptionChart(analyticsData.actual_consumption);
      
      // Update borough distribution chart
      this.updateBoroughChart(analyticsData.actual_consumption?.borough_totals);
      
      // Update system performance metrics
      this.updatePerformanceMetrics(analyticsData.infrastructure);
      
      // Update conservation chart
      this.updateConservationChart(analyticsData.conservation);
      
      // Update system health status
      this.updateSystemHealthStatus(analyticsData.infrastructure);
      
      // Mark all as loaded
      Object.keys(this.loading).forEach(key => {
        this.loading[key] = false;
      });
    },

    updateConsumptionChart(consumptionData) {
      if (!consumptionData?.monthly_trends) return;
      
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const data = consumptionData.monthly_trends.map(trend => trend.consumption || 0);
      
      this.consumptionChartData = {
        labels: months,
        datasets: [
          {
            label: 'Actual Water Consumption (HCF)',
            data: data,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4,
            fill: true
          }
        ]
      };
    },

    updateBoroughChart(boroughData) {
      if (!boroughData) return;
      
      this.boroughChartData = {
        labels: Object.keys(boroughData),
        datasets: [
          {
            label: 'Water Distribution (HCF)',
            data: Object.values(boroughData),
            backgroundColor: [
              'rgba(59, 130, 246, 0.7)',
              'rgba(99, 102, 241, 0.7)',
              'rgba(79, 70, 229, 0.7)',
              'rgba(139, 92, 246, 0.7)',
              'rgba(168, 85, 247, 0.7)'
            ]
          }
        ]
      };
    },

    updatePerformanceMetrics(infrastructureData) {
      if (!infrastructureData) return;
      
      this.formattedUptime = Math.round((infrastructureData.system_uptime || 0) * 100) / 100;
      
      this.uptimeChartData = {
        labels: ['Uptime', 'Downtime'],
        datasets: [
          {
            data: [this.formattedUptime, 100 - this.formattedUptime],
            backgroundColor: [
              'rgba(34, 197, 94, 0.8)',
              'rgba(229, 231, 235, 0.5)'
            ],
            borderWidth: 0
          }
        ]
      };

      this.performanceMetrics = [
        {
          name: 'API Response',
          value: `${infrastructureData.api_response_time_ms || 0}ms`,
          percentage: Math.max(0, 100 - (infrastructureData.api_response_time_ms || 0) / 2),
          valueColor: (infrastructureData.api_response_time_ms || 0) < 100 ? 'text-green-600' : 'text-yellow-600',
          barColor: (infrastructureData.api_response_time_ms || 0) < 100 ? 'bg-green-500' : 'bg-yellow-500'
        },
        {
          name: 'Processing Rate',
          value: `${infrastructureData.data_processing_rate || 0}/hr`,
          percentage: Math.min(100, (infrastructureData.data_processing_rate || 0) * 10),
          valueColor: 'text-blue-600',
          barColor: 'bg-blue-500'
        },
        {
          name: 'Upload Success',
          value: `${infrastructureData.file_upload_success_rate || 100}%`,
          percentage: infrastructureData.file_upload_success_rate || 100,
          valueColor: (infrastructureData.file_upload_success_rate || 100) >= 95 ? 'text-green-600' : 'text-red-600',
          barColor: (infrastructureData.file_upload_success_rate || 100) >= 95 ? 'bg-green-500' : 'bg-red-500'
        }
      ];
    },

    updateConservationChart(conservationData) {
      if (!conservationData?.monthly_conservation_rate) return;
      
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      
      this.conservationChartData = {
        labels: months,
        datasets: [
          {
            label: 'Conservation Rate (%)',
            data: conservationData.monthly_conservation_rate,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4,
            fill: true
          }
        ]
      };
    },



    updateSystemHealthStatus(infrastructureData) {
      if (!infrastructureData) return;
      
      const uptime = infrastructureData.system_uptime || 0;
      const aiStatus = infrastructureData.ai_model_status || 'healthy';
      
      if (uptime >= 99 && aiStatus === 'healthy') {
        this.systemHealthStatus = 'All Systems Operational';
        this.systemHealthColor = 'bg-green-400';
        this.systemHealthTextColor = 'text-green-600';
      } else if (uptime >= 95) {
        this.systemHealthStatus = 'Minor Issues Detected';
        this.systemHealthColor = 'bg-yellow-400';
        this.systemHealthTextColor = 'text-yellow-600';
      } else {
        this.systemHealthStatus = 'System Degraded';
        this.systemHealthColor = 'bg-red-400';
        this.systemHealthTextColor = 'text-red-600';
      }
    },

    async loadAllData() {
      try {
        console.log('Loading infrastructure analytics data...');
        const response = await fetch('http://localhost:8000/analytics');
        if (response.ok) {
          const data = await response.json();
          if (data.analytics) {
            console.log('Loaded infrastructure analytics data');
            this.updateChartsWithRealTimeData(data.analytics);
            return;
          }
        }
      } catch (error) {
        console.error('Error loading infrastructure analytics:', error);
      }
      
      // Fallback to default state
      console.log('No infrastructure data found - using default state');
      Object.keys(this.loading).forEach(key => {
        this.loading[key] = false;
      });
    },
    
    changeYear(year) {
      this.selectedYear = year;
      // Year changes would typically reload data for that year
      // For now, we'll just update the selected year
    },
    
    changeTimeframe(timeframe) {
      this.selectedTimeframe = timeframe;
      // Timeframe changes would typically adjust the borough chart data
      // For now, we'll just update the selected timeframe
    }
  }
};
</script>

<style scoped>
.analytics-container {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style> 