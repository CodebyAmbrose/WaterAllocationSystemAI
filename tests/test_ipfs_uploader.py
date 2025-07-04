#!/usr/bin/env python3
"""
Unit Tests for IPFS Uploader Module

Tests the IPFS upload functionality including:
- File upload to Pinata
- Error handling
- Network failure scenarios
- File validation
"""

import unittest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock, mock_open
import sys
import requests

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pinata_uploader import upload_to_ipfs

class TestIPFSUploader(unittest.TestCase):
    """Test cases for IPFS uploader functions"""
    
    def setUp(self):
        """Set up test files and mock data"""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files of different sizes
        self.small_file = os.path.join(self.test_dir, 'small.json')
        self.medium_file = os.path.join(self.test_dir, 'medium.json')
        self.large_file = os.path.join(self.test_dir, 'large.json')
        
        # Small file (1KB)
        with open(self.small_file, 'w') as f:
            json.dump({"test": "data", "size": "small"}, f)
        
        # Medium file (10KB)
        with open(self.medium_file, 'w') as f:
            data = {"test": "data" * 1000, "size": "medium"}
            json.dump(data, f)
        
        # Large file (100KB)
        with open(self.large_file, 'w') as f:
            data = {"test": "data" * 10000, "size": "large"}
            json.dump(data, f)
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('pinata_uploader.requests.post')
    def test_successful_upload(self, mock_post):
        """Test successful file upload to IPFS"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'IpfsHash': 'QmTestHash123456789abcdef'
        }
        mock_post.return_value = mock_response
        
        # Test upload
        result_hash = upload_to_ipfs(self.small_file)
        
        # Verify result
        self.assertEqual(result_hash, 'QmTestHash123456789abcdef')
        
        # Verify API call was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Check URL
        self.assertEqual(call_args[1]['url'], "https://api.pinata.cloud/pinning/pinFileToIPFS")
        
        # Check headers contain API keys
        headers = call_args[1]['headers']
        self.assertIn('pinata_api_key', headers)
        self.assertIn('pinata_secret_api_key', headers)
        
        # Check files were included
        self.assertIn('files', call_args[1])
        
        # Check metadata was included
        self.assertIn('data', call_args[1])
    
    @patch('pinata_uploader.requests.post')
    def test_upload_different_file_sizes(self, mock_post):
        """Test upload with different file sizes"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        test_files = [self.small_file, self.medium_file, self.large_file]
        expected_hashes = [
            'QmSmallHash123',
            'QmMediumHash456', 
            'QmLargeHash789'
        ]
        
        for i, test_file in enumerate(test_files):
            mock_response.json.return_value = {'IpfsHash': expected_hashes[i]}
            mock_post.return_value = mock_response
            
            result_hash = upload_to_ipfs(test_file)
            self.assertEqual(result_hash, expected_hashes[i])
    
    @patch('pinata_uploader.requests.post')
    def test_upload_failure_response(self, mock_post):
        """Test handling of failed upload response"""
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request: Invalid file format"
        mock_post.return_value = mock_response
        
        # Test upload - should raise exception
        with self.assertRaises(Exception) as context:
            upload_to_ipfs(self.small_file)
        
        # Check error message contains status code and response
        error_message = str(context.exception)
        self.assertIn("400", error_message)
        self.assertIn("Bad Request", error_message)
    
    @patch('pinata_uploader.requests.post')
    def test_network_timeout(self, mock_post):
        """Test handling of network timeout"""
        # Mock network timeout
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        # Test upload - should raise exception
        with self.assertRaises(Exception) as context:
            upload_to_ipfs(self.small_file)
        
        # Check that timeout error is handled
        error_message = str(context.exception)
        self.assertIn("timeout", error_message.lower())
    
    @patch('pinata_uploader.requests.post')
    def test_connection_error(self, mock_post):
        """Test handling of connection error"""
        # Mock connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Failed to connect")
        
        # Test upload - should raise exception
        with self.assertRaises(Exception) as context:
            upload_to_ipfs(self.small_file)
        
        # Check that connection error is handled
        error_message = str(context.exception)
        self.assertIn("connect", error_message.lower())
    
    def test_file_not_found(self):
        """Test handling of missing file"""
        non_existent_file = os.path.join(self.test_dir, 'does_not_exist.json')
        
        # Test upload - should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            upload_to_ipfs(non_existent_file)
    
    @patch('pinata_uploader.PINATA_API_KEY', None)
    @patch('pinata_uploader.PINATA_SECRET_API_KEY', None)
    def test_missing_api_credentials(self):
        """Test handling when API credentials are missing"""
        # With missing credentials, should return dummy hash
        result = upload_to_ipfs(self.small_file)
        
        # Should return dummy hash (44 'a' characters after 'Qm')
        expected_dummy = f"Qm{'a' * 44}"
        self.assertEqual(result, expected_dummy)
    
    @patch('pinata_uploader.requests.post')
    def test_malformed_json_response(self, mock_post):
        """Test handling of malformed JSON response"""
        # Mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Not valid JSON"
        mock_post.return_value = mock_response
        
        # Test upload - should raise exception
        with self.assertRaises(Exception) as context:
            upload_to_ipfs(self.small_file)
        
        # Check that JSON error is handled
        error_message = str(context.exception)
        self.assertTrue(
            "json" in error_message.lower() or "invalid" in error_message.lower()
        )
    
    @patch('pinata_uploader.requests.post')
    def test_missing_hash_in_response(self, mock_post):
        """Test handling when IPFS hash is missing from response"""
        # Mock response without IpfsHash field
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}  # Missing IpfsHash
        mock_post.return_value = mock_response
        
        # Test upload - should raise KeyError
        with self.assertRaises(KeyError):
            upload_to_ipfs(self.small_file)
    
    @patch('pinata_uploader.requests.post')
    def test_metadata_inclusion(self, mock_post):
        """Test that proper metadata is included in upload"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'IpfsHash': 'QmTestHash123'}
        mock_post.return_value = mock_response
        
        # Test upload
        upload_to_ipfs(self.small_file)
        
        # Check that metadata was included
        call_args = mock_post.call_args
        metadata_str = call_args[1]['data']['pinataMetadata']
        metadata = json.loads(metadata_str)
        
        # Verify metadata structure
        self.assertIn('name', metadata)
        self.assertIn('keyvalues', metadata)
        self.assertIn('source', metadata['keyvalues'])
        self.assertIn('timestamp', metadata['keyvalues'])
        
        # Verify values
        self.assertEqual(metadata['name'], 'small.json')
        self.assertEqual(metadata['keyvalues']['source'], 'biwms')
        self.assertIsInstance(metadata['keyvalues']['timestamp'], (int, float))
    
    @patch('pinata_uploader.requests.post')
    def test_file_handle_management(self, mock_post):
        """Test that file handles are properly managed"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'IpfsHash': 'QmTestHash123'}
        mock_post.return_value = mock_response
        
        # Test upload
        upload_to_ipfs(self.small_file)
        
        # File should still be accessible after upload
        self.assertTrue(os.path.exists(self.small_file))
        
        # Should be able to read file content
        with open(self.small_file, 'r') as f:
            content = json.load(f)
            self.assertEqual(content['test'], 'data')
    
    @patch('pinata_uploader.requests.post')
    def test_various_http_status_codes(self, mock_post):
        """Test handling of various HTTP status codes"""
        test_cases = [
            (401, "Unauthorized"),
            (403, "Forbidden"),
            (404, "Not Found"),
            (429, "Too Many Requests"),
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (503, "Service Unavailable")
        ]
        
        for status_code, status_text in test_cases:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_response.text = status_text
            mock_post.return_value = mock_response
            
            # Should raise exception for all non-200 status codes
            with self.assertRaises(Exception) as context:
                upload_to_ipfs(self.small_file)
            
            error_message = str(context.exception)
            self.assertIn(str(status_code), error_message)

class TestIPFSUploaderEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_empty_file_upload(self):
        """Test upload of empty file"""
        empty_file = os.path.join(self.test_dir, 'empty.json')
        with open(empty_file, 'w') as f:
            f.write('')  # Empty file
        
        # Mock successful response
        with patch('pinata_uploader.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'IpfsHash': 'QmEmptyHash123'}
            mock_post.return_value = mock_response
            
            # Should handle empty file
            result = upload_to_ipfs(empty_file)
            self.assertEqual(result, 'QmEmptyHash123')
    
    def test_binary_file_upload(self):
        """Test upload of binary file"""
        binary_file = os.path.join(self.test_dir, 'binary.dat')
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03\xFF' * 1000)  # Binary data
        
        # Mock successful response
        with patch('pinata_uploader.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'IpfsHash': 'QmBinaryHash123'}
            mock_post.return_value = mock_response
            
            # Should handle binary file
            result = upload_to_ipfs(binary_file)
            self.assertEqual(result, 'QmBinaryHash123')
    
    def test_very_long_filename(self):
        """Test upload with very long filename"""
        long_filename = 'a' * 200 + '.json'  # Very long filename
        long_file = os.path.join(self.test_dir, long_filename)
        
        with open(long_file, 'w') as f:
            json.dump({"test": "data"}, f)
        
        # Mock successful response
        with patch('pinata_uploader.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'IpfsHash': 'QmLongNameHash123'}
            mock_post.return_value = mock_response
            
            # Should handle long filename
            result = upload_to_ipfs(long_file)
            self.assertEqual(result, 'QmLongNameHash123')
            
            # Check that filename is included in metadata
            call_args = mock_post.call_args
            metadata_str = call_args[1]['data']['pinataMetadata']
            metadata = json.loads(metadata_str)
            self.assertEqual(metadata['name'], long_filename)
    
    def test_special_characters_in_filename(self):
        """Test upload with special characters in filename"""
        special_file = os.path.join(self.test_dir, 'test@#$%^&*()_+-=[]{}|;:,.<>?.json')
        
        with open(special_file, 'w') as f:
            json.dump({"test": "data"}, f)
        
        # Mock successful response
        with patch('pinata_uploader.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'IpfsHash': 'QmSpecialHash123'}
            mock_post.return_value = mock_response
            
            # Should handle special characters
            result = upload_to_ipfs(special_file)
            self.assertEqual(result, 'QmSpecialHash123')

class TestIPFSUploaderIntegration(unittest.TestCase):
    """Integration tests for IPFS uploader with external dependencies"""
    
    @unittest.skipIf(
        os.getenv('SKIP_INTEGRATION_TESTS', 'true').lower() == 'true',
        "Integration tests skipped - set SKIP_INTEGRATION_TESTS=false to run"
    )
    def test_real_pinata_upload(self):
        """Test actual upload to Pinata (requires real API keys)"""
        # This test requires real Pinata API keys to be set
        # Skip if not available
        api_key = os.getenv('PINATA_API_KEY')
        secret_key = os.getenv('PINATA_SECRET_API_KEY')
        
        if not api_key or not secret_key:
            self.skipTest("Real Pinata API keys not available")
        
        # Create test file
        test_file = 'integration_test.json'
        with open(test_file, 'w') as f:
            json.dump({
                "test": "integration_test",
                "timestamp": str(datetime.now())
            }, f)
        
        try:
            # Attempt real upload
            result_hash = upload_to_ipfs(test_file)
            
            # Verify result format
            self.assertTrue(result_hash.startswith('Qm'))
            self.assertEqual(len(result_hash), 46)  # Standard IPFS hash length
            
        finally:
            # Clean up test file
            if os.path.exists(test_file):
                os.remove(test_file)

if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True) 