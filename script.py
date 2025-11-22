import time
import random
import socket
import subprocess
import platform
import os
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pyautogui
import pygetwindow as gw

# Firefox imports (optional - only needed if using Firefox)
try:
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    FIREFOX_AVAILABLE = True
except ImportError:
    FIREFOX_AVAILABLE = False
    FirefoxOptions = None

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False

def human_delay(min_seconds=1.0, max_seconds=3.0):
    """Add random human-like delay - longer delays to appear more natural"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def longer_human_delay(min_seconds=2.0, max_seconds=5.0):
    """Add longer human-like delay for major actions"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def random_mouse_movement(driver):
    """Perform random mouse movements to simulate human behavior"""
    try:
        # Get window size
        window_size = driver.get_window_size()
        width = window_size['width']
        height = window_size['height']
        
        # Move to random position with slight offset
        x = random.randint(width // 4, 3 * width // 4)
        y = random.randint(height // 4, 3 * height // 4)
        
        # Create small random movements
        for _ in range(random.randint(1, 3)):
            offset_x = random.randint(-50, 50)
            offset_y = random.randint(-50, 50)
            ActionChains(driver).move_by_offset(offset_x, offset_y).perform()
            time.sleep(random.uniform(0.1, 0.3))
        
        # Move back to center
        ActionChains(driver).move_by_offset(-offset_x, -offset_y).perform()
        time.sleep(random.uniform(0.1, 0.2))
    except:
        pass  # Ignore errors in random movements

def human_type(element, text, typing_speed=(0.08, 0.25)):
    """Type text character by character with human-like variable speed"""
    for char in text:
        element.send_keys(char)
        # Variable typing speed - sometimes faster, sometimes slower
        delay = random.uniform(typing_speed[0], typing_speed[1])
        # Occasionally pause longer (simulating thinking or reading)
        if random.random() < 0.15:  # 15% chance
            delay += random.uniform(0.3, 0.8)
        time.sleep(delay)

def random_scroll(driver):
    """Perform random scrolling to simulate human reading behavior"""
    try:
        scroll_amount = random.randint(50, 200)
        if random.random() < 0.5:
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        else:
            driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
        time.sleep(random.uniform(0.3, 0.8))
    except:
        pass

def human_like_action_pause():
    """Pause before major actions as if the user is reading/thinking"""
    # Random pause with occasional longer pauses
    if random.random() < 0.3:  # 30% chance of longer pause
        longer_human_delay(2.0, 4.0)
    else:
        human_delay(1.5, 3.0)

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
    """Check if a port is listening (browser with remote debugging is running)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False

def is_chrome_running():
    """Check if Chrome browser is currently running"""
    if PSUTIL_AVAILABLE:
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if 'chrome' in proc_name and 'chromedriver' not in proc_name:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except:
            pass
    
    # Fallback: try alternative method without psutil
    try:
        system = platform.system()
        if system == "Windows":
            result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=5)
            return 'chrome.exe' in result.stdout.lower()
        elif system == "Darwin":  # macOS
            result = subprocess.run(['pgrep', '-f', 'Google Chrome'], capture_output=True, timeout=5)
            return result.returncode == 0
        else:  # Linux
            result = subprocess.run(['pgrep', '-f', 'chrome'], capture_output=True, timeout=5)
            return result.returncode == 0
    except:
        return False

def detect_browser_type():
    """Detect which browser is running with remote debugging"""
    # Check common ports for different browsers
    if check_port_available(9222):
        return "chrome"  # Chrome uses port 9222
    elif check_port_available(9223):
        return "firefox"  # Firefox uses port 9223 (or you can configure it)
    else:
        return None

def get_chrome_path():
    """Get the path to Chrome executable"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            return chrome_path
    elif system == "Windows":
        # Try common Chrome installation paths on Windows
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    else:  # Linux
        return "google-chrome"  # or "chromium-browser"
    
    return None

def get_default_chrome_user_data_dir():
    """Get the default Chrome user data directory"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/Google/Chrome")
    elif system == "Windows":
        return os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")
    else:  # Linux
        return os.path.expanduser("~/.config/google-chrome")

def connect_to_browser(browser_type=None, auto_start=False):
    """Connect to existing browser (Chrome or Firefox) using remote debugging"""
    if browser_type is None:
        browser_type = detect_browser_type()
    
    if browser_type == "chrome":
        return connect_to_chrome()
    elif browser_type == "firefox":
        return connect_to_firefox()
    else:
        # No browser found with debugging
        print("\n⚠ No browser found with remote debugging enabled")
        
        # Check if Chrome is running normally (without debugging)
        chrome_running = is_chrome_running()
        chrome_path = get_chrome_path()
        
        if chrome_running:
            print("\n⚠ Chrome is currently running, but without remote debugging enabled.")
            print("\n📋 To use your existing Chrome browser with all your tabs:")
            print("   1. Close ALL Chrome windows completely")
            print("   2. Restart Chrome with remote debugging using one of these commands:\n")
            
            system = platform.system()
            if system == "Darwin":  # macOS
                default_user_data = get_default_chrome_user_data_dir()
                print(f"   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\")
                print(f"       --remote-debugging-port=9222 \\")
                print(f"       --user-data-dir=\"{default_user_data}\"")
            elif system == "Windows":
                default_user_data = get_default_chrome_user_data_dir()
                print(f"   \"{chrome_path}\" ^")
                print(f"       --remote-debugging-port=9222 ^")
                print(f"       --user-data-dir=\"{default_user_data}\"")
            else:  # Linux
                default_user_data = get_default_chrome_user_data_dir()
                print(f"   google-chrome \\")
                print(f"       --remote-debugging-port=9222 \\")
                print(f"       --user-data-dir=\"{default_user_data}\"")
            
            print("\n   3. Your existing tabs and bookmarks will be preserved")
            print("   4. Navigate to the DVSA booking page")
            print("   5. Run this script again")
        else:
            print("\n📋 To start Chrome with remote debugging:")
            system = platform.system()
            if system == "Darwin":  # macOS
                default_user_data = get_default_chrome_user_data_dir()
                print(f"   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\")
                print(f"       --remote-debugging-port=9222 \\")
                print(f"       --user-data-dir=\"{default_user_data}\"")
            elif system == "Windows":
                default_user_data = get_default_chrome_user_data_dir()
                if chrome_path:
                    print(f"   \"{chrome_path}\" ^")
                    print(f"       --remote-debugging-port=9222 ^")
                    print(f"       --user-data-dir=\"{default_user_data}\"")
                else:
                    print("   chrome.exe --remote-debugging-port=9222")
            else:  # Linux
                default_user_data = get_default_chrome_user_data_dir()
                print(f"   google-chrome \\")
                print(f"       --remote-debugging-port=9222 \\")
                print(f"       --user-data-dir=\"{default_user_data}\"")
            
            print("\n   Then navigate to the DVSA booking page and run this script again")
        
        return None

def connect_to_chrome():
    """Connect to existing Chrome browser using remote debugging"""
    print("Checking if Chrome is running with remote debugging...")
    if not check_port_available(9222):
        print("\n❌ Chrome is not running with remote debugging on port 9222")
        return None
    
    print("✓ Chrome remote debugging port (9222) is accessible")
    
    try:
        chrome_options = ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        print("Connecting to Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Remove automation detection properties (Chrome-specific CDP)
        try:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    window.chrome = {
                        runtime: {}
                    };
                    Object.defineProperty(navigator, 'permissions', {
                        get: () => ({
                            query: () => Promise.resolve({ state: 'granted' })
                        })
                    });
                '''
            })
        except:
            pass
        
        print("✓ Successfully connected to Chrome")
        
        # Try to find and switch to the correct tab if multiple tabs are open
        try:
            current_url = driver.current_url
            if 'driver-services.dvsa.gov.uk' in current_url:
                print(f"✓ Found DVSA page in current tab: {current_url}")
            else:
                print(f"Current tab URL: {current_url}")
                print("Looking for DVSA tab in other windows...")
                # Get all window handles
                all_handles = driver.window_handles
                found_tab = False
                for handle in all_handles:
                    driver.switch_to.window(handle)
                    if 'driver-services.dvsa.gov.uk' in driver.current_url:
                        print(f"✓ Found DVSA page in another tab, switched to it")
                        found_tab = True
                        break
                if not found_tab:
                    print("⚠ Could not find DVSA page in any open tabs")
                    print("⚠ Please make sure the DVSA booking page is open in your browser")
        except Exception as e:
            print(f"⚠ Could not check tabs: {e}")
        
        human_delay(1.5, 3.0)
        return driver
    except Exception as e:
        print(f"\n❌ Could not connect to Chrome: {e}")
        return None

def connect_to_firefox():
    """Connect to existing Firefox browser using remote debugging"""
    if not FIREFOX_AVAILABLE or FirefoxOptions is None:
        print("\n❌ Firefox support not available")
        print("⚠ Install Firefox WebDriver support or use Chrome instead")
        print("⚠ Firefox options import failed - use Chrome instead")
        return None
        
    print("Checking if Firefox is running with remote debugging...")
    # Firefox typically uses port 9223 or can be configured
    firefox_port = 9223
    if not check_port_available(firefox_port):
        print(f"\n❌ Firefox is not running with remote debugging on port {firefox_port}")
        print("\n⚠ To start Firefox with remote debugging:")
        print("  /Applications/Firefox.app/Contents/MacOS/firefox --marionette --remote-debugging-port 9223")
        print("\n⚠ Note: Firefox remote debugging works differently than Chrome")
        print("⚠ Consider using Chrome for better compatibility")
        return None
    
    print(f"✓ Firefox remote debugging port ({firefox_port}) is accessible")
    
    try:
        print("Connecting to Firefox...")
        
        # Firefox uses Marionette protocol, different from Chrome's CDP
        # Note: Connecting to existing Firefox instance is more complex
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--marionette")
        
        # Firefox doesn't support connecting to existing instance the same way as Chrome
        # You might need to start Firefox programmatically or use different approach
        print("⚠ Note: Firefox remote debugging requires geckodriver and different setup")
        print("⚠ This will create a new Firefox instance (not connect to existing)")
        print("⚠ For best results, use Chrome which supports connecting to existing instances")
        
        # Try to create new Firefox instance (won't connect to existing)
        driver = webdriver.Firefox(options=firefox_options)
        
        # Firefox-specific anti-detection
        try:
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
        except:
            pass
        
        print("✓ Connected to Firefox (new instance)")
        print("⚠ Remember: This is a NEW Firefox window, not your existing one")
        human_delay(1.5, 3.0)
        return driver
    except Exception as e:
        print(f"\n❌ Could not connect to Firefox: {e}")
        print("⚠ Firefox requires geckodriver. Install it separately:")
        print("  macOS: brew install geckodriver")
        print("  Or download from: https://github.com/mozilla/geckodriver/releases")
        print("⚠ Recommendation: Use Chrome for easier setup")
        return None

# Alias for backward compatibility
def connect_to_existing_chrome():
    """Backward compatibility - connects to Chrome or auto-detects browser"""
    return connect_to_browser("chrome")

def launch_new_chrome():
    """Launch a new Chrome browser instance (normal mode - no debugging required)"""
    print("Launching new Chrome browser...")
    
    try:
        chrome_options = ChromeOptions()
        # Add anti-detection options
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Optional: Add user agent to appear more natural
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        print("Creating Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Remove automation detection properties (Chrome-specific CDP)
        try:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    window.chrome = {
                        runtime: {}
                    };
                    Object.defineProperty(navigator, 'permissions', {
                        get: () => ({
                            query: () => Promise.resolve({ state: 'granted' })
                        })
                    });
                '''
            })
        except:
            pass
        
        print("✓ Chrome browser launched successfully")
        human_delay(1.5, 3.0)
        return driver
    except Exception as e:
        print(f"\n❌ Could not launch Chrome: {e}")
        print("⚠ Make sure ChromeDriver is installed and in your PATH")
        return None

def select_dropdown_option(driver, select_id, option_value, use_js=False):
    """Select an option from a dropdown, works even if JS is disabled"""
    try:
        # Try multiple selector strategies
        select_element = None
        selectors = [
            (By.ID, select_id),
            (By.NAME, select_id),
            (By.CSS_SELECTOR, f"#{select_id}"),
            (By.CSS_SELECTOR, f"[name='{select_id}']"),
            (By.CSS_SELECTOR, f"select[id='{select_id}']"),
            (By.XPATH, f"//select[@id='{select_id}']"),
        ]
        
        for selector_type, selector_value in selectors:
            try:
                select_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                if select_element:
                    print(f"  Found dropdown using {selector_type}")
                    break
            except:
                continue
        
        if not select_element:
            raise Exception(f"Could not find dropdown element with ID/name: {select_id}")
        
        # Human-like behavior: random mouse movement
        random_mouse_movement(driver)
        human_delay(0.8, 1.5)
        
        # Scroll into view smoothly
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", select_element)
        human_delay(1.0, 2.0)
        
        # Random scroll to appear more natural
        if random.random() < 0.5:
            random_scroll(driver)
        
        # Wait for dropdown to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(select_element))
        
        # Human-like pause before interaction
        human_delay(0.8, 1.5)
        
        if use_js:
            # Try JavaScript method first (faster if JS is enabled)
            try:
                script = f"""
                var select = document.getElementById('{select_id}');
                if (!select) {{
                    select = document.querySelector("select[name='{select_id}']");
                }}
                if (select) {{
                    select.value = '{option_value}';
                    var changeEvent = new Event('change', {{ bubbles: true }});
                    select.dispatchEvent(changeEvent);
                    var inputEvent = new Event('input', {{ bubbles: true }});
                    select.dispatchEvent(inputEvent);
                    return select.value;
                }}
                return null;
                """
                result = driver.execute_script(script)
                human_delay(0.5, 1.0)
                # Verify selection
                if result == option_value:
                    print(f"  ✓ Selected via JavaScript")
                    return
                else:
                    print(f"  ⚠ JavaScript selection returned: {result}, trying direct method...")
            except Exception as e:
                print(f"  ⚠ JavaScript method failed: {e}, trying direct method...")
        
        # Human-like click with longer pause
        ActionChains(driver).move_to_element(select_element).pause(
            random.uniform(0.5, 1.0)
        ).click().perform()
        human_delay(1.0, 2.0)  # Longer delay after clicking
        
        # Try multiple selection methods
        select_obj = Select(select_element)
        
        # Method 1: Select by value
        try:
            select_obj.select_by_value(option_value)
            human_delay(0.5, 1.0)
            # Verify selection
            selected_value = select_element.get_attribute('value')
            if selected_value == option_value:
                print(f"  ✓ Selected by value: {option_value}")
                return
        except Exception as e:
            print(f"  ⚠ Select by value failed: {e}, trying by visible text...")
        
        # Method 2: Select by visible text (if we know the text)
        # This is a fallback - we'll skip this for now
        
        # Method 3: Direct JavaScript fallback
        try:
            driver.execute_script(f"""
                var select = arguments[0];
                select.value = '{option_value}';
                var event = new Event('change', {{ bubbles: true }});
                select.dispatchEvent(event);
            """, select_element)
            human_delay(0.5, 1.0)
            selected_value = select_element.get_attribute('value')
            if selected_value == option_value:
                print(f"  ✓ Selected via direct JavaScript on element")
                return
        except Exception as e:
            print(f"  ⚠ Direct JavaScript on element failed: {e}")
        
        # Final verification
        final_value = select_element.get_attribute('value')
        if final_value == option_value:
            print(f"  ✓ Selection verified: {final_value}")
        else:
            raise Exception(f"Selection failed. Expected: {option_value}, Got: {final_value}")
            
    except Exception as e:
        print(f"  ❌ Error selecting dropdown option: {e}")
        raise

def select_autocomplete_option(driver, input_id, search_text, option_text, use_js=False):
    """Select an option from an autocomplete input field"""
    try:
        # Find the autocomplete input field
        input_element = None
        selectors = [
            (By.ID, input_id),
            (By.CSS_SELECTOR, f"#{input_id}"),
            (By.CSS_SELECTOR, f"input[id='{input_id}']"),
            (By.XPATH, f"//input[@id='{input_id}']"),
        ]
        
        for selector_type, selector_value in selectors:
            try:
                input_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                if input_element:
                    print(f"  Found autocomplete input using {selector_type}")
                    break
            except:
                continue
        
        if not input_element:
            raise Exception(f"Could not find autocomplete input with ID: {input_id}")
        
        # Human-like behavior: random mouse movement
        random_mouse_movement(driver)
        human_delay(1.0, 2.0)
        
        # Scroll into view smoothly
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", input_element)
        human_delay(1.5, 2.5)
        
        # Random scroll to appear more natural
        if random.random() < 0.5:
            random_scroll(driver)
            human_delay(0.5, 1.0)
        
        # Wait for input to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(input_element))
        
        # Human-like pause before interacting
        human_like_action_pause()
        
        # Clear the input field first
        input_element.clear()
        human_delay(0.8, 1.5)
        
        # Click to focus with human-like movement
        ActionChains(driver).move_to_element(input_element).pause(
            random.uniform(0.8, 1.5)
        ).click().perform()
        human_delay(1.0, 2.0)  # Pause after clicking
        
        # Type the search text using human-like typing function
        human_type(input_element, search_text, typing_speed=(0.12, 0.30))
        
        human_delay(2.0, 3.5)  # Wait longer for autocomplete to appear
        
        # Wait for autocomplete dropdown to appear and be visible
        # Try multiple selectors for the autocomplete dropdown
        autocomplete_dropdown = None
        print("  Waiting for autocomplete dropdown to appear...")
        
        # First, wait for any visible dropdown/menu
        try:
            # Wait for dropdown to be visible (check multiple times)
            for attempt in range(15):  # Wait up to 15 seconds
                try:
                    # Check for ui-autocomplete dropdown
                    dropdowns = driver.find_elements(By.CSS_SELECTOR, "ul.ui-autocomplete")
                    for dd in dropdowns:
                        if dd.is_displayed():
                            autocomplete_dropdown = dd
                            print(f"  Found visible autocomplete dropdown (attempt {attempt + 1})")
                            break
                    
                    if not autocomplete_dropdown:
                        # Try finding by any visible list with class containing menu
                        dropdowns = driver.find_elements(By.XPATH, "//ul[contains(@class, 'ui-menu')]")
                        for dd in dropdowns:
                            if dd.is_displayed() and 'display: none' not in dd.get_attribute('style'):
                                autocomplete_dropdown = dd
                                print(f"  Found visible menu dropdown (attempt {attempt + 1})")
                                break
                    
                    if autocomplete_dropdown:
                        break
                except:
                    pass
                
                time.sleep(0.5)
                human_delay(0.2, 0.3)
            
            if not autocomplete_dropdown:
                print("  ⚠ Autocomplete dropdown not found, trying to find options directly...")
        except Exception as e:
            print(f"  ⚠ Error finding dropdown: {e}, trying to find options directly...")
        
        # Find and click the option containing the desired text
        option_element = None
        print(f"  Looking for option containing: '{option_text}'...")
        
        # Wait for the option to appear (with or without dropdown container)
        option_selectors = [
            (By.XPATH, f"//li[contains(@class, 'ui-menu-item') and contains(., '{option_text}')]"),
            (By.XPATH, f"//li[@class='ui-menu-item']/a[contains(., '{option_text}')]"),
            (By.XPATH, f"//li[contains(., '{option_text}')]"),
            (By.XPATH, f"//*[contains(@class, 'ui-menu-item') and contains(., '{option_text}')]"),
            (By.PARTIAL_LINK_TEXT, option_text),
        ]
        
        # Wait for option to appear (up to 10 seconds)
        for attempt in range(20):
            for selector_type, selector_value in option_selectors:
                try:
                    elements = driver.find_elements(selector_type, selector_value)
                    for elem in elements:
                        if elem.is_displayed():
                            option_element = elem
                            print(f"  Found autocomplete option using {selector_type} (attempt {attempt + 1})")
                            break
                    if option_element:
                        break
                except:
                    continue
            
            if option_element:
                break
            
            time.sleep(0.5)
        
        # Fallback: search all visible list items
        if not option_element:
            try:
                print("  Trying fallback: searching all visible menu items...")
                all_options = driver.find_elements(By.XPATH, "//li[contains(@class, 'ui-menu-item')]")
                for opt in all_options:
                    try:
                        if opt.is_displayed() and option_text.lower() in opt.text.lower():
                            option_element = opt
                            print(f"  Found option by text search: {opt.text}")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"  ⚠ Could not find option by searching: {e}")
        
        if not option_element:
            raise Exception(f"Could not find autocomplete option with text: '{option_text}'. Make sure you typed '{search_text}' and the dropdown appeared.")
        
        # Human-like hover before clicking
        ActionChains(driver).move_to_element(option_element).pause(
            random.uniform(0.8, 1.5)
        ).pause(random.uniform(0.3, 0.7)).click().perform()
        human_delay(1.5, 3.0)  # Longer delay after selection
        
        # Verify selection by checking if input value contains the option text
        input_value = input_element.get_attribute('value')
        if option_text.lower() in input_value.lower():
            print(f"  ✓ Selected autocomplete option: {input_value}")
            return
        else:
            print(f"  ⚠ Selection might not have worked. Input value: {input_value}, Expected: {option_text}")
            # Try one more time with direct click
            time.sleep(1)
            ActionChains(driver).move_to_element(option_element).click().perform()
            human_delay(0.5, 1.0)
            
    except Exception as e:
        print(f"  ❌ Error selecting autocomplete option: {e}")
        raise

def select_radio_button(driver, radio_id, use_js=False):
    """Select a radio button, works even if JS is disabled"""
    try:
        # Try multiple selector strategies
        radio_element = None
        label_element = None
        
        selectors = [
            (By.ID, radio_id),
            (By.CSS_SELECTOR, f"#{radio_id}"),
            (By.CSS_SELECTOR, f"input[type='radio'][id='{radio_id}']"),
            (By.CSS_SELECTOR, f"input[type='radio'][name='{radio_id.split('-')[0]}'][value='{radio_id.split('-')[1] if '-' in radio_id else ''}']"),
            (By.XPATH, f"//input[@type='radio' and @id='{radio_id}']"),
        ]
        
        for selector_type, selector_value in selectors:
            try:
                radio_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                if radio_element:
                    print(f"  Found radio button using {selector_type}")
                    break
            except:
                continue
        
        # If radio not found by ID, try finding by name and value
        if not radio_element:
            # Try to parse ID like "specialNeedsChoice-noneeds" -> name="specialNeedsChoice", value="noneeds"
            if '-' in radio_id:
                name_part, value_part = radio_id.rsplit('-', 1)
                try:
                    radio_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f"input[type='radio'][name='{name_part}'][value='{value_part}']"))
                    )
                    if radio_element:
                        print(f"  Found radio button by name='{name_part}' and value='{value_part}'")
                except:
                    pass
        
        # Try to find associated label
        if radio_element:
            try:
                # Get the 'for' attribute or find label by parent
                radio_id_attr = radio_element.get_attribute('id')
                if radio_id_attr:
                    label_element = driver.find_element(By.CSS_SELECTOR, f"label[for='{radio_id_attr}']")
            except:
                try:
                    # Try finding label that contains the radio
                    label_element = radio_element.find_element(By.XPATH, "./ancestor::label[1]")
                except:
                    pass
        
        if not radio_element:
            raise Exception(f"Could not find radio button with ID: {radio_id}")
        
        # Human-like behavior: random mouse movement
        random_mouse_movement(driver)
        human_delay(1.0, 2.0)
        
        # Scroll into view smoothly
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", radio_element)
        human_delay(1.5, 2.5)
        
        # Random scroll to appear more natural
        if random.random() < 0.5:
            random_scroll(driver)
            human_delay(0.5, 1.0)
        
        # Human-like pause before checking/interacting
        human_delay(0.8, 1.5)
        
        # Check if already selected
        if radio_element.is_selected():
            print(f"  ✓ Radio button '{radio_id}' is already selected")
            return
        
        if use_js:
            # Try JavaScript method first
            try:
                radio_id_attr = radio_element.get_attribute('id')
                script = f"""
                var radio = document.getElementById('{radio_id_attr}');
                if (!radio) {{
                    radio = arguments[0];
                }}
                if (radio) {{
                    radio.checked = true;
                    var changeEvent = new Event('change', {{ bubbles: true }});
                    radio.dispatchEvent(changeEvent);
                    var clickEvent = new Event('click', {{ bubbles: true }});
                    radio.dispatchEvent(clickEvent);
                    return radio.checked;
                }}
                return false;
                """
                result = driver.execute_script(script, radio_element)
                human_delay(0.5, 1.0)
                if result:
                    print(f"  ✓ Selected via JavaScript")
                    return
            except Exception as e:
                print(f"  ⚠ JavaScript method failed: {e}, trying click method...")
        
        # Try clicking the label first (more reliable)
        if label_element:
            try:
                ActionChains(driver).move_to_element(label_element).pause(
                    random.uniform(0.2, 0.4)
                ).click().perform()
                human_delay(0.5, 1.0)
                if radio_element.is_selected():
                    print(f"  ✓ Selected by clicking label")
                    return
            except Exception as e:
                print(f"  ⚠ Label click failed: {e}, trying direct radio click...")
        
        # Direct click on radio button with human-like movement
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(radio_element))
        ActionChains(driver).move_to_element(radio_element).pause(
            random.uniform(0.8, 1.5)
        ).pause(random.uniform(0.3, 0.7)).click().perform()
        human_delay(1.5, 2.5)  # Longer delay after clicking
        
        # Verify selection
        if radio_element.is_selected():
            print(f"  ✓ Radio button selected")
        else:
            # Last resort: force via JavaScript
            driver.execute_script("arguments[0].checked = true; arguments[0].click();", radio_element)
            human_delay(0.5, 1.0)
            if not radio_element.is_selected():
                raise Exception(f"Failed to select radio button '{radio_id}'")
            print(f"  ✓ Radio button selected via force")
            
    except Exception as e:
        print(f"  ❌ Error selecting radio button: {e}")
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
            
            # Human-like behavior: random mouse movement
            random_mouse_movement(driver)
            human_delay(1.0, 2.0)
            
            # Scroll into view smoothly
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button_element)
            human_delay(1.5, 2.5)
            
            # Random scroll to appear more natural
            if random.random() < 0.5:
                random_scroll(driver)
                human_delay(0.5, 1.0)
            
            # Human-like pause before clicking
            human_delay(1.0, 2.0)
            
            # Move to element and click (human-like with longer pause)
            ActionChains(driver).move_to_element(button_element).pause(
                random.uniform(1.0, 2.0)
            ).pause(random.uniform(0.5, 1.0)).click().perform()
            human_delay(2.0, 3.5)  # Longer delay after clicking button
            
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

def wait_for_page_load(driver, timeout=15):
    """Wait for page to load completely"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        human_delay(2.0, 4.0)  # Additional human-like delay
        return True
    except:
        return False

def handle_timeout_dialog(driver):
    """Check for and handle the timeout expiration dialog"""
    try:
        # Check if the timeout dialog is present
        try:
            # Look for the "Okay, thanks" button with id="slotTimeoutClose"
            timeout_button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.ID, "slotTimeoutClose"))
            )
            
            if timeout_button.is_displayed():
                print("  ⚠ Timeout dialog detected - clicking 'Okay, thanks' button...")
                
                # Human-like pause before clicking
                human_delay(1.5, 2.5)
                random_mouse_movement(driver)
                
                # Scroll into view if needed
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", timeout_button)
                human_delay(1.0, 2.0)
                
                # Wait for button to be clickable
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable(timeout_button))
                
                # Human-like click
                ActionChains(driver).move_to_element(timeout_button).pause(
                    random.uniform(1.0, 2.0)
                ).click().perform()
                
                print("  ✓ Clicked 'Okay, thanks' button")
                
                # Wait for dialog to close and page to update
                wait_for_page_load(driver)
                longer_human_delay(2.0, 4.0)
                
                return True
        except TimeoutException:
            # Dialog not present, which is fine
            return False
        except Exception as e:
            # Try alternative selector
            try:
                # Try finding by class
                timeout_button = driver.find_element(By.CSS_SELECTOR, "a.closeDialogAction#slotTimeoutClose")
                if timeout_button.is_displayed():
                    print("  ⚠ Timeout dialog detected (alternative selector) - clicking 'Okay, thanks' button...")
                    human_delay(1.5, 2.5)
                    ActionChains(driver).move_to_element(timeout_button).pause(
                        random.uniform(1.0, 2.0)
                    ).click().perform()
                    print("  ✓ Clicked 'Okay, thanks' button")
                    wait_for_page_load(driver)
                    longer_human_delay(2.0, 4.0)
                    return True
            except:
                pass
            
            # If button not found by ID, try JavaScript click
            try:
                timeout_button = driver.find_element(By.ID, "slotTimeoutClose")
                if timeout_button:
                    print("  ⚠ Timeout dialog detected - clicking via JavaScript...")
                    driver.execute_script("arguments[0].click();", timeout_button)
                    wait_for_page_load(driver)
                    longer_human_delay(2.0, 4.0)
                    print("  ✓ Clicked 'Okay, thanks' button (via JavaScript)")
                    return True
            except:
                pass
            
            return False
    except Exception as e:
        # Dialog check failed, but that's okay - continue
        return False

def find_available_days(driver):
    """Find all days with available tests in the current week view"""
    try:
        # Wait for the table to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "browseslots"))
        )
        human_delay(1.0, 2.0)
        
        # Find all cells with available slots
        available_days = []
        try:
            # Find all td elements with class "day slotsavailable" (has available tests)
            day_cells = driver.find_elements(By.CSS_SELECTOR, "td.day.slotsavailable")
            
            for cell in day_cells:
                try:
                    if not cell.is_displayed():
                        continue
                    
                    # Look for "view" link which indicates availability
                    # Try multiple selectors for the view link
                    view_link = None
                    selectors = [
                        "a[href*='eventId=searchForDailySlots']",
                        "a[href*='searchForDailySlots']",
                        "a:contains('view')",
                        "a.largetext"
                    ]
                    
                    for selector in selectors:
                        try:
                            links = cell.find_elements(By.CSS_SELECTOR, selector)
                            for link in links:
                                if link.is_displayed():
                                    href = link.get_attribute("href") or ""
                                    text = link.text.lower()
                                    # Check if it's a view link
                                    if "searchForDailySlots" in href or "view" in text:
                                        view_link = link
                                        break
                            if view_link:
                                break
                        except:
                            continue
                    
                    # Alternative: look for any link in the cell
                    if not view_link:
                        try:
                            all_links = cell.find_elements(By.TAG_NAME, "a")
                            for link in all_links:
                                if link.is_displayed():
                                    href = link.get_attribute("href") or ""
                                    if "searchForDailySlots" in href or "eventId" in href:
                                        view_link = link
                                        break
                        except:
                            pass
                    
                    if view_link:
                        # Extract day name from headers attribute or table column
                        day_name = cell.get_attribute("headers")
                        if not day_name or day_name == "":
                            # Try to get from table header by column index
                            try:
                                # Get the column index of this cell
                                cells_in_row = cell.find_elements(By.XPATH, "./preceding-sibling::td")
                                col_index = len(cells_in_row) + 1  # +1 for header row
                                
                                # Find the header for this column
                                table = cell.find_element(By.XPATH, "./ancestor::table")
                                headers = table.find_elements(By.XPATH, ".//th")
                                if col_index < len(headers):
                                    day_name = headers[col_index].text.strip()
                                else:
                                    # Try getting from thead
                                    thead = table.find_elements(By.TAG_NAME, "thead")
                                    if thead:
                                        th_elements = thead[0].find_elements(By.TAG_NAME, "th")
                                        if col_index < len(th_elements):
                                            day_name = th_elements[col_index].text.strip()
                            except:
                                day_name = "Unknown"
                        
                        # Clean up day name
                        if day_name:
                            day_name = day_name.strip()
                            # Extract just the day name if it contains date info
                            if " " in day_name:
                                parts = day_name.split()
                                day_name = parts[0]  # Get first part (e.g., "Mon", "Tue")
                        
                        available_days.append({
                            'cell': cell,
                            'link': view_link,
                            'day': day_name or "Unknown"
                        })
                except Exception as e:
                    continue
        except Exception as e:
            print(f"  ⚠ Error finding available days: {e}")
        
        return available_days
    except Exception as e:
        print(f"  ❌ Error in find_available_days: {e}")
        return []

def click_navigation_button(driver, button_id, button_name):
    """Click a navigation button (Previous Week, Next Week, Return to search results)"""
    try:
        human_like_action_pause()
        random_scroll(driver)
        random_mouse_movement(driver)
        
        # Wait for button to be present
        button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, button_id))
        )
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
        human_delay(1.5, 2.5)
        
        # Wait for button to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button))
        
        # Human-like click
        ActionChains(driver).move_to_element(button).pause(
            random.uniform(1.0, 2.0)
        ).click().perform()
        
        print(f"  ✓ Clicked '{button_name}' button")
        
        # Wait for page to load after navigation
        wait_for_page_load(driver)
        longer_human_delay(3.0, 5.0)  # Longer delay after navigation
        
        return True
    except TimeoutException:
        print(f"  ⚠ '{button_name}' button not found (may not be available)")
        return False
    except Exception as e:
        print(f"  ❌ Error clicking '{button_name}' button: {e}")
        return False

def check_navigation_buttons(driver):
    """Check which navigation buttons are available"""
    has_previous_week = False
    has_next_week = False
    has_return_to_search = False
    
    try:
        # Check for Previous Week button
        try:
            driver.find_element(By.ID, "searchForWeeklySlotsPreviousWeek")
            has_previous_week = True
        except:
            pass
        
        # Check for Next Week button
        try:
            driver.find_element(By.ID, "searchForWeeklySlotsNextWeek")
            has_next_week = True
        except:
            pass
        
        # Check for Return to search results button
        try:
            driver.find_element(By.ID, "returnToSearchResults")
            has_return_to_search = True
        except:
            pass
    except:
        pass
    
    return has_previous_week, has_next_week, has_return_to_search

def reserve_all_tests_for_day(driver):
    """Reserve all available tests on the current day's time slot page"""
    try:
        print("    Looking for 'Reserve test' buttons...")
        
        # Wait for the page to load
        wait_for_page_load(driver)
        human_delay(2.0, 3.0)
        
        # Find all Reserve test buttons
        reserve_buttons = []
        try:
            # Look for reserve buttons by various selectors
            selectors = [
                "a[id^='reserve_']",
                "span.greybutton a",
                "a[href*='eventId=reserveSlot']"
            ]
            
            for selector in selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            # Check if it's a reserve button
                            href = btn.get_attribute("href") or ""
                            if "reserveSlot" in href or btn.get_attribute("id", "").startswith("reserve_"):
                                if btn not in reserve_buttons:
                                    reserve_buttons.append(btn)
                except:
                    continue
        except Exception as e:
            print(f"    ⚠ Error finding reserve buttons: {e}")
        
        if not reserve_buttons:
            print("    ℹ No 'Reserve test' buttons found for this day")
            return 0
        
        print(f"    Found {len(reserve_buttons)} 'Reserve test' button(s)")
        
        # Click each reserve button
        reserved_count = 0
        for i, button in enumerate(reserve_buttons, 1):
            try:
                if not button.is_displayed():
                    continue
                
                print(f"    Reserving test {i}/{len(reserve_buttons)}...")
                
                # Check for timeout dialog before reserving
                handle_timeout_dialog(driver)
                
                # Human-like behavior before clicking
                random_mouse_movement(driver)
                human_delay(1.5, 3.0)
                
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                human_delay(1.0, 2.0)
                
                # Wait for button to be clickable
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button))
                
                # Human-like click
                ActionChains(driver).move_to_element(button).pause(
                    random.uniform(1.0, 2.0)
                ).click().perform()
                
                print(f"      ✓ Reserved test {i}")
                
                # Wait for page to update
                wait_for_page_load(driver)
                
                # Check for timeout dialog after reserving
                handle_timeout_dialog(driver)
                
                longer_human_delay(2.0, 4.0)  # Longer delay after reserving
                
                # Re-find buttons after page update (in case DOM changed)
                try:
                    reserve_buttons = driver.find_elements(By.CSS_SELECTOR, "a[id^='reserve_']")
                except:
                    pass
                
                reserved_count += 1
                
            except Exception as e:
                print(f"      ⚠ Error reserving test {i}: {e}")
                continue
        
        print(f"    ✓ Reserved {reserved_count} test(s) for this day")
        return reserved_count
        
    except Exception as e:
        print(f"    ❌ Error in reserve_all_tests_for_day: {e}")
        return 0

def click_available_day(driver, day_info):
    """Click on an available day to view its time slots"""
    try:
        print(f"  Clicking on available day: {day_info['day']}...")
        
        # Check for timeout dialog before clicking
        handle_timeout_dialog(driver)
        
        human_like_action_pause()
        random_scroll(driver)
        random_mouse_movement(driver)
        
        # Scroll the cell into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", day_info['cell'])
        human_delay(1.5, 2.5)
        
        # Try to re-find the link in case DOM changed
        try:
            view_link = day_info['link']
            if not view_link.is_displayed() or not view_link.is_enabled():
                # Re-find the link
                cell = day_info['cell']
                links = cell.find_elements(By.TAG_NAME, "a")
                for link in links:
                    if link.is_displayed():
                        href = link.get_attribute("href") or ""
                        if "searchForDailySlots" in href or "eventId" in href:
                            view_link = link
                            break
        except:
            view_link = day_info['link']
        
        # Wait for link to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(view_link))
        
        # Human-like click
        ActionChains(driver).move_to_element(view_link).pause(
            random.uniform(0.5, 1.0)
        ).move_by_offset(random.randint(-5, 5), random.randint(-5, 5)).pause(
            random.uniform(0.5, 1.0)
        ).click().perform()
        
        print(f"  ✓ Clicked on {day_info['day']}")
        
        # Wait for page to load
        wait_for_page_load(driver)
        
        # Check for timeout dialog after clicking
        handle_timeout_dialog(driver)
        
        longer_human_delay(3.0, 5.0)
        
        return True
    except Exception as e:
        print(f"  ❌ Error clicking available day: {e}")
        # Try alternative: click via JavaScript
        try:
            driver.execute_script("arguments[0].click();", day_info['link'])
            wait_for_page_load(driver)
            longer_human_delay(3.0, 5.0)
            print(f"  ✓ Clicked on {day_info['day']} (via JavaScript)")
            return True
        except:
            return False

def scrape_weekly_availability(driver, direction="forward"):
    """Main function to scrape weekly availability and reserve tests"""
    print("\n" + "=" * 60)
    print("Starting Weekly Availability Scraping")
    print("=" * 60)
    
    iteration_count = 0
    max_iterations = 1000  # Safety limit
    total_reserved = 0
    
    try:
        while iteration_count < max_iterations:
            iteration_count += 1
            print(f"\n{'='*60}")
            print(f"Iteration {iteration_count}")
            print(f"{'='*60}")
            
            # Wait for page to load
            wait_for_page_load(driver)
            human_delay(2.0, 3.0)
            
            # Check for timeout dialog and handle it
            handle_timeout_dialog(driver)
            
            # Check current URL to understand what page we're on
            current_url = driver.current_url
            print(f"Current page: {current_url[:80]}...")
            
            # Check which navigation buttons are available
            has_prev_week, has_next_week, has_return = check_navigation_buttons(driver)
            print(f"Navigation: Previous Week={has_prev_week}, Next Week={has_next_week}, Return={has_return}")
            
            # If we're on the time slot page (has return button), go back
            if has_return:
                print("  On time slot page, returning to search results...")
                if click_navigation_button(driver, "returnToSearchResults", "Return to search results"):
                    # Check for dialog again after returning
                    handle_timeout_dialog(driver)
                    continue
                else:
                    print("  ⚠ Could not return to search results")
                    break
            
            # Check for timeout dialog before searching for available days
            handle_timeout_dialog(driver)
            
            # Find available days in current week
            print("  Searching for available test days...")
            available_days = find_available_days(driver)
            
            if available_days:
                print(f"  ✓ Found {len(available_days)} day(s) with available tests")
                
                # Process each available day
                for day_idx, day_info in enumerate(available_days, 1):
                    print(f"\n  Processing day {day_idx}/{len(available_days)}: {day_info['day']}")
                    
                    # Click on the available day
                    if click_available_day(driver, day_info):
                        # Reserve all tests for this day
                        reserved = reserve_all_tests_for_day(driver)
                        total_reserved += reserved
                        
                        # Return to search results
                        print("  Returning to search results...")
                        if click_navigation_button(driver, "returnToSearchResults", "Return to search results"):
                            # Check for timeout dialog after returning
                            handle_timeout_dialog(driver)
                            # Wait a bit before processing next day
                            longer_human_delay(3.0, 5.0)
                        else:
                            print("  ⚠ Could not return to search results, trying to continue...")
                            # Try to go back or refresh
                            try:
                                driver.back()
                                wait_for_page_load(driver)
                                handle_timeout_dialog(driver)
                                longer_human_delay(3.0, 5.0)
                            except:
                                pass
            else:
                print("  ℹ No available test days found in this week")
                
                # Navigate to next/previous week based on direction
                if direction == "forward":
                    if has_next_week:
                        print("  Clicking 'Next Week'...")
                        if click_navigation_button(driver, "searchForWeeklySlotsNextWeek", "Next Week"):
                            # Check for timeout dialog after navigation
                            handle_timeout_dialog(driver)
                            direction = "forward"  # Continue forward
                        else:
                            # Reached end, switch to backward
                            print("  Reached end of date range, switching to Previous Week...")
                            direction = "backward"
                            if has_prev_week:
                                click_navigation_button(driver, "searchForWeeklySlotsPreviousWeek", "Previous Week")
                                handle_timeout_dialog(driver)
                    else:
                        # No next week button, switch to backward
                        print("  No 'Next Week' button, switching to Previous Week...")
                        direction = "backward"
                        if has_prev_week:
                            click_navigation_button(driver, "searchForWeeklySlotsPreviousWeek", "Previous Week")
                            handle_timeout_dialog(driver)
                else:  # direction == "backward"
                    if has_prev_week:
                        print("  Clicking 'Previous Week'...")
                        if click_navigation_button(driver, "searchForWeeklySlotsPreviousWeek", "Previous Week"):
                            # Check for timeout dialog after navigation
                            handle_timeout_dialog(driver)
                            direction = "backward"  # Continue backward
                        else:
                            # Reached start, switch to forward
                            print("  Reached start of date range, switching to Next Week...")
                            direction = "forward"
                            if has_next_week:
                                click_navigation_button(driver, "searchForWeeklySlotsNextWeek", "Next Week")
                                handle_timeout_dialog(driver)
                    else:
                        # No previous week button, switch to forward
                        print("  No 'Previous Week' button, switching to Next Week...")
                        direction = "forward"
                        if has_next_week:
                            click_navigation_button(driver, "searchForWeeklySlotsNextWeek", "Next Week")
                            handle_timeout_dialog(driver)
            
            # Random longer pause between iterations
            longer_human_delay(4.0, 7.0)
        
        print(f"\n{'='*60}")
        print(f"Scraping completed!")
        print(f"Total iterations: {iteration_count}")
        print(f"Total tests reserved: {total_reserved}")
        print(f"{'='*60}")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠ Scraping interrupted by user")
        print(f"Total tests reserved so far: {total_reserved}")
    except Exception as e:
        print(f"\n❌ Error in scraping loop: {e}")
        import traceback
        traceback.print_exc()
    
    return total_reserved

def script_second_page():
    """Script the second page (booking form)"""
    print("=" * 60)
    print("Starting DVSA Booking Form Automation")
    print("=" * 60)
    
    # Connect to existing browser tab (must have remote debugging enabled)
    print("\n[Step 1] Connecting to existing browser tab...")
    print("Looking for Chrome browser with remote debugging enabled...")
    driver = connect_to_browser(auto_start=False)  # Don't auto-start, use existing browser
    
    if not driver:
        print("❌ Failed to connect to browser")
        return False
    
    # Check if we're on the correct page, if not try to find it or navigate to it
    print("\n[Step 2] Checking current page...")
    current_url = driver.current_url
    target_url = "https://driver-services.dvsa.gov.uk/obs-web/pages/home"
    
    if 'driver-services.dvsa.gov.uk' in current_url:
        print(f"✓ Found DVSA page: {current_url}")
        if 'obs-web/pages/home' not in current_url:
            print("⚠ Not on the booking form page, navigating...")
            try:
                driver.get(target_url)
                print(f"✓ Navigated to: {target_url}")
                human_delay(3.0, 5.0)
            except Exception as e:
                print(f"⚠ Could not navigate: {e}")
    else:
        print(f"Current URL: {current_url}")
        print("DVSA page not found, navigating to booking page...")
        try:
            driver.get(target_url)
            print(f"✓ Navigated to: {target_url}")
            human_delay(3.0, 5.0)
        except Exception as e:
            print(f"⚠ Could not navigate: {e}")
            print("⚠ Please manually navigate to the DVSA booking page")
    
    # Verify we're on the correct page
    print("\n[Step 3] Verifying page...")
    if not verify_page_loaded(driver, 'driver-services.dvsa.gov.uk/obs-web/pages/home'):
        print("⚠ Warning: May not be on the correct page")
        print("⚠ Please make sure you have the DVSA booking page open")
        print("⚠ Continuing anyway...")
    
    # Human-like behavior: random scrolling and mouse movement to simulate reading
    random_scroll(driver)
    random_mouse_movement(driver)
    longer_human_delay(3.0, 6.0)  # Longer initial delay as if reading the page
    
    # Check if JavaScript is enabled
    try:
        js_enabled = driver.execute_script("return typeof window !== 'undefined'")
        print(f"\n[Info] JavaScript enabled: {js_enabled}")
    except:
        js_enabled = False
        print(f"\n[Info] JavaScript appears to be disabled - using direct DOM methods")
    
    try:
        # Step 1: Select "Car" from the business booking test category dropdown
        print("\n[Step 4] Selecting 'Car' option from test category dropdown...")
        # Human-like pause before action
        human_like_action_pause()
        random_scroll(driver)  # Random scroll before interaction
        select_dropdown_option(
            driver, 
            'businessBookingTestCategoryRecordId', 
            'TC-B',  # Car option value
            use_js=js_enabled
        )
        print("✓ Selected 'Car' option")
        # Longer delay after selection with random behavior
        random_mouse_movement(driver)
        longer_human_delay(3.0, 5.0)  # Wait longer for dropdown to populate options
        
        # Step 2: Select "Wood Green (London)" from test centre autocomplete
        print("\n[Step 5] Selecting 'Wood Green (London)' from test centre autocomplete...")
        # Human-like pause before action
        human_like_action_pause()
        random_scroll(driver)  # Random scroll before interaction
        
        # Wait for the autocomplete input to be available
        try:
            test_centre_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, 'auto-testcentres'))
            )
            print("  Test centre autocomplete input is ready")
        except Exception as e:
            print(f"  ⚠ Warning: Could not find autocomplete input: {e}")
        
        # Use autocomplete function to type "wood" and select "Wood Green (London)"
        select_autocomplete_option(
            driver,
            'auto-testcentres',  # Autocomplete input ID
            'wood',  # Text to type to trigger autocomplete
            'Wood Green (London)',  # Option text to select
            use_js=js_enabled
        )
        print("✓ Selected 'Wood Green (London)' option")
        # Longer delay after selection with random behavior
        random_mouse_movement(driver)
        longer_human_delay(3.0, 5.0)
        
        # Step 3: Select "No" radio button for special needs
        print("\n[Step 6] Selecting 'No' radio button for special needs...")
        # Human-like pause before action
        human_like_action_pause()
        random_scroll(driver)  # Random scroll before interaction
        
        # Try multiple possible IDs for the "No" radio button
        radio_ids = [
            'specialNeedsChoice-noneeds',
            'specialNeedsChoice-None',
            'specialNeedsChoice-no',
            'specialNeedsChoice-No',
        ]
        
        radio_selected = False
        for radio_id in radio_ids:
            try:
                print(f"  Trying radio button ID: {radio_id}")
                select_radio_button(
                    driver,
                    radio_id,
                    use_js=js_enabled
                )
                print(f"✓ Selected 'No' option using ID: {radio_id}")
                radio_selected = True
                break
            except Exception as e:
                print(f"  ⚠ Failed with ID '{radio_id}': {e}")
                human_delay(1.0, 2.0)  # Pause between attempts
                continue
        
        if not radio_selected:
            # Try to find the radio button by looking for the "No" option
            try:
                human_delay(1.0, 2.0)  # Pause before fallback
                no_radio = driver.find_element(By.XPATH, "//input[@type='radio' and contains(@name, 'specialNeedsChoice') and (contains(@value, 'no') or contains(@value, 'none'))]")
                ActionChains(driver).move_to_element(no_radio).pause(
                    random.uniform(0.8, 1.5)
                ).click().perform()
                human_delay(1.5, 2.5)
                print("✓ Selected 'No' option by searching")
                radio_selected = True
            except Exception as e:
                print(f"  ❌ Could not find 'No' radio button: {e}")
                raise
        
        # Longer delay after selection with random behavior
        random_mouse_movement(driver)
        longer_human_delay(3.0, 5.0)
        
        # Step 4: Click the "Book test" button
        print("\n[Step 7] Clicking 'Book test' button...")
        # Human-like pause before final action
        human_like_action_pause()
        random_scroll(driver)  # Random scroll before clicking
        random_mouse_movement(driver)  # Random mouse movement
        
        click_button(
            driver,
            'submitSlotSearch',  # Book test button ID
            use_js=js_enabled
        )
        print("✓ Clicked 'Book test' button")
        # Longer delay after clicking
        longer_human_delay(3.0, 5.0)
        
        print("\n" + "=" * 60)
        print("✓ First part of scripting completed successfully!")
        print("=" * 60)
        
        # CRITICAL: Explicitly continue to second page scraping
        # This ensures the script doesn't exit here
        print("\n" + "=" * 60)
        print(">>> TRANSITIONING TO SECOND PAGE SCRAPING <<<")
        print("STARTING: Weekly Availability Scraping")
        print("=" * 60)
        import sys
        sys.stdout.flush()  # Force output to appear immediately
        
        # Wait for the availability page to load
        print("\n[Transition] Waiting for availability page to load after form submission...")
        try:
            # Wait for the availability table to appear (this indicates we're on the results page)
            print("  Looking for availability table (id='browseslots')...")
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "browseslots"))
            )
            print("  ✓ Availability page loaded successfully")
        except TimeoutException:
            print("  ⚠ Availability table not found immediately, checking page state...")
            # Check current URL
            current_url = driver.current_url
            print(f"  Current URL: {current_url[:100]}...")
            # Check for timeout dialog
            handle_timeout_dialog(driver)
            # Try waiting a bit more
            time.sleep(3)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "browseslots"))
                )
                print("  ✓ Availability page loaded (after retry)")
            except:
                print("  ⚠ Still waiting for availability table, but continuing anyway...")
        
        wait_for_page_load(driver)
        longer_human_delay(3.0, 5.0)
        
        # Check for timeout dialog before starting scraping
        print("  Checking for timeout dialog...")
        handle_timeout_dialog(driver)
        
        # Start scraping weekly availability
        print("\n" + "=" * 60)
        print("BEGINNING WEEKLY AVAILABILITY SCRAPING")
        print("=" * 60)
        try:
            total_reserved = scrape_weekly_availability(driver, direction="forward")
            
            print("\n" + "=" * 60)
            print("✓ Script completed successfully!")
            print(f"✓ Total tests reserved: {total_reserved}")
            print("=" * 60)
        except Exception as e:
            print(f"\n❌ Error during weekly availability scraping: {e}")
            import traceback
            traceback.print_exc()
            print("\n⚠ Scraping stopped, but browser remains open.")
            total_reserved = 0
        
        # Keep browser open
        print("\nBrowser will remain open. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n\nScript interrupted by user.")
        
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

