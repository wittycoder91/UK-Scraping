#!/bin/bash

echo "Enabling Safari Remote Automation..."
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is for macOS only"
    echo "Safari automation is only available on macOS"
    exit 1
fi

echo "This script will enable Safari WebDriver for automation."
echo ""
echo "Requirements:"
echo "  1. Safari → Preferences → Advanced → Show Develop menu in menu bar (must be checked)"
echo "  2. Safari → Develop → Allow Remote Automation (must be checked)"
echo ""
read -p "Have you completed the above steps? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Please complete the Safari setup first:"
    echo "  1. Open Safari"
    echo "  2. Safari → Preferences (or Settings) → Advanced"
    echo "  3. Check 'Show Develop menu in menu bar'"
    echo "  4. Safari → Develop → Check 'Allow Remote Automation'"
    echo "  5. Run this script again"
    exit 1
fi

echo ""
echo "Enabling safaridriver..."
echo "You may be prompted for your password."

# Enable safaridriver
/usr/bin/safaridriver --enable

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Safari WebDriver enabled successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Make sure Safari is open"
    echo "  2. Navigate to the DVSA website in Safari"
    echo "  3. Make sure you're logged in"
    echo "  4. Run: python3 script.py"
    echo ""
else
    echo ""
    echo "❌ Failed to enable safaridriver"
    echo ""
    echo "Troubleshooting:"
    echo "  - Make sure 'Allow Remote Automation' is enabled in Safari → Develop menu"
    echo "  - You may need administrator privileges"
    echo "  - Try running: sudo /usr/bin/safaridriver --enable"
    echo ""
    exit 1
fi

