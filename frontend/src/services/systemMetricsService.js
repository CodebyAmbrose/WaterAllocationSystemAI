import { generateEfficiencyReport } from './efficiencyService';
import contractService from './ContractService';

class SystemMetricsService {
  constructor() {
    this.metrics = {
      actualUsed: 0,
      totalAllocated: 0,
      waterDelivered: 0,
      waterInput: 0,
      predicted_allocation: {}
    };
    this.lastUpdate = null;
  }

  async initialize() {
    try {
      await this.refreshMetrics();
      // Set up periodic refresh every 5 minutes
      setInterval(() => this.refreshMetrics(), 5 * 60 * 1000);
    } catch (error) {
      console.error('Error initializing SystemMetricsService:', error);
    }
  }

  async refreshMetrics() {
    try {
      // Get contract service data
      await contractService.initialize();
      const predictions = await this.getRecentPredictions();
      
      if (predictions.length > 0) {
        // Get the most recent prediction
        const latestPrediction = predictions[0];
        
        // Calculate actual water usage from blockchain data
        const actualUsage = await this.calculateActualUsage(predictions);
        
        // Update metrics with real data
        this.metrics = {
          actualUsed: actualUsage.used,
          totalAllocated: actualUsage.allocated,
          waterDelivered: actualUsage.delivered,
          waterInput: actualUsage.input,
          predicted_allocation: latestPrediction.allocations || {}
        };

        this.lastUpdate = new Date();
      }
    } catch (error) {
      console.error('Error refreshing system metrics:', error);
      throw error;
    }
  }

  async getRecentPredictions() {
    try {
      const totalPredictions = await contractService.getPredictionCount();
      const startId = Math.max(0, totalPredictions - 10); // Get last 10 predictions
      const predictions = await contractService.getMultiplePredictions(startId, 10);
      return predictions;
    } catch (error) {
      console.error('Error getting recent predictions:', error);
      return [];
    }
  }

  async calculateActualUsage(predictions) {
    // Calculate actual usage metrics from recent predictions
    const recentPredictions = predictions.slice(0, 5); // Use last 5 predictions
    
    let totalUsed = 0;
    let totalAllocated = 0;
    let totalDelivered = 0;
    let totalInput = 0;
    
    recentPredictions.forEach(prediction => {
      if (prediction.metadata) {
        totalUsed += prediction.metadata.actualUsage || 0;
        totalAllocated += prediction.metadata.allocatedAmount || 0;
        totalDelivered += prediction.metadata.deliveredAmount || 0;
        totalInput += prediction.metadata.inputAmount || 0;
      }
    });

    // Calculate averages
    const count = recentPredictions.length;
    return {
      used: count > 0 ? Math.round(totalUsed / count) : 0,
      allocated: count > 0 ? Math.round(totalAllocated / count) : 0,
      delivered: count > 0 ? Math.round(totalDelivered / count) : 0,
      input: count > 0 ? Math.round(totalInput / count) : 0
    };
  }

  getEfficiencyReport() {
    if (!this.lastUpdate) {
      return null;
    }
    return generateEfficiencyReport(this.metrics);
  }

  getLastUpdateTime() {
    return this.lastUpdate;
  }
}

// Create a singleton instance
const systemMetricsService = new SystemMetricsService();
export default systemMetricsService; 