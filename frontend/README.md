# Water Allocation System Frontend

Modern Vue.js frontend for the Water Allocation System that integrates AI prediction with blockchain technology.

## Features

- User-friendly interface for uploading water consumption data
- Visualization of AI-predicted water allocations across boroughs using charts
- Integration with IPFS for decentralized storage
- Blockchain verification through BSC Testnet
- Real-time display of prediction confidence scores and transaction details

## Tech Stack

- Vue 3 with Composition API
- Tailwind CSS for styling
- Chart.js and vue-chartjs for data visualization
- Axios for API communication

## Project Setup

```sh
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Configuration

The frontend connects to your FastAPI backend running at `http://localhost:8000`. If your backend is running on a different host or port, update the `apiBaseUrl` in `src/components/FileUpload.vue`.

## Integration Points

- **Backend API**: Submits files for prediction and receives prediction results
- **IPFS via Pinata**: Stores prediction data permanently
- **BSC Testnet**: Verifies and manages the multi-signature approval process

## Backend Requirements

Make sure your backend FastAPI server is running with:

```sh
# From the project root directory
python app.py
```

## Blockchain Contract

The frontend interfaces with the AIPredictionMultisig smart contract deployed at:
`0x6b282341D709b3c6f6cfdF366Be2d326dDA39Ce4` (BSC Testnet)
