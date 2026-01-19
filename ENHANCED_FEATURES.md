# Enhanced Features Guide

Your trading bot now has three powerful new capabilities! Here's what changed and how to use them.

---

## 🆕 New Features

### 1. **Universe Scanning** - Scan ALL Stocks
Instead of just 8 hardcoded stocks, the bot can now scan hundreds of tradable stocks automatically.

### 2. **Position-Aware Signals** - Smart Recommendations
The bot now checks what you own before making recommendations:
- **SELL signals**: Only shown for stocks you actually own
- **HOLD signals**: Only shown for your current positions
- **BUY signals**: Always shown (if you have buying power)

### 3. **Automatic Trade Execution** - Hands-Free Trading
The bot can now automatically place trades based on its analysis (with safety controls).

---

## 📊 Feature 1: Universe Scanning

### What It Does:
- Fetches ALL tradable stocks from Alpaca (thousands of them)
- Filters to major exchanges (NYSE, NASDAQ, ARCA)
- Scans up to 50 most liquid stocks (configurable)
- Always includes your current positions

### How to Enable:
Edit your `.env` file:
```env
SCAN_UNIVERSE=true
MAX_STOCKS_TO_SCAN=50  # Adjust this number
```

### When to Use:
- **Use universe scanning** when you want to discover new opportunities beyond the usual suspects
- **Use default watchlist** for faster daily scans (scans in ~10 seconds vs ~5 minutes)

### Example:
```bash
# Default mode - scan 8 stocks + your positions
python src/main_enhanced.py

# Universe mode - scan 50 stocks + your positions
# (Set SCAN_UNIVERSE=true first)
python src/main_enhanced.py
```

---

## 🎯 Feature 2: Position-Aware Signals

### What Changed:
**Old behavior:**
- Would show SELL signals for stocks you don't even own 🤦
- Would show HOLD signals for random stocks
- Cluttered output with irrelevant information

**New behavior:**
- **BUY signals**: Any stock with strong buy signal (only if you have money)
- **SELL signals**: Only for stocks in your portfolio
- **HOLD signals**: Only for stocks you're currently holding
- Clean, actionable recommendations

### How It Works:
The bot automatically:
1. Checks your current positions via Alpaca API
2. Filters signals based on what you own
3. Always scans your positions (even if not in watchlist)

### Example Output:
```
[POSITIONS] Currently holding: 2 stocks
  AAPL, TSLA

[BUY OPPORTUNITIES] 3 signals
  NVDA: STRONG_BUY (Strength: 0.75)
  MSFT: BUY (Strength: 0.45)
  ...

[SELL ALERTS] 1 signal (stocks you own)
  TSLA: SELL (Strength: -0.50)
  - RSI overbought (78.5)
  - Price above resistance
  
[POSITIONS TO HOLD] 1 stock
  AAPL: $255.47 (Strength: 0.10)
```

### No Configuration Needed:
This feature is always enabled in `src/main_enhanced.py`!

---

## 🤖 Feature 3: Automatic Trade Execution

### ⚠️ **IMPORTANT SAFETY WARNING** ⚠️

When enabled, the bot will **ACTUALLY PLACE TRADES** automatically. Even in paper trading mode, it's executing orders without your approval.

### How It Works:
1. Bot scans stocks and generates signals
2. For each BUY signal: Places bracket order (entry + stop loss + take profit)
3. For each SELL signal: Closes entire position
4. All trades respect risk management rules

### How to Enable:

**Step 1:** Edit `.env`:
```env
AUTO_TRADE=true
AUTO_TRADE_CONFIRMED=true  # Required safety confirmation
```

**Step 2:** Run the enhanced bot:
```bash
python src/main_enhanced.py
```

### Safety Features:
- ✅ **Double confirmation required**: Must set both `AUTO_TRADE=true` AND `AUTO_TRADE_CONFIRMED=true`
- ✅ **Risk limits enforced**: 10% max position, 5% stop loss, 3% daily loss limit
- ✅ **Bracket orders**: Every buy comes with automatic stop loss and take profit
- ✅ **Paper trading first**: Test in paper mode before considering live
- ✅ **Manual override**: Can still be disabled instantly via `.env`

### When to Use Auto-Trading:

**✅ Good use cases:**
- After 60+ days successful paper trading
- You've validated the strategy works
- You trust the risk management
- You want hands-free trading
- You'll monitor daily results

**❌ Bad use cases:**
- First time using the bot
- Haven't tested in paper mode extensively
- Don't understand the strategy
- Can't monitor regularly
- Uncomfortable with automated decisions

---

## 🎮 Usage Examples

### Example 1: Basic Daily Scan (Default)
```bash
# Uses default watchlist, shows position-aware signals
python src/main_enhanced.py
```

### Example 2: Universe Scan (Find New Opportunities)
```bash
# 1. Edit .env: Set SCAN_UNIVERSE=true
# 2. Run:
python src/main_enhanced.py
```
Takes 3-5 minutes, scans 50+ stocks.

### Example 3: Auto-Trading (Paper Mode)
```bash
# 1. Edit .env:
#    AUTO_TRADE=true
#    AUTO_TRADE_CONFIRMED=true
# 2. Run:
python src/main_enhanced.py
```
Bot will place actual paper trades!

### Example 4: Full Auto Universe Scan
```bash
# 1. Edit .env:
#    SCAN_UNIVERSE=true
#    MAX_STOCKS_TO_SCAN=100
#    AUTO_TRADE=true
#    AUTO_TRADE_CONFIRMED=true
# 2. Run:
python src/main_enhanced.py
```
Ultimate hands-free mode: Scans 100 stocks, auto-executes best opportunities.

---

## ⚙️ Configuration Reference

### `.env` Settings:

```env
# Universe Scanning
SCAN_UNIVERSE=false          # true = scan all stocks, false = watchlist only
MAX_STOCKS_TO_SCAN=50        # How many stocks to scan (if SCAN_UNIVERSE=true)

# Auto Trading
AUTO_TRADE=false             # true = place trades automatically
AUTO_TRADE_CONFIRMED=false   # Must be true if AUTO_TRADE=true (safety check)
```

### Recommended Settings:

**Conservative (Default):**
```env
SCAN_UNIVERSE=false
AUTO_TRADE=false
```
Fast daily scans, manual trade execution.

**Opportunity Finder:**
```env
SCAN_UNIVERSE=true
MAX_STOCKS_TO_SCAN=50
AUTO_TRADE=false
```
Find hidden gems, but still trade manually.

**Full Automation (Advanced):**
```env
SCAN_UNIVERSE=true
MAX_STOCKS_TO_SCAN=100
AUTO_TRADE=true
AUTO_TRADE_CONFIRMED=true
```
Complete hands-free trading. **Use with caution!**

---

## 🚀 GitHub Actions Integration

To enable these features in your automated daily runs:

1. Go to your repo settings → Secrets → Actions
2. Add new secrets:
   - `SCAN_UNIVERSE` → `true` or `false`
   - `AUTO_TRADE` → `true` or `false`
   - `AUTO_TRADE_CONFIRMED` → `true` (if auto-trading)
   - `MAX_STOCKS_TO_SCAN` → `50` (or your preferred number)

3. Update `.github/workflows/trading-bot.yml`:
   ```yaml
   - name: Run trading bot
     env:
       # ... existing vars ...
       SCAN_UNIVERSE: ${{ secrets.SCAN_UNIVERSE }}
       MAX_STOCKS_TO_SCAN: ${{ secrets.MAX_STOCKS_TO_SCAN }}
       AUTO_TRADE: ${{ secrets.AUTO_TRADE }}
       AUTO_TRADE_CONFIRMED: ${{ secrets.AUTO_TRADE_CONFIRMED }}
     run: |
       python src/main_enhanced.py  # Changed from src/main.py
   ```

---

## 📈 Performance Impact

| Mode | Scan Time | API Calls | Best For |
|------|-----------|-----------|----------|
| Default Watchlist | 10-20 sec | ~10 | Daily quick scans |
| Universe (50 stocks) | 3-5 min | ~150 | Weekly opportunity hunts |
| Universe (100 stocks) | 6-10 min | ~300 | Deep market analysis |

**Note:** Alpaca free tier has rate limits. Stay under 200 requests/minute.

---

## 🛡️ Safety Checklist

Before enabling auto-trading:

- [ ] Tested in paper trading for 60+ days
- [ ] Win rate consistently above 50%
- [ ] Max drawdown acceptable (<10%)
- [ ] Understand all risk management settings
- [ ] Comfortable with automated decisions
- [ ] Can monitor daily results
- [ ] Have `AUTO_TRADE_CONFIRMED=true` in `.env`
- [ ] Started with small position sizes
- [ ] Reviewed recent signals manually

---

## 🐛 Troubleshooting

### "Rate limit exceeded"
- Reduce `MAX_STOCKS_TO_SCAN`
- Use default watchlist mode
- Add small delays between API calls

### "No buy signals in universe scan"
- Market might be overvalued
- Try different technical indicator thresholds
- Check that filters aren't too restrictive

### "Auto-trade not working"
- Verify `AUTO_TRADE=true` and `AUTO_TRADE_CONFIRMED=true`
- Check account has buying power
- Ensure risk limits not exceeded
- Review logs for specific errors

### "Takes too long to scan"
- Reduce `MAX_STOCKS_TO_SCAN`
- Use faster instance (if on cloud)
- Cache results (advanced)

---

## 📝 Summary

**What you have now:**
- ✅ Can scan the entire stock universe (thousands of stocks)
- ✅ Smart filtering - only see relevant recommendations
- ✅ Optional fully automated trading
- ✅ All safety features still active
- ✅ Choose your own risk level

**Still has the old features:**
- ✅ Original 8-stock watchlist mode (still the default)
- ✅ Manual trading mode (still the default)
- ✅ All technical indicators
- ✅ Risk management
- ✅ Paper trading

**Next steps:**
1. Try universe scanning: Set `SCAN_UNIVERSE=true` and run
2. Review position-aware signals (automatic in enhanced version)
3. Consider auto-trading only after extensive paper trading success

---

**Questions?** Check `DEPLOYMENT.md` for general setup, or `INSTALLATION.md` for basic installation.
