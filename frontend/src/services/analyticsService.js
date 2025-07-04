/**
 * Analytics Service
 * Provides functions to fetch water usage analytics data
 */

// Mock data for development purposes
// In a real implementation, this would fetch data from the server

/**
 * Fetch monthly water usage data for the selected year
 * @param {number} year - The year to get data for
 * @returns {Promise} - Promise that resolves to water usage data
 */
export async function getMonthlyUsageData(year = 2023) {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Sample data mapping
  const yearData = {
    2023: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      data: [450, 420, 430, 410, 400, 425, 450, 470, 445, 430, 410, 405]
    },
    2022: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      data: [440, 430, 425, 415, 410, 420, 435, 460, 450, 425, 415, 410]
    }
  };
  
  return yearData[year] || yearData[2023];
}

/**
 * Fetch borough water allocation data
 * @param {string} timeframe - Time period to get data for (3, 6, or 12 months)
 * @returns {Promise} - Promise that resolves to borough allocation data
 */
export async function getBoroughAllocationData(timeframe = '12') {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Sample allocation data by borough
  return {
    labels: ['BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS'],
    datasets: [
      {
        label: 'Allocation (Million Gallons)',
        data: [105, 165, 130, 150],
        backgroundColor: [
          'rgba(59, 130, 246, 0.7)',
          'rgba(99, 102, 241, 0.7)',
          'rgba(79, 70, 229, 0.7)',
          'rgba(139, 92, 246, 0.7)'
        ]
      }
    ]
  };
}

/**
 * Fetch water quality metrics data
 * @returns {Promise} - Promise that resolves to water quality metrics
 */
export async function getWaterQualityData() {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  return {
    labels: ['Clarity', 'pH Level', 'Bacterial Count', 'Chemical Balance', 'Mineral Content', 'Treatment Efficiency'],
    datasets: [
      {
        label: 'System Average',
        data: [85, 90, 78, 88, 92, 86],
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgba(59, 130, 246, 0.8)',
        pointBackgroundColor: 'rgba(59, 130, 246, 1)'
      }
    ]
  };
}

/**
 * Fetch efficiency scores for boroughs
 * @returns {Promise} - Promise that resolves to borough efficiency scores
 */
export async function getEfficiencyScores() {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  return {
    overall: 87,
    boroughs: [
      { name: 'BRONX', score: 82 },
      { name: 'BROOKLYN', score: 91 },
      { name: 'MANHATTAN', score: 85 },
      { name: 'QUEENS', score: 89 }
    ]
  };
}

/**
 * Fetch prediction accuracy history
 * @returns {Promise} - Promise that resolves to prediction accuracy data
 */
export async function getPredictionAccuracy() {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  return {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'AI Prediction Accuracy (%)',
        data: [93.2, 93.8, 94.3, 94.7, 95.1, 95.4, 95.6, 95.8, 95.9, 96.0, 96.0, 96.0],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)'
      }
    ]
  };
} 