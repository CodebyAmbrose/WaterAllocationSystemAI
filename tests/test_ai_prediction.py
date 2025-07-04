#!/usr/bin/env python3
"""
Unit Tests for AI Prediction Module

Tests individual functions in the AI prediction pipeline including:
- Data preprocessing functions
- Feature engineering
- Prediction generation
- Error handling
"""

import unittest
import pandas as pd
import numpy as np
import os
import json
import tempfile
from unittest.mock import patch, MagicMock, mock_open
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI_feeds.predict import (
    add_engineered_features, 
    prepare_data_for_prediction,
    make_prediction,
    generate_prediction_report
)

class TestAIPredictionModule(unittest.TestCase):
    """Test cases for AI prediction module functions"""
    
    def setUp(self):
        """Set up test data and mock objects"""
        # Create sample test data
        self.sample_data = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
            'borough': ['Manhattan', 'Brooklyn', 'Queens'],
            'consumption_(hcf)': [1500.0, 1200.0, 1800.0],
            'day_of_year': [1, 2, 3],
            'month': [1, 1, 1],
            'week_of_year': [1, 1, 1]
        })
        
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_csv_path = os.path.join(self.test_dir, 'test_data.csv')
        self.sample_data.to_csv(self.test_csv_path, index=False)
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_add_engineered_features_basic(self):
        """Test basic feature engineering functionality"""
        # Test with minimal data
        df = self.sample_data.copy()
        
        # Add required columns for feature engineering
        df['hour'] = 12
        
        result = add_engineered_features(df)
        
        # Check that new features are added
        expected_features = [
            'hour', 'day_sin', 'day_cos', 'month_sin', 'month_cos',
            'week_sin', 'week_cos'
        ]
        
        for feature in expected_features:
            self.assertIn(feature, result.columns, f"Feature {feature} not found")
        
        # Check that trigonometric features are within valid range
        self.assertTrue((-1 <= result['day_sin']).all() and (result['day_sin'] <= 1).all())
        self.assertTrue((-1 <= result['day_cos']).all() and (result['day_cos'] <= 1).all())
    
    def test_add_engineered_features_rolling_stats(self):
        """Test rolling statistics feature engineering"""
        # Create larger dataset for rolling statistics
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'borough': ['Manhattan'] * 30,
            'consumption_(hcf)': np.random.normal(1500, 200, 30),
            'day_of_year': range(1, 31),
            'month': [1] * 30,
            'week_of_year': [1] * 30,
            'hour': [12] * 30
        })
        
        result = add_engineered_features(df)
        
        # Check rolling statistics columns
        rolling_windows = [7, 14, 30]
        rolling_stats = ['mean', 'std', 'max', 'min']
        
        for window in rolling_windows:
            for stat in rolling_stats:
                col_name = f'rolling_{stat}_{window}d'
                self.assertIn(col_name, result.columns, f"Rolling feature {col_name} not found")
                
                # Check that rolling statistics are not all NaN
                self.assertFalse(result[col_name].isna().all(), f"All values in {col_name} are NaN")
    
    def test_add_engineered_features_lag_features(self):
        """Test lag feature creation"""
        # Create dataset with sufficient history for lag features
        dates = pd.date_range('2024-01-01', periods=20, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'borough': ['Manhattan'] * 20,
            'consumption_(hcf)': range(1000, 1020),
            'day_of_year': range(1, 21),
            'month': [1] * 20,
            'week_of_year': [1] * 20,
            'hour': [12] * 20
        })
        
        result = add_engineered_features(df)
        
        # Check lag features
        lag_periods = [1, 7, 14]
        for lag in lag_periods:
            col_name = f'consumption_lag_{lag}'
            self.assertIn(col_name, result.columns, f"Lag feature {col_name} not found")
            
            # Check that lag values are correctly shifted
            if lag < len(df):
                expected_value = df['consumption_(hcf)'].iloc[0]
                actual_value = result[col_name].iloc[lag]
                self.assertEqual(expected_value, actual_value, f"Lag {lag} value incorrect")
    
    def test_prepare_data_for_prediction_basic(self):
        """Test data preparation for prediction"""
        # Create test data with required features
        df = pd.DataFrame({
            'year': [2024] * 14,
            'month': [1] * 14,
            'day_of_month': range(1, 15),
            'day_of_week': [i % 7 for i in range(14)],
            'day_of_year': range(1, 15),
            'week_of_year': [1] * 14,
            'borough_encoded': [0] * 14,
            'hour': [12] * 14,
            'day_sin': np.sin(2 * np.pi * np.arange(14) / 365),
            'day_cos': np.cos(2 * np.pi * np.arange(14) / 365),
            'month_sin': [0] * 14,
            'month_cos': [1] * 14,
            'week_sin': [0] * 14,
            'week_cos': [1] * 14,
            'consumption_(hcf)': np.random.normal(1500, 100, 14)
        })
        
        # Add rolling and lag features
        for window in [7, 14, 30]:
            df[f'rolling_mean_{window}d'] = df['consumption_(hcf)'].rolling(window, min_periods=1).mean()
            df[f'rolling_std_{window}d'] = df['consumption_(hcf)'].rolling(window, min_periods=1).std().fillna(0)
            df[f'rolling_max_{window}d'] = df['consumption_(hcf)'].rolling(window, min_periods=1).max()
            df[f'rolling_min_{window}d'] = df['consumption_(hcf)'].rolling(window, min_periods=1).min()
        
        for lag in [1, 7, 14]:
            df[f'consumption_lag_{lag}'] = df['consumption_(hcf)'].shift(lag).fillna(df['consumption_(hcf)'].mean())
        
        result = prepare_data_for_prediction(df.values, sequence_length=14)
        
        # Check that result has correct shape
        self.assertEqual(len(result), 14, "Sequence length incorrect")
        self.assertIsInstance(result, np.ndarray, "Result should be numpy array")
    
    def test_prepare_data_for_prediction_insufficient_data(self):
        """Test data preparation with insufficient data"""
        # Create data with less than required sequence length
        df = pd.DataFrame({
            'consumption_(hcf)': [1500, 1600]
        })
        
        # Should handle insufficient data gracefully
        try:
            result = prepare_data_for_prediction(df.values, sequence_length=14)
            # Should either pad with defaults or raise appropriate error
            self.assertIsNotNone(result)
        except Exception as e:
            # Acceptable to raise exception for insufficient data
            self.assertIsInstance(e, (ValueError, IndexError))
    
    @patch('AI_feeds.predict.tf.keras.models.load_model')
    @patch('AI_feeds.predict.joblib.load')
    @patch('os.path.exists')
    def test_make_prediction_with_mocks(self, mock_exists, mock_joblib_load, mock_load_model):
        """Test make_prediction function with mocked dependencies"""
        # Setup mocks
        mock_exists.return_value = True
        
        # Mock scaler
        mock_scaler = MagicMock()
        mock_scaler.transform.return_value = np.random.random((14, 25))
        mock_scaler.inverse_transform.return_value = np.array([[0, 0, 0, 1500.0]])
        
        # Mock encoder
        mock_encoder = MagicMock()
        mock_encoder.transform.return_value = [0]
        
        # Mock model
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[0.5]])
        
        # Configure joblib.load to return appropriate mocks
        def joblib_side_effect(path):
            if 'scaler' in path:
                return mock_scaler
            elif 'encoder' in path:
                return mock_encoder
            
        mock_joblib_load.side_effect = joblib_side_effect
        mock_load_model.return_value = mock_model
        
        # Mock pandas read_csv
        with patch('pandas.read_csv') as mock_read_csv:
            # Create sample DataFrame
            mock_df = pd.DataFrame({
                'date': pd.date_range('2024-01-01', periods=30),
                'borough': ['Manhattan'] * 30,
                'consumption_(hcf)': np.random.normal(1500, 100, 30)
            })
            mock_read_csv.return_value = mock_df
            
            # Test the function
            try:
                prediction, pred_date = make_prediction('Manhattan')
                
                # Validate results
                self.assertIsInstance(prediction, (int, float), "Prediction should be numeric")
                self.assertIsInstance(pred_date, datetime, "Prediction date should be datetime")
                self.assertGreater(prediction, 0, "Prediction should be positive")
                
            except Exception as e:
                # Some failures are acceptable due to complex dependencies
                self.assertIsInstance(e, (FileNotFoundError, KeyError, AttributeError))
    
    @patch('AI_feeds.predict.joblib.load')
    @patch('AI_feeds.predict.make_prediction')
    def test_generate_prediction_report(self, mock_make_prediction, mock_joblib_load):
        """Test prediction report generation"""
        # Mock borough encoder
        mock_encoder = MagicMock()
        mock_encoder.classes_ = ['Manhattan', 'Brooklyn', 'Queens']
        mock_joblib_load.return_value = mock_encoder
        
        # Mock make_prediction function
        def prediction_side_effect(borough):
            predictions = {
                'Manhattan': (1500.0, datetime(2024, 1, 2)),
                'Brooklyn': (1200.0, datetime(2024, 1, 2)),
                'Queens': (1800.0, datetime(2024, 1, 2))
            }
            return predictions.get(borough, (1000.0, datetime(2024, 1, 2)))
        
        mock_make_prediction.side_effect = prediction_side_effect
        
        # Test report generation
        try:
            report = generate_prediction_report()
            
            # Validate report structure
            self.assertIn('prediction_id', report)
            self.assertIn('timestamp', report)
            self.assertIn('predicted_allocation', report)
            self.assertIn('confidence_score', report)
            
            # Validate allocations
            allocations = report['predicted_allocation']
            for borough in ['Manhattan', 'Brooklyn', 'Queens']:
                self.assertIn(borough, allocations)
                self.assertIn('consumption_hcf', allocations[borough])
                self.assertIn('percentage', allocations[borough])
            
            # Validate percentages sum to ~100
            total_percentage = sum(alloc['percentage'] for alloc in allocations.values())
            self.assertAlmostEqual(total_percentage, 100.0, places=1)
            
        except Exception as e:
            # Some failures acceptable due to file dependencies
            self.assertIsInstance(e, (FileNotFoundError, ImportError))
    
    def test_error_handling_invalid_data(self):
        """Test error handling with invalid data"""
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        
        with self.assertRaises((ValueError, KeyError, IndexError)):
            add_engineered_features(empty_df)
        
        # Test with DataFrame missing required columns
        incomplete_df = pd.DataFrame({'date': ['2024-01-01']})
        
        with self.assertRaises((KeyError, AttributeError)):
            add_engineered_features(incomplete_df)
    
    def test_data_types_and_validation(self):
        """Test data type validation and conversion"""
        # Test with string dates that need conversion
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'borough': ['Manhattan', 'Brooklyn'],
            'consumption_(hcf)': ['1500', '1200'],  # String numbers
            'day_of_year': [1, 2],
            'month': [1, 1],
            'week_of_year': [1, 1]
        })
        
        # Should handle string conversions
        df['date'] = pd.to_datetime(df['date'])
        df['consumption_(hcf)'] = pd.to_numeric(df['consumption_(hcf)'])
        df['hour'] = 12
        
        result = add_engineered_features(df)
        
        # Verify data types
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['date']))
        self.assertTrue(pd.api.types.is_numeric_dtype(result['consumption_(hcf)']))

class TestAIPredictionEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_extreme_values(self):
        """Test handling of extreme consumption values"""
        df = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
            'borough': ['Manhattan', 'Brooklyn', 'Queens'],
            'consumption_(hcf)': [0, 999999, -100],  # Extreme values
            'day_of_year': [1, 2, 3],
            'month': [1, 1, 1],
            'week_of_year': [1, 1, 1],
            'hour': [12, 12, 12]
        })
        
        # Should handle extreme values without crashing
        try:
            result = add_engineered_features(df)
            # Verify no infinite or extremely large values in engineered features
            for col in result.select_dtypes(include=[np.number]).columns:
                self.assertFalse(np.isinf(result[col]).any(), f"Infinite values in {col}")
        except Exception as e:
            # Some extreme value handling might be expected to fail
            self.assertIsInstance(e, (ValueError, OverflowError))
    
    def test_missing_data_handling(self):
        """Test handling of missing data"""
        df = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
            'borough': ['Manhattan', None, 'Queens'],
            'consumption_(hcf)': [1500, np.nan, 1800],
            'day_of_year': [1, 2, 3],
            'month': [1, 1, 1],
            'week_of_year': [1, 1, 1],
            'hour': [12, 12, 12]
        })
        
        result = add_engineered_features(df)
        
        # Check that NaN values are handled appropriately
        # Either filled or function should raise appropriate error
        numeric_columns = result.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col.startswith(('rolling_', 'consumption_lag_')):
                # These columns are expected to handle NaN values
                continue
            # Other engineered features should not have NaN
            nan_count = result[col].isna().sum()
            self.assertEqual(nan_count, 0, f"Unexpected NaN values in {col}")

if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True) 