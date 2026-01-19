# Installation Wizard Guide
## Automated Setup for Easy Deployment

---

## Why an Installation Wizard?

Instead of asking the end user to manually run commands, you can create an **automated installation wizard** that:

✅ **Guides the user** through setup with a friendly interface
✅ **Checks prerequisites** automatically (Python version, etc.)
✅ **Installs dependencies** without manual pip commands
✅ **Configures API keys** with validation
✅ **Creates necessary directories** automatically
✅ **Tests the installation** to verify everything works
✅ **Provides clear error messages** if something goes wrong
✅ **Makes handoff professional** and easy

**Result:** The end user just runs one file and answers a few questions. Everything else happens automatically.

---

## Option 1: Simple Command-Line Wizard (Easiest)

### What It Looks Like:

```
═══════════════════════════════════════════════════════
   Trading System Installation Wizard
═══════════════════════════════════════════════════════

Welcome! This wizard will set up your trading system.

Step 1/5: Checking Python version...
✓ Python 3.11.0 detected (OK)

Step 2/5: Creating virtual environment...
✓ Virtual environment created

Step 3/5: Installing dependencies...
✓ Installing pandas... Done
✓ Installing alpaca-trade-api... Done
✓ Installing pandas-ta... Done
[... more packages ...]

Step 4/5: Configuring API keys...

Please enter your Alpaca Paper Trading API Key: **********************
Please enter your Alpaca Paper Trading Secret: **********************
✓ API keys configured

Testing connection to Alpaca...
✓ Connection successful!

Step 5/5: Final setup...
✓ Created data directories
✓ Created log directories
✓ Configuration file created

═══════════════════════════════════════════════════════
Installation Complete!
═══════════════════════════════════════════════════════

To start the trading system:
  1. Open terminal in this directory
  2. Run: venv\Scripts\activate
  3. Run: python main.py

See USER_MANUAL.md for more information.
```

### Implementation

Create a file called `install_wizard.py`:

```python
"""
Trading System Installation Wizard
Automated setup script for easy deployment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import time

class Colors:
    """Terminal colors for better UX"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Print welcome header"""
    print("\n" + "="*60)
    print(f"{Colors.BOLD}   Trading System Installation Wizard{Colors.END}")
    print("="*60 + "\n")
    print("Welcome! This wizard will set up your trading system.\n")

def print_step(step_num, total_steps, message):
    """Print step progress"""
    print(f"\n{Colors.BLUE}Step {step_num}/{total_steps}: {message}...{Colors.END}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.END} {message}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.END} {message}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.END} {message}")

def check_python_version():
    """Check if Python version is 3.10+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        return True, f"{version.major}.{version.minor}.{version.micro}"
    return False, f"{version.major}.{version.minor}.{version.micro}"

def create_virtual_environment():
    """Create Python virtual environment"""
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], 
                      check=True, 
                      capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

def get_pip_path():
    """Get the path to pip in virtual environment"""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "pip.exe")
    else:
        return os.path.join("venv", "bin", "pip")

def install_dependencies():
    """Install Python packages from requirements.txt"""
    pip_path = get_pip_path()
    
    if not os.path.exists("requirements.txt"):
        print_warning("requirements.txt not found, creating minimal version...")
        # Create minimal requirements
        packages = [
            "pandas",
            "numpy",
            "requests",
            "alpaca-trade-api",
            "pandas-ta",
            "vaderSentiment",
            "python-dotenv",
            "pyyaml",
            "pytest"
        ]
        with open("requirements.txt", "w") as f:
            f.write("\n".join(packages))
    
    try:
        # Upgrade pip first
        subprocess.run([pip_path, "install", "--upgrade", "pip"], 
                      check=True, 
                      capture_output=True)
        
        # Install packages
        result = subprocess.run([pip_path, "install", "-r", "requirements.txt"],
                              check=True,
                              capture_output=True,
                              text=True)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e.stderr}")
        return False

def configure_api_keys():
    """Interactive API key configuration"""
    print("\nYou'll need Alpaca API keys for paper trading.")
    print("Get them at: https://alpaca.markets (Paper Trading section)\n")
    
    # Get paper trading keys
    while True:
        paper_key = input("Enter your Alpaca Paper Trading API Key: ").strip()
        if len(paper_key) > 10:  # Basic validation
            break
        print_error("API key seems too short. Please check and try again.")
    
    while True:
        paper_secret = input("Enter your Alpaca Paper Trading Secret: ").strip()
        if len(paper_secret) > 10:
            break
        print_error("Secret seems too short. Please check and try again.")
    
    # Optional: News API
    print("\n(Optional) NewsAPI key for sentiment analysis")
    print("Get free key at: https://newsapi.org (100 requests/day free)")
    news_key = input("Enter NewsAPI key (or press Enter to skip): ").strip()
    
    # Create .env file
    env_content = f"""# Trading System Configuration
# Generated by Installation Wizard

# Alpaca Paper Trading (NO REAL MONEY)
ALPACA_PAPER_KEY_ID={paper_key}
ALPACA_PAPER_SECRET={paper_secret}

# Live Trading (DO NOT USE UNTIL READY)
# ALPACA_LIVE_KEY_ID=your_live_key_here
# ALPACA_LIVE_SECRET=your_live_secret_here

# News API (Optional)
{"NEWS_API_KEY=" + news_key if news_key else "# NEWS_API_KEY=your_key_here"}

# Trading Mode (paper or live)
TRADING_MODE=paper
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    return paper_key, paper_secret

def test_alpaca_connection(api_key, api_secret):
    """Test connection to Alpaca API"""
    try:
        # Import inside function to ensure it's installed
        from alpaca_trade_api import REST
        
        api = REST(
            key_id=api_key,
            secret_key=api_secret,
            base_url='https://paper-api.alpaca.markets',
            api_version='v2'
        )
        
        # Try to get account info
        account = api.get_account()
        return True, account
    except Exception as e:
        return False, str(e)

def create_directory_structure():
    """Create necessary directories"""
    directories = [
        "data",
        "data/collectors",
        "data/storage",
        "analysis",
        "analysis/technical",
        "analysis/sentiment",
        "strategies",
        "alerts",
        "logs",
        "config",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    return True

def create_config_file():
    """Create default configuration file"""
    config_content = """# Trading System Configuration

# Risk Management
max_position_size: 0.10  # Maximum 10% per position
max_daily_loss: 0.03     # Stop trading if lose 3% in one day
stop_loss_pct: 0.05      # 5% stop loss per trade

# Strategy Parameters
rsi_period: 14
rsi_oversold: 30
rsi_overbought: 70
ma_short_period: 20
ma_long_period: 50

# Alert Settings
email_alerts: true
alert_cooldown_minutes: 60  # Don't spam similar alerts
"""
    
    with open("config/settings.yaml", "w") as f:
        f.write(config_content)
    
    return True

def run_installation():
    """Main installation flow"""
    print_header()
    
    # Step 1: Check Python version
    print_step(1, 5, "Checking Python version")
    is_valid, version = check_python_version()
    if is_valid:
        print_success(f"Python {version} detected (OK)")
    else:
        print_error(f"Python {version} detected")
        print_error("This system requires Python 3.10 or higher")
        print("\nPlease install Python 3.10+ from: https://www.python.org/downloads/")
        return False
    
    # Step 2: Create virtual environment
    print_step(2, 5, "Creating virtual environment")
    if create_virtual_environment():
        print_success("Virtual environment created")
    else:
        print_error("Failed to create virtual environment")
        return False
    
    # Step 3: Install dependencies
    print_step(3, 5, "Installing dependencies")
    print("This may take a few minutes...")
    if install_dependencies():
        print_success("All dependencies installed")
    else:
        print_error("Failed to install dependencies")
        print_warning("Check your internet connection and try again")
        return False
    
    # Step 4: Configure API keys
    print_step(4, 5, "Configuring API keys")
    paper_key, paper_secret = configure_api_keys()
    print_success("API keys configured")
    
    # Test connection
    print("\nTesting connection to Alpaca...")
    success, result = test_alpaca_connection(paper_key, paper_secret)
    if success:
        account = result
        print_success("Connection successful!")
        print(f"  Paper Trading Account Balance: ${float(account.cash):,.2f}")
        print(f"  Account Status: {account.status}")
    else:
        print_error(f"Connection failed: {result}")
        print_warning("Check your API keys and try again")
        print_warning("Installation will continue, but fix this before running the system")
    
    # Step 5: Final setup
    print_step(5, 5, "Final setup")
    create_directory_structure()
    print_success("Created data directories")
    print_success("Created log directories")
    
    create_config_file()
    print_success("Configuration file created")
    
    # Success!
    print("\n" + "="*60)
    print(f"{Colors.GREEN}{Colors.BOLD}Installation Complete!{Colors.END}")
    print("="*60 + "\n")
    
    # Instructions
    print("To start the trading system:\n")
    if platform.system() == "Windows":
        print("  1. Open terminal in this directory")
        print("  2. Run: venv\\Scripts\\activate")
        print("  3. Run: python main.py")
    else:
        print("  1. Open terminal in this directory")
        print("  2. Run: source venv/bin/activate")
        print("  3. Run: python main.py")
    
    print("\nSee USER_MANUAL.md for more information.")
    print("\n" + Colors.YELLOW + "IMPORTANT: You are in PAPER TRADING mode (fake money).")
    print("This is safe for testing. No real money is at risk." + Colors.END + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = run_installation()
        if not success:
            print("\n" + Colors.RED + "Installation failed. Please fix errors and try again." + Colors.END)
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
```

### How to Use:

**For the developer (you):**
1. Include `install_wizard.py` in your delivery package
2. Tell user: "Just run `python install_wizard.py`"

**For the end user (your boyfriend):**
1. Extract the project files
2. Open terminal/command prompt
3. Navigate to the project folder
4. Run: `python install_wizard.py`
5. Answer the questions
6. Done!

---

## Option 2: GUI Installation Wizard (More Professional)

### What It Looks Like:

A window-based installer with:
- Welcome screen
- Progress bar
- Input fields for API keys
- Test connection button
- Success/error dialogs
- Finish screen with next steps

### Implementation

Use `tkinter` (comes with Python, no extra install needed):

```python
"""
GUI Installation Wizard for Trading System
Professional graphical installer
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import sys
import os
from pathlib import Path

class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading System Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Variables
        self.paper_key = tk.StringVar()
        self.paper_secret = tk.StringVar()
        self.news_key = tk.StringVar()
        
        # Create UI
        self.create_welcome_page()
    
    def create_welcome_page(self):
        """Welcome screen"""
        self.clear_frame()
        
        frame = ttk.Frame(self.root, padding="40")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Trading System Installer", 
                         font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        # Description
        desc = ttk.Label(frame, text="""
Welcome to the Trading System Installation Wizard!

This wizard will:
• Check your Python installation
• Install all required packages
• Configure your API keys
• Set up the trading environment
• Test the installation

The process takes about 5-10 minutes.
        """, justify=tk.LEFT)
        desc.pack(pady=20)
        
        # Start button
        start_btn = ttk.Button(frame, text="Start Installation", 
                              command=self.create_dependency_page)
        start_btn.pack(pady=20)
    
    def create_dependency_page(self):
        """Dependency installation page"""
        self.clear_frame()
        
        frame = ttk.Frame(self.root, padding="40")
        frame.pack(fill=tk.BOTH, expand=True)
        
        title = ttk.Label(frame, text="Installing Dependencies", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.pack(pady=20, fill=tk.X)
        self.progress.start()
        
        # Log output
        self.log_text = scrolledtext.ScrolledText(frame, height=15, state='disabled')
        self.log_text.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Start installation in background thread
        thread = threading.Thread(target=self.install_dependencies)
        thread.start()
    
    def log(self, message):
        """Add message to log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()
    
    def install_dependencies(self):
        """Install packages in background"""
        try:
            self.log("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], 
                          check=True, capture_output=True)
            self.log("✓ Virtual environment created")
            
            pip_path = os.path.join("venv", "Scripts", "pip.exe")
            
            self.log("\nInstalling packages (this may take a few minutes)...")
            packages = [
                "pandas", "numpy", "requests", "alpaca-trade-api",
                "pandas-ta", "vaderSentiment", "python-dotenv", "pyyaml"
            ]
            
            for package in packages:
                self.log(f"Installing {package}...")
                subprocess.run([pip_path, "install", package],
                             check=True, capture_output=True)
            
            self.log("\n✓ All packages installed successfully!")
            self.progress.stop()
            
            # Move to API configuration
            self.root.after(1000, self.create_api_config_page)
            
        except Exception as e:
            self.progress.stop()
            self.log(f"\n✗ Error: {str(e)}")
            messagebox.showerror("Installation Error", 
                               "Failed to install dependencies. Check the log for details.")
    
    def create_api_config_page(self):
        """API key configuration page"""
        self.clear_frame()
        
        frame = ttk.Frame(self.root, padding="40")
        frame.pack(fill=tk.BOTH, expand=True)
        
        title = ttk.Label(frame, text="Configure API Keys", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Instructions
        instructions = ttk.Label(frame, text="""
You need Alpaca API keys for paper trading (risk-free testing).
Get them at: https://alpaca.markets

Sign up and navigate to the Paper Trading section to generate keys.
        """, justify=tk.LEFT)
        instructions.pack(pady=10)
        
        # Input fields
        ttk.Label(frame, text="Alpaca Paper Trading API Key:").pack(anchor=tk.W, pady=(10,0))
        ttk.Entry(frame, textvariable=self.paper_key, width=50).pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Alpaca Paper Trading Secret:").pack(anchor=tk.W, pady=(10,0))
        ttk.Entry(frame, textvariable=self.paper_secret, width=50, show="*").pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="NewsAPI Key (optional):").pack(anchor=tk.W, pady=(10,0))
        ttk.Entry(frame, textvariable=self.news_key, width=50).pack(fill=tk.X, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Test Connection", 
                  command=self.test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Continue", 
                  command=self.finish_installation).pack(side=tk.LEFT, padx=5)
    
    def test_connection(self):
        """Test Alpaca connection"""
        if not self.paper_key.get() or not self.paper_secret.get():
            messagebox.showwarning("Missing Keys", "Please enter both API key and secret.")
            return
        
        try:
            from alpaca_trade_api import REST
            api = REST(
                key_id=self.paper_key.get(),
                secret_key=self.paper_secret.get(),
                base_url='https://paper-api.alpaca.markets',
                api_version='v2'
            )
            account = api.get_account()
            messagebox.showinfo("Success", 
                              f"Connection successful!\n\n"
                              f"Paper Trading Balance: ${float(account.cash):,.2f}\n"
                              f"Account Status: {account.status}")
        except Exception as e:
            messagebox.showerror("Connection Failed", 
                               f"Could not connect to Alpaca:\n\n{str(e)}\n\n"
                               f"Please check your API keys.")
    
    def finish_installation(self):
        """Finalize installation"""
        if not self.paper_key.get() or not self.paper_secret.get():
            messagebox.showwarning("Missing Keys", "Please enter API keys before continuing.")
            return
        
        # Create .env file
        env_content = f"""ALPACA_PAPER_KEY_ID={self.paper_key.get()}
ALPACA_PAPER_SECRET={self.paper_secret.get()}
NEWS_API_KEY={self.news_key.get()}
TRADING_MODE=paper
"""
        with open(".env", "w") as f:
            f.write(env_content)
        
        # Create directories
        for directory in ["data", "logs", "config"]:
            Path(directory).mkdir(exist_ok=True)
        
        # Show completion
        self.create_completion_page()
    
    def create_completion_page(self):
        """Installation complete page"""
        self.clear_frame()
        
        frame = ttk.Frame(self.root, padding="40")
        frame.pack(fill=tk.BOTH, expand=True)
        
        title = ttk.Label(frame, text="Installation Complete!", 
                         font=("Arial", 18, "bold"), foreground="green")
        title.pack(pady=20)
        
        message = ttk.Label(frame, text="""
The trading system has been successfully installed!

Next steps:

1. Activate the virtual environment:
   venv\\Scripts\\activate

2. Run the system:
   python main.py

3. Check USER_MANUAL.md for usage instructions

You are in PAPER TRADING mode (fake money).
This is completely safe for testing.
        """, justify=tk.LEFT)
        message.pack(pady=20)
        
        ttk.Button(frame, text="Finish", command=self.root.quit).pack(pady=20)
    
    def clear_frame(self):
        """Clear all widgets from root"""
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerGUI(root)
    root.mainloop()
```

---

## Option 3: Web-Based Installer (Most Modern)

Create a simple Flask web app that runs locally and guides through installation with a web interface.

**Advantages:**
- Most user-friendly
- Better UI/UX options
- Can include videos/GIFs
- Responsive design

**AI Assistance:**
```
Prompt: "Create a Flask web-based installation wizard for a Python trading 
system. Include routes for: welcome page, dependency installation with 
real-time progress, API key configuration with validation, and completion 
page. Use AJAX for async operations. Include Bootstrap for styling."
```

---

## Making the Installer Executable (One-Click Install)

The best option: Convert your wizard to a standalone `.exe` file using **PyInstaller**.

### Steps:

1. **Install PyInstaller:**
```bash
pip install pyinstaller
```

2. **Create executable:**
```bash
# For command-line wizard
pyinstaller --onefile --name="TradingSystemInstaller" install_wizard.py

# For GUI wizard
pyinstaller --onefile --windowed --name="TradingSystemInstaller" gui_installer.py
```

3. **Result:**
- A single `.exe` file in the `dist/` folder
- User just double-clicks it
- No Python installation required on their machine!

### AI Assistance:
```
Prompt: "Show me how to use PyInstaller to create a standalone executable 
from my Python installation wizard. Include: how to bundle dependencies, 
set an icon, hide the console window (for GUI), and reduce file size. 
Explain any issues with antivirus false positives."
```

---

## Recommended Approach for Your Project

**For maximum ease of handoff:**

1. **Create the command-line wizard** (Option 1)
   - Simplest to maintain
   - Works on any system
   - Easy to debug

2. **Include it with the project:**
   ```
   trading-system/
   ├── install_wizard.py      ← The installer
   ├── requirements.txt
   ├── src/
   └── ... other files
   ```

3. **Create a simple README:**
   ```
   # Quick Installation
   
   1. Ensure Python 3.10+ is installed
   2. Run: python install_wizard.py
   3. Follow the prompts
   4. Done!
   ```

4. **Optional: Create executable version:**
   - Use PyInstaller to make `.exe`
   - User doesn't even need Python
   - Just double-click and go

---

## What the Wizard Should Do (Checklist)

### Must-Have Features:
- ✅ Check Python version (3.10+)
- ✅ Create virtual environment
- ✅ Install dependencies from requirements.txt
- ✅ Collect API keys interactively
- ✅ Validate API keys work
- ✅ Create .env file securely
- ✅ Create directory structure
- ✅ Create default config files
- ✅ Test installation
- ✅ Provide clear next steps

### Nice-to-Have Features:
- ⭐ Progress bars
- ⭐ Colored output
- ⭐ Detailed logging
- ⭐ Rollback on failure
- ⭐ Multiple language support
- ⭐ Custom installation path
- ⭐ Update checker

---

## AI Prompts for Building the Wizard

### Initial Setup:
```
Prompt: "Create a Python installation wizard script that checks for Python 
3.10+, creates a virtual environment, and installs packages from requirements.txt. 
Include a progress indicator, colored terminal output using colorama or ANSI 
codes, and comprehensive error handling. Make it beginner-friendly."
```

### API Configuration:
```
Prompt: "Add an interactive API key configuration section to my installer. 
It should: prompt for Alpaca paper trading keys, validate key format, 
test the connection, create a .env file with the keys, and give clear 
error messages if connection fails. Include retry logic."
```

### Making it GUI:
```
Prompt: "Convert this command-line installer to a tkinter GUI. Include: 
welcome screen, progress bar during installation, text input fields for 
API keys, a 'Test Connection' button, and a completion screen. Use modern 
ttk widgets and a clean layout."
```

### Creating Executable:
```
Prompt: "Show me how to package this Python installer as a standalone 
Windows executable using PyInstaller. Include: command to create exe, 
how to set a custom icon, how to hide console window, troubleshooting 
antivirus warnings, and reducing file size."
```

---

## Testing Your Wizard

Before delivering, test the wizard:

1. **Fresh Windows VM:**
   - Install clean Windows
   - Don't install Python (or install just Python)
   - Run your installer
   - Verify everything works

2. **Test failure scenarios:**
   - Wrong API keys → Clear error message?
   - No internet → Graceful failure?
   - Insufficient permissions → Helpful guidance?
   - Already installed → Handles correctly?

3. **Test with your end user:**
   - Have your boyfriend try it
   - Watch for confusion points
   - Refine based on feedback

---

## Example Delivery Package

```
trading-system-delivery/
├── install_wizard.py          ← One-click installer
├── requirements.txt
├── README.md                  ← "Run install_wizard.py"
├── src/                       ← Your trading system code
│   ├── main.py
│   ├── data/
│   ├── analysis/
│   └── ...
├── docs/
│   ├── USER_MANUAL.md
│   ├── TROUBLESHOOTING.md
│   └── FAQ.md
└── examples/
    └── sample_config.yaml
```

**User experience:**
1. Extract ZIP file
2. Double-click `install_wizard.py` (or `.exe`)
3. Answer a few questions
4. System is ready!

---

## Summary

**Yes, you absolutely should create an installation wizard!**

**Recommended path:**
1. Start with **command-line wizard** (easiest to build and test)
2. Add **GUI version** if you want it more professional
3. Optionally convert to **`.exe`** for ultimate ease

**Benefits:**
- ✅ Professional presentation
- ✅ Reduces support burden
- ✅ Prevents installation errors
- ✅ Tests everything automatically
- ✅ Makes handoff smooth

**Time investment:** 2-4 hours to build a solid installer, but saves hours of support and troubleshooting later.

Use the code examples above or use AI to generate the installer based on your specific project structure!
