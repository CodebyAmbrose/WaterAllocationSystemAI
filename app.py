from fastapi import FastAPI, File, UploadFile, HTTPException
import uuid
import os
import json
import subprocess
from datetime import datetime
import shutil
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import functions from other modules
from AI_feeds.predict import run_prediction
from pinata_uploader import upload_to_ipfs

# Create FastAPI app
app = FastAPI(title="Water Allocation System API", 
              description="API for water consumption prediction and allocation",
              version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs("data_uploads", exist_ok=True)
os.makedirs("AI_feeds/outputs", exist_ok=True)

def validate_file_extension(filename: str) -> bool:
    """Validate that the file has an allowed extension"""
    allowed_extensions = [".csv", ".json"]
    return any(filename.endswith(ext) for ext in allowed_extensions)

@app.post("/predict", response_class=JSONResponse)
async def predict(file: UploadFile = File(...)):
    """
    Upload a file with water consumption data, run predictions, 
    upload results to IPFS, and submit to the AIPredictionMultisig contract.
    
    Args:
        file: CSV or JSON file with water consumption data
    
    Returns:
        JSON response with prediction details
    """
    # Generate a unique prediction ID
    prediction_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(status_code=400, detail="Only CSV or JSON files are allowed")
    
    # Create unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{timestamp}_{prediction_id}{file_extension}"
    file_path = os.path.join("data_uploads", unique_filename)
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Run prediction on the uploaded file
        prediction_file_path = run_prediction(file_path)
        
        # Load the prediction JSON file to extract confidence score
        with open(prediction_file_path, "r") as f:
            prediction_data = json.load(f)
            confidence_score = prediction_data.get("confidence_score", 0)
            
        # Convert confidence score to integer between 0-100
        # AIPredictionMultisig contract expects uint8 (0-255)
        confidence_int = int(round(confidence_score))
        # Ensure it's within valid range
        confidence_int = max(0, min(100, confidence_int))
        
        # Upload prediction to IPFS
        ipfs_hash = upload_to_ipfs(prediction_file_path)
        
        # Submit to AIPredictionMultisig contract
        oracle_result = subprocess.run(
            ["node", "oracle_submit.js", ipfs_hash, str(confidence_int)],
            capture_output=True,
            text=True
        )
        
        tx_result = None
        if oracle_result.returncode != 0:
            # Log the error but don't fail the request
            print(f"Contract submission warning: {oracle_result.stderr}")
        else:
            # Try to extract transaction ID or prediction ID from output
            output_lines = oracle_result.stdout.split('\n')
            for line in output_lines:
                if 'Transaction submitted:' in line:
                    tx_result = line.split('Transaction submitted:')[1].strip()
                elif 'Prediction submitted with ID:' in line:
                    prediction_blockchain_id = line.split('Prediction submitted with ID:')[1].strip()
        
        # Return successful response
        response = {
            "status": "success",
            "prediction_id": prediction_id,
            "ipfsHash": ipfs_hash,
            "confidence_score": confidence_int,
            "timestamp": timestamp,
            "prediction_file": os.path.basename(prediction_file_path),
            "oracle_address": os.environ.get("ORACLE_ADDRESS", "Not configured")
        }
        
        # Add transaction info if available
        if tx_result:
            response["transaction_hash"] = tx_result
            
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint to verify the API is running"""
    contract_address = os.environ.get("SMART_CONTRACT_ADDRESS", "Not configured")
    oracle_address = os.environ.get("ORACLE_ADDRESS", "Not configured")
    return {
        "message": "Water Allocation System API is running.",
        "smart_contract": contract_address,
        "oracle_address": oracle_address,
        "network": "BSC Testnet (Chain ID: 97)"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 