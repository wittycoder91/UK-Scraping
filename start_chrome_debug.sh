#!/bin/bash

echo "Starting Chrome with remote debugging enabled..."
echo ""

# Chrome path on macOS
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Check if Chrome exists
if [ ! -f "$CHROME_PATH" ]; then
    echo "❌ Chrome not found at: $CHROME_PATH"
    echo "Please make sure Google Chrome is installed."
    exit 1
fi

# Check if port 9222 is already in use
if lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠ Port 9222 is already in use."
    echo "Closing existing Chrome instances..."
    killall "Google Chrome" 2>/dev/null
    sleep 2
fi

# Close any existing Chrome instances
echo "Closing any existing Chrome windows..."
killall "Google Chrome" 2>/dev/null
sleep 1

# Create temp directory if it doesn't exist
mkdir -p ~/temp/chrome_debug

# Start Chrome with remote debugging
echo "Starting Chrome with remote debugging on port 9222..."
"$CHROME_PATH" --remote-debugging-port=9222 --user-data-dir="$HOME/temp/chrome_debug" > /dev/null 2>&1 &

# Wait a moment for Chrome to start
sleep 2

# Verify Chrome started successfully
if lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo ""
    echo "✅ Chrome started successfully with remote debugging on port 9222"
    echo ""
    echo "Next steps:"
    echo "1. Navigate to the DVSA website in the Chrome window that opened"
    echo "2. Make sure you're logged in"
    echo "3. Run: python3 script.py"
    echo ""
else
    echo ""
    echo "❌ Failed to start Chrome with remote debugging"
    echo "Please try running manually:"
    echo "$CHROME_PATH --remote-debugging-port=9222 --user-data-dir=\"\$HOME/temp/chrome_debug\""
    echo ""
    exit 1
fi

