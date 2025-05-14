# Water Allocation System

An AI-powered system for predicting and allocating water consumption across different boroughs.

## Overview

This system uses LSTM neural networks to predict water consumption patterns based on historical data. The predictions are used to allocate water resources efficiently and are stored on IPFS for transparency and immutability.

## Features

- AI model trained on historical water consumption data
- FastAPI backend for file uploads and prediction generation
- IPFS integration via Pinata for decentralized storage
- Blockchain oracle integration for on-chain data availability

## Installation

### Prerequisites

- Python 3.8+
- Node.js 14+
- pip
- npm

### Python Dependencies

```bash
pip install -r requirements.txt
```

### Node.js Dependencies

```bash
npm install
```

## Environment Setup

Create a `.env` file in the root directory with the following variables:

```
# Pinata IPFS Credentials
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_API_KEY=your_pinata_secret_key

# Blockchain Oracle Credentials (optional)
ORACLE_PRIVATE_KEY=your_private_key
ORACLE_CONTRACT_ADDRESS=your_contract_address
RPC_URL=your_rpc_url
```

## Running the API

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`.

## API Usage

### Prediction Endpoint

**POST** `/predict`

Upload a CSV file with water consumption data to generate predictions.

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/water_consumption_data.csv"
```

**Response:**

```json
{
  "status": "success",
  "prediction_id": "550e8400-e29b-41d4-a716-446655440000",
  "ipfsHash": "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG",
  "confidence_score": 95.6,
  "timestamp": "20230301_120000",
  "prediction_file": "prediction_20230301_120000.json"
}
```

## Model Details

- Architecture: Bidirectional LSTM
- Features: Time-based, rolling statistics, lag features
- Performance: ~89% R² on test data

## File Structure

```
├── AI_feeds/
│   ├── models/            # Trained models and artifacts
│   ├── outputs/           # Model predictions
│   ├── predict.py         # Prediction logic
│   └── train_lstm_model.py # Model training script
├── app.py                 # FastAPI application
├── pinata_uploader.py     # IPFS upload functionality
├── oracle_submit.js       # Blockchain oracle submission script
├── data_uploads/          # Uploaded data files
├── package.json           # Node.js dependencies
└── requirements.txt       # Python dependencies
```

## License

ISC 