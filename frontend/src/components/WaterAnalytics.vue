<template>
  <div class="analytics-container">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Water Usage Trend Chart -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Monthly Water Usage Trends</h3>
          <div class="flex space-x-2">
            <button 
              class="px-3 py-1 text-xs font-medium rounded-full"
              :class="selectedYear === 2023 ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'"
              @click="changeYear(2023)"
            >
              2023
            </button>
            <button 
              class="px-3 py-1 text-xs font-medium rounded-full"
              :class="selectedYear === 2022 ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'"
              @click="changeYear(2022)"
            >
              2022
            </button>
          </div>
        </div>
        <div class="h-64 relative">
          <div v-if="loading.usageData" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-70">
            <div class="w-8 h-8 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
          </div>
          <Line :data="lineChartData" :options="lineChartOptions" />
        </div>
      </div>

      <!-- Borough Comparison Chart -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Borough Water Allocation</h3>
          <select 
            class="text-sm border-gray-300 rounded-md"
            v-model="selectedTimeframe"
            @change="changeTimeframe(selectedTimeframe)"
          >
            <option value="12">Last 12 Months</option>
            <option value="6">Last 6 Months</option>
            <option value="3">Last 3 Months</option>
          </select>
        </div>
        <div class="h-64 relative">
          <div v-if="loading.boroughData" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-70">
            <div class="w-8 h-8 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
          </div>
          <Bar :data="barChartData" :options="barChartOptions" />
        </div>
      </div>

      <!-- Water Quality Metrics -->
      <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Water Quality Metrics</h3>
        <div class="h-64 relative">
          <div v-if="loading.qualityData" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-70">
            <div class="w-8 h-8 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
          </div>
          <Radar :data="radarChartData" :options="radarChartOptions" />
        </div>
      </div>

      <!-- Efficiency Score -->
      <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Water Usage Efficiency</h3>
        <div v-if="loading.efficiencyData" class="flex items-center justify-center py-10">
          <div class="w-8 h-8 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
        </div>
        <div v-else class="grid grid-cols-2 gap-4">
          <div class="bg-gray-50 p-4 rounded-lg">
            <h4 class="text-sm font-medium text-gray-700 mb-2">Overall Efficiency Score</h4>
            <div class="h-40 relative">
              <Doughnut :data="doughnutChartData" :options="doughnutChartOptions" />
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="text-center">
                  <span class="text-2xl font-bold text-blue-600">{{ doughnutChartData.datasets[0].data[0] }}%</span>
                  <div class="text-xs text-gray-500">Efficiency</div>
                </div>
              </div>
            </div>
          </div>
          <div class="space-y-4">
            <div v-for="(borough, index) in boroughScores" :key="index" class="bg-gray-50 p-3 rounded-lg">
              <div class="flex justify-between items-center mb-1">
                <span class="text-sm font-medium text-gray-700">{{ borough.name }}</span>
                <span class="text-sm font-semibold" :class="getScoreColor(borough.score)">{{ borough.score }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="h-2 rounded-full" :class="getScoreBackground(borough.score)" :style="{ width: `${borough.score}%` }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Prediction Accuracy -->
      <div class="bg-white rounded-lg shadow p-4 col-span-1 lg:col-span-2">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Prediction Accuracy History</h3>
        <div class="h-64 relative">
          <div v-if="loading.accuracyData" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-70">
            <div class="w-8 h-8 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
          </div>
          <Line :data="accuracyChartData" :options="accuracyChartOptions" />
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
  RadialLinearScale,
  ArcElement,
  Title,
  Tooltip, 
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar, Radar, Doughnut } from 'vue-chartjs';
import { 
  getMonthlyUsageData, 
  getBoroughAllocationData, 
  getWaterQualityData, 
  getEfficiencyScores, 
  getPredictionAccuracy 
} from '../services/analyticsService';

ChartJS.register(
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement,
  BarElement,
  RadialLinearScale,
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
    Radar,
    Doughnut
  },
  data() {
    return {
      selectedYear: 2023,
      selectedTimeframe: '12',
      loading: {
        usageData: true,
        boroughData: true,
        qualityData: true,
        efficiencyData: true,
        accuracyData: true
      },
      // Default empty data structures
      lineChartData: {
        labels: [],
        datasets: [{ data: [] }]
      },
      lineChartOptions: {
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
            beginAtZero: false,
            grid: {
              drawBorder: false,
            },
          },
          x: {
            grid: {
              display: false,
            }
          }
        }
      },
      barChartData: {
        labels: [],
        datasets: [{ data: [] }]
      },
      barChartOptions: {
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
          },
          x: {
            grid: {
              display: false,
            }
          }
        }
      },
      radarChartData: {
        labels: [],
        datasets: [{ data: [] }]
      },
      radarChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: {
              color: 'rgba(200, 200, 200, 0.3)',
            },
            grid: {
              color: 'rgba(200, 200, 200, 0.3)',
            },
            pointLabels: {
              font: {
                size: 10
              }
            },
            suggestedMin: 50,
            suggestedMax: 100
          }
        }
      },
      doughnutChartData: {
        labels: ['Efficient', 'Inefficient'],
        datasets: [{ data: [0, 100] }]
      },
      doughnutChartOptions: {
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
      boroughScores: [],
      accuracyChartData: {
        labels: [],
        datasets: [{ data: [] }]
      },
      accuracyChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          }
        },
        scales: {
          y: {
            min: 90,
            max: 100,
            grid: {
              drawBorder: false,
            },
          },
          x: {
            grid: {
              display: false,
            }
          }
        }
      }
    };
  },
  mounted() {
    this.loadAllData();
  },
  methods: {
    async loadAllData() {
      this.fetchMonthlyUsageData();
      this.fetchBoroughAllocationData();
      this.fetchWaterQualityData();
      this.fetchEfficiencyScores();
      this.fetchPredictionAccuracy();
    },
    
    async fetchMonthlyUsageData() {
      this.loading.usageData = true;
      try {
        const data = await getMonthlyUsageData(this.selectedYear);
        this.lineChartData = {
          labels: data.labels,
          datasets: [
            {
              label: 'Total Usage (Million Gallons)',
              data: data.data,
              borderColor: '#3b82f6',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              tension: 0.4,
              fill: true
            }
          ]
        };
      } catch (error) {
        console.error('Error fetching usage data:', error);
      } finally {
        this.loading.usageData = false;
      }
    },
    
    async fetchBoroughAllocationData() {
      this.loading.boroughData = true;
      try {
        this.barChartData = await getBoroughAllocationData(this.selectedTimeframe);
      } catch (error) {
        console.error('Error fetching borough data:', error);
      } finally {
        this.loading.boroughData = false;
      }
    },
    
    async fetchWaterQualityData() {
      this.loading.qualityData = true;
      try {
        this.radarChartData = await getWaterQualityData();
      } catch (error) {
        console.error('Error fetching quality data:', error);
      } finally {
        this.loading.qualityData = false;
      }
    },
    
    async fetchEfficiencyScores() {
      this.loading.efficiencyData = true;
      try {
        const data = await getEfficiencyScores();
        this.doughnutChartData = {
          labels: ['Efficient', 'Inefficient'],
          datasets: [
            {
              data: [data.overall, 100 - data.overall],
              backgroundColor: [
                'rgba(59, 130, 246, 0.8)',
                'rgba(229, 231, 235, 0.5)'
              ],
              borderWidth: 0
            }
          ]
        };
        this.boroughScores = data.boroughs;
      } catch (error) {
        console.error('Error fetching efficiency data:', error);
      } finally {
        this.loading.efficiencyData = false;
      }
    },
    
    async fetchPredictionAccuracy() {
      this.loading.accuracyData = true;
      try {
        this.accuracyChartData = await getPredictionAccuracy();
      } catch (error) {
        console.error('Error fetching accuracy data:', error);
      } finally {
        this.loading.accuracyData = false;
      }
    },
    
    changeYear(year) {
      this.selectedYear = year;
      this.fetchMonthlyUsageData();
    },
    
    changeTimeframe(timeframe) {
      this.selectedTimeframe = timeframe;
      this.fetchBoroughAllocationData();
    },
    
    getScoreColor(score) {
      if (score >= 90) return 'text-green-600';
      if (score >= 80) return 'text-blue-600';
      if (score >= 70) return 'text-yellow-600';
      return 'text-red-600';
    },
    
    getScoreBackground(score) {
      if (score >= 90) return 'bg-green-500';
      if (score >= 80) return 'bg-blue-500';
      if (score >= 70) return 'bg-yellow-500';
      return 'bg-red-500';
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