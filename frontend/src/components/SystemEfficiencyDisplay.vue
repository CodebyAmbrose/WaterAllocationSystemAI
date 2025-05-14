<template>
  <div class="bg-white rounded-lg shadow p-4">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">System Efficiency Metrics</h3>
    
    <!-- Overall Efficiency Gauge -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-gray-700">Overall System Efficiency</span>
        <span class="text-lg font-bold" :class="efficiencyColorClass">
          {{ formatPercentage(efficiencyData.systemEfficiency) }}
        </span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2.5">
        <div class="h-2.5 rounded-full transition-all duration-500"
             :class="efficiencyColorClass"
             :style="{ width: `${efficiencyData.systemEfficiency}%` }">
        </div>
      </div>
    </div>
    
    <!-- Individual Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Resource Utilization Rate -->
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-700">Resource Utilization</span>
          <span class="text-sm font-semibold">
            {{ formatPercentage(efficiencyData.resourceUtilization) }}
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-blue-600 h-2 rounded-full transition-all duration-500"
               :style="{ width: `${efficiencyData.resourceUtilization}%` }">
          </div>
        </div>
        <p class="mt-2 text-xs text-gray-500">
          Measures how effectively allocated water is being used
        </p>
      </div>
      
      <!-- Distribution Efficiency -->
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-700">Distribution Efficiency</span>
          <span class="text-sm font-semibold">
            {{ formatPercentage(efficiencyData.distributionEfficiency) }}
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-green-600 h-2 rounded-full transition-all duration-500"
               :style="{ width: `${efficiencyData.distributionEfficiency}%` }">
          </div>
        </div>
        <p class="mt-2 text-xs text-gray-500">
          Tracks water delivery success rate and system losses
        </p>
      </div>
      
      <!-- Allocation Balance -->
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-700">Allocation Balance</span>
          <span class="text-sm font-semibold">
            {{ formatPercentage(efficiencyData.allocationBalance * 100) }}
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-purple-600 h-2 rounded-full transition-all duration-500"
               :style="{ width: `${efficiencyData.allocationBalance * 100}%` }">
          </div>
        </div>
        <p class="mt-2 text-xs text-gray-500">
          Indicates how evenly water is distributed across boroughs
        </p>
      </div>
    </div>
    
    <!-- Additional Details -->
    <div class="mt-6 pt-4 border-t border-gray-200">
      <div class="flex items-center justify-between">
        <span class="text-sm text-gray-500">Last Updated</span>
        <span class="text-sm text-gray-700">
          {{ formatDate(efficiencyData.details.timestamp) }}
        </span>
      </div>
      <div class="mt-2 flex items-center justify-between">
        <span class="text-sm text-gray-500">Calculation Weights</span>
        <span class="text-sm text-gray-700">
          RUR: {{ efficiencyData.details.weights.rur }},
          DE: {{ efficiencyData.details.weights.de }},
          ABS: {{ efficiencyData.details.weights.abs }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SystemEfficiencyDisplay',
  props: {
    efficiencyData: {
      type: Object,
      required: true
    }
  },
  computed: {
    efficiencyColorClass() {
      const efficiency = this.efficiencyData.systemEfficiency;
      if (efficiency >= 90) return 'bg-green-600 text-green-600';
      if (efficiency >= 75) return 'bg-blue-600 text-blue-600';
      if (efficiency >= 60) return 'bg-yellow-600 text-yellow-600';
      return 'bg-red-600 text-red-600';
    }
  },
  methods: {
    formatPercentage(value) {
      return `${Math.round(value)}%`;
    },
    formatDate(timestamp) {
      return new Date(timestamp).toLocaleString();
    }
  }
};
</script>

<style scoped>
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 500ms;
}
</style> 