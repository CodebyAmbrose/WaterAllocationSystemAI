import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Pinata API keys from environment variables
PINATA_API_KEY = os.getenv('PINATA_API_KEY') or "c997e201e99cf5899683"
PINATA_SECRET_API_KEY = os.getenv('PINATA_SECRET_API_KEY') or "cd6e6eb6fec9d07601589ce2837bda1afa6c306d368c0e3ed98a72a155c692a6"

# If API keys are not set, provide instructions
if not PINATA_API_KEY or not PINATA_SECRET_API_KEY:
    print("Warning: Pinata API keys not found in environment variables.")
    print("Please create a .env file with the following variables:")
    print("PINATA_API_KEY=your_api_key")
    print("PINATA_SECRET_API_KEY=your_secret_api_key")

def upload_to_ipfs(file_path):
    """
    Upload a file to IPFS using Pinata and return the IPFS hash
    
    Args:
        file_path (str): Path to the file to upload
        
    Returns:
        str: IPFS hash (CID) of the uploaded file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check if we have Pinata credentials
    if not PINATA_API_KEY or not PINATA_SECRET_API_KEY:
        # For testing/demo, return a dummy hash if no credentials
        print("Warning: Using dummy IPFS hash since Pinata credentials are missing")
        return f"Qm{''.join(['a' for _ in range(44)])}"
    
    try:
        # Prepare the file for upload
        file_name = os.path.basename(file_path)
        
        # Pinata API endpoint for pinning files
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        
        # Prepare headers with authentication
        headers = {
            'pinata_api_key': PINATA_API_KEY,
            'pinata_secret_api_key': PINATA_SECRET_API_KEY
        }
        
        # Prepare the files payload with metadata
        payload = {
            'pinataMetadata': json.dumps({
                'name': file_name,
                'keyvalues': {
                    'source': 'biwms',
                    'timestamp': os.path.getmtime(file_path)
                }
            })
        }
        
        # Open file for upload
        with open(file_path, 'rb') as file_data:
            files = {
                'file': (file_name, file_data)
            }
            
            # Make the request to Pinata
            response = requests.post(
                url,
                headers=headers,
                files=files,
                data=payload
            )
            
            # Check if upload was successful
            if response.status_code == 200:
                # Extract and return the IPFS hash
                ipfs_hash = response.json()['IpfsHash']
                print(f"Successfully pinned file to IPFS with hash: {ipfs_hash}")
                return ipfs_hash
            else:
                # Handle error
                error_msg = f"Failed to upload to IPFS. Status: {response.status_code}, Response: {response.text}"
                print(error_msg)
                raise Exception(error_msg)
    
    except Exception as e:
        print(f"Error uploading to IPFS: {str(e)}")
        raise

# For testing the module directly
if __name__ == "__main__":
    # Example usage
    test_file = "test_file.json"
    
    # Create a test file if it doesn't exist
    if not os.path.exists(test_file):
        with open(test_file, 'w') as f:
            json.dump({"test": "data"}, f)
    
    try:
        ipfs_hash = upload_to_ipfs(test_file)
        print(f"IPFS Hash: {ipfs_hash}")
    except Exception as e:
        print(f"Error: {str(e)}") 