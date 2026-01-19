# Installation Guide for Non-Technical Users

This guide will help you install and run the trading bot on your computer, even if you're not familiar with programming.

## What You'll Need

- A Windows, Mac, or Linux computer
- About 30 minutes
- The API credentials (your girlfriend will send these to you separately)

---

## Step 1: Install Python

**Windows:**
1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python" button
3. Run the downloaded file
4. **IMPORTANT:** Check the box that says "Add Python to PATH" at the bottom
5. Click "Install Now"
6. Wait for it to finish, then click "Close"

**Mac:**
1. Open Terminal (press Cmd+Space, type "terminal", press Enter)
2. Copy and paste this command, then press Enter:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. After that finishes, run:
   ```bash
   brew install python
   ```

**How to verify it worked:**
- Open Command Prompt (Windows) or Terminal (Mac)
- Type: `python --version`
- You should see something like "Python 3.12.1"

---

## Step 2: Install Git

**Windows:**
1. Go to https://git-scm.com/download/win
2. Download will start automatically
3. Run the installer
4. Click "Next" through all the options (defaults are fine)
5. Click "Install"

**Mac:**
- Git is usually already installed. If not, it will prompt you to install when you try to use it.

**How to verify it worked:**
- Open Command Prompt (Windows) or Terminal (Mac)
- Type: `git --version`
- You should see something like "git version 2.43.0"

---

## Step 3: Download the Trading Bot

1. **Open Command Prompt (Windows) or Terminal (Mac)**
   - Windows: Press Windows key, type "cmd", press Enter
   - Mac: Press Cmd+Space, type "terminal", press Enter

2. **Navigate to where you want to save the bot**
   ```bash
   cd Desktop
   ```

3. **Download the code**
   - If your girlfriend added you as a collaborator:
     ```bash
     git clone https://github.com/HER-USERNAME/trading-bot.git
     ```
   - Replace `HER-USERNAME` with her actual GitHub username
   - If the repo is private, it will ask for your GitHub username and password

4. **Go into the folder**
   ```bash
   cd trading-bot
   ```

---

## Step 4: Set Up API Credentials

1. **Create a file called `.env`**
   - Windows: Right-click in the folder → New → Text Document
   - Rename it to `.env` (yes, it starts with a dot, and has no `.txt` at the end)
   - If Windows won't let you, open Notepad and save as `.env` with "All Files" selected

2. **Copy the credentials your girlfriend sent you**
   - Open `.env` in Notepad (right-click → Open with → Notepad)
   - Paste the credentials she sent (should look like this):
   ```
   ALPACA_PAPER_KEY_ID=PKXXXXXXXXXXXXXXXXXX
   ALPACA_PAPER_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ALPACA_BASE_URL=https://paper-api.alpaca.markets
   NEWS_API_KEY=test_news_key_placeholder
   TRADING_MODE=paper
   ```
   - Save and close

---

## Step 5: Install Required Software

1. **Still in Command Prompt/Terminal, run these commands one at a time:**

   **Create a virtual environment (isolated space for the bot):**
   ```bash
   python -m venv venv
   ```
   (This takes about 1 minute)

2. **Activate the virtual environment:**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **Mac/Linux:**
   ```bash
   source venv/bin/activate
   ```
   
   You should see `(venv)` appear at the beginning of your command line.

3. **Install all the bot's dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   (This takes about 2-5 minutes)

---

## Step 6: Test It Works

1. **Run the demo:**
   ```bash
   python demo.py
   ```
   
   You should see:
   - A connection test to your Alpaca account
   - Technical analysis on some stocks
   - Risk calculations
   - Trading strategy analysis
   - Backtesting results

2. **Run the actual trading bot:**
   ```bash
   python src/main.py
   ```
   
   This will:
   - Connect to your paper trading account
   - Analyze 8 stocks
   - Show you which ones look good to buy

---

## Daily Use

**Every time you want to run the bot:**

1. Open Command Prompt/Terminal
2. Navigate to the folder:
   ```bash
   cd Desktop/trading-bot
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac: `source venv/bin/activate`
4. Run the bot:
   ```bash
   python src/main.py
   ```

---

## Troubleshooting

### "Python is not recognized"
- You need to install Python (Step 1)
- Or, you forgot to check "Add Python to PATH" during installation. Reinstall Python and check that box.

### "Git is not recognized"
- You need to install Git (Step 2)

### "No module named 'alpaca_trade_api'"
- You forgot to run `pip install -r requirements.txt` (Step 5, part 3)
- Or, you forgot to activate the virtual environment (Step 5, part 2)

### "Could not authenticate"
- Check your `.env` file has the correct API credentials
- Make sure there are no extra spaces or quotes around the values

### "Permission denied"
- You may need to run Command Prompt/Terminal as Administrator
- Right-click → Run as Administrator

### Files are missing after downloading
- Make sure you're in the right folder: `cd trading-bot`
- Try downloading again: `git pull`

---

## What's Next?

Once everything is working:

1. **Let it run in paper trading mode for 60+ days**
   - This uses fake money to test the strategy
   - No real money is at risk

2. **Monitor the results**
   - Check your Alpaca paper trading account at https://app.alpaca.markets
   - Run `python src/main.py` daily to see new recommendations

3. **After 60 days of good results:**
   - Review the performance with your girlfriend
   - If win rate is >50% and returns are positive, consider live trading
   - **Never skip the paper trading phase!**

---

## Getting Help

If you're stuck:
1. Read the error message carefully
2. Check the Troubleshooting section above
3. Ask your girlfriend (she set this up for you!)
4. Check `DEPLOYMENT.md` for more advanced setup options

---

## Important Safety Notes

- ⚠️ **The bot is in PAPER TRADING mode** - it uses fake money, not real money
- ⚠️ **Never change `TRADING_MODE=paper` to `live`** without 60+ days of successful testing
- ⚠️ **Never share your API credentials** with anyone
- ⚠️ **The bot does NOT automatically place trades** - it only gives recommendations
- ✅ **Paper trading is 100% safe** - no real money can be lost

---

**Need help?** Your girlfriend set this all up for you. She knows how it works! 💙
