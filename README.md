# Crypto Buy/Sell ML Platform

## Project Overview
A machine learning-powered cryptocurrency trading platform that automates the process of data ingestion, feature engineering, and predictive modeling. The system generates buy/sell signals and forecasts future crypto values using historical data, presenting the insights through an intuitive React-based frontend.

## Features
- **Automated Data Pipeline**: Fetches historical/real-time crypto data and engineers predictive features.
- **Machine Learning Models**: 
  - Buy/Sell Classification Model for trade signals.
  - Regression Model for predicting future asset values.
- **Interactive Dashboard**: Modern UI with charts (Lightweight Charts, Recharts) to visualize market trends and portfolio performance.
- **Dockerized Setup**: Easy deployment using Docker Compose for both backend and frontend services.
- **Local Database**: Stores trading history and state using SQLite.

## Tech Stack
**Frontend:**
- React 19 (Vite)
- Tailwind CSS
- Lightweight Charts & Recharts
- Axios
- React Router

**Backend & ML:**
- Python
- Scikit-Learn (ML Models)
- SQLite (`trading.db`)
- Docker & Docker Compose

## Installation Steps

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose installed.
- (Optional) Python 3.9+ if running locally without Docker.
- (Optional) Node.js 18+ for running frontend manually.

### Using Docker (Recommended)
1. Clone the repository:
   ```bash
   git clone https://github.com/ChiragPednekar/crypto-buy-sell-ml.git
   cd "crypto-buy-sell-ml"
   ```
2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
3. Access the application:
   - Frontend Dashboard: `http://localhost:5173`
   - Backend API: `http://localhost:8000`

### Running Locally (Without Docker)
**Backend:**
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Run the ML pipeline (downloads data and trains models):
   ```bash
   python main.py
   ```
3. Start the API server:
   ```bash
   # Adjust based on your API framework setup (e.g. FastAPI/Flask)
   # uvicorn src.api.app:app --reload --port 8000
   ```

**Frontend:**
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```

## Screenshots
*(Add your screenshots here)*
- `![Dashboard](screenshot_link_here)`
- `![Trade View](screenshot_link_here)`
- `![Portfolio](screenshot_link_here)`

## Folder Structure
```text
crypto-buy-sell-ml/
├── frontend/                 # React UI application (Vite + Tailwind)
│   ├── src/                  # React components, pages, and styles
│   └── package.json          # Frontend dependencies
├── src/                      # Python backend and ML source code
│   ├── api/                  # API endpoints and schemas
│   ├── buy_sell/             # Buy/Sell classification model scripts
│   ├── future_value/         # Future value regression model scripts
│   ├── pipeline/             # Training and inference pipelines
│   └── data_loader.py        # Data ingestion script
├── models/                   # Pickled ML models (.pkl)
├── data/                     # Raw and processed datasets
├── trading.db                # SQLite database for trade history
├── main.py                   # Main pipeline execution script
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker composition file
└── Dockerfile.*              # Dockerfiles for frontend and backend
```

## Future Improvements
- [ ] Integration with real-time crypto exchanges (e.g., Binance, Coinbase) for live trading.
- [ ] Advanced Deep Learning models (LSTM/Transformers) for better price action prediction.
- [ ] User Authentication and multi-user portfolio tracking.
- [ ] Deployment to cloud providers (AWS/GCP/Vercel) with CI/CD pipelines.
- [ ] Email/SMS alerts for high-confidence trading signals.