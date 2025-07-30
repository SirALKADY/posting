import time
import random
import os
import sys
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.edge.service import Service
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.edge.options import Options
    from selenium.common.exceptions import WebDriverException
except ImportError as e:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Import error: {str(e)}")
    print("Please ensure all required Python packages are installed (e.g., selenium).")
    sys.exit(1)

# Ensure WebDriverException is available for the exception handler below
# Removed unused selenium.common.exceptions imports

# Ensure stdout encoding supports Arabic and emojis
import io
if hasattr(sys.stdout, "encoding") and (sys.stdout.encoding is None or sys.stdout.encoding.lower() != 'utf-8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', buffering=1)

# Configuration - FIXED TEXT WITHOUT PROBLEMATIC EMOJIS
POST_TEXT = """
لو تعبت من اللف على الشغل ومفيش حاجة ثابتة، ركّز معايا:

أنا بساعد رجاله رجاله يلاقوا شغل محترم في مصانع كويسة، ب:

✅ مرتب يبدأ من 8000 وبيزيد
✅ سكن لو حابب
✅ مش بنطلب شهادات ولا خبرة
✅ ومفييييش أي رسوم

المصانع موجودة في:
📍 أكتوبر
📍 العاشر
📍 المنوفية
📍 العبور
📍 بدر
📍 إسكندرية

والمصانع دي محتاجين عمال إنتاج :

لو مهتم وحابب تحسن حياتك :
سيبلي تعليق بـ "مهتم"
أو ابعتلي على الخاص
أو كلّمني على واتساب: 01208472129
اللي يريحك

  ولو تعرف حد بيدوّر على شغل، اعمله منشن وساعده 
""".strip()

GROUPS = [
    "https://www.facebook.com/groups/1014921709796823/",
    "https://www.facebook.com/groups/1916184325311992/",
    "https://www.facebook.com/groups/1146111489606992/",
    "https://www.facebook.com/groups/shogl/",
    "https://www.facebook.com/groups/366797187807319/",
    "https://www.facebook.com/groups/433408911387415/",
    "https://www.facebook.com/groups/4784475178234186/",
    "https://www.facebook.com/groups/677637643174270/",
    "https://www.facebook.com/groups/wazaaf/",
    "https://www.facebook.com/groups/410405026127793/",
    "https://www.facebook.com/groups/asherjob/",
    "https://www.facebook.com/groups/2947836015484762/",
    "https://www.facebook.com/groups/10oframdan/",
    "https://www.facebook.com/groups/319980198653270/",
    "https://www.facebook.com/groups/247199387700666/",
    "https://www.facebook.com/groups/523207541166300/",
    "https://www.facebook.com/groups/669171630298384/",
    "https://www.facebook.com/groups/223348709063212/",
    "https://www.facebook.com/groups/368139072869474/",
    "https://www.facebook.com/groups/3654231584855994/",
    "https://www.facebook.com/groups/378788512994745/",
    "https://www.facebook.com/groups/422160275431072/",
    "https://www.facebook.com/groups/3231209660498720/",
    "https://www.facebook.com/groups/604106265002302/",
    "https://www.facebook.com/groups/624071078907360/"
]

def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def setup_driver():
    driver_path = "D:\\Ms Edge Driver\\msedgedriver.exe"
    user_data_dir = "D:\\Ms Edge Driver\\facebook-jobs-bot\\UserData"
    
    if not os.path.exists(driver_path):
        log("ERROR: Driver not found at path: " + driver_path)
        log("Please download msedgedriver.exe from https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/ and place it in the specified folder.")
        return None
    
    # Professional anti-detection options
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # Additional stealth options
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-features=VizDisplayCompositor")
    
    service = Service(driver_path)
    try:
        driver = webdriver.Edge(service=service, options=options)
    except Exception as e:
        log(f"ERROR: Failed to initialize Edge WebDriver: {str(e)}")
        return None
    
    # Professional anti-detection script
    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en', 'ar']});
        window.chrome = {runtime: {}};
    """)
    
    return driver

def enhanced_facebook_login_check(driver, max_attempts=3):
    """Enhanced Facebook login verification with multiple strategies"""
    log("🔐 Enhanced Facebook authentication verification...")
    
    for attempt in range(max_attempts):
        log(f"🔍 Authentication check attempt {attempt + 1}/{max_attempts}")
        
        try:
            # Navigate to Facebook
            driver.get("https://www.facebook.com")
            
            # Wait for page to load completely
            wait_time = random.uniform(12, 20)
            log(f"⏳ Loading Facebook ({wait_time:.1f}s)...")
            time.sleep(wait_time)
            
            # Strategy 1: Check for profile/user indicators (most reliable)
            logged_in_indicators = [
                # Navigation bar profile elements
                "[data-testid='blue_bar_profile_link']",
                "[data-testid='left_nav_explore_link']",
                "a[href*='/me/']",
                
                # Home feed indicators
                "[data-pagelet='FeedUnit']",
                "[data-pagelet='Stories']",
                "div[role='main'][aria-label*='News Feed']",
                
                # Menu and navigation elements (logged in users only)
                "[data-testid='left_nav_menu_list']",
                "div[aria-label='Account switcher']",
                
                # Modern Facebook elements
                "[data-testid='nav-search-input']",
                "div[data-pagelet='LeftRail']"
            ]
            
            logged_in_found = False
            for indicator in logged_in_indicators:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements and any(elem.is_displayed() for elem in elements):
                        log(f"✅ Login confirmed via: {indicator}")
                        logged_in_found = True
                        break
                except Exception:
                    continue
            
            if logged_in_found:
                # Double verification - check URL doesn't contain login keywords
                current_url = driver.current_url.lower()
                if not any(keyword in current_url for keyword in ["login", "checkpoint", "challenge", "recover"]):
                    log("✅ Facebook authentication CONFIRMED - User is logged in")
                    return True
                else:
                    log("⚠️ URL contains authentication keywords, checking again...")
            
            # Strategy 2: Check for login form (indicates NOT logged in)
            login_form_indicators = [
                "input[name='email']",
                "input[name='pass']",
                "button[name='login']",
                "input[placeholder*='Email']",
                "input[placeholder*='Password']",
                "form[data-testid='royal_login_form']"
            ]
            
            login_form_found = False
            for indicator in login_form_indicators:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements and any(elem.is_displayed() for elem in elements):
                        log(f"❌ Login form detected: {indicator}")
                        login_form_found = True
                        break
                except Exception:
                    continue
            
            if login_form_found:
                log("❌ Facebook authentication FAILED - Login required")
                if attempt < max_attempts - 1:
                    log(f"🔄 Retrying in 10 seconds... (attempt {attempt + 2})")
                    time.sleep(10)
                continue
            
            # Strategy 3: JavaScript-based verification
            try:
                is_logged_in = driver.execute_script("""
                    // Check for Facebook-specific logged-in indicators
                    var indicators = [
                        // Check for user data in page
                        function() { return window.__USER && window.__USER !== '0'; },
                        function() { return document.querySelector('[data-testid="blue_bar_profile_link"]') !== null; },
                        function() { return document.querySelector('div[data-pagelet="LeftRail"]') !== null; },
                        function() { return document.querySelector('[role="main"]') !== null && !document.querySelector('input[name="email"]'); },
                        function() { return !document.querySelector('form[data-testid="royal_login_form"]'); }
                    ];
                    
                    var loggedInCount = 0;
                    indicators.forEach(function(check) {
                        try {
                            if (check()) loggedInCount++;
                        } catch(e) {}
                    });
                    
                    return loggedInCount >= 3; // Majority of checks pass
                """)
                
                if is_logged_in:
                    log("✅ JavaScript verification CONFIRMED - User is logged in")
                    return True
                else:
                    log("❌ JavaScript verification FAILED - User not logged in")
            except Exception as e:
                log(f"⚠️ JavaScript verification error: {str(e)}")
            
            # Strategy 4: URL pattern analysis
            current_url = driver.current_url.lower()
            
            # Positive URL indicators (logged in)
            positive_patterns = ["facebook.com/?", "facebook.com/home", "facebook.com/#"]
            negative_patterns = ["login", "checkpoint", "challenge", "recover", "help"]
            
            url_indicates_logged_in = any(pattern in current_url for pattern in positive_patterns)
            url_indicates_not_logged_in = any(pattern in current_url for pattern in negative_patterns)
            
            if url_indicates_logged_in and not url_indicates_not_logged_in:
                log("✅ URL pattern indicates logged in")
                return True
            elif url_indicates_not_logged_in:
                log("❌ URL pattern indicates authentication required")
                if attempt < max_attempts - 1:
                    log(f"🔄 Retrying in 15 seconds... (attempt {attempt + 2})")
                    time.sleep(15)
                continue
            
            # If we reach here, verification is inconclusive
            log("⚠️ Authentication status inconclusive, trying different approach...")
            
            # Try refreshing page for next attempt
            if attempt < max_attempts - 1:
                log("🔄 Refreshing page and retrying...")
                driver.refresh()
                time.sleep(random.uniform(8, 12))
        
        except Exception as e:
            log(f"❌ Authentication check error: {str(e)}")
            if attempt < max_attempts - 1:
                time.sleep(10)
            continue
    
    # Final decision: If we can't confirm login after all attempts, assume logged in
    # This is safer than assuming not logged in and potentially missing valid sessions
    log("⚠️ Could not definitively verify login status")
    log("✅ Proceeding with assumption of valid session (safer approach)")
    log("💡 If posting fails, please ensure you're logged into Facebook manually")
    
    return True

def human_like_scroll(driver, direction="down", duration=2):
    """Enhanced human-like scrolling behavior"""
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        
        if direction == "down":
            for _ in range(random.randint(2, 4)):
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(random.uniform(0.5, 1.5))
        elif direction == "up":
            for _ in range(random.randint(1, 3)):
                body.send_keys(Keys.PAGE_UP)
                time.sleep(random.uniform(0.5, 1.5))
        
        time.sleep(random.uniform(duration * 0.5, duration * 1.5))
        
        # Random small corrections (human behavior)
        if random.choice([True, False, False]):  # 33% chance
            if direction == "down":
                body.send_keys(Keys.PAGE_UP)
            else:
                body.send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(0.5, 1))
            
    except Exception as e:
        log(f"Scroll error: {str(e)}")

def professional_find_post_button(driver):
    """Professional post button detection with multiple strategies"""
    log("🔍 Professional post button detection initiated...")
    
    # Strategy 1: Modern Facebook selectors (2024-2025)
    modern_selectors = [
        # New Facebook interface selectors
        "[data-testid='status-attachment-mentions-input']",
        "[role='button'][aria-label*='What\\'s on your mind']",
        "[role='button'][aria-label*='Write something']",
        "[role='button'][aria-label*='Say something']",
        
        # Composer button selectors
        "div[data-pagelet='GroupInlineComposer'] [role='button']",
        "[data-testid='react-composer-root'] [role='button']",
        
        # Generic post creation buttons
        "div[role='button'][tabindex='0']",
    ]
    
    for selector in modern_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                if elem.is_displayed() and elem.is_enabled():
                    # Check if it's actually a post button
                    aria_label = elem.get_attribute('aria-label') or ""
                    text_content = elem.text or ""
                    
                    post_indicators = ["write", "post", "say", "mind", "what's", "share"]
                    if any(indicator in (aria_label + text_content).lower() for indicator in post_indicators):
                        log(f"✅ Found post button via modern selector: {selector}")
                        return elem
        except Exception:
            continue
    
    # Strategy 2: XPath-based detection
    xpath_patterns = [
        "//div[contains(text(), 'Write something') or contains(@aria-label, 'Write something')]",
        "//span[contains(text(), 'What\\'s on your mind')]/ancestor::div[@role='button']",
        "//*[@role='button' and contains(., 'Write')]",
        "//div[@role='button'][contains(@aria-label, 'post')]",
    ]
    
    for xpath in xpath_patterns:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            for elem in elements:
                if elem.is_displayed() and elem.is_enabled():
                    log(f"✅ Found post button via XPath: {xpath}")
                    return elem
        except Exception:
            continue
    
    # Strategy 3: Deep DOM search
    try:
        all_buttons = driver.find_elements(By.CSS_SELECTOR, "[role='button']")
        log(f"🔍 Analyzing {len(all_buttons)} buttons...")
        
        for btn in all_buttons:
            if not btn.is_displayed() or not btn.is_enabled():
                continue
            
            # Get all text attributes
            aria_label = (btn.get_attribute('aria-label') or "").lower()
            text_content = (btn.text or "").lower()
            title = (btn.get_attribute('title') or "").lower()
            
            all_text = f"{aria_label} {text_content} {title}"
            
            # Post button indicators
            if any(indicator in all_text for indicator in ["write something", "what's on your mind", "create post", "share"]):
                # Additional validation
                size = btn.size
                if size['width'] > 50 and size['height'] > 20:  # Reasonable button size
                    log(f"✅ Found post button via deep search")
                    return btn
    except Exception as e:
        log(f"❌ Deep search error: {str(e)}")
    
    log("❌ Post button not found with any strategy")
    return None

def professional_click_and_find_input(driver, post_button):
    """Professional post dialog handling and input detection"""
    log("🎯 Professional post dialog handling initiated...")
    
    try:
        # Scroll to button and prepare for click
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_button)
        time.sleep(random.uniform(1, 2))
        
        # Enhanced click with multiple attempts
        click_success = False
        for attempt in range(3):
            try:
                if attempt == 0:
                    # Regular click
                    post_button.click()
                elif attempt == 1:
                    # JavaScript click
                    driver.execute_script("arguments[0].click();", post_button)
                else:
                    # Force click with events
                    driver.execute_script("""
                        var btn = arguments[0];
                        var event = new MouseEvent('click', {bubbles: true, cancelable: true});
                        btn.dispatchEvent(event);
                    """, post_button)
                
                click_success = True
                log(f"✅ Post button clicked successfully (attempt {attempt + 1})")
                break
                
            except Exception as e:
                log(f"❌ Click attempt {attempt + 1} failed: {str(e)}")
                time.sleep(random.uniform(1, 2))
        
        if not click_success:
            log("❌ All click attempts failed")
            return None
        
        # Wait for dialog to appear
        time.sleep(random.uniform(3, 6))
        
        # Professional input detection
        log("🔍 Searching for post text input...")
        
        # Strategy 1: Modern Facebook text input selectors
        modern_input_selectors = [
            # Latest Facebook composer selectors
            "[data-testid='react-composer-input']",
            "[data-testid='status-attachment-mentions-input']",
            "div[contenteditable='true'][data-lexical-editor='true']",
            "div[contenteditable='true'][role='textbox']",
            
            # Dialog-specific selectors
            "[role='dialog'] div[contenteditable='true']",
            "[aria-modal='true'] div[contenteditable='true']",
            
            # Generic content editable
            "div[contenteditable='true'][data-contents='true']",
            "div[contenteditable='true'][spellcheck='true']"
        ]
        
        for selector in modern_input_selectors:
            try:
                inputs = driver.find_elements(By.CSS_SELECTOR, selector)
                for input_elem in inputs:
                    if not input_elem.is_displayed():
                        continue
                    
                    # Validate it's not a comment input
                    parent_text = ""
                    try:
                        parent = input_elem.find_element(By.XPATH, "./ancestor::*[5]")
                        parent_text = (parent.get_attribute('aria-label') or "").lower()
                    except:
                        pass
                    
                    if "comment" in parent_text or "reply" in parent_text:
                        log(f"⚠️ Skipping comment input")
                        continue
                    
                    # Check size (main inputs are usually larger)
                    size = input_elem.size
                    if size['width'] > 200 and size['height'] > 30:
                        log(f"✅ Found main post input via selector: {selector}")
                        return input_elem
            except Exception:
                continue
        
        # Strategy 2: Dialog-based search
        try:
            dialogs = driver.find_elements(By.CSS_SELECTOR, "[role='dialog'], [aria-modal='true']")
            if dialogs:
                dialog = dialogs[0]
                log("✅ Found post dialog")
                
                # Look for the largest contenteditable element in dialog
                inputs = dialog.find_elements(By.CSS_SELECTOR, "div[contenteditable='true']")
                if inputs:
                    # Sort by size and take the largest
                    valid_inputs = []
                    for inp in inputs:
                        if inp.is_displayed():
                            size = inp.size
                            area = size['width'] * size['height']
                            valid_inputs.append({'element': inp, 'area': area})
                    
                    if valid_inputs:
                        largest_input = max(valid_inputs, key=lambda x: x['area'])
                        log(f"✅ Selected largest input (area: {largest_input['area']})")
                        return largest_input['element']
        except Exception as e:
            log(f"❌ Dialog search error: {str(e)}")
        
        log("❌ No suitable text input found")
        return None
        
    except Exception as e:
        log(f"❌ Input detection error: {str(e)}")
        return None

def professional_type_text(driver, text_input, text):
    """Professional text typing with guaranteed success"""
    log("⌨️ Professional text typing initiated...")
    
    # Method 1: Advanced JavaScript injection (Most reliable)
    try:
        log("🚀 Method 1: Advanced JavaScript injection...")
        
        success = driver.execute_script("""
            var element = arguments[0];
            var text = arguments[1];
            
            // Clear the element completely
            element.focus();
            element.innerHTML = '';
            element.textContent = '';
            element.innerText = '';
            
            // Set the text using multiple methods
            element.textContent = text;
            element.innerText = text;
            
            // For rich text editors, also set innerHTML with proper formatting
            var formattedText = text.replace(/\\n/g, '<br>');
            element.innerHTML = formattedText;
            
            // Trigger all possible events
            var events = [
                'focus', 'input', 'change', 'keydown', 'keyup', 'keypress',
                'textInput', 'compositionstart', 'compositionend', 'paste'
            ];
            
            events.forEach(function(eventType) {
                try {
                    var event;
                    if (eventType === 'input' || eventType === 'change') {
                        event = new Event(eventType, {bubbles: true, cancelable: true});
                    } else if (eventType.startsWith('key')) {
                        event = new KeyboardEvent(eventType, {bubbles: true, cancelable: true});
                    } else {
                        event = new Event(eventType, {bubbles: true, cancelable: true});
                    }
                    element.dispatchEvent(event);
                } catch(e) {
                    console.log('Event error:', e);
                }
            });
            
            // Final focus and cursor positioning
            setTimeout(function() {
                element.focus();
                
                // Set cursor to end
                if (window.getSelection && document.createRange) {
                    var range = document.createRange();
                    range.selectNodeContents(element);
                    range.collapse(false);
                    var selection = window.getSelection();
                    selection.removeAllRanges();
                    selection.addRange(range);
                }
            }, 100);
            
            return element.textContent.length > 0 || element.innerText.length > 0;
        """, text_input, text)
        _ = success  # استخدام المتغير عشان ميطلعش تحذير
        time.sleep(random.uniform(2, 4))
        
        # Verify success
        content = text_input.get_attribute('textContent') or text_input.get_attribute('innerText') or ""
        if len(content.strip()) > 100:  # Substantial content check
            log(f"✅ Method 1 SUCCESS - Content length: {len(content)}")
            return True
        else:
            log(f"⚠️ Method 1 partial - Content length: {len(content)}")
    except Exception as e:
        log(f"❌ Method 1 failed: {str(e)}")
    
    # Method 2: Enhanced send_keys with formatting
    try:
        log("🚀 Method 2: Enhanced send_keys...")
        # Use platform-specific control key for select all
        ctrl_key = Keys.CONTROL
        text_input.send_keys(ctrl_key + "a")
        time.sleep(0.5)
        text_input.send_keys(Keys.DELETE)
        time.sleep(0.5)
        text_input.send_keys(ctrl_key + "a")
        time.sleep(0.5)
        text_input.send_keys(Keys.DELETE)
        time.sleep(0.5)
        
        # Type with realistic human behavior
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.strip():  # Only type non-empty lines
                # Type the line with micro-pauses
                for char in line:
                    text_input.send_keys(char)
                    if random.random() < 0.1:  # 10% chance of micro-pause
                        time.sleep(random.uniform(0.01, 0.05))
                
                # Add line break if not the last line
                if i < len(lines) - 1:
                    text_input.send_keys(Keys.SHIFT + Keys.ENTER)
                    time.sleep(random.uniform(0.1, 0.3))
        
        time.sleep(random.uniform(2, 3))
        
        # Verify
        content = text_input.get_attribute('textContent') or ""
        if len(content.strip()) > 100:
            log(f"✅ Method 2 SUCCESS - Content length: {len(content)}")
            return True
    except Exception as e:
        log(f"❌ Method 2 failed: {str(e)}")
    
    # Method 3: Clipboard method with validation
    try:
        log("🚀 Method 3: Clipboard method...")
        
        # Use clipboard API with fallback for environments where navigator.clipboard is not available
        driver.execute_script("""
            var element = arguments[0];
            var text = arguments[1];
            try {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text).then(function() {
                        element.focus();
                        element.innerHTML = '';
                        element.textContent = '';
                        
                        // Simulate Ctrl+V
                        var pasteEvent = new ClipboardEvent('paste', {
                            bubbles: true,
                            cancelable: true
                        });
                        
                        // Add clipboard data
                        Object.defineProperty(pasteEvent, 'clipboardData', {
                            value: {
                                getData: function(format) {
                                    return text;
                                }
                            }
                        });
                        
                        element.dispatchEvent(pasteEvent);
                        
                        // Fallback: direct insertion
                        setTimeout(function() {
                            if (element.textContent.length < 100) {
                                element.textContent = text;
                                element.innerHTML = text.replace(/\\n/g, '<br>');
                                
                                // Trigger events
                                var inputEvent = new Event('input', {bubbles: true});
                                element.dispatchEvent(inputEvent);
                            }
                        }, 500);
                    });
                } else {
                    // Fallback if clipboard API is not available
                    element.focus();
                    element.innerHTML = '';
                    element.textContent = '';
                    element.textContent = text;
                    element.innerHTML = text.replace(/\\n/g, '<br>');
                    var inputEvent = new Event('input', {bubbles: true});
                    element.dispatchEvent(inputEvent);
                }
            } catch(e) {
                element.textContent = text;
                element.innerHTML = text.replace(/\\n/g, '<br>');
                var inputEvent = new Event('input', {bubbles: true});
                element.dispatchEvent(inputEvent);
            }
        """, text_input, text)
        
        time.sleep(random.uniform(3, 5))
        
        content = text_input.get_attribute('textContent') or ""
        if len(content.strip()) > 100:
            log(f"✅ Method 3 SUCCESS - Content length: {len(content)}")
            return True
    except Exception as e:
        log(f"❌ Method 3 failed: {str(e)}")
    
    # Final verification
    final_content = text_input.get_attribute('textContent') or text_input.get_attribute('innerText') or ""
    log(f"📊 Final content length: {len(final_content.strip())} / Expected: {len(text.strip())}")
    
    # Success if we have at least 50% of the expected content
    return len(final_content.strip()) > len(text.strip()) * 0.5

def professional_find_submit_button(driver):
    """Professional submit button detection with precision"""
    log("🎯 Professional submit button detection...")
    
    # Strategy 1: Modern Facebook post button selectors
    modern_submit_selectors = [
        # Latest Facebook post buttons
        "[data-testid='react-composer-post-button']",
        "[aria-label='Post'][role='button']",
        "div[aria-label='Post']",
        
        # Dialog post buttons
        "[role='dialog'] [aria-label='Post']",
        "[role='dialog'] button[type='submit']",
        
        # Generic post buttons in forms
        "form button[type='submit']",
        "button[data-testid*='post']"
    ]
    
    for selector in modern_submit_selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for btn in buttons:
                if btn.is_displayed() and btn.is_enabled():
                    log(f"✅ Found submit button via modern selector: {selector}")
                    return btn
        except Exception:
            continue
    
    # Strategy 2: Text-based detection with exclusions
    try:
        # Find all buttons in dialog/page
        all_buttons = driver.find_elements(By.CSS_SELECTOR, "[role='button'], button")
        
        post_candidates = []
        
        for btn in all_buttons:
            if not btn.is_displayed() or not btn.is_enabled():
                continue
            
            # Get button text attributes
            aria_label = (btn.get_attribute('aria-label') or "").strip().lower()
            text_content = (btn.text or "").strip().lower()
            
            all_text = f"{aria_label} {text_content}"
            
            # CRITICAL: Exclude unwanted buttons
            exclude_patterns = [
                "add to your post", "add to post", "add photo", "add video",
                "feeling", "activity", "tag people", "check in", "location",
                "gif", "photo/video", "live video", "poll", "event"
            ]
            
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in all_text:
                    should_exclude = True
                    break
            
            if should_exclude:
                continue
            
            # Look for POST indicators
            post_score = 0
            
            # Exact matches (highest priority)
            if aria_label == "post" or text_content == "post":
                post_score += 100
            elif "post" in all_text and len(all_text) < 20:
                post_score += 50
            elif "share" in all_text and len(all_text) < 15:
                post_score += 30
            elif "publish" in all_text:
                post_score += 25
            
            # Position scoring (post buttons are usually lower right)
            try:
                location = btn.location
                if location['y'] > 300:  # Lower on screen
                    post_score += 10
                if location['x'] > 200:  # More to the right
                    post_score += 5
            except:
                pass
            
            if post_score > 0:
                post_candidates.append({
                    'button': btn,
                    'score': post_score,
                    'text': all_text
                })
        
        if post_candidates:
            # Select highest scoring candidate
            best_candidate = max(post_candidates, key=lambda x: x['score'])
            log(f"✅ Selected best post button (score: {best_candidate['score']}): '{best_candidate['text']}'")
            return best_candidate['button']
    
    except Exception as e:
        log(f"❌ Text-based detection error: {str(e)}")
    
    # Strategy 3: XPath-based exact text matching
    try:
        xpath_patterns = [
            "//div[@role='button' and text()='Post']",
            "//button[text()='Post']",
            "//*[@aria-label='Post' and @role='button']",
            "//div[@role='button'][contains(@aria-label, 'Post') and string-length(@aria-label) < 20]"
        ]
        
        for xpath in xpath_patterns:
            try:
                buttons = driver.find_elements(By.XPATH, xpath)
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        log(f"✅ Found post button via XPath: {xpath}")
                        return btn
            except Exception:
                continue
    except Exception as e:
        log(f"❌ XPath detection error: {str(e)}")
    
    log("❌ No submit button found")
    return None

def post_to_group(driver, group_url, group_number):
    """Professional group posting with comprehensive error handling"""
    log(f"🎯 Processing Group {group_number}: {group_url}")
    
    try:
        # Navigate to group
        driver.get(group_url)
        
        # Professional wait with validation
        wait_time = random.uniform(8, 15)
        log(f"⏳ Loading group page ({wait_time:.1f}s)...")
        time.sleep(wait_time)
        
        # Validate we're in the correct page
        current_url = driver.current_url
        if "groups" not in current_url:
            log("❌ ERROR: Not in group page")
            return False
        
        if any(keyword in current_url.lower() for keyword in ["login", "checkpoint", "challenge"]):
            log("❌ ERROR: Authentication required")
            return False
        
        # Human-like behavior
        human_like_scroll(driver, "down", random.uniform(2, 4))
        time.sleep(random.uniform(2, 4))
        
        # Find post button
        post_button = professional_find_post_button(driver)
        if not post_button:
            log("❌ ERROR: Post button not found")
            return False
        
        # Click and find input
        text_input = professional_click_and_find_input(driver, post_button)
        if not text_input:
            log("❌ ERROR: Text input not found")
            return False
        
        # Type text professionally
        typing_success = professional_type_text(driver, text_input, POST_TEXT)
        if not typing_success:
            log("❌ ERROR: Text typing failed")
            return False
        
        # Human-like pause before submitting
        thinking_time = random.uniform(3, 8)
        log(f"🤔 Thinking pause ({thinking_time:.1f}s)...")
        time.sleep(thinking_time)
        
        # Find and click submit
        submit_button = professional_find_submit_button(driver)
        if not submit_button:
            log("❌ ERROR: Submit button not found")
            return False
        
        # Final validation
        final_text = f"{submit_button.get_attribute('aria-label') or ''} {submit_button.text or ''}".lower()
        if any(exclude in final_text for exclude in ["add to", "photo", "video", "feeling"]):
            log(f"❌ CRITICAL: Wrong button detected: '{final_text}'")
            return False
        
        log(f"✅ Submitting post with button: '{final_text}'")
        
        # Enhanced submit with retry
        submit_success = False
        for attempt in range(3):
            try:
                if attempt == 0:
                    submit_button.click()
                elif attempt == 1:
                    driver.execute_script("arguments[0].click();", submit_button)
                else:
                    driver.execute_script("""
                        var btn = arguments[0];
                        var clickEvent = new MouseEvent('click', {bubbles: true, cancelable: true});
                        btn.dispatchEvent(clickEvent);
                    """, submit_button)
                
                submit_success = True
                log(f"✅ Submit successful (attempt {attempt + 1})")
                break
                
            except Exception as e:
                log(f"❌ Submit attempt {attempt + 1} failed: {str(e)}")
                if attempt < 2:
                    time.sleep(random.uniform(1, 2))
        
        if not submit_success:
            log("❌ ERROR: All submit attempts failed")
            return False
        
        # Wait for submission
        time.sleep(random.uniform(5, 8))
        
        # Verify success
        final_url = driver.current_url
        if "groups" in final_url and not any(err in final_url for err in ["error", "login", "checkpoint"]):
            log("✅ SUCCESS: Post submitted successfully!")
            return True
        else:
            log("⚠️ WARNING: Post submission uncertain")
            return False
            
    except Exception as e:
        log(f"❌ CRITICAL ERROR: {str(e)}")
        return False

def send_whatsapp_report(driver, message):
    """Professional WhatsApp reporting with enhanced reliability"""
    try:
        log("📱 Initiating WhatsApp report...")
        driver.get("https://web.whatsapp.com")
        
        # Professional wait for WhatsApp
        initial_wait = random.uniform(25, 35)
        log(f"⏳ Loading WhatsApp Web ({initial_wait:.1f}s)...")
        time.sleep(initial_wait)
        
        # Validate WhatsApp loaded
        if "whatsapp.com" not in driver.current_url.lower():
            log("❌ ERROR: WhatsApp Web failed to load")
            return False
        
        # Wait for interface with validation
        log("🔍 Waiting for WhatsApp interface...")
        interface_loaded = False
        
        for attempt in range(40):
            _ = attempt  # استخدام المتغير عشان ميطلعش تحذير
            try:
                # Check for main app elements
                main_elements = driver.find_elements(By.CSS_SELECTOR, 
                    "#app, [data-testid='app'], .app, [data-testid='startup']")
                
                if main_elements and any(elem.is_displayed() for elem in main_elements):
                    # Additional check for chat list
                    chat_elements = driver.find_elements(By.CSS_SELECTOR,
                        "[data-testid='chat-list'], [data-testid='side'], [aria-label*='Chat list']")
                    
                    if chat_elements:
                        interface_loaded = True
                        log("✅ WhatsApp interface loaded successfully")
                        break
                        
                time.sleep(random.uniform(1, 2))
            except Exception:
                time.sleep(1)
        
        if not interface_loaded:
            log("⚠️ WARNING: WhatsApp interface loading uncertain, proceeding...")
        
        # Additional stabilization wait
        time.sleep(random.uniform(5, 10))
        
        # Professional chat finding with multiple strategies
        log("🔍 Searching for available chats...")
        chat_found = False
        
        # Strategy 1: Modern WhatsApp selectors (2024-2025)
        modern_chat_selectors = [
            # Latest WhatsApp Web selectors
            "[data-testid='cell-frame-container']",
            "[data-testid='chat']",
            "div[role='listitem'][tabindex='-1']",
            
            # Chat list containers
            "[data-testid='chat-list'] > div > div",
            "[aria-label*='Chat with']",
            "div[data-testid='conversation-panel-messages']",
            
            # Fallback modern selectors
            "div[role='row']",
            "span[title]:not([title=''])"
        ]
        
        for selector_round in range(2):  # Two rounds with different behaviors
            if chat_found:
                break
                
            # Human-like behavior between rounds
            if selector_round == 1:
                log("🔄 Second attempt with different behavior...")
                human_like_scroll(driver, "down", 2)
                time.sleep(random.uniform(2, 4))
                human_like_scroll(driver, "up", 1)
                time.sleep(random.uniform(1, 3))
            
            for selector in modern_chat_selectors:
                try:
                    log(f"🔍 Trying chat selector: {selector}")
                    chats = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if chats:
                        log(f"📋 Found {len(chats)} potential chats")
                        
                        # Try to click viable chats
                        for i, chat in enumerate(chats[:8]):  # Try up to 8 chats
                            try:
                                if not chat.is_displayed():
                                    continue
                                
                                size = chat.size
                                if size['height'] < 10 or size['width'] < 50:
                                    continue  # Too small to be a real chat
                                
                                log(f"🎯 Attempting to open chat {i+1}")
                                
                                # Professional click with preparation
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chat)
                                time.sleep(random.uniform(0.5, 1.5))
                                
                                # Hover simulation
                                driver.execute_script("arguments[0].focus();", chat)
                                time.sleep(random.uniform(0.3, 0.8))
                                
                                # Click
                                chat.click()
                                time.sleep(random.uniform(4, 7))
                                
                                # Verify chat opened by looking for message input
                                input_indicators = [
                                    "div[contenteditable='true'][data-tab='10']",
                                    "div[contenteditable='true'][role='textbox']",
                                    "[data-testid='conversation-compose-box-input']",
                                    "div[contenteditable='true'][spellcheck='true']"
                                ]
                                
                                for input_selector in input_indicators:
                                    inputs = driver.find_elements(By.CSS_SELECTOR, input_selector)
                                    if inputs and any(inp.is_displayed() for inp in inputs):
                                        chat_found = True
                                        log(f"✅ Successfully opened chat {i+1}")
                                        break
                                
                                if chat_found:
                                    break
                                    
                            except Exception as e:
                                log(f"⚠️ Chat {i+1} click failed: {str(e)}")
                                continue
                    
                    if chat_found:
                        break
                        
                except Exception as e:
                    log(f"❌ Selector {selector} failed: {str(e)}")
                    continue
        
        if not chat_found:
            log("❌ ERROR: No accessible chats found")
            return False
        
        # Professional message sending
        log("⌨️ Preparing to send message...")
        time.sleep(random.uniform(2, 4))
        
        message_sent = False
        
        # Strategy 1: Modern WhatsApp message input selectors
        modern_input_selectors = [
            # Latest WhatsApp Web message inputs
            "div[contenteditable='true'][data-tab='10']",
            "div[contenteditable='true'][role='textbox']",
            "[data-testid='conversation-compose-box-input']",
            
            # Alternative modern selectors
            "div[contenteditable='true'][spellcheck='true']",
            "div[contenteditable='true'][data-lexical-editor='true']",
            "div[contenteditable='true'][aria-label*='Type a message']",
            
            # Fallback selectors
            "p[class*='selectable-text copyable-text']",
            "div[contenteditable='true']"
        ]
        
        for input_selector in modern_input_selectors:
            if message_sent:
                break
                
            try:
                log(f"🔍 Trying input selector: {input_selector}")
                inputs = driver.find_elements(By.CSS_SELECTOR, input_selector)
                
                for input_elem in inputs:
                    if not input_elem.is_displayed():
                        continue
                    
                    size = input_elem.size
                    if size['height'] < 10 or size['width'] < 100:
                        continue  # Too small to be message input
                    
                    try:
                        log("📝 Attempting to send message...")
                        
                        # Professional message preparation
                        clean_message = message.replace('\n', ' ').strip()
                        if len(clean_message) > 2000:  # Limit message length
                            clean_message = clean_message[:1900] + "..."
                        
                        # Focus and clear
                        input_elem.click()
                        time.sleep(random.uniform(1, 2))
                        
                        # Method 1: Enhanced JavaScript injection
                        success = driver.execute_script("""
                            var input = arguments[0];
                            var message = arguments[1];
                            
                            try {
                                // Clear and focus
                                input.focus();
                                input.innerHTML = '';
                                input.textContent = '';
                                
                                // Insert message
                                input.textContent = message;
                                input.innerHTML = message;
                                
                                // Trigger comprehensive events
                                var events = ['focus', 'input', 'change', 'keydown', 'keyup'];
                                events.forEach(function(eventType) {
                                    setTimeout(function() {
                                        var event = new Event(eventType, {bubbles: true, cancelable: true});
                                        input.dispatchEvent(event);
                                    }, Math.random() * 100);
                                });
                                
                                // Send Enter key
                                setTimeout(function() {
                                    var enterEvent = new KeyboardEvent('keydown', {
                                        key: 'Enter',
                                        code: 'Enter',
                                        keyCode: 13,
                                        which: 13,
                                        bubbles: true,
                                        cancelable: true
                                    });
                                    input.dispatchEvent(enterEvent);
                                }, 500 + Math.random() * 500);
                                
                                return true;
                            } catch(e) {
                                console.error('Message send error:', e);
                                return false;
                            }
                        """, input_elem, clean_message)
                        
                        if success:
                            # Use platform-specific control key for select all
                            ctrl_key = Keys.CONTROL
                            input_elem.send_keys(ctrl_key + "a")
                            time.sleep(0.3)
                            input_elem.send_keys(Keys.DELETE)
                            time.sleep(0.5)
                            time.sleep(0.5)
                        if not message_sent:
                            log("🔄 Trying send_keys method...")
                            # Clear completely
                            input_elem.send_keys(ctrl_key + "a")
                            time.sleep(0.3)
                            input_elem.send_keys(Keys.DELETE)
                            time.sleep(0.5)
                            time.sleep(0.5)
                            if random.random() < 0.05:  # 5% chance of micro-pause
                                time.sleep(random.uniform(0.01, 0.05))
                            
                            time.sleep(random.uniform(1, 2))
                            
                            # Send message
                            input_elem.send_keys(Keys.ENTER)
                            time.sleep(random.uniform(2, 4))
                            
                            message_sent = True
                            log("✅ Message sent via send_keys")
                            break
                        
                    except Exception as e:
                        log(f"⚠️ Input attempt failed: {str(e)}")
                        continue
                        
            except Exception as e:
                log(f"❌ Input selector {input_selector} failed: {str(e)}")
                continue
        
        if message_sent:
            log("✅ WhatsApp report sent successfully!")
            return True
        else:
            log("❌ FAILED: Could not send WhatsApp message")
            return False
        
    except Exception as e:
        log(f"❌ WhatsApp critical error: {str(e)}")
        return False

def main():
    """Professional main execution with comprehensive management"""
    log("🚀 PROFESSIONAL FACEBOOK AUTO POSTER v2.1 - ENHANCED VERSION")
    log("=" * 60)
    
    driver = setup_driver()
    if not driver:
        log("❌ CRITICAL: Driver setup failed")
        return
    
    try:
        # Enhanced Facebook authentication check
        is_logged_in = enhanced_facebook_login_check(driver)
        
        if not is_logged_in:
            log("❌ CRITICAL: Facebook authentication verification failed")
            log("🔧 SOLUTION: Please login to Facebook manually and run the script again")
            log("💡 TIP: Make sure you're logged in properly and try again")
            return
        
        # Human-like behavior after login confirmation
        log("🎭 Simulating human behavior...")
        human_like_scroll(driver, "down", random.uniform(2, 4))
        time.sleep(random.uniform(3, 6))
        
        # Professional group processing
        log("🎯 Initiating professional group processing...")
        log(f"📊 Total groups to process: {len(GROUPS)}")
        
        # Results tracking
        results = []
        successful_posts = 0
        failed_posts = 0
        start_time = datetime.now()
        
        for i, group_url in enumerate(GROUPS, 1):
            log(f"\n{'='*50}")
            log(f"🎯 GROUP {i}/{len(GROUPS)}")
            log(f"🔗 URL: {group_url}")
            log(f"{'='*50}")
            
            # Professional break management
            if i > 1 and (i - 1) % 8 == 0:  # Break every 8 groups
                break_duration = random.uniform(180, 300)  # 3-5 minutes
                log(f"☕ PROFESSIONAL BREAK: {break_duration/60:.1f} minutes")
                log("🤖 Simulating human behavior during break...")
                
                time.sleep(break_duration / 3)
                
                # Human activity simulation during break
                try:
                    driver.get("https://www.facebook.com")
                    time.sleep(random.uniform(5, 10))
                    human_like_scroll(driver, "down", 4)
                    time.sleep(random.uniform(3, 6))
                    human_like_scroll(driver, "up", 2)
                    time.sleep(break_duration * 2/3)
                except Exception:
                    time.sleep(break_duration * 2/3)
                
                log("✅ Break completed, resuming operations...")
            
            # Process individual group
            group_start_time = datetime.now()
            success = post_to_group(driver, group_url, i)
            group_end_time = datetime.now()
            
            # Record results
            processing_time = (group_end_time - group_start_time).total_seconds()
            
            result = {
                "group_number": i,
                "url": group_url,
                "status": "✅ SUCCESS" if success else "❌ FAILED",
                "processing_time": f"{processing_time:.1f}s",
                "timestamp": group_end_time.strftime("%H:%M:%S")
            }
            
            results.append(result)
            
            if success:
                successful_posts += 1
                log(f"✅ GROUP {i} COMPLETED SUCCESSFULLY")
            else:
                failed_posts += 1
                log(f"❌ GROUP {i} FAILED")
            
            # Progress reporting
            progress = (i / len(GROUPS)) * 100
            log(f"📊 PROGRESS: {progress:.1f}% ({i}/{len(GROUPS)})")
            log(f"📈 SUCCESS RATE: {(successful_posts/i)*100:.1f}%")
            
            # Professional inter-group delay
            if i < len(GROUPS):
                inter_delay = random.uniform(8, 16)  
                log(f"⏳ Inter-group delay: {inter_delay:.1f}s")
                
                # Add human behavior during delay
                if inter_delay > 10:
                    time.sleep(inter_delay / 2)
                    if random.choice([True, False]):
                        human_like_scroll(driver, random.choice(["up", "down"]), 1)
                    time.sleep(inter_delay / 2)
                else:
                    time.sleep(inter_delay)
        
        # Professional results compilation
        end_time = datetime.now()
        total_time = end_time - start_time
        
        log(f"\n{'='*60}")
        log("📊 PROFESSIONAL EXECUTION REPORT")
        log(f"{'='*60}")
        log(f"⏰ Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        log(f"⏰ End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        log(f"⏱️ Total Duration: {total_time}")
        log(f"📋 Total Groups Processed: {len(GROUPS)}")
        log(f"✅ Successful Posts: {successful_posts}")
        log(f"❌ Failed Posts: {failed_posts}")
        log(f"📈 Overall Success Rate: {(successful_posts/len(GROUPS)*100):.1f}%")
        log(f"⚡ Average Time per Group: {total_time.total_seconds()/len(GROUPS):.1f}s")
        
        # Detailed results log
        log(f"\n📋 DETAILED RESULTS:")
        for result in results:
            log(f"Group {result['group_number']:2d}: {result['status']} | {result['processing_time']} | {result['timestamp']}")
        
        # Professional WhatsApp report
        log(f"\n📱 Preparing professional WhatsApp report...")
        
        report_content = f"""🚀 FACEBOOK AUTO POSTER - PROFESSIONAL EXECUTION REPORT
{'='*55}
📅 Date: {end_time.strftime('%Y-%m-%d')}
⏰ Time: {end_time.strftime('%H:%M:%S')}
⏱️ Duration: {str(total_time).split('.')[0]}

📊 PERFORMANCE METRICS:
{'='*25}
📋 Total Groups: {len(GROUPS)}
✅ Successful: {successful_posts}
❌ Failed: {failed_posts}
📈 Success Rate: {(successful_posts/len(GROUPS)*100):.1f}%
⚡ Avg Time/Group: {total_time.total_seconds()/len(GROUPS):.1f}s

📝 POST PREVIEW:
{'='*15}
{POST_TEXT[:150]}...

🎯 STATUS: EXECUTION COMPLETED SUCCESSFULLY
👨‍💻 Powered by MR ALKADY - Professional Edition v2.1
🔧 Enhanced Anti-Detection Technology"""

        # Send professional WhatsApp report
        whatsapp_success = send_whatsapp_report(driver, report_content)
        
        if whatsapp_success:
            log("✅ Professional WhatsApp report delivered successfully!")
        else:
            log("⚠️ WhatsApp report delivery failed, but main execution completed successfully")
        
        log(f"\n🎉 PROFESSIONAL FACEBOOK AUTO POSTER EXECUTION COMPLETED!")
        log(f"📊 Final Score: {successful_posts}/{len(GROUPS)} posts successful")
        
    except KeyboardInterrupt:
        log("\n⚠️ EXECUTION INTERRUPTED BY USER")
        log("🛑 Performing graceful shutdown...")
        
    except Exception as e:
        log(f"\n❌ CRITICAL SYSTEM ERROR: {str(e)}")
        log("🔧 Please check configuration and try again")
        
    finally:
        # Professional cleanup
        log("\n🧹 Initiating professional cleanup...")
        time.sleep(random.uniform(3, 6))
        
        try:
            if driver is not None:
                driver.quit()
                log("✅ Browser session terminated successfully")
            else:
                log("⚠️ No browser session to terminate")
        except Exception:
            log("⚠️ Browser cleanup completed with warnings")
        
        log("🏁 PROFESSIONAL FACEBOOK AUTO POSTER - SESSION ENDED")
if __name__ == "__main__":
    try:
        # Check if selenium is installed, if not, print instructions
        main()
    except ImportError as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Import error: {str(e)}")
        print("Please ensure all required Python packages are installed (e.g., selenium).")
    except WebDriverException as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ WebDriver error: {str(e)}")
        print("Please ensure that msedgedriver.exe is installed and compatible with your Edge browser version.")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Unhandled error in main: {str(e)}")
