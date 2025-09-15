# ================================ REFACTORED FACEBOOK JOB SCRAPER ================================
"""
Modular Facebook Job Scraper - Main Application
Uses modular architecture for better maintainability and reliability
"""

# ================================ STANDARD IMPORTS ================================
import time
import random
import logging
import sys
import os
from datetime import datetime

# ================================ SELENIUM IMPORTS ================================
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

# ================================ MODULAR IMPORTS ================================
from Config import (
    GROUP_URLS, KEYWORDS, EXCLUDE_KEYWORDS, DRIVER_PATH, 
    WHATSAPP_CHAT, SEE_MORE_SELECTORS, POST_SELECTORS, INPUT_BOX_SELECTORS,
    MIN_SCROLLS, MAX_SCROLLS, BREAK_AFTER_GROUPS, BREAK_TIME_RANGE, LAST_SET
)
from Utils import setup_logging, check_internet_connection, save_progress, _post_sig

# ================================ GLOBAL VARIABLES ================================
processed_post_signatures = set()
sent_post_signatures = set()
session_stats = {
    'groups_processed': 0,
    'total_posts_found': 0,
    'qualified_posts': 0,
    'excluded_posts': 0,
    'duplicate_posts': 0,
    'messages_sent': 0,
    'start_time': time.time()
}

def click_most_recent_switch(driver):
    """Click the 'Most Recent' switch to enable chronological order in Facebook search results"""
    try:
        print(f"• Looking for 'Most Recent' switch to enable chronological order...")
        
        # Comprehensive selectors for the Most Recent switch based on provided HTML
        most_recent_selectors = [
            # Primary selectors based on provided HTML structure
            "//input[@aria-label='Most Recent'][@role='switch'][@type='checkbox']",
            "//input[@aria-checked='false'][@aria-label='Most Recent']",
            "//div[contains(@class, 'x78zum5')]//input[@aria-label='Most Recent']",
            
            # Alternative selectors for different Facebook layouts
            "//input[@type='checkbox'][contains(@aria-label, 'Most Recent')]",
            "//input[@role='switch'][contains(@aria-label, 'Recent')]",
            "//input[@class='x1i10hfl x9f619 xggy1nq xtpw4lu x1tutvks x1s3xk63 x1s07b3s x1ypdohk x5yr21d x1o0tod xdj266r x14z9mp xat24cr x1lziwak x1w3u9th x1a2a7pz xexx8yu xyri2b x18d9i69 x1c1uobl x10l6tqk x13vifvy xh8yej3']",
            
            # Text-based selectors
            "//div[contains(text(), 'Most Recent')]/following::input[@type='checkbox'][1]",
            "//div[contains(text(), 'Most Recent')]/preceding::input[@type='checkbox'][1]",
            "//span[contains(text(), 'Most Recent')]/ancestor::div[1]//input[@type='checkbox']",
            
            # Generic switch selectors
            "//input[@role='switch'][contains(@dir, 'ltr')]",
            "//div[@role='button']//input[@type='checkbox'][@aria-checked='false']"
        ]
        
        most_recent_switch = None
        used_selector = None
        
        for selector in most_recent_selectors:
            try:
                switch = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                
                if switch.is_displayed():
                    # Check if switch is not already checked
                    aria_checked = switch.get_attribute('aria-checked')
                    aria_label = switch.get_attribute('aria-label')
                    
                    if aria_checked == 'false' and 'most recent' in (aria_label or '').lower():
                        most_recent_switch = switch
                        used_selector = selector
                        print(f"• Found 'Most Recent' switch using selector: {selector[:50]}...")
                        break
                    elif aria_checked == 'true' and 'most recent' in (aria_label or '').lower():
                        print(f"• ℹ️ 'Most Recent' switch already enabled")
                        return True
                        
            except Exception as e:
                continue
        
        if most_recent_switch:
            try:
                # Enhanced human-like interaction
                print(f"• Activating 'Most Recent' switch...")
                
                # Method 1: Direct click with human-like behavior
                random_mouse_movement(driver)
                human_like_delay(0.3, 0.8)
                
                # Scroll switch into view if needed
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", most_recent_switch)
                human_like_delay(0.5, 1.0)
                
                # Click the switch
                most_recent_switch.click()
                print(f"• 'Most Recent' switch activated successfully!")
                print(f"• Posts will now be displayed in chronological order (newest first)")
                
                # Wait for the page to update
                time.sleep(random.uniform(2, 4))
                
                # Verify the switch was activated
                try:
                    updated_switch = driver.find_element(By.XPATH, used_selector)
                    new_aria_checked = updated_switch.get_attribute('aria-checked')
                    if new_aria_checked == 'true':
                        print(f"• ✓ Verified: 'Most Recent' switch is now active")
                        return True
                    else:
                        print(f"• Warning: Switch state verification failed")
                except:
                    print(f"• ℹ️ Could not verify switch state, assuming success")
                    return True
                    
            except Exception as click_error:
                try:
                    # Method 2: JavaScript fallback
                    print(f"• Trying JavaScript click as fallback...")
                    driver.execute_script("arguments[0].click();", most_recent_switch)
                    print(f"• 'Most Recent' switch activated via JavaScript!")
                    time.sleep(random.uniform(2, 4))
                    return True
                    
                except Exception as js_error:
                    print(f"• Could not click 'Most Recent' switch: {str(js_error)[:50]}...")
                    return False
        else:
            print(f"• ℹ️ 'Most Recent' switch not found or already enabled")
            return False
            
    except Exception as e:
        print(f"• Error handling 'Most Recent' switch: {str(e)[:50]}...")
        return False

# ================================ HUMAN-LIKE BEHAVIOR FUNCTIONS ================================
def human_like_delay(min_delay=0.5, max_delay=2.0):
    """Add human-like random delays"""
    if HUMAN_LIKE_DELAYS:
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

def apply_window_blocking(driver):
    """Apply comprehensive window blocking to prevent new tabs/windows"""
    try:
        driver.execute_script("""
        if (!window.windowBlockingApplied) {
            // Block window.open function COMPLETELY
            window.open = function() {
                console.log('New window/tab BLOCKED by automation script');
                return null;
            };
            
            // Block all target="_blank" links
            document.addEventListener('click', function(e) {
                const target = e.target;
                const link = target.tagName === 'A' ? target : target.closest('a');
                
                if (link && (link.target === '_blank' || link.target === '_new')) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    console.log('Blocked link:', link.href);
                    
                    if (link.href && link.href !== '#' && !link.href.startsWith('javascript:')) {
                        window.location.href = link.href;
                    }
                    return false;
                }
            }, true);
            
            // AGGRESSIVE VIDEO BLOCKING
            function eliminateAllVideos() {
                const videos = document.querySelectorAll('video, audio');
                videos.forEach(video => {
                    try {
                        video.pause();
                        video.muted = true;
                        video.autoplay = false;
                        video.style.display = 'none !important';
                        video.remove();
                    } catch(e) {}
                });
            }
            
            eliminateAllVideos();
            setInterval(eliminateAllVideos, 100);
            
            // Remove target attributes from existing links
            function removeTargets() {
                const links = document.querySelectorAll('a[target="_blank"], a[target="_new"]');
                links.forEach(link => {
                    link.removeAttribute('target');
                    link.target = '_self';
                });
            }
            
            removeTargets();
            setInterval(removeTargets, 500);
            
            window.windowBlockingApplied = true;
            console.log('Window blocking and video blocking applied successfully');
        }
        """)
    except Exception as e:
        print(f"• Warning: Could not apply window blocking: {str(e)[:50]}...")

def random_mouse_movement(driver):
    """Perform random mouse movements to simulate human behavior"""
    if RANDOM_MOUSE_MOVEMENTS:
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            # Random coordinates within viewport
            x_offset = random.randint(-50, 50)
            y_offset = random.randint(-50, 50)
            actions.move_by_offset(x_offset, y_offset).perform()
            human_like_delay(0.1, 0.5)
        except:
            pass

def human_like_typing(element, text):
    """Type text with human-like delays between characters"""
    for char in text:
        element.send_keys(char)
        if HUMAN_LIKE_DELAYS:
            time.sleep(random.uniform(TYPING_DELAY_MIN, TYPING_DELAY_MAX))

def random_pause():
    """Add random pauses to simulate human thinking time"""
    if RANDOM_PAUSES:
        pause_duration = random.uniform(RANDOM_PAUSE_MIN, RANDOM_PAUSE_MAX)
        time.sleep(pause_duration)

def simulate_human_reading(content_length):
    """Simulate time needed for human to read content"""
    # Assume reading speed of 200 words per minute
    words = content_length / 5  # Approximate words based on character count
    reading_time = (words / 200) * 60  # Convert to seconds
    # Cap at reasonable max and add randomness
    reading_time = min(reading_time, 3) + random.uniform(0.5, 1.5)
    time.sleep(reading_time)

# ================================ PROGRESS MANAGEMENT ================================
# ================================ DUPLICATE FUNCTION NOTE ================================

# ================================ DATE EXTRACTION AND FILTERING FUNCTIONS ================================

def extract_post_timestamp(driver, post_element):
    """Extract timestamp from a Facebook post element with detailed verification output"""
    try:
        print(f"    • DEBUG: Starting detailed timestamp extraction process...")
        # ================================ FACEBOOK TIMESTAMP SELECTORS ================================
        timestamp_selectors = [
            # ================================ COMMON FACEBOOK TIMESTAMP SELECTORS ================================
            ".//abbr[contains(@class, 'timestamp') or @title]",
            ".//time[@datetime]",
            ".//a[contains(@class, 'timestamp') or contains(text(), 'ago') or contains(text(), 'h') or contains(text(), 'd') or contains(text(), 'w')]",
            ".//span[contains(text(), 'ago') or contains(text(), 'h') or contains(text(), 'd') or contains(text(), 'w') or contains(text(), 'm')]",
            ".//div[contains(@aria-label, 'ago') or contains(text(), 'ago')]",
            # ================================ ARABIC TIMESTAMP SELECTORS ================================
            ".//span[contains(text(), 'منذ') or contains(text(), 'ساعة') or contains(text(), 'يوم') or contains(text(), 'أسبوع')]",
            ".//a[contains(text(), 'منذ') or contains(text(), 'ساعة') or contains(text(), 'يوم')]",
            # ================================ GENERIC SELECTORS ================================
            ".//span[contains(@class, 'timestampContent')]",
            ".//span[@data-hover='tooltip']",
            ".//a[@data-hover='tooltip']",
            # ================================ MOBILE FACEBOOK SELECTORS ================================
            ".//div[contains(@class, 'story_body_container')]//abbr",
            ".//div[contains(@data-ft, 'top_level_post_id')]//abbr",
            # ================================ ADDITIONAL SELECTORS FOR VARIOUS FACEBOOK LAYOUTS ================================
            ".//span[contains(text(), 'january') or contains(text(), 'february') or contains(text(), 'march')]",
            ".//span[contains(text(), 'april') or contains(text(), 'may') or contains(text(), 'june')]",
            ".//span[contains(text(), 'july') or contains(text(), 'august') or contains(text(), 'september')]",
            ".//span[contains(text(), 'october') or contains(text(), 'november') or contains(text(), 'december')]",
            ".//a[contains(text(), 'january') or contains(text(), 'february') or contains(text(), 'march')]",
            ".//a[contains(text(), 'april') or contains(text(), 'may') or contains(text(), 'june')]",
            ".//a[contains(text(), 'july') or contains(text(), 'august') or contains(text(), 'september')]",
            ".//a[contains(text(), 'october') or contains(text(), 'november') or contains(text(), 'december')]"
        ]
        
        for selector_index, selector in enumerate(timestamp_selectors):
            try:
                print(f"    • DEBUG: Trying selector {selector_index + 1}/{len(timestamp_selectors)}: {selector[:60]}...")
                timestamp_elements = post_element.find_elements(By.XPATH, selector)
                
                if not timestamp_elements:
                    print(f"    • DEBUG: No elements found with this selector")
                    continue
                    
                print(f"    • DEBUG: Found {len(timestamp_elements)} timestamp element(s) with this selector")
                
                for element_index, element in enumerate(timestamp_elements):
                    print(f"    • DEBUG: Examining element {element_index + 1}/{len(timestamp_elements)}")
                    
                    # ================================ TRY TO GET FULL TIMESTAMP FROM TITLE ATTRIBUTE ================================
                    title = element.get_attribute('title')
                    if title and ('at' in title.lower() or 'في' in title or len(title) > 10):
                        print(f"    • DEBUG: Found title attribute: '{title}'")
                        parsed_date = parse_facebook_timestamp(title)
                        if parsed_date:
                            print(f"    • DEBUG: SUCCESS - Parsed title timestamp: {parsed_date.strftime('%Y-%m-%d %H:%M:%S')}")
                            return parsed_date, title
                    
                    # ================================ TRY TO GET DATETIME ATTRIBUTE ================================
                    datetime_attr = element.get_attribute('datetime')
                    if datetime_attr:
                        print(f"    • DEBUG: Found datetime attribute: '{datetime_attr}'")
                        try:
                            parsed_date = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                            print(f"    • DEBUG: SUCCESS - Parsed datetime: {parsed_date.strftime('%Y-%m-%d %H:%M:%S')}")
                            return parsed_date, datetime_attr
                        except Exception as parse_error:
                            print(f"    • DEBUG: Failed to parse datetime: {parse_error}")
                            pass
                    
                    # ================================ TRY TO GET RELATIVE TIME FROM TEXT ================================
                    text = element.text.strip()
                    if text and len(text) < 50:  # Avoid long content
                        print(f"    • DEBUG: Found element text: '{text}'")
                        parsed_date = parse_relative_time(text)
                        if parsed_date:
                            print(f"    • DEBUG: SUCCESS - Parsed relative time: {parsed_date.strftime('%Y-%m-%d %H:%M:%S')}")
                            return parsed_date, text
                        else:
                            print(f"    • DEBUG: Could not parse relative time from: '{text}'")
                    else:
                        if text:
                            print(f"    • DEBUG: Element text too long ({len(text)} chars): '{text[:30]}...'")
                        else:
                            print(f"    • DEBUG: No text content in element")
                            
            except Exception as e:
                print(f"    • DEBUG: Error with selector {selector_index + 1}: {str(e)[:50]}...")
                continue
        
        # ================================ FALLBACK: SEARCH IN POST HTML FOR TIMESTAMP PATTERNS ================================
        try:
            post_html = post_element.get_attribute('innerHTML')
            if post_html:
                # Look for common timestamp patterns in HTML
                import re
                timestamp_patterns = [
                    r'title="([^"]*(?:at|في)[^"]*(?:20\d{2})[^"]*)"',
                    r'datetime="([^"]+)"',
                    r'data-utime="(\d+)"'
                ]
                
                for pattern in timestamp_patterns:
                    matches = re.findall(pattern, post_html)
                    for match in matches:
                        if 'data-utime' in pattern:
                            try:
                                # Unix timestamp
                                timestamp = int(match)
                                parsed_date = datetime.fromtimestamp(timestamp)
                                return parsed_date, f"Unix: {match}"
                            except:
                                continue
                        else:
                            parsed_date = parse_facebook_timestamp(match)
                            if parsed_date:
                                return parsed_date, match
        except:
            pass
            
    except Exception as e:
        print(f"• Warning: Error extracting timestamp: {str(e)[:50]}...")
    
    return None, None

def parse_facebook_timestamp(timestamp_str):
    """Parse Facebook's full timestamp format"""
    try:
        # ================================ FACEBOOK TIMESTAMP FORMATS ================================
        formats = [
            "%A, %B %d, %Y at %I:%M %p",  # Monday, January 1, 2024 at 12:30 PM
            "%B %d, %Y at %I:%M %p",       # January 1, 2024 at 12:30 PM
            "%B %d at %I:%M %p",           # January 1 at 12:30 PM
            "%Y-%m-%d %H:%M:%S",           # 2024-01-01 12:30:00
            "%Y-%m-%dT%H:%M:%S",           # 2024-01-01T12:30:00
            "%d/%m/%Y %H:%M",              # 01/01/2024 12:30
            "%m/%d/%Y %H:%M",              # 01/01/2024 12:30
        ]
        
        # Clean the timestamp string
        clean_timestamp = timestamp_str.strip()
        
        for fmt in formats:
            try:
                return datetime.strptime(clean_timestamp, fmt)
            except ValueError:
                continue
                
        # ================================ TRY PARSING WITH DATEUTIL IF AVAILABLE ================================
        try:
            from dateutil.parser import parse as dateutil_parse
            return dateutil_parse(clean_timestamp)
        except ImportError:
            pass
        except Exception:
            pass
            
    except Exception as e:
        pass
    
    return None

def parse_relative_time(time_text):
    """Parse relative time strings like '2h', '3d', '1w ago', '23september', etc."""
    try:
        import re
        from datetime import timedelta
        
        if not time_text:
            return None
            
        text = time_text.lower().strip()
        now = datetime.now()
        
        print(f"    • DEBUG: Parsing Facebook timestamp text: '{text}'")
        
        # ================================ ENHANCED PATTERNS FOR FACEBOOK FORMATS ================================
        patterns = [
            # ================================ FACEBOOK'S INCOMPLETE FORMATS (8m, 8h, 23d, etc.) ================================
            (r'^(\d+)\s*m$', 'minutes'),  # "8m"
            (r'^(\d+)\s*h$', 'hours'),   # "8h" 
            (r'^(\d+)\s*d$', 'days'),    # "23d"
            (r'^(\d+)\s*w$', 'weeks'),   # "2w"
            (r'^(\d+)\s*mo$', 'months'), # "3mo"
            (r'^(\d+)\s*y$', 'years'),   # "1y"
            
            # ================================ STANDARD RELATIVE TIME WITH VARIATIONS ================================
            (r'(\d+)\s*m(?:in|inute|inutes)?(?:\s+ago)?$', 'minutes'),
            (r'(\d+)\s*minutes?\s*ago?', 'minutes'),
            (r'(\d+)\s*mins?\s*ago?', 'minutes'),
            
            # Hours variations
            (r'(\d+)\s*h(?:r|our|ours|rs)?(?:\s+ago)?$', 'hours'),
            (r'(\d+)\s*hours?\s*ago?', 'hours'),
            (r'(\d+)\s*hrs?\s*ago?', 'hours'),
            
            # Days variations
            (r'(\d+)\s*d(?:ay|ays)?(?:\s+ago)?$', 'days'),
            (r'(\d+)\s*days?\s*ago?', 'days'),
            
            # Weeks variations
            (r'(\d+)\s*w(?:eek|eeks)?(?:\s+ago)?$', 'weeks'),
            (r'(\d+)\s*weeks?\s*ago?', 'weeks'),
            
            # Months variations
            (r'(\d+)\s*months?\s*ago?', 'months'),
            (r'(\d+)\s*mo\s*ago?', 'months'),
            (r'(\d+)\s*mos\s*ago?', 'months'),
            
            # Years variations
            (r'(\d+)\s*y(?:ear|ears)?(?:\s+ago)?$', 'years'),
            (r'(\d+)\s*years?\s*ago?', 'years'),
            (r'(\d+)\s*yrs?\s*ago?', 'years'),
        ]
        
        # ================================ ARABIC RELATIVE TIME PATTERNS ================================
        arabic_patterns = [
            (r'منذ\s*(\d+)\s*دقيقة', 'minutes'),
            (r'منذ\s*(\d+)\s*ساعة', 'hours'),
            (r'منذ\s*(\d+)\s*يوم', 'days'),
            (r'منذ\s*(\d+)\s*أسبوع', 'weeks'),
            (r'منذ\s*(\d+)\s*شهر', 'months'),
            (r'منذ\s*(\d+)\s*سنة', 'years'),
        ]
        
        all_patterns = patterns + arabic_patterns
        
        for pattern, unit in all_patterns:
            match = re.search(pattern, text)
            if match:
                amount = int(match.group(1))
                print(f"    • DATE FORMAT DETECTED: Relative Time Pattern - '{pattern}'")
                print(f"    • PARSED VALUE: {amount} {unit} ago")
                
                if unit == 'minutes':
                    result = now - timedelta(minutes=amount)
                elif unit == 'hours':
                    result = now - timedelta(hours=amount)
                elif unit == 'days':
                    result = now - timedelta(days=amount)
                elif unit == 'weeks':
                    result = now - timedelta(weeks=amount)
                elif unit == 'months':
                    result = now - timedelta(days=amount * 30)  # Approximate
                elif unit == 'years':
                    result = now - timedelta(days=amount * 365)  # Approximate
                    
                print(f"    • CALCULATED DATE: {result.strftime('%Y-%m-%d %H:%M:%S')}")
                return result
        
        # ================================ FACEBOOK FULL DATE WITH TIME (e.g., "August 16 at 11:51 AM") ================================
        # Month name to number mapping
        month_map = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        
        # Facebook full date patterns with time: "August 16 at 11:51 AM"
        facebook_full_patterns = [
            (r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})\s+at\s+(\d{1,2}):(\d{2})\s+(am|pm)', 'full_datetime'),
            (r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})\s+at\s+(\d{1,2}):(\d{2})\s+(am|pm)', 'full_datetime'),
            (r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?!\d)', 'date_only'),
            (r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})(?!\d)', 'date_only')
        ]
        
        for pattern, format_type in facebook_full_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                month_name = match.group(1).lower()
                day = int(match.group(2))
                month_num = month_map.get(month_name)
                
                if month_num:
                    current_year = now.year
                    
                    if format_type == 'full_datetime':
                        # Handle time components
                        hour = int(match.group(3))
                        minute = int(match.group(4))
                        ampm = match.group(5).lower()
                        
                        print(f"    • DATE FORMAT DETECTED: Facebook Full DateTime - '{month_name.title()} {day} at {hour}:{minute:02d} {ampm.upper()}'")
                        print(f"    • PATTERN MATCHED: {pattern}")
                        
                        # Convert to 24-hour format
                        if ampm == 'pm' and hour != 12:
                            hour += 12
                        elif ampm == 'am' and hour == 12:
                            hour = 0
                        
                        try:
                            result = datetime(current_year, month_num, day, hour, minute)
                            
                            # If date is in future, use previous year
                            if result > now:
                                result = datetime(current_year - 1, month_num, day, hour, minute)
                                print(f"    • YEAR ADJUSTMENT: Using previous year {current_year - 1} (original date was in future)")
                            else:
                                print(f"    • YEAR USED: Current year {current_year}")
                            
                            print(f"    • FINAL PARSED DATE: {result.strftime('%Y-%m-%d %H:%M:%S')}")
                            return result
                        except ValueError as ve:
                            print(f"    • DATE FORMAT ERROR: Invalid Facebook datetime (Day {day}, Month {month_num}): {ve}")
                            continue
                    else:
                        # Date only format
                        print(f"    • DATE FORMAT DETECTED: Facebook Date Only - '{month_name.title()} {day}'")
                        print(f"    • PATTERN MATCHED: {pattern}")
                        
                        try:
                            result = datetime(current_year, month_num, day)
                            
                            # If date is in future, use previous year
                            if result > now:
                                result = datetime(current_year - 1, month_num, day)
                                print(f"    • YEAR ADJUSTMENT: Using previous year {current_year - 1} (original date was in future)")
                            else:
                                print(f"    • YEAR USED: Current year {current_year}")
                            
                            print(f"    • FINAL PARSED DATE: {result.strftime('%Y-%m-%d')}")
                            return result
                        except ValueError as ve:
                            print(f"    • DATE FORMAT ERROR: Invalid Facebook date (Day {day}, Month {month_num}): {ve}")
                            continue
        
        # ================================ FACEBOOK'S INCOMPLETE MONTH FORMATS (e.g., "23september", "23 sep") ================================
        month_patterns = [
            # No space between day and month (Facebook's compact format)
            (r'(\d{1,2})jan(?:uary)?(?:\s|$)', 1),
            (r'(\d{1,2})feb(?:ruary)?(?:\s|$)', 2),
            (r'(\d{1,2})mar(?:ch)?(?:\s|$)', 3),
            (r'(\d{1,2})apr(?:il)?(?:\s|$)', 4),
            (r'(\d{1,2})may(?:\s|$)', 5),
            (r'(\d{1,2})jun(?:e)?(?:\s|$)', 6),
            (r'(\d{1,2})jul(?:y)?(?:\s|$)', 7),
            (r'(\d{1,2})aug(?:ust)?(?:\s|$)', 8),
            (r'(\d{1,2})sep(?:tember)?(?:\s|$)', 9),  # Handles "23september"
            (r'(\d{1,2})oct(?:ober)?(?:\s|$)', 10),
            (r'(\d{1,2})nov(?:ember)?(?:\s|$)', 11),
            (r'(\d{1,2})dec(?:ember)?(?:\s|$)', 12),
            
            # With space between day and month (standard format)
            (r'(\d{1,2})\s+(jan|january)(?:\s|$)', 1),
            (r'(\d{1,2})\s+(feb|february)(?:\s|$)', 2),
            (r'(\d{1,2})\s+(mar|march)(?:\s|$)', 3),
            (r'(\d{1,2})\s+(apr|april)(?:\s|$)', 4),
            (r'(\d{1,2})\s+(may)(?:\s|$)', 5),
            (r'(\d{1,2})\s+(jun|june)(?:\s|$)', 6),
            (r'(\d{1,2})\s+(jul|july)(?:\s|$)', 7),
            (r'(\d{1,2})\s+(aug|august)(?:\s|$)', 8),
            (r'(\d{1,2})\s+(sep|september)(?:\s|$)', 9),
            (r'(\d{1,2})\s+(oct|october)(?:\s|$)', 10),
            (r'(\d{1,2})\s+(nov|november)(?:\s|$)', 11),
            (r'(\d{1,2})\s+(dec|december)(?:\s|$)', 12),
            
            # Month first format (common in some regions)
            (r'(jan|january)\s+(\d{1,2})(?:\s|$)', 1),
            (r'(feb|february)\s+(\d{1,2})(?:\s|$)', 2),
            (r'(mar|march)\s+(\d{1,2})(?:\s|$)', 3),
            (r'(apr|april)\s+(\d{1,2})(?:\s|$)', 4),
            (r'(may)\s+(\d{1,2})(?:\s|$)', 5),
            (r'(jun|june)\s+(\d{1,2})(?:\s|$)', 6),
            (r'(jul|july)\s+(\d{1,2})(?:\s|$)', 7),
            (r'(aug|august)\s+(\d{1,2})(?:\s|$)', 8),
            (r'(sep|september)\s+(\d{1,2})(?:\s|$)', 9),
            (r'(oct|october)\s+(\d{1,2})(?:\s|$)', 10),
            (r'(nov|november)\s+(\d{1,2})(?:\s|$)', 11),
            (r'(dec|december)\s+(\d{1,2})(?:\s|$)', 12),
        ]
        
        for pattern, month_num in month_patterns:
            match = re.search(pattern, text)
            if match:
                current_year = now.year
                
                # Determine day based on pattern structure
                if '\\s+' in pattern and pattern.startswith('(\\d'):
                    # Day-first format: "23 september" or "23september"
                    day = int(match.group(1))
                    format_name = "Facebook Day-Month Format"
                    print(f"    • DATE FORMAT DETECTED: {format_name} - Day {day}, Month {month_num}")
                elif pattern.startswith('(jan|') or pattern.startswith('(feb|') or pattern.startswith('(mar|'):
                    # Month-first format: "september 23"
                    day = int(match.group(2))
                    format_name = "Facebook Month-Day Format"
                    print(f"    • DATE FORMAT DETECTED: {format_name} - Month {month_num}, Day {day}")
                else:
                    # Compact format: "23september"
                    day = int(match.group(1))
                    format_name = "Facebook Compact Format"
                    print(f"    • DATE FORMAT DETECTED: {format_name} - Day {day}, Month {month_num}")
                
                print(f"    • PATTERN MATCHED: {pattern}")
                
                try:
                    # Try current year first
                    result = datetime(current_year, month_num, day)
                    
                    # If the date is in the future, it's probably from last year
                    if result > now:
                        result = datetime(current_year - 1, month_num, day)
                        print(f"    • YEAR ADJUSTMENT: Using previous year {current_year - 1} (original date was in future)")
                    else:
                        print(f"    • YEAR USED: Current year {current_year}")
                    
                    print(f"    • FINAL PARSED DATE: {result.strftime('%Y-%m-%d')}")
                    return result
                except ValueError as ve:
                    print(f"    • DATE FORMAT ERROR: Invalid date (Day {day}, Month {month_num}): {ve}")
                    continue
        
        # ================================ FULL DATE WITH YEAR (e.g., "23 september 2025", "sep 23 2025") ================================
        full_date_patterns = [
            # Day-Month-Year format: "23 september 2025"
            (r'(\d{1,2})\s+(jan|january)\s+(\d{4})', 1),
            (r'(\d{1,2})\s+(feb|february)\s+(\d{4})', 2),
            (r'(\d{1,2})\s+(mar|march)\s+(\d{4})', 3),
            (r'(\d{1,2})\s+(apr|april)\s+(\d{4})', 4),
            (r'(\d{1,2})\s+(may)\s+(\d{4})', 5),
            (r'(\d{1,2})\s+(jun|june)\s+(\d{4})', 6),
            (r'(\d{1,2})\s+(jul|july)\s+(\d{4})', 7),
            (r'(\d{1,2})\s+(aug|august)\s+(\d{4})', 8),
            (r'(\d{1,2})\s+(sep|september)\s+(\d{4})', 9),  # Handles "23 september 2025"
            (r'(\d{1,2})\s+(oct|october)\s+(\d{4})', 10),
            (r'(\d{1,2})\s+(nov|november)\s+(\d{4})', 11),
            (r'(\d{1,2})\s+(dec|december)\s+(\d{4})', 12),
            
            # Month-Day-Year format: "september 23 2025"
            (r'(jan|january)\s+(\d{1,2})\s+(\d{4})', 1),
            (r'(feb|february)\s+(\d{1,2})\s+(\d{4})', 2),
            (r'(mar|march)\s+(\d{1,2})\s+(\d{4})', 3),
            (r'(apr|april)\s+(\d{1,2})\s+(\d{4})', 4),
            (r'(may)\s+(\d{1,2})\s+(\d{4})', 5),
            (r'(jun|june)\s+(\d{1,2})\s+(\d{4})', 6),
            (r'(jul|july)\s+(\d{1,2})\s+(\d{4})', 7),
            (r'(aug|august)\s+(\d{1,2})\s+(\d{4})', 8),
            (r'(sep|september)\s+(\d{1,2})\s+(\d{4})', 9),
            (r'(oct|october)\s+(\d{1,2})\s+(\d{4})', 10),
            (r'(nov|november)\s+(\d{1,2})\s+(\d{4})', 11),
            (r'(dec|december)\s+(\d{1,2})\s+(\d{4})', 12),
            
            # Compact format with year: "23september2025"
            (r'(\d{1,2})(jan|january)(\d{4})', 1),
            (r'(\d{1,2})(feb|february)(\d{4})', 2),
            (r'(\d{1,2})(mar|march)(\d{4})', 3),
            (r'(\d{1,2})(apr|april)(\d{4})', 4),
            (r'(\d{1,2})(may)(\d{4})', 5),
            (r'(\d{1,2})(jun|june)(\d{4})', 6),
            (r'(\d{1,2})(jul|july)(\d{4})', 7),
            (r'(\d{1,2})(aug|august)(\d{4})', 8),
            (r'(\d{1,2})(sep|september)(\d{4})', 9),
            (r'(\d{1,2})(oct|october)(\d{4})', 10),
            (r'(\d{1,2})(nov|november)(\d{4})', 11),
            (r'(\d{1,2})(dec|december)(\d{4})', 12),
        ]
        
        for pattern, month_num in full_date_patterns:
            match = re.search(pattern, text)
            if match:
                # Determine day and year based on pattern structure
                if pattern.startswith('(\\d') and '\\s+' in pattern:
                    # Day-Month-Year format: "23 september 2025"
                    day = int(match.group(1))
                    year = int(match.group(3))
                    format_name = "Facebook Day-Month-Year Format"
                    print(f"    • DATE FORMAT DETECTED: {format_name} - Day {day}, Month {month_num}, Year {year}")
                elif pattern.startswith('(jan|') or pattern.startswith('(feb|') or pattern.startswith('(mar|'):
                    # Month-Day-Year format: "september 23 2025"
                    day = int(match.group(2))
                    year = int(match.group(3))
                    format_name = "Facebook Month-Day-Year Format"
                    print(f"    • DATE FORMAT DETECTED: {format_name} - Month {month_num}, Day {day}, Year {year}")
                else:
                    # Compact format: "23september2025"
                    day = int(match.group(1))
                    year = int(match.group(3))
                    format_name = "Facebook Compact Year Format"
                    print(f"    • DATE FORMAT DETECTED: {format_name} - Day {day}, Month {month_num}, Year {year}")
                
                print(f"    • PATTERN MATCHED: {pattern}")
                
                try:
                    result = datetime(year, month_num, day)
                    print(f"    • FINAL PARSED DATE: {result.strftime('%Y-%m-%d')}")
                    return result
                except ValueError as ve:
                    print(f"    • DATE FORMAT ERROR: Invalid full date (Day {day}, Month {month_num}, Year {year}): {ve}")
                    continue
        

        if 'just now' in text or 'now' in text or 'الآن' in text:
            print(f"    • DATE FORMAT DETECTED: Special Case - 'Just Now'")
            print(f"    • FINAL PARSED DATE: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            return now
        elif 'yesterday' in text or 'أمس' in text:
            result = now - timedelta(days=1)
            print(f"    • DATE FORMAT DETECTED: Special Case - 'Yesterday'")
            print(f"    • FINAL PARSED DATE: {result.strftime('%Y-%m-%d %H:%M:%S')}")
            return result
            
        print(f"    • DATE FORMAT: No matching pattern found for '{text}'")
        print(f"    • RESULT: Unable to parse timestamp - treating as unknown age")
        return None
            
    except Exception as e:
        print(f"    • DEBUG: Error parsing time '{time_text}': {str(e)[:50]}...")
        return None

def is_post_within_timeframe(post_date, months=3):
    """Check if a post is within the specified number of months"""
    if not post_date:
        return True  # If we can't determine date, include the post
    
    try:
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=months * 30)  # Approximate
        return post_date >= cutoff_date
    except Exception:
        return True  # Include post if there's an error

def should_stop_scrolling_based_on_dates(recent_post_dates, months=3, min_recent_posts=2):
    """Determine if scrolling should stop based on recent post dates"""
    if not ENABLE_DATE_FILTERING or not STOP_SCROLLING_ON_OLD_POSTS:
        return False
        
    if len(recent_post_dates) < min_recent_posts:
        return False
        
    # Check if most recent posts are old
    old_posts_count = 0
    for post_date in recent_post_dates[-min_recent_posts:]:
        if post_date and not is_post_within_timeframe(post_date, months):
            old_posts_count += 1
    
    # Stop if most recent posts are old
    return old_posts_count >= min_recent_posts

# ================================ INTERNET CONNECTION CHECK ================================
def check_internet_connection(timeout=INTERNET_CHECK_TIMEOUT, max_wait_minutes=MAX_WAIT_MINUTES, groups_processed=0, qualified_posts=None):
    """Check if there is an active internet connection and wait until it returns."""
    host = "8.8.8.8"  # ================================ GOOGLE DNS SERVER ================================
    port = 53  # ================================ TCP PORT FOR DNS ================================
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    while True:
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            print("Internet connection is active.")
            return True
        except socket.error as e:
            elapsed_time = time.time() - start_time
            if elapsed_time > max_wait_seconds:
                print(f"• No internet connection after waiting {max_wait_minutes} minutes. Saving progress and giving up.")
                if qualified_posts is not None:
                    save_progress(current_set,groups_processed, qualified_posts)
                return False
            print(f"• No internet connection. Waiting 10 seconds before retrying... (Elapsed: {elapsed_time:.1f}s)")
            time.sleep(10)

# ================================ ENHANCED AUTHENTICATION SYSTEM ================================

class FacebookAuthManager:
    def __init__(self, mobile, password):
        self.mobile = mobile
        self.password = password
        self.session_data = {}
        self.last_auth_check = None
        self.login_attempts = 0
        self.max_login_attempts = 3
        
    def load_session(self):
        """Load saved session data"""
        try:
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, 'rb') as f:
                    self.session_data = pickle.load(f)
                    
                # ================================ CHECK SESSION NOT TOO OLD 24 HOURS ================================
                try:
                    # Handle different datetime parsing methods for compatibility
                    timestamp_str = self.session_data.get('timestamp', '2020-01-01T00:00:00')
                    if hasattr(datetime, 'fromisoformat'):
                        # Python 3.7+
                        session_time = datetime.fromisoformat(timestamp_str)
                    else:
                        # Older Python versions - parse manually
                        # Remove timezone info if present
                        if '+' in timestamp_str:
                            timestamp_str = timestamp_str.split('+')[0]
                        elif 'T' in timestamp_str:
                            # Parse ISO format: YYYY-MM-DDTHH:MM:SS
                            session_time = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
                        else:
                            # Parse date only: YYYY-MM-DD
                            session_time = datetime.strptime(timestamp_str, '%Y-%m-%d')
                    
                    if datetime.now() - session_time > timedelta(hours=24):
                        print("• Session data too old, will create fresh session")
                        return False
                except Exception as parse_error:
                    print(f"• Warning: Could not parse session timestamp: {parse_error}")
                    return False
                    
                print(f"• Session data loaded from {SESSION_FILE}")
                return True
        except Exception as e:
            print(f"• Warning: Could not load session data: {str(e)[:50]}...")
        return False
    
    def save_session(self, driver):
        """Save session data for persistence"""
        try:
            cookies = driver.get_cookies()
            
            # ================================ GET STORAGE DATA SAFELY ================================
            local_storage = {}
            session_storage = {}
            try:
                local_storage = driver.execute_script("return localStorage;") or {}
                session_storage = driver.execute_script("return sessionStorage;") or {}
            except:
                pass
            
            self.session_data = {
                'cookies': cookies,
                'local_storage': local_storage,
                'session_storage': session_storage,
                'current_url': driver.current_url,
                'timestamp': datetime.now().isoformat(),
                'user_agent': driver.execute_script("return navigator.userAgent;")
            }
            
            with open(SESSION_FILE, 'wb') as f:
                pickle.dump(self.session_data, f)
            print(f"• Session data saved to {SESSION_FILE}")
            return True
        except Exception as e:
            print(f"• Warning: Could not save session data: {str(e)[:50]}...")
        return False
    
    def restore_session(self, driver):
        """Restore saved session to browser"""
        try:
            if not self.session_data:
                return False
                
            print("• Restoring previous session...")
            driver.get("https://www.facebook.com")
            time.sleep(3)
            
            # ================================ RESTORE COOKIES ================================
            if 'cookies' in self.session_data:
                for cookie in self.session_data['cookies']:
                    try:
                        if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                            cookie['sameSite'] = 'Lax'
                        driver.add_cookie(cookie)
                    except Exception:
                        continue
            
            # ================================ RESTORE STORAGE SAFELY ================================
            if 'local_storage' in self.session_data:
                for key, value in self.session_data['local_storage'].items():
                    try:
                        driver.execute_script(f"localStorage.setItem(arguments[0], arguments[1]);", key, value)
                    except:
                        continue
            
            driver.refresh()
            time.sleep(5)
            
            print("• Session restored successfully")
            return True
            
        except Exception as e:
            print(f"• Warning: Could not restore session: {str(e)[:50]}...")
        return False
    
    def is_logged_in(self, driver):
        """Check if user is currently logged into Facebook"""
        try:
            current_url = driver.current_url.lower()
            
            # ================================ CHECK IF ON LOGIN PAGE ================================
            if any(keyword in current_url for keyword in ['login', 'checkpoint', 'recover']):
                return False
            
            if 'facebook.com' not in current_url:
                return False
            
            # ================================ CHECK FOR LOGIN FORM PRESENCE ================================
            try:
                email_field = driver.find_element(By.CSS_SELECTOR, "input[name='email'], #email")
                pass_field = driver.find_element(By.CSS_SELECTOR, "input[name='pass'], #pass")
                if email_field.is_displayed() and pass_field.is_displayed():
                    return False
            except:
                pass
            
            # ================================ CHECK FOR LOGGED IN INDICATORS ================================
            logged_in_selectors = [
                "[data-testid='blue_bar']",
                "[role='navigation']",
                "[data-testid='nav-search-input']",
                "div[role='banner']",
                "[data-testid='left_nav_menu_list']"
            ]
            
            for selector in logged_in_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element and element.is_displayed():
                        print("• User is logged in - navigation elements found")
                        return True
                except:
                    continue
            
            # ================================ JAVASCRIPT CHECK FOR USER DATA ================================
            try:
                is_logged = driver.execute_script("""
                    return document.cookie.includes('c_user') || 
                           document.querySelector('[role="navigation"]') !== null ||
                           document.querySelector('[data-testid="blue_bar"]') !== null;
                """)
                if is_logged:
                    print("• User is logged in - verified via JavaScript")
                    return True
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"• Error checking login status: {str(e)[:50]}...")
            return False
    
    def perform_login(self, driver):
        """Perform Facebook login"""
        try:
            print("• Performing Facebook login...")
            self.login_attempts += 1
            
            if self.login_attempts > self.max_login_attempts:
                print(f"• Maximum login attempts reached")
                return False
            
            driver.get("https://m.facebook.com/login")
            time.sleep(random.uniform(5, 8))
            
            # ================================ FIND LOGIN FIELDS ================================
            email_selectors = [
                "input[name='email']",
                "#m_login_email",
                "input[type='email']",
                "input[placeholder*='email']",
                "input[placeholder*='phone']"
            ]
            
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not email_field:
                print("• Could not find email field")
                return False
            
            password_field = None
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, "input[name='pass'], input[type='password']")
            except:
                print("• Could not find password field")
                return False
            
            # ================================ ENTER CREDENTIALS HUMAN LIKE TYPING ================================
            email_field.clear()
            time.sleep(random.uniform(1, 2))
            
            for char in self.mobile:
                email_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(random.uniform(1, 3))
            
            password_field.clear()
            time.sleep(random.uniform(1, 2))
            
            for char in self.password:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(random.uniform(2, 4))
            password_field.send_keys(Keys.ENTER)
            
            print("• Login credentials submitted...")
            time.sleep(random.uniform(8, 12))
            
            # ================================ WAIT FOR LOGIN COMPLETION ================================
            wait_start = time.time()
            while time.time() - wait_start < LOGIN_TIMEOUT:
                if self.is_logged_in(driver):
                    print("• Successfully logged into Facebook!")
                    self.save_session(driver)
                    self.login_attempts = 0
                    return True
                
                current_url = driver.current_url.lower()
                if any(keyword in current_url for keyword in ['checkpoint', 'two_factor']):
                    print("• Security checkpoint detected")
                    print("• Please complete the security check manually...")
                    input("• Press Enter after completing security verification...")
                    continue
                
                print(f"• Waiting for login... ({int(time.time() - wait_start)}s)")
                time.sleep(5)
            
            return False
            
        except Exception as e:
            print(f"• Login error: {str(e)[:100]}...")
            return False

def ensure_facebook_authentication(driver, auth_manager):
    """Ensure Facebook authentication with persistence"""
    print("• Checking authentication status...")
    
    # ================================ TRY RESTORE SESSION FIRST ================================
    if auth_manager.load_session():
        if auth_manager.restore_session(driver):
            if auth_manager.is_logged_in(driver):
                print("• Session restored successfully!")
                auth_manager.last_auth_check = datetime.now()
                return True
    
    # ================================ CHECK CURRENT LOGIN STATUS ================================
    try:
        driver.get("https://www.facebook.com")
        time.sleep(5)
        
        if auth_manager.is_logged_in(driver):
            print("• Already logged in!")
            auth_manager.save_session(driver)
            auth_manager.last_auth_check = datetime.now()
            return True
    except Exception as e:
        print(f"• Error checking login: {str(e)[:50]}...")
    
    # ================================ PERFORM LOGIN ================================
    print("• Authentication required...")
    if auth_manager.perform_login(driver):
        auth_manager.last_auth_check = datetime.now()
        return True
    
    return False

def periodic_auth_check(driver, auth_manager):
    """Periodically check authentication status"""
    if not auth_manager.last_auth_check:
        return True
    
    time_since_check = datetime.now() - auth_manager.last_auth_check
    if time_since_check.total_seconds() > AUTH_CHECK_INTERVAL:
        print("• Performing periodic authentication check...")
        
        if auth_manager.is_logged_in(driver):
            print("• Authentication still valid")
            auth_manager.last_auth_check = datetime.now()
            return True
        else:
            print("• Authentication expired, re-authenticating...")
            return ensure_facebook_authentication(driver, auth_manager)
    
    return True

# ================================ LOGIN CREDENTIALS ================================
Mobile = "+201099669048"
Password = "#*26AL5KADY99sSs*#"
print(f"• Using mobile: {Mobile}")
print(f"• Password length: {len(Password)} characters")

# ================================ AUTHENTICATION MANAGER INIT ================================
auth_manager = FacebookAuthManager(Mobile, Password)
print(f"• Enhanced Authentication System Initialized")

# ================================ INITIALIZE GLOBAL DEDUPLICATION SYSTEM ================================
print("• Initializing global sent posts tracking system...")
load_sent_posts()  # Load previously sent posts for cross-group deduplication

# ================================ AUTHENTICATION VERIFICATION ================================
def verify_authentication_during_operation(driver, auth_manager, operation_name="operation"):
    """Verify authentication during long-running operations"""
    try:
        if not periodic_auth_check(driver, auth_manager):
            print(f"• Authentication lost during {operation_name} - attempting re-authentication...")
            if ensure_facebook_authentication(driver, auth_manager):
                print(f"• Re-authentication successful, continuing {operation_name}")
                return True
            else:
                print(f"• Re-authentication failed during {operation_name}")
                return False
        return True
    except Exception as e:
        print(f"• Error during authentication check: {str(e)[:50]}...")
        return False

# ================================ WHATSAPP CONFIGURATION ================================
WhatsApp = "First Chat (Pinned)"
print(f"• Target WhatsApp chat: {WhatsApp}")

# ================================ SEARCH KEYWORDS ================================

print(f"• Monitoring {len(KEYWORDS)} keywords")
print(f"• Keywords: {', '.join(KEYWORDS[:1])}... (and {len(KEYWORDS)-1} more)")

# ================================ DATE FILTERING STATUS ================================
if ENABLE_DATE_FILTERING:
    print(f"• DATE FILTERING ENABLED: Only processing posts from last {MAX_POST_AGE_MONTHS} months")
    print(f"• Posts older than {MAX_POST_AGE_MONTHS} months will be automatically skipped")
    if STOP_SCROLLING_ON_OLD_POSTS:
        print(f"• SMART SCROLLING: Will stop scrolling when reaching old posts (saves time)")
        print(f"• Enhanced per-scroll date checking: Up to {POST_DATE_CHECK_COUNT} posts checked per scroll")
        print(f"• Auto-stop trigger: {MAX_OLD_POSTS_PER_SCROLL} old posts in one scroll")
    print(f"• This prevents processing outdated job posts from 1+ years ago")
    if ENABLE_MOST_RECENT_SWITCH:
        print(f"• 'MOST RECENT' SWITCH: Auto-activated for chronological order in search results")
        print(f"• Search results will show newest posts first for better date filtering")
else:
    print(f"• DATE FILTERING DISABLED: Processing all posts regardless of age")

# ================================ FACEBOOK GROUPS ================================
GROUP_URLS = [

    # ================================ FIRST SET ================================

    "https://www.facebook.com/groups/4824536287645294",
    "https://www.facebook.com/groups/wzaef.5alyh/",
    "https://www.facebook.com/groups/egyptjop",
    "https://www.facebook.com/groups/406340257579040",
    "https://www.facebook.com/groups/1451415425336164/",
    "https://www.facebook.com/groups/247199387700666",
    "https://www.facebook.com/groups/1018762211898559/",
    "https://www.facebook.com/groups/4784475178234186/",
    "https://www.facebook.com/groups/1916184325311992/",
    "https://www.facebook.com/groups/193648525211921/",
    "https://www.facebook.com/groups/1152277776175878/",
    "https://www.facebook.com/groups/1146111489606992/",
    "https://www.facebook.com/groups/shogl/",
    "https://www.facebook.com/groups/366797187807319/",
    "https://www.facebook.com/groups/677637643174270/",
    "https://www.facebook.com/groups/wazaaf/",
    "https://www.facebook.com/groups/410405026127793/",
    "https://www.facebook.com/groups/2947836015484762/",
    "https://www.facebook.com/groups/319980198653270/",
    "https://www.facebook.com/groups/247199387700666/",

    # ================================ SECOND SET ================================

    "https://www.facebook.com/groups/669171630298384/",
    "https://www.facebook.com/groups/223348709063212/",
    "https://www.facebook.com/groups/368139072869474/",
    "https://www.facebook.com/groups/3654231584855994/",
    "https://www.facebook.com/groups/378788512994745/",
    "https://www.facebook.com/groups/422160275431072/",
    "https://www.facebook.com/groups/3231209660498720/",
    "https://www.facebook.com/groups/604106265002302/",
    "https://www.facebook.com/groups/624071078907360/",
    "https://www.facebook.com/groups/123161027731575/",
    "https://www.facebook.com/groups/917942815082778/",
    "https://www.facebook.com/groups/186709744497956/",
    "https://www.facebook.com/groups/3289936394596490/",
    "https://www.facebook.com/groups/1505902203117792/",
    "https://www.facebook.com/groups/3587620811562542/",
    "https://www.facebook.com/groups/421663304184299/",
    "https://www.facebook.com/groups/242363121292280/",
    "https://www.facebook.com/groups/512900877030780/",
    "https://www.facebook.com/groups/683665275513607/",

    # ================================ THIRD SET ================================

    "https://www.facebook.com/groups/4551981621528903/",
    "https://www.facebook.com/groups/472932864668915/",
    "https://www.facebook.com/groups/944502455566634/",
    "https://www.facebook.com/groups/1080074946630317/",
    "https://www.facebook.com/groups/4867585773363159/",
    "https://www.facebook.com/groups/624845461941487/",
    "https://www.facebook.com/groups/1185103282324595/",
    "https://www.facebook.com/groups/278352690717079/",
    "https://www.facebook.com/groups/egyptjobtoday/",
    "https://www.facebook.com/groups/603195790200704/",
    "https://www.facebook.com/groups/3037843946432081/",
    "https://www.facebook.com/groups/698401717821227/",
    "https://www.facebook.com/groups/1604434263131684/",
    "https://www.facebook.com/groups/5328728670580322/",
    "https://www.facebook.com/groups/jobzawi/",
    "https://www.facebook.com/groups/462466716319201/",
    "https://www.facebook.com/groups/833764204052419/",

]

print(f"• Monitoring {len(GROUP_URLS)} Facebook groups")

# ================================ SET CALCULATION SYSTEM ================================
def calculate_sets(num_groups):
    """Calculate 4 sets for better browser performance and memory management"""
    sets = []
    if num_groups <= 15:
        sets.append((0, num_groups))
    elif num_groups <= 30:
        sets.append((0, 15))
        sets.append((15, num_groups))
    elif num_groups <= 45:
        sets.append((0, 15))
        sets.append((15, 30))
        sets.append((30, num_groups))
    else:
        # ================================ 4 SETS FOR OPTIMAL BROWSER PERFORMANCE PREVENTS FREEZING ================================
        set_size = num_groups // 4
        sets.append((0, set_size))                    # ================================ SET 1 GROUPS ================================
        sets.append((set_size, set_size * 2))         # ================================ SET 2 GROUPS ================================
        sets.append((set_size * 2, set_size * 3))     # ================================ SET 3 GROUPS ================================
        sets.append((set_size * 3, num_groups))       # ================================ SET 4 GROUPS ================================
    return sets  # ================================ LIST OF TUPLES START INDEX END INDEX ================================

set_ranges = calculate_sets(len(GROUP_URLS))
print(f"• Groups divided into {len(set_ranges)} sets for optimal performance:")
for i, (start, end) in enumerate(set_ranges):
    print(f"  Set {i+1}: Groups {start+1}-{end} ({end-start} groups)")

# ================================ BROWSER MEMORY CLEANUP ================================
def cleanup_browser_memory(driver):
    """Clean browser memory to prevent freezing"""
    try:
        # ================================ CLEAR BROWSER CACHE AND COOKIES ================================
        driver.delete_all_cookies()
        # ================================ EXECUTE JAVASCRIPT TO CLEAR MEMORY ================================
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        driver.execute_script("if (window.gc) { window.gc(); }")
        print("• Browser memory cleaned")
    except Exception as e:
        print(f"• Warning: Could not clean browser memory: {str(e)[:50]}...")

# ================================ ERROR RECOVERY SYSTEM ================================
def restart_browser_if_needed(driver, error_count):
    """Restart browser if too many errors occur"""
    if error_count >= 3:
        print("• Multiple errors detected - restarting browser for stability...")
        try:
            driver.quit()
        except:
            pass
        
        # ================================ RECREATE BROWSER WITH SAME CONFIGURATION ================================
        time.sleep(10)
        return create_browser_instance()
    return driver

def create_browser_instance():
    """Create a new browser instance with full configuration"""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    
    # ================================ MEDIA STREAM CONFIGURATION ================================
    options.add_argument('--disable-features=AutoplayIgnoreWebAudio,AutoplayIgnoreMuteSettings')
    options.add_experimental_option("prefs", { 
      "profile.managed_default_content_settings.media_stream": 2,  
      "profile.default_content_setting_values.media_stream_mic": 2,
      "profile.default_content_setting_values.media_stream_camera": 2
    })
    
    # ================================ MEMORY MANAGEMENT OPTIONS ================================
    options.add_argument("--memory-pressure-off")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-features=TranslateUI")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--aggressive-cache-discard")
    
    # ================================ ANTI DETECTION ARGUMENTS ================================
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=0")
    
    service = Service(EDGE_DRIVER_PATH)
    new_driver = webdriver.Edge(service=service, options=options)
    new_driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    new_driver.implicitly_wait(IMPLICIT_WAIT)
    
    # ================================ APPLY ANTI DETECTION SCRIPTS ================================
    new_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    new_driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    new_driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
    new_driver.execute_script("Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8})")
    new_driver.execute_script("Object.defineProperty(navigator, 'doNotTrack', {get: () => null})")
    
    return new_driver

def load_progress():
    """Load the most recent progress file and determine current set."""
    progress_files = [f for f in os.listdir() if f.startswith("progress_") and f.endswith(".json")]
    if not progress_files:
        # ================================ NO PROGRESS AT ALL START FROM SET 0 GROUP 0 ================================
        return 0, 0, []
    # ================================ GET NEWEST PROGRESS FILE BY DATE IN NAME ================================
    latest_file = sorted(progress_files)[-1]
    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    current_set = data.get("current_set", 0)
    groups_processed = data.get("groups_processed", 0)
    qualified_posts = data.get("qualified_posts", [])
    return current_set, groups_processed, qualified_posts

def save_progress(current_set, groups_processed, qualified_posts, filename=None):
    """Enhanced progress saving with performance metrics and error recovery"""
    filename = f"progress_set{current_set+1}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    
    # ================================ CALCULATE PERFORMANCE METRICS ================================
    elapsed_time = time.time() - start_time
    avg_time_per_group = elapsed_time / max(groups_processed, 1)
    
    progress_data = {
        "current_set": current_set,
        "groups_processed": groups_processed,
        "qualified_posts": qualified_posts,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "performance_metrics": {
            "elapsed_time_seconds": elapsed_time,
            "elapsed_time_minutes": elapsed_time / 60,
            "avg_time_per_group": avg_time_per_group,
            "total_posts_found": len(qualified_posts),
            "posts_per_minute": len(qualified_posts) / max(elapsed_time / 60, 1)
        },
        "configuration": {
            "memory_cleanup_interval": MEMORY_CLEANUP_INTERVAL,
            "max_qualified_posts": MAX_QUALIFIED_POSTS,
            "retry_delay": RETRY_DELAY,
            "scroll_count_range": f"{SCROLL_COUNT_MIN}-{SCROLL_COUNT_MAX}"
        }
    }
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=4)
        print(f"• Progress saved to {filename} at {progress_data['timestamp']}")
        log_with_timestamp(f"Progress saved: {groups_processed} groups, {len(qualified_posts)} posts, {elapsed_time/60:.1f}min elapsed")
    except Exception as e:
        print(f"• Error saving progress to {filename}: {str(e)[:100]}...")
        log_error(f"Failed to save progress: {str(e)}")

# ================================ EXCLUDE KEYWORDS ================================

EXCLUDE_KEYWORDS = [

    # ================================ ARABIC EXCLUDE KEYWORDS ================================

    "تليسيلز", "تلي", "تلي سيلز", "تلي-سيلز", "تليسيلز", "تلي سيلز", "سيلز" ,
    "عقارات", "عقاري", "عقار", "عقارية", "عقاريه", "عقاريين", "عقاريه",
    "فنادق", "فندق", "فندقة", "فندقي", "فندقيه", "فندقيين", "فندقية",
    "عيادة", "عيادات", "مستشفى", "مستشفيات", "مستشفي","أعضائنا",
    "صيدلي","صيدلية", "صيدليات", "صيدليه", "صيدليين", "صيدلة", "صيدلات",
    "مندوب", "مندوبين", "مندوبة", "مندوبات", "مناديب", "خدمة", "خدمه",
    "تسويق", "تسويقي", "تسويقية", "تسويق الكتروني", "تسويق الكترونى",
    "العقاري", "العقارية", "العقاريه", "العقاريين", " اكونت", "أكونت",
    "كولسنتر", "كول", "مساج", "أمن", "المطار","معمل", "الشيوخ", "النت",
    "تمريض", "البيت ", "المنزل", "الامارات", "الأمارات", "لاين", "آمين", "امن",
    "مقاولات", "مقاول", "مقاولة", "جيم", "اونلاين", "أونلاين", "انجلش", "الانجلش", 
    "الاردن", "الأردن", "اردن", "أردن", "البحيرة", "البحيره", "مصانع", "مصنع", "المنصور"
    "المنصوره", "المنصورة", "عمان", "الاسكندريه", "الاسكندرية", "اسكندريه", "اسكندرية",
    "السعوديه", "السعودية", "سعوديه", "سعودية", "الجيزه", "الجيزة", "جيزه", "جيزة", 
    "خريج", "خريجات", "خريجين", "خريجة", "سنترال",  "اكسيل", "سرقه", "سرقة",
    "التحاليل","تعبئه","تغليف","سكرتاريه","سكرتارية",
    "مودل", "المنصورها", "سكرتيره", "فاشون", "نظافه", "عمال", "سليز", "انتاج",
    "كمبيوتر", "كومبيوتر", "كمبوتر",

    # ================================ ENGLISH EXCLUDE KEYWORDS ================================

    "sales", "tele", "estate", "hotel", "clinic", "hospitals", "excel",
    "call", "callcenter", "WFH", "wfh", "B2", "B1", "customer", "service",
    "representative", "manager", "director", "jordan", "saudi", "oman", "Members", 
    "Public", "Like", "Share", "Reply", "Tito", "Store",
]

print(f"• Monitoring {len(EXCLUDE_KEYWORDS)} keywords")
print(f"• Keywords: {', '.join(EXCLUDE_KEYWORDS[:1])}... (and {len(EXCLUDE_KEYWORDS)-1} more)")

# ================================ ENHANCED BROWSER SETUP ================================
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# ================================ PREVENT NEW TABS/WINDOWS ================================
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-extensions-file-access-check")
options.add_argument("--disable-plugins-discovery")
options.add_argument("--block-new-web-contents")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-default-apps")
options.add_argument("--disable-background-mode")
options.add_argument("--single-process")
# ================================ ADDITIONAL WINDOW BLOCKING ================================
options.add_argument("--disable-features=TranslateUI,Translate")
options.add_argument("--disable-component-extensions-with-background-pages")
options.add_argument("--disable-background-networking")
options.add_argument("--disable-sync")
options.add_argument("--disable-features=MediaRouter")
options.add_argument("--disable-features=VizDisplayCompositor")
options.add_argument("--force-app-mode")
options.add_argument("--app=https://facebook.com")
options.add_argument("--disable-features=Translate,OptimizationHints,MediaRouter,DialMediaRouteProvider")

# ================================ USER DATA PERSISTENCE ================================
options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
options.add_argument(f"--profile-directory={os.path.basename(PROFILE_DIR)}")

# ================================ PERSISTENCE OPTIONS ================================
options.add_argument("--enable-features=NetworkService")
options.add_argument("--disable-features=VizDisplayCompositor")
options.add_argument("--disable-web-security")
options.add_argument("--disable-features=TranslateUI")
options.add_argument("--disable-iframes-sandbox")

# ================================ MEDIA STREAM CONFIG ================================
options.add_argument('--disable-features=AutoplayIgnoreWebAudio,AutoplayIgnoreMuteSettings')

# ================================ VIDEO AUTOPLAY PREVENTION ================================
options.add_argument('--autoplay-policy=document-user-activation-required')
options.add_argument('--disable-features=VizDisplayCompositor,AutoplayIgnoreWebAudio,AutoplayIgnoreMuteSettings')
options.add_argument('--disable-background-media-suspend')
options.add_argument('--disable-background-playback-for-testing')
options.add_argument('--disable-media-session-api')
options.add_argument('--mute-audio')
# ================================ MAXIMUM VIDEO BLOCKING OPTIONS ================================
options.add_argument('--disable-media-foundation')
options.add_argument('--disable-media-session')
options.add_argument('--disable-background-media-download')
options.add_argument('--disable-background-video-track')
options.add_argument('--disable-video-capture-use-gpu-memory-buffer')
options.add_argument('--disable-video-decode-accelerator')
options.add_argument('--disable-audio-output')
options.add_argument('--simulate-outdated-no-au')
options.add_argument('--disable-audio-support-for-desktop-share')

# ================================ MAXIMUM VIDEO BLOCKING PREFERENCES ================================
options.add_experimental_option("prefs", { 
  "profile.managed_default_content_settings.media_stream": 2,  
  "profile.default_content_setting_values.media_stream_mic": 2,
  "profile.default_content_setting_values.media_stream_camera": 2,
  # ================================ VIDEO AUTOPLAY PREVENTION SETTINGS ================================
  "profile.default_content_setting_values.media_stream": 2,
  "profile.default_content_settings.popups": 2,  # Block all popups
  "profile.default_content_setting_values.popups": 2,  # Block popups
  "profile.managed_default_content_settings.popups": 2,  # Block managed popups
  "profile.content_settings.exceptions.media_stream_mic": {},
  "profile.content_settings.exceptions.media_stream_camera": {},
  "profile.managed_default_content_settings.images": 2,
  "profile.managed_default_content_settings.media_stream": 2,
  # ================================ ENHANCED SESSION PERSISTENCE ================================
  "credentials_enable_service": True,
  "profile.password_manager_enabled": True,
  "profile.default_content_setting_values.automatic_downloads": 1,
  # ================================ PREVENT NEW WINDOWS AND TABS ================================
  "profile.default_content_setting_values.plugins": 2,
  "profile.managed_default_content_settings.plugins": 2,
  "browser.tabs.warnOnClose": False,
  "browser.tabs.warnOnCloseOtherTabs": False,
  "browser.sessionstore.resume_from_crash": False,
  # ================================ COMPLETE VIDEO AND MEDIA BLOCKING ================================
  "profile.default_content_setting_values.media_stream_mic": 2,
  "profile.default_content_setting_values.media_stream_camera": 2,
  "profile.managed_default_content_settings.media_stream": 2,
  "profile.content_settings.plugin_whitelist.adobe-flash-player": 0,
  "profile.content_settings.exceptions.plugins": {},
  "profile.managed_default_content_settings.media_stream_camera": 2,
  "profile.managed_default_content_settings.media_stream_mic": 2,
  # ================================ DISABLE ALL MEDIA CONTENT COMPLETELY ================================
  "profile.default_content_setting_values.media_stream": 2,
  "profile.default_content_setting_values.media_stream_camera": 2,
  "profile.default_content_setting_values.media_stream_mic": 2,
  "profile.managed_default_content_settings.media_stream": 2,
  # ================================ ADDITIONAL MEDIA BLOCKING ================================
  "profile.content_settings.exceptions.media_stream_camera": {},
  "profile.content_settings.exceptions.media_stream_mic": {},
  "profile.default_content_setting_values.media_galleries": 2,
  "profile.default_content_setting_values.midi_sysex": 2,
  # ================================ AGGRESSIVE VIDEO BLOCKING ================================
  "profile.managed_default_content_settings.flash": 2,
  "profile.default_content_setting_values.media_stream": 2,
  "profile.content_settings.exceptions.media_stream": {},
  "profile.default_content_settings.media_stream": 2,
  "profile.managed_default_content_settings.media_stream": 2,
  "profile.content_settings.pattern_pairs": {},
  "profile.default_content_setting_values.notifications": 2,
  "profile.managed_default_content_settings.notifications": 2
})

# ================================ MEMORY MANAGEMENT OPTIONS ================================
options.add_argument("--memory-pressure-off")
options.add_argument("--disable-background-timer-throttling")
options.add_argument("--disable-backgrounding-occluded-windows")
options.add_argument("--disable-renderer-backgrounding")
options.add_argument("--disable-features=TranslateUI")
options.add_argument("--disable-extensions")
options.add_argument("--disable-plugins")
options.add_argument("--aggressive-cache-discard")

# ================================ ANTI-DETECTION ARGUMENTS ================================
options.add_argument("--disable-web-security")
options.add_argument("--disable-features=VizDisplayCompositor")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
# ================================ UNIQUE DEBUG PORT TO PREVENT CONFLICTS ================================
import random
debug_port = random.randint(9222, 9999)
options.add_argument(f"--remote-debugging-port={debug_port}")
# ================================ GPU ERROR SUPPRESSION ================================
options.add_argument("--disable-gpu-sandbox")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--enable-unsafe-swiftshader")
options.add_argument("--disable-webgl")
options.add_argument("--disable-webgl2")
options.add_argument("--disable-3d-apis")

print("• Initializing Edge browser with enhanced authentication persistence...")

# ================================ CLEAN UP ANY EXISTING BROWSER SESSIONS ================================
try:
    import psutil
    # Find and close any existing Edge driver processes
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'msedgedriver' in proc.info['name'].lower():
                proc.terminate()
                print(f"• Cleaned up existing Edge driver process (PID: {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
            pass
except ImportError:
    print("• psutil not available for session cleanup (continuing anyway)")
except Exception as e:
    print(f"• Session cleanup warning: {str(e)[:50]}...")
    
service = Service(EDGE_DRIVER_PATH)
driver = webdriver.Edge(service=service, options=options)

# ================================ TIMEOUT CONFIGURATION ================================
driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
driver.implicitly_wait(IMPLICIT_WAIT)

driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
driver.execute_script("Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8})")
driver.execute_script("Object.defineProperty(navigator, 'doNotTrack', {get: () => null})")

# ================================ PREVENT NEW TABS AND WINDOWS ================================
driver.execute_script("""
// ================================ COMPLETE WINDOW BLOCKING SYSTEM ================================

// 1. Block window.open function COMPLETELY
const originalOpen = window.open;
window.open = function() {
    console.log('New window/tab BLOCKED by automation script');
    return null;
};

// 2. Override window.close to prevent accidental closure
const originalClose = window.close;
window.close = function() {
    console.log('Window close attempt blocked');
    return false;
};

// 3. Block all target="_blank" and new window events
document.addEventListener('click', function(e) {
    const target = e.target;
    const link = target.tagName === 'A' ? target : target.closest('a');
    
    if (link) {
        // Remove target attributes that open new windows
        if (link.target === '_blank' || link.target === '_new' || link.target === '_parent' || link.target === '_top') {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            console.log('Blocked link with target:', link.target, 'URL:', link.href);
            
            // Navigate in same window instead
            if (link.href && link.href !== '#' && !link.href.startsWith('javascript:')) {
                window.location.href = link.href;
            }
            return false;
        }
        
        // Block onclick handlers that might open windows
        const onclick = link.getAttribute('onclick');
        if (onclick && (onclick.includes('window.open') || onclick.includes('open('))) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Blocked onclick window.open:', onclick);
            return false;
        }
    }
    
    // Block any element with window.open in onclick
    if (target.onclick && target.onclick.toString().includes('window.open')) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Blocked element onclick window.open');
        return false;
    }
}, true);

// 4. Override createElement to modify elements that open new windows
const originalCreateElement = document.createElement;
document.createElement = function(tagName) {
    const element = originalCreateElement.call(this, tagName);
    
    if (tagName.toLowerCase() === 'a') {
        // Monitor and block target attributes
        const originalSetAttribute = element.setAttribute;
        element.setAttribute = function(name, value) {
            if (name === 'target' && (value === '_blank' || value === '_new')) {
                console.log('Blocked setting target attribute:', value);
                return;
            }
            return originalSetAttribute.call(this, name, value);
        };
        
        // Block target property
        Object.defineProperty(element, 'target', {
            get: function() { return '_self'; },
            set: function(value) {
                if (value === '_blank' || value === '_new') {
                    console.log('Blocked setting target property:', value);
                    return;
                }
            }
        });
    }
    
    return element;
};

// 5. Block form submissions that open new windows
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form.target === '_blank' || form.target === '_new') {
        e.preventDefault();
        console.log('Blocked form submission to new window');
        form.target = '_self';
        form.submit();
        return false;
    }
}, true);

// 6. Aggressive link monitoring and modification
function blockNewWindowLinks() {
    const links = document.querySelectorAll('a[target="_blank"], a[target="_new"], a[target="_parent"], a[target="_top"]');
    links.forEach(link => {
        const originalTarget = link.target;
        link.removeAttribute('target');
        link.target = '_self';
        console.log('Removed target attribute:', originalTarget, 'from link:', link.href);
    });
    
    // Also check for forms
    const forms = document.querySelectorAll('form[target="_blank"], form[target="_new"]');
    forms.forEach(form => {
        form.removeAttribute('target');
        form.target = '_self';
        console.log('Removed target from form');
    });
}

// 7. Run link blocking immediately and continuously
blockNewWindowLinks();
setInterval(blockNewWindowLinks, 500);

// 8. Monitor DOM changes with MutationObserver
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.addedNodes) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    if (node.tagName === 'A') {
                        if (node.target === '_blank' || node.target === '_new') {
                            node.removeAttribute('target');
                            node.target = '_self';
                            console.log('Blocked new link target:', node.href);
                        }
                    } else if (node.querySelectorAll) {
                        const newLinks = node.querySelectorAll('a[target="_blank"], a[target="_new"]');
                        newLinks.forEach(link => {
                            link.removeAttribute('target');
                            link.target = '_self';
                            console.log('Blocked new link target:', link.href);
                        });
                    }
                }
            });
        }
    });
});

// Start observing
if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
} else {
    document.addEventListener('DOMContentLoaded', function() {
        observer.observe(document.body, { childList: true, subtree: true });
    });
}

// 9. Block window focus/blur events that might trigger popups
window.addEventListener('focus', function(e) {
    e.stopPropagation();
}, true);

window.addEventListener('blur', function(e) {
    e.stopPropagation();
}, true);

// 10. Override history manipulation that might open new windows
const originalPushState = history.pushState;
const originalReplaceState = history.replaceState;

history.pushState = function(state, title, url) {
    if (url && url.includes('target=_blank')) {
        console.log('Blocked history pushState with target=_blank');
        return;
    }
    return originalPushState.call(this, state, title, url);
};

history.replaceState = function(state, title, url) {
    if (url && url.includes('target=_blank')) {
        console.log('Blocked history replaceState with target=_blank');
        return;
    }
    return originalReplaceState.call(this, state, title, url);
};

console.log('=== COMPLETE NEW WINDOW BLOCKING SYSTEM ACTIVATED ===');
""")

# ================================ APPLY ADDITIONAL WINDOW BLOCKING ================================
apply_window_blocking(driver)
print("• ✓ Advanced window blocking system activated")

# ================================ OVERRIDE NAVIGATION TO REAPPLY BLOCKING ================================
original_get = driver.get
def enhanced_get(url):
    result = original_get(url)
    time.sleep(1)  # Wait for page to load
    apply_window_blocking(driver)
    return result
driver.get = enhanced_get

# ================================ JAVASCRIPT VIDEO PREVENTION ================================
driver.execute_script("""
// ================================ MOST AGGRESSIVE VIDEO BLOCKING POSSIBLE ================================

// 1. Completely disable HTMLMediaElement play function
HTMLMediaElement.prototype.play = function() {
    console.log('Video play COMPLETELY BLOCKED by automation script');
    this.pause();
    this.currentTime = 0;
    this.muted = true;
    this.autoplay = false;
    this.removeAttribute('autoplay');
    this.style.display = 'none';
    this.style.visibility = 'hidden';
    this.style.opacity = '0';
    this.style.width = '0px';
    this.style.height = '0px';
    this.remove();
    return Promise.reject('Autoplay permanently blocked');
};

// 2. Override load function
HTMLMediaElement.prototype.load = function() {
    console.log('Video load BLOCKED');
    this.style.display = 'none';
    this.remove();
};

// 3. Override autoplay and other video attributes completely
Object.defineProperty(HTMLVideoElement.prototype, 'autoplay', {
    get: function() { return false; },
    set: function(value) { this.style.display = 'none'; this.remove(); }
});

Object.defineProperty(HTMLVideoElement.prototype, 'muted', {
    get: function() { return true; },
    set: function(value) { this.style.display = 'none'; this.remove(); }
});

Object.defineProperty(HTMLVideoElement.prototype, 'controls', {
    get: function() { return false; },
    set: function(value) { this.style.display = 'none'; this.remove(); }
});

// 4. Override src property to prevent loading
Object.defineProperty(HTMLVideoElement.prototype, 'src', {
    get: function() { return ''; },
    set: function(value) { 
        console.log('Video src blocked:', value);
        this.style.display = 'none';
        try { this.remove(); } catch(e) {}
    }
});

// 5. Aggressive video elimination function
function eliminateAllVideos() {
    const videos = document.querySelectorAll('video, audio');
    videos.forEach(video => {
        try {
            video.pause();
            video.currentTime = 0;
            video.muted = true;
            video.autoplay = false;
            video.controls = false;
            video.removeAttribute('autoplay');
            video.removeAttribute('controls');
            video.removeAttribute('src');
            video.style.display = 'none !important';
            video.style.visibility = 'hidden !important';
            video.style.opacity = '0 !important';
            video.style.width = '0px !important';
            video.style.height = '0px !important';
            video.style.position = 'absolute !important';
            video.style.left = '-9999px !important';
            video.src = '';
            video.onplay = null;
            video.oncanplay = null;
            video.onloadstart = null;
            video.onloadeddata = null;
            video.onloadedmetadata = null;
            video.remove();
            console.log('Video element completely removed');
        } catch(e) {
            try {
                video.style.display = 'none !important';
                video.parentNode.removeChild(video);
            } catch(e2) {}
        }
    });
    
    // Also remove video containers and players
    const videoContainers = document.querySelectorAll('[class*="video"], [id*="video"], [class*="player"], [id*="player"]');
    videoContainers.forEach(container => {
        if (container.querySelector('video') || container.innerHTML.includes('video')) {
            try {
                container.style.display = 'none !important';
                container.remove();
            } catch(e) {}
        }
    });
}

// 6. Block video loading at the source level
const originalCreateElement = document.createElement;
document.createElement = function(tagName) {
    const element = originalCreateElement.call(this, tagName);
    if (tagName.toLowerCase() === 'video' || tagName.toLowerCase() === 'audio') {
        element.autoplay = false;
        element.muted = true;
        element.controls = false;
        element.style.display = 'none !important';
        setTimeout(() => {
            try { element.remove(); } catch(e) {}
        }, 1);
        console.log('Video/Audio element creation blocked and removed');
    }
    return element;
};

// 7. Run elimination immediately and very frequently
eliminateAllVideos();
setInterval(eliminateAllVideos, 100); // Every 100ms for maximum blocking

// 8. Monitor for new videos with MutationObserver
const videoObserver = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.addedNodes) {
            mutation.addedNodes.forEach(function(node) {
                if (node.tagName === 'VIDEO' || node.tagName === 'AUDIO') {
                    try {
                        node.pause();
                        node.muted = true;
                        node.autoplay = false;
                        node.style.display = 'none !important';
                        node.remove();
                        console.log('New video/audio detected and immediately removed');
                    } catch(e) {}
                } else if (node.querySelectorAll) {
                    const videos = node.querySelectorAll('video, audio');
                    videos.forEach(video => {
                        try {
                            video.pause();
                            video.muted = true;
                            video.autoplay = false;
                            video.style.display = 'none !important';
                            video.remove();
                            console.log('Nested video/audio detected and removed');
                        } catch(e) {}
                    });
                }
            });
        }
    });
});
if (document.body) {
    videoObserver.observe(document.body, { childList: true, subtree: true });
}

// 9. Block all media-related network requests
if (window.fetch) {
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const url = args[0];
        if (typeof url === 'string' && (url.includes('.mp4') || url.includes('.webm') || url.includes('.mov') || url.includes('.avi') || url.includes('.m4v') || url.includes('video') || url.includes('.mp3') || url.includes('.wav'))) {
            console.log('Media request blocked:', url);
            return Promise.reject('Media request blocked');
        }
        return originalFetch.apply(this, args);
    };
}

// 10. Override XMLHttpRequest for media blocking
const originalXHROpen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function(method, url) {
    if (url && (url.includes('.mp4') || url.includes('.webm') || url.includes('.mov') || url.includes('video') || url.includes('.mp3'))) {
        console.log('XHR media request blocked:', url);
        return;
    }
    return originalXHROpen.apply(this, arguments);
};

console.log('=== MAXIMUM AGGRESSIVE VIDEO BLOCKING ACTIVATED ===');
""")

print("• MAXIMUM AGGRESSIVE video blocking activated - All videos will be eliminated")

# ================================ WEBGL OVERRIDE EDGE ================================
driver.execute_script(
    "const getParameter = WebGLRenderingContext.prototype.getParameter;"
    "WebGLRenderingContext.prototype.getParameter = function(p){"
    "  if (p === 37445) return 'Intel Inc.';"
    "  if (p === 37446) return 'Intel Iris OpenGL Engine';"
    "  return getParameter.call(this,p);"
    "};"
)

print("• Ensuring Facebook authentication with persistence...")
# ================================ INTERNET CONNECTION VERIFICATION ================================
if not check_internet_connection(groups_processed=0, qualified_posts=[]):
    print("• No internet connection after maximum wait time. Progress saved. Exiting program...")
    # ================================ ENHANCED BROWSER CLEANUP WITH ERROR HANDLING ================================
    try:
        driver.quit()
        print("• Browser closed successfully")
    except Exception as e:
        print(f"• Error closing browser: {str(e)[:50]}...")
        try:
            driver.close()
            print("• Browser force-closed")
        except:
            print("• Unable to close browser - may need manual termination")
    sys.exit(1)

# ================================ AUTHENTICATION SYSTEM USAGE ================================
if not ensure_facebook_authentication(driver, auth_manager):
    print("• Authentication failed after multiple attempts. Exiting...")
    try:
        driver.quit()
    except:
        pass
    sys.exit(1)

print("• AUTHENTICATION SUCCESSFUL!")
print("• Session is persistent - no re-login required for future runs")
print("• Your credentials are saved in browser profile for automatic login")

# ================================ DATE-AWARE SEE MORE BUTTON HANDLER ================================
def click_see_more_buttons_with_date_check(driver):
    """Click 'See More' buttons ONLY after verifying post dates are within 3 months"""
    see_more_clicked = 0
    buttons_found = False
    cutoff_date = datetime.now() - relativedelta(months=MAX_POST_AGE_MONTHS)
    today_date = datetime.now()
    
    try:
        print("• DATE-FIRST PROCESSING: Checking post dates before expanding 'See More'...")
        
        # Find all posts first
        posts_selectors = [
            "//div[@role='article']",
            "//div[@data-testid='post_message']",
            "//div[contains(@class, 'userContent')]",
            "//div[contains(@class, 'x1iorvi4') and string-length(normalize-space(.)) > 20]"
        ]
        
        all_posts = []
        for selector in posts_selectors:
            try:
                found_posts = driver.find_elements(By.XPATH, selector)
                if found_posts:
                    all_posts.extend(found_posts)
            except Exception:
                continue
        
        # Remove duplicates
        unique_posts = []
        seen_elements = set()
        for post in all_posts:
            try:
                post_signature = f"{post.location}_{post.size}_{hash(post.text[:50] if post.text else '')}"
                if post_signature not in seen_elements:
                    seen_elements.add(post_signature)
                    unique_posts.append(post)
            except:
                unique_posts.append(post)
        
        print(f"• Found {len(unique_posts)} posts to check dates for...")
        
        # Process each post: DATE FIRST, then See More
        for post_index, post in enumerate(unique_posts, 1):
            try:
                # ================================ STEP 1: CHECK DATE FIRST ================================
                print(f"• POST {post_index} - CHECKING DATE BEFORE 'See More' expansion...")
                
                post_date, timestamp_str = extract_post_timestamp(driver, post)
                
                if post_date:
                    days_old = (today_date - post_date).days
                    post_date_formatted = post_date.strftime('%Y-%m-%d')
                    
                    print(f"• POST {post_index} - Date: {post_date_formatted} ({timestamp_str})")
                    print(f"• POST {post_index} - Age: {days_old} days old")
                    
                    # Check if older than cutoff
                    if post_date <= cutoff_date:
                        print(f"• POST {post_index} - TOO OLD - Skipping 'See More' (>= {MAX_POST_AGE_MONTHS} months old)")
                        continue
                    else:
                        print(f"• POST {post_index} - DATE OK - Post is recent enough ({days_old} days old)")
                else:
                    # No date found, assume recent (cautious approach)
                    print(f"• POST {post_index} - NO DATE FOUND - Assuming recent, proceeding with 'See More'")
                
                # ================================ STEP 2: FIND AND CLICK SEE MORE ONLY IF DATE IS OK ================================
                see_more_selectors = [
                    ".//span[contains(text(), 'See more') or contains(text(), 'عرض المزيد')]",
                    ".//div[contains(text(), 'See more') or contains(text(), 'عرض المزيد')]",
                    ".//*[@aria-label='See more' or @aria-label='عرض المزيد']"
                ]
                
                post_see_more_clicked = False
                for selector in see_more_selectors:
                    try:
                        see_more_button = post.find_element(By.XPATH, selector)
                        if see_more_button.is_displayed() and see_more_button.is_enabled():
                            # Check button text
                            button_text = see_more_button.text.strip().lower()
                            valid_texts = ['see more', 'عرض المزيد', 'more', 'المزيد']
                            
                            if any(valid_text in button_text for valid_text in valid_texts) and len(button_text) <= 20:
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", see_more_button)
                                time.sleep(0.5)
                                
                                try:
                                    see_more_button.click()
                                    print(f"• POST {post_index} - 'See More' clicked (date verified)")
                                    post_see_more_clicked = True
                                    see_more_clicked += 1
                                    buttons_found = True
                                    time.sleep(random.uniform(2, 4))
                                    break
                                except:
                                    try:
                                        driver.execute_script("arguments[0].click();", see_more_button)
                                        print(f"• POST {post_index} - 'See More' JS-clicked (date verified)")
                                        post_see_more_clicked = True
                                        see_more_clicked += 1
                                        buttons_found = True
                                        time.sleep(random.uniform(2, 4))
                                        break
                                    except:
                                        continue
                    except:
                        continue
                
                if not post_see_more_clicked:
                    print(f"• POST {post_index} - No 'See More' button found (content already visible)")
                    
            except Exception as e:
                print(f"• POST {post_index} - Error: {str(e)[:50]}...")
                continue
                
    except Exception as e:
        print(f"• Error in date-aware 'See More' processing: {str(e)[:50]}...")
    
    # Provide summary
    if see_more_clicked > 0:
        print(f"• DATE-VERIFIED EXPANSION: Clicked {see_more_clicked} 'See More' buttons (all date-verified)")
    elif buttons_found:
        print(f"• 'See More' buttons found but none passed date verification")
    else:
        print(f"• No 'See More' buttons found or all content already expanded")
    
    return see_more_clicked
def click_see_more_buttons(driver):
    """Click all visible 'See more' buttons on the current page with enhanced anti-detection"""
    see_more_clicked = 0
    buttons_found = False
    try:
        print("• Expanding posts... still processing 'See More' buttons")
        # ================================ UPDATED 2025 SELECTORS SEE MORE COMPREHENSIVE ================================
        see_more_selectors = [
            # ================================ PRIMARY 2025 SELECTORS MOST COMMON ================================
            "//span[contains(text(), 'See more') or contains(text(), 'عرض المزيد') or contains(text(), 'See More')]",
            "//div[contains(text(), 'See more') or contains(text(), 'عرض المزيد') or contains(text(), 'See More')]",
            # ================================ BUTTON ROLE SELECTORS UPDATED ATTRIBUTES ================================
            "//div[@role='button'][contains(., 'See more') or contains(., 'عرض المزيد') or contains(., 'See More')]",
            "//span[@role='button'][contains(., 'See more') or contains(., 'عرض المزيد') or contains(., 'See More')]",
            # ================================ 2025 FACEBOOK SPECIFIC SELECTORS ================================
            "//div[contains(@class, 'x1i10hfl')][contains(., 'See more') or contains(., 'عرض المزيد')]",
            "//div[contains(@class, 'x1emribx')][contains(., 'See more') or contains(., 'عرض المزيد')]",
            "//span[contains(@class, 'x193iq5w')][contains(., 'See more') or contains(., 'عرض المزيد')]",
            # ================================ DATA ATTRIBUTES FACEBOOK 2025 ================================
            "//div[@data-visualcompletion='ignore-dynamic'][contains(., 'See more') or contains(., 'عرض المزيد')]",
            "//span[@data-visualcompletion='ignore'][contains(., 'See more') or contains(., 'عرض المزيد')]",
            # ================================ GENERIC CLICKABLE SEE MORE ELEMENTS ================================
            "//*[contains(@class, 'see') or contains(@class, 'more') or contains(@class, 'expand')][contains(text(), 'See more') or contains(text(), 'عرض المزيد')]",
            # ================================ ARIA LABEL BASED SELECTORS ================================
            "//*[@aria-label='See more' or @aria-label='عرض المزيد' or @aria-label='Show more']",
            # ================================ LINK BASED SELECTORS ================================
            "//a[contains(., 'See more') or contains(., 'عرض المزيد') or contains(., 'Show more')]"
        ]
        
        for selector in see_more_selectors:
            try:
                buttons = driver.find_elements(By.XPATH, selector)
                if buttons:  # Only process if buttons are found
                    buttons_found = True
                    
                for button in buttons:
                    try:
                        # ================================ GET BUTTON TEXT FOR VALIDATION ================================
                        button_text = button.text.strip().lower()
                        
                        # ================================ MORE FLEXIBLE TEXT MATCHING VARIATIONS ================================
                        valid_texts = ['see more', 'عرض المزيد', 'more', 'المزيد', 'show more', 'view more', 'read more']
                        if not any(valid_text in button_text for valid_text in valid_texts):
                            continue
                            
                        # ================================ SKIP IF BUTTON TEXT TOO LONG ================================
                        if len(button_text) > 50:
                            continue
                        
                        # ================================ CHECK IF BUTTON VISIBLE CLICKABLE ================================
                        if button.is_displayed() and button.is_enabled():
                            # ================================ SCROLL ELEMENT INTO VIEW BETTER POSITIONING ================================
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", button)
                            time.sleep(random.uniform(1, 2))
                            
                            # ================================ TRY MULTIPLE CLICK METHODS ================================
                            try:
                                # ================================ METHOD 1 REGULAR CLICK ================================
                                button.click()
                                print(f"• Clicked 'See More' button: '{button_text[:20]}'")
                            except:
                                try:
                                    # ================================ METHOD 2 JAVASCRIPT CLICK ================================
                                    driver.execute_script("arguments[0].click();", button)
                                    print(f"• JS-clicked 'See More' button: '{button_text[:20]}'")
                                except:
                                    try:
                                        # ================================ METHOD 3 ACTION CHAINS CLICK ================================
                                        from selenium.webdriver.common.action_chains import ActionChains
                                        ActionChains(driver).move_to_element(button).click().perform()
                                        print(f"• Action-clicked 'See More' button: '{button_text[:20]}'")
                                    except:
                                        continue
                            
                            see_more_clicked += 1
                            # Show progress message after each successful click
                            if see_more_clicked % 3 == 0:  # Every 3 clicks to avoid spam
                                print("• Expanding posts... still processing 'See More' buttons")
                            time.sleep(random.uniform(3, 6))  # ================================ LONGER DELAY CONTENT LOAD ================================
                    except Exception as e:
                        continue
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"• Error clicking See More buttons: {str(e)[:50]}...")
    
    # Provide clear completion status
    if see_more_clicked > 0:
        print(f"• Clicked {see_more_clicked} 'See More' buttons")
        print("• Expanding posts... still processing 'See More' buttons")
    elif buttons_found:
        print("• 'See More' buttons found but none were clickable")
        print("• No more 'See More' buttons detected, proceeding to scrolling phase")
    else:
        print("• No more 'See More' buttons detected, proceeding to scrolling phase")
    
    return see_more_clicked

# ================================ BATCH POST PROCESSING FUNCTION ================================
def process_post_batch(driver, processed_post_ids, qualified_posts_list, cutoff_date, today_date, batch_name):
    """
    Process a batch of currently visible posts with deduplication and date checking
    Returns: (number_of_new_posts_processed, cutoff_reached)
    """
    print(f"• Processing {batch_name}...")
    
    # Get all currently visible posts
    posts_selectors = [
        "//div[@role='article']",
        "//div[@data-testid='post_message']",
        "//div[contains(@class, 'userContent')]",
        "//div[contains(@class, 'x1iorvi4') and string-length(normalize-space(.)) > 20]",
        "//div[contains(@class, 'x1yztbdb') and contains(@class, 'x1n2onr6')]",
        "//div[@data-ad-preview='message']",
        "//div[contains(@class, 'x1lliihq') and contains(@class, 'x6ikm8r')]",
        "//div[contains(@class, 'x1n2onr6') and contains(@class, 'xh8yej3')]"
    ]
    
    all_posts = []
    for selector in posts_selectors:
        try:
            found_posts = driver.find_elements(By.XPATH, selector)
            if found_posts:
                all_posts.extend(found_posts)
        except Exception:
            continue
    
    # Remove duplicates while preserving order
    unique_posts = []
    seen_elements = set()
    for post in all_posts:
        try:
            # Create unique identifier for each post element
            post_signature = f"{post.location}_{post.size}_{hash(post.text[:100] if post.text else '')}"[:50]
            if post_signature not in seen_elements:
                seen_elements.add(post_signature)
                unique_posts.append(post)
        except:
            unique_posts.append(post)
    
    print(f"• Found {len(unique_posts)} total posts in {batch_name}")
    
    new_posts_processed = 0
    cutoff_reached = False
    
    for post_index, post in enumerate(unique_posts, 1):
        try:
            # ================================ STEP 1: EXTRACT DATE FIRST (BEFORE ANY PROCESSING) ================================
            print(f"="*80)
            print(f"• POST {post_index} - DATE VERIFICATION (BEFORE ANY PROCESSING)")
            print(f"="*80)
            print(f"• Post {post_index} - CHECKING DATE FIRST before deduplication, expansion, or qualification...")
            
            post_date, timestamp_str = extract_post_timestamp(driver, post)
            
            if post_date:
                days_old = (today_date - post_date).days
                post_date_formatted = post_date.strftime('%Y-%m-%d')
                
                # ================================ EXPLICIT DATE VERIFICATION OUTPUT ================================
                print(f"• POST {post_index} - DATE EXTRACTED SUCCESSFULLY:")
                print(f"   • Date: {post_date_formatted} ({timestamp_str})")
                print(f"   • Age: {days_old} days old")
                print(f"   • Cutoff: {cutoff_date.strftime('%Y-%m-%d')} ({MAX_POST_AGE_MONTHS} months ago)")
                print(f"   • Status: {'WITHIN' if post_date > cutoff_date else 'BEYOND'} acceptable age range")
                
                # Check if older than cutoff - STOP IMMEDIATELY if too old
                if post_date <= cutoff_date:
                    print(f"• POST {post_index} - CUTOFF REACHED")
                    print(f"   • Post from {post_date_formatted} is >= {MAX_POST_AGE_MONTHS} months old")
                    print(f"   • SKIPPING ALL PROCESSING - Post is too old ({days_old} days)")
                    print(f"   • Stopping batch processing - Date cutoff reached")
                    cutoff_reached = True
                    break
                else:
                    print(f"• POST {post_index} - DATE VERIFICATION PASSED")
                    print(f"   • Post is within {MAX_POST_AGE_MONTHS} months ({days_old} days old)")
                    print(f"   • PROCEEDING with deduplication and processing")
            else:
                print(f"• POST {post_index} - DATE EXTRACTION FAILED")
                print(f"   • Raw timestamp found: '{timestamp_str}'")
                
                if timestamp_str:
                    # Try to determine if it's a relative time that might be recent
                    recent_indicators = ['m', 'h', 'min', 'hour', 'دقيقة', 'ساعة']
                    if any(indicator in timestamp_str.lower() for indicator in recent_indicators):
                        print(f"• POST {post_index} - ASSUMING RECENT POST")
                        print(f"   • Contains minutes/hours indicator: '{timestamp_str}'")
                        print(f"   • PROCEEDING with processing - Likely recent post")
                    else:
                        print(f"• POST {post_index} - UNKNOWN DATE FORMAT")
                        print(f"   • Format not recognized: '{timestamp_str}'")
                        print(f"   • PROCEEDING with processing - Being cautious (unknown = include)")
                else:
                    print(f"• POST {post_index} - NO TIMESTAMP FOUND")
                    print(f"   • No date information available")
                    print(f"   • PROCEEDING with processing - No date info (unknown = include)")
            
            print(f"="*80)
            
            # ================================ STEP 2: DEDUPLICATION (ONLY AFTER DATE VERIFICATION PASSES) ================================
            post_id = generate_post_id(post)
            
            if post_id in processed_post_ids:
                print(f"• Post {post_index} - DUPLICATE DETECTED - Skipping (already processed)")
                continue
            
            # Mark as processed
            processed_post_ids.add(post_id)
            new_posts_processed += 1
            print(f"• Post {post_index} - NEW POST - Adding to processing queue")
            
            # ================================ STEP 3: EXPAND POST (ONLY AFTER DATE & DEDUPLICATION) ================================
            print(f"• POST {post_index} - EXPANDING CONTENT (Date verified, not duplicate)")
            print(f"• Post {post_index} - Looking for 'See More' buttons to expand content...")
            
            expanded = expand_post_content(driver, post)
            if expanded:
                print(f"• Post {post_index} - 'See More' expansion completed successfully")
                time.sleep(random.uniform(1, 2))
            else:
                print(f"• Post {post_index} - No 'See More' button found (content already fully visible)")
            
            # ================================ STEP 4: EXTRACT CONTENT AND CHECK QUALIFICATION ================================
            # Extract full content
            content = extract_post_content(driver, post)
            
            if content and len(content.strip()) > 20:
                # Run qualification checks
                is_qualified, qualification_reason = check_post_qualification(content)
                
                if is_qualified:
       