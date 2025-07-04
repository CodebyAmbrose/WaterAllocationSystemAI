#!/usr/bin/env python3
"""
BIWMS Performance Testing Script

This script comprehensively tests the performance of:
1. AI prediction module (LSTM-based)
2. IPFS data storage (Pinata)
3. Smart contract submission (BSC testnet)
4. Frontend dashboard performance

Measures response times, resource usage, and identifies bottlenecks.
"""

import time
import psutil
import os
import json
import sys
import requests
import subprocess
import threading
import traceback
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from statistics import mean, median, stdev

# Import system modules
from AI_feeds.predict import run_prediction
from pinata_uploader import upload_to_ipfs

class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.cpu_samples = []
        self.memory_samples = []
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start monitoring system resources"""
        self.start_time = time.time()
        self.cpu_samples = []
        self.memory_samples = []
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_resources)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring and return statistics"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        
        duration = time.time() - self.start_time if self.start_time else 0
        
        return {
            'duration': duration,
            'cpu_avg': mean(self.cpu_samples) if self.cpu_samples else 0,
            'cpu_max': max(self.cpu_samples) if self.cpu_samples else 0,
            'memory_avg': mean(self.memory_samples) if self.memory_samples else 0,
            'memory_max': max(self.memory_samples) if self.memory_samples else 0,
            'memory_samples': len(self.memory_samples)
        }
    
    def _monitor_resources(self):
        """Monitor CPU and memory usage in background"""
        while self.monitoring:
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                
                self.cpu_samples.append(cpu_percent)
                self.memory_samples.append(memory_mb)
                
                time.sleep(0.5)  # Sample every 500ms
            except Exception as e:
                print(f"Warning: Resource monitoring error: {e}")
                break

class BIWMSTester:
    def __init__(self):
        self.results = []
        self.test_data_file = "test_data.csv"
        self.ensure_test_data_exists()
        
    def ensure_test_data_exists(self):
        """Ensure test data file exists for predictions"""
        if not os.path.exists(self.test_data_file):
            print("Creating test data file...")
            # Create minimal test data
            test_data = {
                'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
                'borough': ['Manhattan', 'Brooklyn', 'Queens'],
                'consumption_(hcf)': [1500, 1200, 1800]
            }
            pd.DataFrame(test_data).to_csv(self.test_data_file, index=False)
    
    def log_result(self, component: str, operation: str, duration: float, 
                   cpu_avg: float, cpu_max: float, memory_avg: float, 
                   memory_max: float, notes: str = ""):
        """Log test results"""
        result = {
            'component': component,
            'operation': operation,
            'time_taken_s': round(duration, 3),
            'cpu_avg_%': round(cpu_avg, 1),
            'cpu_max_%': round(cpu_max, 1),
            'memory_avg_mb': round(memory_avg, 1),
            'memory_max_mb': round(memory_max, 1),
            'notes': notes
        }
        self.results.append(result)
        print(f"✓ {component} - {operation}: {duration:.3f}s (CPU: {cpu_avg:.1f}%, Memory: {memory_avg:.1f}MB)")
    
    def test_ai_prediction(self, num_iterations: int = 3) -> Dict:
        """Test AI model prediction performance"""
        print("\n🧠 Testing AI Prediction Module...")
        
        times = []
        all_stats = []
        
        for i in range(num_iterations):
            monitor = PerformanceMonitor()
            monitor.start_monitoring()
            
            try:
                start_time = time.time()
                prediction_file = run_prediction(self.test_data_file)
                duration = time.time() - start_time
                times.append(duration)
                
                stats = monitor.stop_monitoring()
                all_stats.append(stats)
                
                # Check if prediction file was created
                file_exists = os.path.exists(prediction_file) if prediction_file else False
                notes = f"Iter {i+1}, Output: {file_exists}"
                
                self.log_result("AI Prediction", f"LSTM Inference (Run {i+1})", 
                              duration, stats['cpu_avg'], stats['cpu_max'],
                              stats['memory_avg'], stats['memory_max'], notes)
                
            except Exception as e:
                print(f"❌ AI prediction failed on iteration {i+1}: {e}")
                self.log_result("AI Prediction", f"LSTM Inference (Run {i+1})", 
                              0, 0, 0, 0, 0, f"FAILED: {str(e)[:50]}")
        
        return {
            'avg_time': mean(times) if times else 0,
            'median_time': median(times) if times else 0,
            'times': times,
            'stats': all_stats
        }
    
    def test_ipfs_upload(self, num_iterations: int = 3) -> Dict:
        """Test IPFS upload performance with different file sizes"""
        print("\n🌐 Testing IPFS Upload Performance...")
        
        # Create test files of different sizes
        test_files = self.create_test_files()
        times = []
        all_stats = []
        
        for file_path, file_size in test_files:
            monitor = PerformanceMonitor()
            monitor.start_monitoring()
            
            try:
                start_time = time.time()
                ipfs_hash = upload_to_ipfs(file_path)
                duration = time.time() - start_time
                times.append(duration)
                
                stats = monitor.stop_monitoring()
                all_stats.append(stats)
                
                notes = f"Size: {file_size}KB, Hash: {ipfs_hash[:10]}..."
                
                self.log_result("IPFS Upload", f"File Upload ({file_size}KB)", 
                              duration, stats['cpu_avg'], stats['cpu_max'],
                              stats['memory_avg'], stats['memory_max'], notes)
                
            except Exception as e:
                print(f"❌ IPFS upload failed for {file_path}: {e}")
                self.log_result("IPFS Upload", f"File Upload ({file_size}KB)", 
                              0, 0, 0, 0, 0, f"FAILED: {str(e)[:50]}")
        
        # Clean up test files
        for file_path, _ in test_files:
            try:
                os.remove(file_path)
            except:
                pass
        
        return {
            'avg_time': mean(times) if times else 0,
            'median_time': median(times) if times else 0,
            'times': times,
            'stats': all_stats
        }
    
    def test_smart_contract_submission(self, num_iterations: int = 3) -> Dict:
        """Test smart contract submission performance"""
        print("\n⛓️ Testing Smart Contract Submission...")
        
        times = []
        all_stats = []
        
        for i in range(num_iterations):
            monitor = PerformanceMonitor()
            monitor.start_monitoring()
            
            try:
                # Create dummy IPFS hash and confidence score
                dummy_hash = f"QmTest{i:030d}"
                confidence_score = 85
                
                start_time = time.time()
                result = subprocess.run(
                    ["node", "oracle_submit.js", dummy_hash, str(confidence_score)],
                    capture_output=True,
                    text=True,
                    timeout=60  # 60 second timeout
                )
                duration = time.time() - start_time
                times.append(duration)
                
                stats = monitor.stop_monitoring()
                all_stats.append(stats)
                
                success = result.returncode == 0
                notes = f"Iter {i+1}, Success: {success}"
                if not success and result.stderr:
                    notes += f", Error: {result.stderr[:30]}"
                
                self.log_result("Smart Contract", f"Oracle Submission (Run {i+1})", 
                              duration, stats['cpu_avg'], stats['cpu_max'],
                              stats['memory_avg'], stats['memory_max'], notes)
                
            except subprocess.TimeoutExpired:
                print(f"❌ Smart contract submission timed out on iteration {i+1}")
                self.log_result("Smart Contract", f"Oracle Submission (Run {i+1})", 
                              60, 0, 0, 0, 0, "TIMEOUT (60s)")
            except Exception as e:
                print(f"❌ Smart contract submission failed on iteration {i+1}: {e}")
                self.log_result("Smart Contract", f"Oracle Submission (Run {i+1})", 
                              0, 0, 0, 0, 0, f"FAILED: {str(e)[:50]}")
        
        return {
            'avg_time': mean(times) if times else 0,
            'median_time': median(times) if times else 0,
            'times': times,
            'stats': all_stats
        }
    
    def test_api_endpoint_performance(self) -> Dict:
        """Test FastAPI endpoint performance"""
        print("\n🚀 Testing API Endpoint Performance...")
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        try:
            # Test the root endpoint first
            start_time = time.time()
            response = requests.get("http://localhost:8000/", timeout=10)
            duration = time.time() - start_time
            
            stats = monitor.stop_monitoring()
            
            success = response.status_code == 200
            notes = f"Status: {response.status_code}, Response: {success}"
            
            self.log_result("API Endpoint", "Root Endpoint", 
                          duration, stats['cpu_avg'], stats['cpu_max'],
                          stats['memory_avg'], stats['memory_max'], notes)
            
            return {
                'success': success,
                'response_time': duration,
                'status_code': response.status_code
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API endpoint test failed: {e}")
            self.log_result("API Endpoint", "Root Endpoint", 
                          0, 0, 0, 0, 0, f"FAILED: {str(e)[:50]}")
            return {'success': False, 'error': str(e)}
    
    def test_concurrent_operations(self, num_concurrent: int = 5) -> Dict:
        """Test system under concurrent load"""
        print(f"\n⚡ Testing Concurrent Operations ({num_concurrent} parallel)...")
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        results = []
        threads = []
        
        def run_prediction_thread(thread_id):
            try:
                start_time = time.time()
                prediction_file = run_prediction(self.test_data_file)
                duration = time.time() - start_time
                results.append({'thread_id': thread_id, 'duration': duration, 'success': True})
            except Exception as e:
                results.append({'thread_id': thread_id, 'duration': 0, 'success': False, 'error': str(e)})
        
        # Start concurrent threads
        start_time = time.time()
        for i in range(num_concurrent):
            thread = threading.Thread(target=run_prediction_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_duration = time.time() - start_time
        stats = monitor.stop_monitoring()
        
        successful_results = [r for r in results if r['success']]
        avg_thread_time = mean([r['duration'] for r in successful_results]) if successful_results else 0
        
        notes = f"Success: {len(successful_results)}/{num_concurrent}, Avg: {avg_thread_time:.3f}s"
        
        self.log_result("Concurrent Test", f"{num_concurrent} Parallel Predictions", 
                      total_duration, stats['cpu_avg'], stats['cpu_max'],
                      stats['memory_avg'], stats['memory_max'], notes)
        
        return {
            'total_time': total_duration,
            'successful_operations': len(successful_results),
            'total_operations': num_concurrent,
            'avg_thread_time': avg_thread_time,
            'results': results
        }
    
    def create_test_files(self) -> List[Tuple[str, int]]:
        """Create test files of different sizes for upload testing"""
        test_files = []
        
        # Small file (1KB)
        small_file = "test_small.json"
        with open(small_file, 'w') as f:
            json.dump({"test": "data", "size": "small"}, f)
        test_files.append((small_file, 1))
        
        # Medium file (10KB)
        medium_file = "test_medium.json"
        with open(medium_file, 'w') as f:
            data = {"test": "data" * 1000, "size": "medium"}
            json.dump(data, f)
        test_files.append((medium_file, 10))
        
        # Large file (100KB)
        large_file = "test_large.json"
        with open(large_file, 'w') as f:
            data = {"test": "data" * 10000, "size": "large"}
            json.dump(data, f)
        test_files.append((large_file, 100))
        
        return test_files
    
    def analyze_bottlenecks(self) -> Dict:
        """Analyze results to identify performance bottlenecks"""
        print("\n🔍 Analyzing Performance Bottlenecks...")
        
        bottlenecks = {
            'slowest_operations': [],
            'high_cpu_operations': [],
            'high_memory_operations': [],
            'failed_operations': [],
            'recommendations': []
        }
        
        # Sort by duration to find slowest operations
        sorted_results = sorted(self.results, key=lambda x: x['time_taken_s'], reverse=True)
        bottlenecks['slowest_operations'] = sorted_results[:3]
        
        # Find high CPU usage operations (>50%)
        high_cpu = [r for r in self.results if r['cpu_avg_%'] > 50]
        bottlenecks['high_cpu_operations'] = high_cpu
        
        # Find high memory usage operations (>500MB)
        high_memory = [r for r in self.results if r['memory_avg_mb'] > 500]
        bottlenecks['high_memory_operations'] = high_memory
        
        # Find failed operations
        failed = [r for r in self.results if 'FAILED' in r['notes'] or 'TIMEOUT' in r['notes']]
        bottlenecks['failed_operations'] = failed
        
        # Generate recommendations
        recommendations = []
        
        if any(r['time_taken_s'] > 10 for r in self.results):
            recommendations.append("Consider optimizing operations taking >10 seconds")
        
        if high_cpu:
            recommendations.append("High CPU usage detected - consider CPU optimization or scaling")
        
        if high_memory:
            recommendations.append("High memory usage detected - consider memory optimization")
        
        if failed:
            recommendations.append("Failed operations detected - check network connectivity and configurations")
        
        # Check AI prediction times
        ai_results = [r for r in self.results if r['component'] == 'AI Prediction']
        if ai_results and mean([r['time_taken_s'] for r in ai_results]) > 5:
            recommendations.append("AI prediction times are high - consider model optimization or GPU acceleration")
        
        # Check IPFS upload times
        ipfs_results = [r for r in self.results if r['component'] == 'IPFS Upload']
        if ipfs_results and mean([r['time_taken_s'] for r in ipfs_results]) > 3:
            recommendations.append("IPFS upload times are high - check network bandwidth or consider IPFS node optimization")
        
        bottlenecks['recommendations'] = recommendations
        
        return bottlenecks
    
    def generate_summary_table(self):
        """Generate a summary table of all test results"""
        print("\n📊 Performance Test Summary")
        print("=" * 100)
        print(f"{'Component':<20} {'Operation':<30} {'Time (s)':<10} {'CPU %':<8} {'Memory MB':<12} {'Notes'}")
        print("-" * 100)
        
        for result in self.results:
            print(f"{result['component']:<20} {result['operation']:<30} "
                  f"{result['time_taken_s']:<10} {result['cpu_avg_%']:<8} "
                  f"{result['memory_avg_mb']:<12} {result['notes']}")
    
    def run_full_test_suite(self):
        """Run the complete performance test suite"""
        print("🧪 Starting BIWMS Performance Testing")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test individual components
        ai_results = self.test_ai_prediction(num_iterations=3)
        ipfs_results = self.test_ipfs_upload(num_iterations=3)
        contract_results = self.test_smart_contract_submission(num_iterations=3)
        api_results = self.test_api_endpoint_performance()
        concurrent_results = self.test_concurrent_operations(num_concurrent=5)
        
        # Analyze bottlenecks
        bottleneck_analysis = self.analyze_bottlenecks()
        
        total_time = time.time() - start_time
        
        # Generate summary
        self.generate_summary_table()
        
        print(f"\n🎯 Performance Analysis Complete ({total_time:.2f}s total)")
        print("\n🚨 Identified Bottlenecks:")
        
        if bottleneck_analysis['slowest_operations']:
            print("Slowest Operations:")
            for op in bottleneck_analysis['slowest_operations'][:3]:
                print(f"  - {op['component']} {op['operation']}: {op['time_taken_s']}s")
        
        if bottleneck_analysis['failed_operations']:
            print("Failed Operations:")
            for op in bottleneck_analysis['failed_operations']:
                print(f"  - {op['component']} {op['operation']}: {op['notes']}")
        
        print("\n💡 Recommendations:")
        for rec in bottleneck_analysis['recommendations']:
            print(f"  - {rec}")
        
        # Save detailed results
        results_file = f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'test_summary': {
                    'total_time': total_time,
                    'timestamp': datetime.now().isoformat(),
                    'system_info': {
                        'cpu_count': psutil.cpu_count(),
                        'memory_total_gb': round(psutil.virtual_memory().total / 1024**3, 2),
                        'python_version': sys.version
                    }
                },
                'results': self.results,
                'bottleneck_analysis': bottleneck_analysis,
                'component_summaries': {
                    'ai_prediction': ai_results,
                    'ipfs_upload': ipfs_results,
                    'smart_contract': contract_results,
                    'api_endpoint': api_results,
                    'concurrent_test': concurrent_results
                }
            }, f, indent=2)
        
        print(f"\n📋 Detailed results saved to: {results_file}")
        
        return {
            'results': self.results,
            'bottlenecks': bottleneck_analysis,
            'total_time': total_time
        }

def main():
    """Main function to run performance tests"""
    print("BIWMS Performance Tester")
    print("==========================================")
    
    # Check if required files exist
    required_files = [
        "app.py",
        "oracle_submit.js",
        "pinata_uploader.py",
        "AI_feeds/predict.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please ensure all system components are present.")
        return
    
    # Initialize tester
    tester = BIWMSTester()
    
    # Run tests
    try:
        results = tester.run_full_test_suite()
        print("\n✅ Performance testing completed successfully!")
        return results
    except KeyboardInterrupt:
        print("\n❌ Testing interrupted by user")
        return None
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main() 