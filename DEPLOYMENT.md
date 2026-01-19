# Deployment Guide - Cloud Hosting

## ✅ System Status: COMPLETE & READY TO DEPLOY

Your quantitative trading bot is fully built and tested. All 6 phases are complete:

- ✅ **Phase 1**: Data Layer (Alpaca API integration)
- ✅ **Phase 2**: Technical Analysis (RSI, MA, MACD, Bollinger Bands)
- ✅ **Phase 3**: Sentiment Analysis (NewsAPI + VADER)
- ✅ **Phase 4**: Risk Management (Position sizing, stop loss)
- ✅ **Phase 5**: Paper Trading (Order execution)
- ✅ **Phase 6**: Backtesting Engine

---

## 🚀 Quick Deploy to GitHub Actions (FREE 24/7)

### Step 1: Create GitHub Repository

```bash
# In PowerShell
cd "C:\Users\sorox\OneDrive\Desktop\Stock trading app"

# Create new repository on GitHub.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/trading-bot.git
git branch -M main
git push -u origin main
```

### Step 2: Configure GitHub Secrets

1. Go to your repository on GitHub.com
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

| Secret Name | Value |
|------------|-------|
| `ALPACA_PAPER_KEY_ID` | Your Alpaca paper trading key ID |
| `ALPACA_PAPER_SECRET` | Your Alpaca paper trading secret |
| `NEWS_API_KEY` | (Optional) Your NewsAPI key for sentiment |

### Step 3: Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. Click **"I understand my workflows, go ahead and enable them"**
3. The bot will now run automatically **Monday-Friday at 4:30 PM ET** (after market close)

### Step 4: Monitor Execution

- Check **Actions** tab to see workflow runs
- Download **artifacts** to view execution logs
- Each run shows account status, signals, and trade opportunities

---

## 📊 Local Development & Testing

### Running Locally

```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Run daily scan
python src/main.py

# Run comprehensive demo
python demo.py

# Test individual components
python src/data/alpaca_client.py
python src/analysis/technical_indicators.py
python src/risk/risk_manager.py
python src/backtesting/backtester.py
```

### Manual Trading

```powershell
# Test paper trading (interactive)
python src/trading/paper_trader.py

# Follow prompts to place test trades
```

---

## 🔧 Configuration

### Edit Strategy Parameters

Edit `config/settings.yaml`:

```yaml
risk:
  max_position_size: 0.10    # 10% of portfolio per position
  max_daily_loss: 0.03       # 3% max daily loss
  stop_loss_pct: 0.05        # 5% stop loss
  max_positions: 5           # Max concurrent positions

technical:
  rsi:
    period: 14
    oversold: 30
    overbought: 70
  moving_averages:
    short_period: 20
    long_period: 50

sentiment:
  enabled: true              # Enable/disable sentiment
  weight: 0.3                # Sentiment influence (0-1)
```

### Edit Watchlist

Edit `src/main.py` line 66:

```python
watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'AMD']
```

---

## 🔄 Alternative Cloud Options

### Option 1: Oracle Cloud (FREE 24/7 Always-On)

**Pros**: True 24/7 operation, generous free tier
**Cons**: More setup complexity

1. Sign up at https://cloud.oracle.com/free
2. Create Ubuntu VM (Always Free tier)
3. SSH into server
4. Clone repository and install dependencies
5. Set up cron job:
   ```bash
   crontab -e
   # Add: 30 21 * * 1-5 cd /path/to/trading-bot && /path/to/venv/bin/python src/main.py
   ```

### Option 2: PythonAnywhere (FREE 1 task/day)

1. Sign up at https://www.pythonanywhere.com
2. Upload code
3. Create scheduled task (daily at 4:30 PM ET)

### Option 3: Render.com (Background Worker)

1. Sign up at https://render.com
2. Connect GitHub repository
3. Deploy as background worker
4. Add cron schedule in render.yaml

---

## 📈 Performance Monitoring

### Check Account Performance

```python
from src.data.alpaca_client import AlpacaClient

client = AlpacaClient()
account = client.get_account_info()
print(f"Portfolio Value: ${account['portfolio_value']:,.2f}")
print(f"Today's P/L: ${account['equity'] - account['portfolio_value']:+,.2f}")

positions = client.get_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['unrealized_plpc']*100:+.2f}%")
```

### Run Backtest

```python
from src.backtesting.backtester import Backtester
from src.data.alpaca_client import AlpacaClient

# Get historical data
client = AlpacaClient()
data = client.get_historical_data('AAPL', days_back=365)

# Run backtest
backtester = Backtester(initial_capital=100000)
results = backtester.run_backtest('AAPL', data)
backtester.print_results(results)
```

---

## 🎯 Next Steps for Live Trading

### Before Going Live:

1. **Run paper trading for 30-60 days** to validate strategy
2. **Monitor performance metrics**:
   - Win rate should be >50%
   - Max drawdown should be <10%
   - Risk/reward ratio should be >1:1.5
3. **Test different market conditions** (bull, bear, choppy)
4. **Adjust parameters** based on backtest results
5. **Review all trades manually** before automating

### When Ready for Live Trading:

1. Get Alpaca live trading API keys
2. Update `.env` with live credentials
3. Change `TRADING_MODE=live` in `.env`
4. **Start with small capital** (10-20% of intended amount)
5. **Monitor closely** for first week
6. **Gradually increase** capital as confidence grows

---

## ⚠️ Important Safety Notes

- **Paper trading first**: Never skip this step
- **Daily loss limits**: System enforces 3% max daily loss
- **Position sizing**: Limited to 10% per position
- **Stop losses**: Automatic 5% stop loss on all positions
- **Manual override**: You can always manually close positions through Alpaca dashboard
- **Market hours**: Bot only trades during market hours
- **News events**: Be cautious around earnings, Fed announcements

---

## 🛠️ Troubleshooting

### Historical Data Errors

**Issue**: "subscription does not permit querying recent SIP data"
**Solution**: This is expected with free Alpaca tier. System uses latest prices instead.

### Sentiment Analysis Disabled

**Issue**: NewsAPI errors
**Solution**: Add valid `NEWS_API_KEY` to `.env` file (get free at https://newsapi.org)

### GitHub Actions Not Running

**Issue**: Workflow not executing
**Solution**: 
- Check Actions tab is enabled
- Verify cron schedule in `.github/workflows/trading-bot.yml`
- Ensure secrets are configured correctly

---

## 📞 Support & Resources

- **Alpaca API Docs**: https://alpaca.markets/docs/
- **Paper Trading Dashboard**: https://app.alpaca.markets/paper/dashboard
- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Your Code Repository**: All documentation is in the README.md

---

## 🎓 Learning & Optimization

### Strategy Improvement Ideas:

1. **Add more indicators**: Stochastic, ADX, Volume analysis
2. **Machine learning**: Train model on historical patterns
3. **Multiple timeframes**: Analyze both daily and hourly data
4. **Sector rotation**: Focus on strongest sectors
5. **Correlation analysis**: Avoid correlated positions
6. **Options integration**: Hedge with protective puts
7. **Portfolio optimization**: Use Modern Portfolio Theory

### Recommended Reading:

- "Quantitative Trading" by Ernest Chan
- "Algorithmic Trading" by Jeffrey Bacidore
- Alpaca API documentation
- QuantConnect tutorials

---

**Your bot is ready! Start with `python src/main.py` to see it in action.**
