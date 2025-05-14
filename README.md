# Water Allocation System

An AI-powered water allocation system with blockchain verification and IPFS integration.

## Features

- AI-based water allocation predictions
- Blockchain verification using smart contracts
- IPFS integration for prediction metadata storage
- Real-time system efficiency monitoring
- Multi-stakeholder approval system
- Interactive dashboard with analytics

## System Efficiency Metrics

The system tracks three key efficiency metrics:

1. **Resource Utilization Rate (RUR)**
   - Measures how effectively allocated water is being used
   - Formula: (Actual Water Used / Total Water Allocated) × 100%

2. **Distribution Efficiency (DE)**
   - Tracks water delivery success rate and system losses
   - Formula: (Water Delivered / Water Input) × 100%

3. **Allocation Balance Score (ABS)**
   - Indicates how evenly water is distributed across boroughs
   - Formula: 1 - (Standard Deviation / Mean) of borough allocations

## Setup

1. Clone the repository:
   ```bash
   git clone [your-repo-url]
   cd WaterAllocationSystem
   ```

2. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the variables with your configuration

4. Run the development server:
   ```bash
   npm run serve
   ```

## Technology Stack

- Frontend: Vue.js 3
- Blockchain: BSC (Binance Smart Chain)
- Storage: IPFS
- UI: Tailwind CSS
- State Management: Vuex
- Smart Contracts: Solidity

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Vue components
│   ├── services/        # API and blockchain services
│   ├── assets/         # Static assets
│   └── App.vue         # Root component
├── public/             # Public static files
└── package.json        # Project dependencies
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 