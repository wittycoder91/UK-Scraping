import time
import random
import socket
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pyautogui
import pygetwindow as gw

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False

def human_delay(min_seconds=0.5, max_seconds=1.5):
    """Add random human-like delay"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def find_chrome_window_with_url(target_url):
    """Find Chrome window that has the target URL open"""
    try:
        # Get all Chrome windows
        chrome_windows = gw.getWindowsWithTitle('Chrome')
        
        for window in chrome_windows:
            if window.visible:
                # Try to get the window title which might contain URL info
                title = window.title
                if 'driver-services.dvsa.gov.uk' in title or 'DVSA' in title:
                    return window
        
        # If not found by title, return the first visible Chrome window
        for window in chrome_windows:
            if window.visible:
                return window
                
        return None
    except Exception as e:
        print(f"Error finding Chrome window: {e}")
        return None

def check_port_available(port=9222):
    """Check if a port is listening (Chrome with remote debugging is running)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False

def connect_to_existing_chrome():
    """Connect to existing Chrome browser using remote debugging"""
    # First check if port 9222 is accessible
    print("Checking if Chrome is running with remote debugging...")
    if not check_port_available(9222):
        print("\n❌ Chrome is not running with remote debugging enabled!")
        print("\n⚠ IMPORTANT: You need to start Chrome with remote debugging first.")
        print("\n📋 Quick fix - Run this command in Terminal:")
        print("\nFor macOS:")
        print('  ./start_chrome_debug.sh')
        print('  or manually:')
        print('  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/temp/chrome_debug"')
        print("\nFor Windows:")
        print('  start_chrome_debug.bat')
        print('  or manually:')
        print('  chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\temp\\chrome_debug"')
        print("\nThen wait a few seconds and run this script again.")
        return None
    
    print("✓ Chrome remote debugging port is accessible")
    
    try:
        # Chrome options for remote debugging
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Try to connect
        print("Connecting to Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        # Remove webdriver property to avoid detection
        try:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
        except:
            pass  # If JS is disabled, this will fail but that's okay
        print("✓ Successfully connected to Chrome")
        return driver
    except Exception as e:
        print(f"\n❌ Could not connect to existing Chrome: {e}")
        print("\n⚠ Make sure:")
        print("  1. Chrome is started with --remote-debugging-port=9222")
        print("  2. No other process is using port 9222")
        print("  3. You have the correct ChromeDriver installed")
        return None

def select_dropdown_option(driver, select_id, option_value, use_js=False):
    """Select an option from a dropdown, works even if JS is disabled"""
    try:
        # Always try direct method first (works without JS)
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, select_id))
        )
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", select_element)
        human_delay(0.3, 0.6)
        
        if use_js:
            # Try JavaScript method (faster if JS is enabled)
            try:
                script = f"""
                var select = document.getElementById('{select_id}');
                if (select) {{
                    select.value = '{option_value}';
                    var event = new Event('change', {{ bubbles: true }});
                    select.dispatchEvent(event);
                    var inputEvent = new Event('input', {{ bubbles: true }});
                    select.dispatchEvent(inputEvent);
                }}
                """
                driver.execute_script(script)
                human_delay(0.3, 0.7)
                # Verify selection
                selected_value = driver.execute_script(f"return document.getElementById('{select_id}').value;")
                if selected_value == option_value:
                    return
            except:
                pass  # Fall through to direct method
        
        # Direct DOM manipulation method (works without JS)
        # Click to focus
        ActionChains(driver).move_to_element(select_element).pause(
            random.uniform(0.1, 0.3)
        ).click().perform()
        human_delay(0.2, 0.4)
        
        # Use Selenium's Select class for reliable selection
        select_obj = Select(select_element)
        select_obj.select_by_value(option_value)
        human_delay(0.3, 0.7)
            
    except Exception as e:
        print(f"Error selecting dropdown option: {e}")
        raise

def select_radio_button(driver, radio_id, use_js=False):
    """Select a radio button, works even if JS is disabled"""
    try:
        # Always try direct method first (works without JS)
        radio_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, radio_id))
        )
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", radio_element)
        human_delay(0.3, 0.6)
        
        if use_js:
            # Try JavaScript method (faster if JS is enabled)
            try:
                script = f"""
                var radio = document.getElementById('{radio_id}');
                if (radio) {{
                    radio.checked = true;
                    var changeEvent = new Event('change', {{ bubbles: true }});
                    radio.dispatchEvent(changeEvent);
                    var clickEvent = new Event('click', {{ bubbles: true }});
                    radio.dispatchEvent(clickEvent);
                }}
                """
                driver.execute_script(script)
                human_delay(0.3, 0.7)
                # Verify selection
                is_checked = driver.execute_script(f"return document.getElementById('{radio_id}').checked;")
                if is_checked:
                    return
            except:
                pass  # Fall through to direct method
        
        # Direct click method (works without JS)
        # Check if already selected
        if not radio_element.is_selected():
            # Move to element and click (human-like)
            ActionChains(driver).move_to_element(radio_element).pause(
                random.uniform(0.1, 0.3)
            ).click().perform()
            human_delay(0.3, 0.7)
        else:
            print(f"  Radio button '{radio_id}' is already selected")
            
    except Exception as e:
        print(f"Error selecting radio button: {e}")
        raise

def click_button(driver, button_id, use_js=False):
    """Click a button, works even if JS is disabled"""
    try:
        if use_js:
            # Try JavaScript method
            script = f"""
            var button = document.getElementById('{button_id}');
            if (button) {{
                button.click();
            }}
            """
            driver.execute_script(script)
            human_delay(0.5, 1.0)
        else:
            # Direct click method
            button_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, button_id))
            )
            
            # Scroll into view if needed
            driver.execute_script("arguments[0].scrollIntoView(true);", button_element)
            human_delay(0.2, 0.4)
            
            # Move to element and click (human-like)
            ActionChains(driver).move_to_element(button_element).pause(
                random.uniform(0.2, 0.5)
            ).click().perform()
            human_delay(0.5, 1.0)
            
    except Exception as e:
        print(f"Error clicking button: {e}")
        raise

def verify_page_loaded(driver, target_url):
    """Verify that we're on the correct page"""
    try:
        current_url = driver.current_url
        if 'driver-services.dvsa.gov.uk' in current_url and 'obs-web/pages/home' in current_url:
            print(f"✓ Successfully connected to page: {current_url}")
            return True
        else:
            print(f"⚠ Current URL: {current_url}")
            print(f"⚠ Expected URL containing: driver-services.dvsa.gov.uk/obs-web/pages/home")
            return False
    except Exception as e:
        print(f"Error verifying page: {e}")
        return False

def script_second_page():
    """Script the second page (booking form)"""
    print("=" * 60)
    print("Starting DVSA Booking Form Automation")
    print("=" * 60)
    
    # Connect to existing Chrome browser
    print("\n[Step 1] Connecting to existing Chrome browser...")
    driver = connect_to_existing_chrome()
    
    if not driver:
        print("❌ Failed to connect to Chrome browser")
        print("\nPlease start Chrome with remote debugging enabled:")
        print('chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\temp\\chrome_debug"')
        return False
    
    # Verify we're on the correct page
    print("\n[Step 2] Verifying page...")
    if not verify_page_loaded(driver, 'driver-services.dvsa.gov.uk/obs-web/pages/home'):
        print("⚠ Warning: May not be on the correct page, continuing anyway...")
    
    human_delay(1, 2)
    
    # Check if JavaScript is enabled
    try:
        js_enabled = driver.execute_script("return typeof window !== 'undefined'")
        print(f"\n[Info] JavaScript enabled: {js_enabled}")
    except:
        js_enabled = False
        print(f"\n[Info] JavaScript appears to be disabled - using direct DOM methods")
    
    try:
        # Step 1: Select "Car" from the business booking test category dropdown
        print("\n[Step 3] Selecting 'Car' option from test category dropdown...")
        select_dropdown_option(
            driver, 
            'businessBookingTestCategoryRecordId', 
            'TC-B',  # Car option value
            use_js=js_enabled
        )
        print("✓ Selected 'Car' option")
        human_delay(1, 2)
        
        # Step 2: Select "Wood Green (London)" from test centre dropdown
        print("\n[Step 4] Selecting 'Wood Green (London)' from test centre dropdown...")
        select_dropdown_option(
            driver,
            'testcentres',
            '148',  # Wood Green (London) option value
            use_js=js_enabled
        )
        print("✓ Selected 'Wood Green (London)' option")
        human_delay(1, 2)
        
        # Step 3: Select "No" radio button for special needs
        print("\n[Step 5] Selecting 'No' radio button for special needs...")
        select_radio_button(
            driver,
            'specialNeedsChoice-noneeds',  # No option ID
            use_js=js_enabled
        )
        print("✓ Selected 'No' option")
        human_delay(1, 2)
        
        # Step 4: Click the "Book test" button
        print("\n[Step 6] Clicking 'Book test' button...")
        click_button(
            driver,
            'submitSlotSearch',  # Book test button ID
            use_js=js_enabled
        )
        print("✓ Clicked 'Book test' button")
        
        print("\n" + "=" * 60)
        print("✓ First part of scripting completed successfully!")
        print("=" * 60)
        
        # Keep browser open
        print("\nBrowser will remain open. Press Ctrl+C to exit.")
        time.sleep(5)
        
        return True
        
    except TimeoutException as e:
        print(f"\n❌ Timeout error: {e}")
        print("Element not found. Please check if the page has loaded correctly.")
        return False
    except NoSuchElementException as e:
        print(f"\n❌ Element not found: {e}")
        print("Please verify that you're on the correct page.")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Don't close the browser, just keep it open
        pass

if __name__ == "__main__":
    try:
        script_second_page()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()

