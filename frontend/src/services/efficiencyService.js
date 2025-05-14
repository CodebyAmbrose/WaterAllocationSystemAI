/**
 * Efficiency Service
 * Calculates various efficiency metrics for the water allocation system
 */

/**
 * Calculate Resource Utilization Rate
 * @param {number} actualUsed - Actual water usage in HCF
 * @param {number} totalAllocated - Total water allocated in HCF
 * @returns {number} Resource Utilization Rate as a percentage
 */
export function calculateRUR(actualUsed, totalAllocated) {
  if (!totalAllocated) return 0;
  return (actualUsed / totalAllocated) * 100;
}

/**
 * Calculate Distribution Efficiency
 * @param {number} waterDelivered - Water successfully delivered in HCF
 * @param {number} waterInput - Total water input into system in HCF
 * @returns {number} Distribution Efficiency as a percentage
 */
export function calculateDE(waterDelivered, waterInput) {
  if (!waterInput) return 0;
  return (waterDelivered / waterInput) * 100;
}

/**
 * Calculate Allocation Balance Score
 * @param {Object} boroughAllocations - Object containing borough allocations
 * @returns {number} Allocation Balance Score (0-1)
 */
export function calculateABS(boroughAllocations) {
  if (!boroughAllocations || Object.keys(boroughAllocations).length === 0) return 0;
  
  const percentages = Object.values(boroughAllocations).map(b => b.percentage);
  const mean = percentages.reduce((a, b) => a + b, 0) / percentages.length;
  const variance = percentages.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / percentages.length;
  const stdDev = Math.sqrt(variance);
  
  return Math.max(0, 1 - (stdDev / mean));
}

/**
 * Calculate Overall System Efficiency
 * @param {Object} metrics - Object containing RUR, DE, and ABS values
 * @param {Object} weights - Object containing weights for each metric
 * @returns {number} Overall System Efficiency as a percentage
 */
export function calculateSystemEfficiency(metrics, weights = { rur: 0.4, de: 0.3, abs: 0.3 }) {
  const { rur, de, abs } = metrics;
  return (
    (weights.rur * rur + 
     weights.de * de + 
     weights.abs * abs)
  );
}

/**
 * Generate efficiency report with all metrics
 * @param {Object} data - Prediction data containing allocations and usage
 * @returns {Object} Complete efficiency report
 */
export function generateEfficiencyReport(data) {
  const rur = calculateRUR(data.actualUsed, data.totalAllocated);
  const de = calculateDE(data.waterDelivered, data.waterInput);
  const abs = calculateABS(data.predicted_allocation);
  
  const systemEfficiency = calculateSystemEfficiency({ rur, de, abs });
  
  return {
    resourceUtilization: rur,
    distributionEfficiency: de,
    allocationBalance: abs,
    systemEfficiency,
    details: {
      weights: { rur: 0.4, de: 0.3, abs: 0.3 },
      timestamp: new Date().toISOString()
    }
  };
} 