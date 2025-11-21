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
        # When connecting to existing Chrome, we don't need these automation flags
        # They should have been set when Chrome was started
        
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
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", select_element)
        human_delay(0.5, 1.0)
        
        # Wait for dropdown to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(select_element))
        
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
        
        # Click to focus and open dropdown
        ActionChains(driver).move_to_element(select_element).pause(
            random.uniform(0.2, 0.4)
        ).click().perform()
        human_delay(0.3, 0.5)
        
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
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", input_element)
        human_delay(0.5, 1.0)
        
        # Wait for input to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(input_element))
        
        # Clear the input field first
        input_element.clear()
        human_delay(0.3, 0.5)
        
        # Click to focus
        ActionChains(driver).move_to_element(input_element).pause(
            random.uniform(0.2, 0.4)
        ).click().perform()
        human_delay(0.3, 0.5)
        
        # Type the search text (character by character for more human-like behavior)
        for char in search_text:
            input_element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        human_delay(1.0, 1.5)  # Wait for autocomplete to appear
        
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
        
        # Click on the option
        ActionChains(driver).move_to_element(option_element).pause(
            random.uniform(0.2, 0.4)
        ).click().perform()
        human_delay(0.8, 1.2)
        
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
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", radio_element)
        human_delay(0.5, 1.0)
        
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
        
        # Direct click on radio button
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(radio_element))
        ActionChains(driver).move_to_element(radio_element).pause(
            random.uniform(0.2, 0.4)
        ).click().perform()
        human_delay(0.5, 1.0)
        
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
        human_delay(2, 3)  # Wait longer for dropdown to populate options
        
        # Step 2: Select "Wood Green (London)" from test centre autocomplete
        print("\n[Step 4] Selecting 'Wood Green (London)' from test centre autocomplete...")
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
        human_delay(1, 2)
        
        # Step 3: Select "No" radio button for special needs
        print("\n[Step 5] Selecting 'No' radio button for special needs...")
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
                continue
        
        if not radio_selected:
            # Try to find the radio button by looking for the "No" option
            try:
                no_radio = driver.find_element(By.XPATH, "//input[@type='radio' and contains(@name, 'specialNeedsChoice') and (contains(@value, 'no') or contains(@value, 'none'))]")
                ActionChains(driver).move_to_element(no_radio).click().perform()
                human_delay(0.5, 1.0)
                print("✓ Selected 'No' option by searching")
                radio_selected = True
            except Exception as e:
                print(f"  ❌ Could not find 'No' radio button: {e}")
                raise
        
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

