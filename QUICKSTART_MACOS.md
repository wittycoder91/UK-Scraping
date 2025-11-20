# Quick Start Guide for macOS

## Step-by-Step Instructions

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Make the Shell Script Executable (First Time Only)
```bash
chmod +x start_chrome_debug.sh
```

### 3. Start Chrome with Debugging
```bash
./start_chrome_debug.sh
```

This will open Chrome with remote debugging enabled.

### 4. Navigate to DVSA Website
In the Chrome window that opened, go to:
```
https://driver-services.dvsa.gov.uk/obs-web/pages/home?execution=e1s24&org.apache.catalina.filters.CSRF_NONCE=1E3B18F5D7537C5CFAD6EB36D11245B1
```

Make sure you're logged in to the DVSA system.

### 5. Run the Automation Script
In a new Terminal window:
```bash
python3 script.py
```

The script will:
- ✅ Connect to your Chrome window
- ✅ Select "Car" from test category
- ✅ Select "Wood Green (London)" from test centre
- ✅ Select "No" for special needs
- ✅ Click "Book test" button

## Troubleshooting

### Permission Errors
If you get permission errors, grant Terminal accessibility permissions:
1. System Preferences → Security & Privacy → Privacy → Accessibility
2. Click the lock icon and enter your password
3. Add Terminal (or iTerm2, etc.) to the list

### Port Already in Use
If port 9222 is already in use:
```bash
lsof -i :9222
kill -9 <PID>
```

### Chrome Not Found
If Chrome is installed in a different location, edit `start_chrome_debug.sh` and update the `CHROME_PATH` variable.

## Alternative: Manual Chrome Start

If you prefer not to use the shell script:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/temp/chrome_debug" &
```

