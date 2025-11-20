# DVSA Booking Form Automation Script

This script automates the DVSA (Driver and Vehicle Standards Agency) booking form interactions. It connects to an existing Chrome browser window and fills out the form to book a driving test.

## Features

- ✅ Connects to an existing Chrome browser window
- ✅ Works even when JavaScript is disabled
- ✅ Human-like interactions with random delays
- ✅ Selects "Car" test category
- ✅ Selects "Wood Green (London)" test centre
- ✅ Selects "No" for special needs
- ✅ Clicks "Book test" button

## Prerequisites

1. **Python 3.7+** installed (use `python3` command on macOS)
2. **Chrome browser** installed
3. **ChromeDriver** - The script will attempt to use Selenium's built-in driver manager

**Note for macOS users:** You may need to grant Terminal accessibility permissions:
- Go to System Preferences → Security & Privacy → Privacy → Accessibility
- Add Terminal (or your terminal app) to the list of allowed apps

## Installation

1. Install required packages:
```bash
pip3 install -r requirements.txt
```

## Setup Chrome for Remote Debugging (macOS)

**IMPORTANT:** Before running the script, you must start Chrome with remote debugging enabled.

### Option 1: Using the Shell Script (Recommended)

1. Close all Chrome windows
2. Open Terminal
3. Navigate to the project directory:
   ```bash
   cd /path/to/Driver
   ```
4. Make the script executable (first time only):
   ```bash
   chmod +x start_chrome_debug.sh
   ```
5. Run the shell script:
   ```bash
   ./start_chrome_debug.sh
   ```

### Option 2: Command Line (Manual)

1. Close all Chrome windows
2. Open Terminal
3. Run Chrome with remote debugging:
   ```bash
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/temp/chrome_debug"
   ```

### Option 3: Create an Alias (Optional)

Add this to your `~/.zshrc` or `~/.bash_profile`:
```bash
alias chrome-debug='/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/temp/chrome_debug"'
```

Then reload your shell configuration:
```bash
source ~/.zshrc  # or source ~/.bash_profile
```

Now you can simply run `chrome-debug` from Terminal.

## Usage

1. **Start Chrome with remote debugging** (see Setup above)

2. **Navigate to the DVSA booking page** in Chrome:
   ```
   https://driver-services.dvsa.gov.uk/obs-web/pages/home?execution=e1s24&org.apache.catalina.filters.CSRF_NONCE=1E3B18F5D7537C5CFAD6EB36D11245B1
   ```

3. **Run the script**:
   ```bash
   python3 script.py
   ```

4. The script will:
   - Connect to your open Chrome window
   - Verify it's on the correct page
   - Select "Car" from the test category dropdown
   - Select "Wood Green (London)" from the test centre dropdown
   - Select "No" for special needs
   - Click the "Book test" button

## Notes

- The script works even if JavaScript is disabled in Chrome settings
- All interactions include human-like delays to avoid detection
- The browser window will remain open after the script completes
- Make sure you're logged into the DVSA system before running the script

## Troubleshooting

### "Could not connect to existing Chrome"
- Make sure Chrome is started with `--remote-debugging-port=9222`
- Close all Chrome windows and restart with the debug flag
- Check if port 9222 is already in use: `lsof -i :9222`
- On macOS, you may need to grant Terminal accessibility permissions in System Preferences → Security & Privacy → Privacy → Accessibility

### "Element not found"
- Verify you're on the correct page
- Make sure the page has fully loaded
- Check if the page structure has changed

### "Timeout error"
- The page might be loading slowly
- Check your internet connection
- Try refreshing the page and running the script again

## Next Steps

After completing the first part (this script), you can proceed with the second part of the automation as needed.

