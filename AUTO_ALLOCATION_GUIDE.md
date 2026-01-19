# Automated Portfolio Allocation Guide

## 🎯 What Is This?

Your trading bot now has an **intelligent portfolio manager** that automatically:

1. **Checks your available capital** (how much you can invest)
2. **Analyzes all opportunities** and ranks them by risk/reward ratio
3. **Automatically invests** in the best opportunities
4. **Respects all safety limits** (5% max loss per trade, 3% max daily loss)
5. **Diversifies** across multiple stocks to spread risk

Think of it as: **Your bot is now a complete investment manager, not just an advisor.**

---

## 🧠 How It Works (Simple Explanation)

### **Old Way (Manual):**
1. Bot scans stocks → finds "Apple looks good"
2. You read the recommendation
3. You decide how much to invest
4. You manually place the trade

### **New Way (Automated):**
1. Bot scans stocks → finds 10 good opportunities
2. Bot calculates: "I have $50,000 available"
3. Bot ranks opportunities: "NVDA has 2.5:1 risk/reward (best), AAPL has 2.0:1, etc."
4. Bot decides: "Invest $10k in NVDA, $9k in AAPL, $8k in MSFT" (diversified)
5. Bot automatically places all trades with stop losses and take profits
6. Done! Your money is working for you.

---

## 📊 The Intelligence Behind It

### **Risk/Reward Ratio Calculation:**

For each opportunity, the bot calculates:

```
Risk per share = Entry price - Stop loss price
Reward per share = Take profit price - Entry price
Risk/Reward Ratio = Reward / Risk

Example:
- Buy AAPL at $255
- Stop loss at $242 (5% below)
- Take profit at $281 (10% above)
- Risk: $255 - $242 = $13
- Reward: $281 - $255 = $26
- Ratio: $26 / $13 = 2.0:1 ✓ Good!
```

**Only invests if ratio ≥ 1.5:1** (you stand to make at least 50% more than you could lose)

### **Smart Capital Allocation:**

```
Available Capital: $50,000
Max Position: 10% = $10,000 per stock
Max Positions: 5 stocks

Top opportunities ranked:
1. NVDA: 2.5:1 ratio → Allocate $10,000
2. AAPL: 2.0:1 ratio → Allocate $10,000  
3. MSFT: 1.8:1 ratio → Allocate $10,000
4. META: 1.6:1 ratio → Allocate $10,000
5. GOOGL: 1.5:1 ratio → Allocate $10,000

Total deployed: $50,000 across 5 stocks
```

---

## 🛡️ Built-In Safety Features

### ✅ **All Existing Safety Nets Still Active:**

1. **5% Stop Loss Per Trade**
   - If AAPL drops 5%, automatically sells
   - Maximum loss: $500 on $10,000 investment

2. **3% Daily Loss Limit**
   - If portfolio loses 3% in one day ($3,000 on $100k)
   - Bot stops trading for the day

3. **10% Max Position Size**
   - Never puts more than 10% in one stock
   - Forces diversification

4. **Max 5 Positions**
   - Won't spread too thin
   - Manageable portfolio size

### ✅ **New Portfolio-Level Protections:**

5. **Minimum Risk/Reward Filter (1.5:1)**
   - Only invests if potential reward > 1.5x potential risk
   - No bad trades get through

6. **Capital Preservation**
   - Checks buying power before every allocation
   - Never over-leverages

7. **Position Slot Management**
   - Respects max position limit
   - Won't add 6th stock if limit is 5

---

## ⚙️ How to Enable

### **Step 1: Edit `.env` file**

```env
# Enable automated allocation
AUTO_ALLOCATE=true
AUTO_ALLOCATE_CONFIRMED=true

# Auto-allocation requires auto-trading
AUTO_TRADE=true
AUTO_TRADE_CONFIRMED=true
```

### **Step 2: Run the enhanced bot**

```bash
python src/main_enhanced.py
```

### **What Happens:**

```
[CAPITAL] Available: $100,000
[POSITIONS] Current: 0/5

[RANKING] Evaluating 8 opportunities...
  NVDA: R/R 2.15 - QUALIFIED ✓
  AAPL: R/R 1.95 - QUALIFIED ✓
  META: R/R 1.60 - QUALIFIED ✓
  MSFT: R/R 1.45 - Below minimum threshold
  
[RESULT] 3 qualified opportunities

[ALLOCATION] Deploying $100,000
[SLOTS] 5 position slots available

  ✓ NVDA: 66 shares @ $150.23 = $9,915
    Risk/Reward: 2.15 | Max Loss: $495 | Max Gain: $1,065
  ✓ AAPL: 39 shares @ $255.47 = $9,963
    Risk/Reward: 1.95 | Max Loss: $498 | Max Gain: $971
  ✓ META: 16 shares @ $612.34 = $9,797
    Risk/Reward: 1.60 | Max Loss: $490 | Max Gain: $784

[SUMMARY] 3 allocations created
  Total deployed: $29,675
  Total risk: $1,483 (1.48% of portfolio)
  Total potential: $2,820 (9.5% return)
  
[EXECUTING] Placing orders for allocated positions...
  ✓ NVDA: Order placed successfully
  ✓ AAPL: Order placed successfully
  ✓ META: Order placed successfully
```

---

## 🎮 Usage Examples

### **Example 1: Conservative Allocation (Default)**

```env
AUTO_ALLOCATE=true
AUTO_ALLOCATE_CONFIRMED=true
AUTO_TRADE=true
AUTO_TRADE_CONFIRMED=true
SCAN_UNIVERSE=false  # Just watchlist
```

**Result:** Scans 8 stocks, invests in top 3-5 with best risk/reward

### **Example 2: Aggressive Opportunity Hunter**

```env
AUTO_ALLOCATE=true
AUTO_ALLOCATE_CONFIRMED=true
AUTO_TRADE=true
AUTO_TRADE_CONFIRMED=true
SCAN_UNIVERSE=true
MAX_STOCKS_TO_SCAN=100
```

**Result:** Scans 100 stocks, finds hidden gems, automatically invests

### **Example 3: Testing Mode (Recommended First)**

```env
AUTO_ALLOCATE=false  # Turn off allocation
AUTO_TRADE=false
SCAN_UNIVERSE=false
```

**Result:** Bot shows you WHAT it WOULD allocate, but doesn't execute

---

## 📈 Real-World Example

### **Scenario: Monday Morning**

**Your Account:**
- Cash: $100,000
- Current positions: 0
- Max positions: 5

**Bot Scans Market:**
- Finds 12 buy signals
- Calculates risk/reward for each
- Filters to 5 that meet minimum 1.5:1 ratio

**Bot's Analysis:**

| Stock | Price | Risk/Reward | Signal Strength | Score |
|-------|-------|-------------|-----------------|-------|
| NVDA | $150 | 2.5:1 | 0.82 | 2.05 (Top!) |
| AAPL | $255 | 2.0:1 | 0.75 | 1.50 |
| META | $612 | 1.8:1 | 0.68 | 1.22 |
| MSFT | $460 | 1.7:1 | 0.62 | 1.05 |
| GOOGL | $330 | 1.6:1 | 0.58 | 0.93 |

**Bot's Allocation:**

```
Portfolio Size: $100,000
Max per position: 10% = $10,000

Allocation:
1. NVDA: $10,000 (66 shares @ $150) - Best risk/reward
2. AAPL: $10,000 (39 shares @ $255)
3. META: $10,000 (16 shares @ $612)
4. MSFT: $10,000 (21 shares @ $460)
5. GOOGL: $10,000 (30 shares @ $330)

Total invested: $50,000 (50% of capital)
Remaining cash: $50,000 (dry powder for opportunities)
```

**Safety Setup for Each:**

- NVDA: Stop loss $142.50 (-5%), Take profit $165.00 (+10%)
- AAPL: Stop loss $242.70 (-5%), Take profit $281.02 (+10%)
- META: Stop loss $581.72 (-5%), Take profit $673.57 (+10%)
- MSFT: Stop loss $437.00 (-5%), Take profit $506.00 (+10%)
- GOOGL: Stop loss $313.50 (-5%), Take profit $363.00 (+10%)

**Maximum Portfolio Risk:**
- If ALL 5 hit stop loss: $2,500 total loss (2.5% of portfolio)
- Well within 3% daily loss limit ✓

**Maximum Portfolio Gain:**
- If ALL 5 hit take profit: $5,000 total gain (5% portfolio return)
- Risk/Reward: 2:1 at portfolio level ✓

---

## 🔧 Configuration Options

### **In `.env`:**

```env
# Must be enabled for auto-allocation
AUTO_ALLOCATE=true
AUTO_ALLOCATE_CONFIRMED=true
AUTO_TRADE=true
AUTO_TRADE_CONFIRMED=true

# Optional: Scan more stocks
SCAN_UNIVERSE=true
MAX_STOCKS_TO_SCAN=50
```

### **In `config/settings.yaml`:**

```yaml
risk:
  max_position_size: 0.10  # 10% max per stock
  max_daily_loss: 0.03     # 3% daily loss limit
  stop_loss_pct: 0.05      # 5% stop loss per trade
  take_profit_pct: 0.10    # 10% take profit (2:1 R/R)
  max_positions: 5         # Maximum 5 stocks
```

**Want to change the allocation logic?** Edit `src/portfolio/portfolio_manager.py`

---

## 🚦 Decision Tree: When to Use Auto-Allocation

### ✅ **Use Auto-Allocation If:**

- [ ] You've paper traded for 60+ days successfully
- [ ] You understand risk/reward ratios
- [ ] You trust the bot's analysis
- [ ] You want hands-free investing
- [ ] You're comfortable with diversification
- [ ] You can monitor daily (not required, but recommended)

### ❌ **DON'T Use Auto-Allocation If:**

- [ ] First time using the bot
- [ ] Haven't tested in paper mode
- [ ] Don't understand the strategy
- [ ] Want complete control over every trade
- [ ] Uncomfortable with automated decisions
- [ ] Using live money without extensive testing

---

## 🐛 Troubleshooting

### **"No capital available"**
- Check account balance
- Verify not at max positions (5)
- Check if daily loss limit reached (3%)

### **"No opportunities meet threshold"**
- Market might be overvalued
- Try lowering min_ratio in code (default 1.5)
- Check technical indicators are working

### **"Auto-allocation not executing"**
- Verify `AUTO_ALLOCATE=true` AND `AUTO_ALLOCATE_CONFIRMED=true`
- Verify `AUTO_TRADE=true` (required)
- Check logs for specific errors

### **"Allocated wrong amounts"**
- Check `max_position_size` in settings.yaml (default 10%)
- Verify buying power vs cash available
- Review allocation logic in portfolio_manager.py

---

## 📊 Monitoring Your Auto-Allocated Portfolio

### **Daily Check (Recommended):**

1. **Check GitHub Actions logs** (if running in cloud)
2. **Review allocations made** that day
3. **Monitor positions** at Alpaca dashboard
4. **Verify stop losses** are in place
5. **Check P&L** vs. expectations

### **Weekly Review:**

- Win rate: Are >50% of trades profitable?
- Avg R/R: Is realized R/R close to 2:1?
- Drawdown: Staying under 10%?
- Portfolio balance: Diversified across 5 stocks?

### **Monthly Analysis:**

- Total return vs. S&P 500
- Best/worst performers
- Adjust parameters if needed
- Consider increasing capital if successful

---

## 🎯 Summary

**What You Now Have:**

- ✅ Intelligent portfolio manager that ranks opportunities
- ✅ Automatic capital allocation based on risk/reward
- ✅ Diversification across multiple stocks
- ✅ All safety nets active (5% stop, 3% daily limit)
- ✅ Minimum 1.5:1 risk/reward threshold
- ✅ Hands-free investing

**Still Manual:**
- Withdrawing profits
- Changing strategy parameters
- Enabling/disabling auto-allocation

**Next Steps:**
1. Test in paper mode for 30+ days
2. Review allocation decisions
3. Verify safety limits working
4. Monitor performance metrics
5. Consider live deployment if successful

---

**Questions?** See `ENHANCED_FEATURES.md` for related features or `DEPLOYMENT.md` for setup help.
