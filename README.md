# Quantitative Stock Trading Bot

A cloud-first, math-driven stock trading system optimized for paper trading and GitHub Actions deployment.

## Features

- **Cloud-Ready**: Designed to run on GitHub Actions (free, scheduled execution)
- **Paper Trading**: Test strategies risk-free using Alpaca's paper trading API
- **Three-Layer Analysis**:
  - Technical indicators (RSI, Moving Averages, Bollinger Bands)
  - News sentiment analysis (VADER, NewsAPI)
  - Risk management and position sizing
- **Automated Execution**: Daily runs after market close via GitHub Actions
- **Alerts & Logging**: Track decisions and performance

## Quick Start (Local Development)

1. **Clone and setup environment**:
   ```bash
   git clone <your-repo-url>
   cd "Stock trading app"
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Configure API keys**:
   - Copy `.env.example` to `.env`
   - Get Alpaca paper trading keys from https://alpaca.markets
   - Get NewsAPI key from https://newsapi.org (free tier)
   - Fill in your keys in `.env`

3. **Run locally**:
   ```bash
   python src/main.py
   ```

## Cloud Deployment (GitHub Actions)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial trading bot setup"
   git remote add origin <your-github-repo>
   git push -u origin main
   ```

2. **Configure GitHub Secrets**:
   - Go to repository Settings → Secrets and variables → Actions
   - Add secrets:
     - `ALPACA_PAPER_KEY_ID`
     - `ALPACA_PAPER_SECRET`
     - `NEWS_API_KEY`

3. **The bot will run automatically**:
   - Monday-Friday at 4:30 PM ET (after market close)
   - Check Actions tab for logs
   - Download artifacts to review execution logs

## Project Structure

```
Stock trading app/
├── src/
│   └── main.py              # Entry point
├── config/
│   └── settings.yaml        # Strategy parameters
├── data/                    # Historical data (local only)
├── logs/                    # Execution logs
├── tests/                   # Unit tests
├── .github/
│   └── workflows/
│       └── trading-bot.yml  # GitHub Actions config
├── .env                     # API keys (DO NOT COMMIT)
├── .env.example             # Template for API keys
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Safety Notice

⚠️ **PAPER TRADING FIRST**: This system is configured for paper trading by default. Do NOT use real money until you've thoroughly tested and validated the strategy over several weeks/months.

## Next Steps

1. Complete Phase 1: Data Layer (Alpaca API integration)
2. Implement Phase 2: Technical Analysis
3. Build Phase 3: Sentiment Analysis
4. Add Phase 4: Backtesting
5. Deploy to GitHub Actions for automated operation
