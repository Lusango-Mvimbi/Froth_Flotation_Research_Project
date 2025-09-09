#!/usr/bin/env python3
"""
Specific test for prediction cards and recommendations with correct selectors
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class PredictionCardsTest:
    def __init__(self):
        self.driver = None
        self.base_url = "http://localhost:3000"
        self.login_url = f"{self.base_url}/login"
        self.dashboard_url = f"{self.base_url}/dashboard"
        self.backend_url = "http://localhost:8000"
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ Chrome driver initialized successfully (VISIBLE BROWSER)")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Chrome driver: {e}")
            return False
    
    def login(self):
        """Login to the dashboard"""
        try:
            print("🔐 Attempting to login...")
            self.driver.get(self.login_url)
            
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            username_field.clear()
            username_field.send_keys("admin")
            password_field.clear()
            password_field.send_keys("admin123")
            
            login_button.click()
            
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("/dashboard")
            )
            
            print("✅ Login successful")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def get_sliders(self):
        """Get KEX and SIPX slider elements"""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='range']"))
            )
            
            sliders = self.driver.find_elements(By.CSS_SELECTOR, "input[type='range']")
            if len(sliders) >= 2:
                kex_slider = sliders[0]
                sipx_slider = sliders[1]
                return kex_slider, sipx_slider
            else:
                print(f"❌ Expected 2 sliders, found {len(sliders)}")
                return None, None
                
        except Exception as e:
            print(f"❌ Failed to find sliders: {e}")
            return None, None
    
    def set_slider_value(self, slider, value):
        """Set slider value with proper timing"""
        try:
            print(f"   🎚️ Setting slider to value: {value}")
            
            self.driver.execute_script(f"""
                arguments[0].value = {value};
                arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                arguments[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
            """, slider)
            
            time.sleep(3)  # Wait for debounced API call
            print(f"   ✅ Slider set to {value}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set slider value: {e}")
            return False
    
    def find_prediction_cards(self):
        """Find prediction cards using multiple strategies"""
        print("   🔍 Searching for prediction cards...")
        
        # Strategy 1: Look for motion.div elements (Framer Motion)
        try:
            motion_divs = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='motion']")
            print(f"   📋 Found {len(motion_divs)} motion divs")
        except:
            motion_divs = []
        
        # Strategy 2: Look for cards with specific background classes
        try:
            bg_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='bg-dark-800']")
            print(f"   📋 Found {len(bg_cards)} dark background cards")
        except:
            bg_cards = []
        
        # Strategy 3: Look for cards with border classes
        try:
            border_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='border-dark-600']")
            print(f"   📋 Found {len(border_cards)} border cards")
        except:
            border_cards = []
        
        # Strategy 4: Look for elements with prediction-related text
        try:
            prediction_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Pb') or contains(text(), 'Recovery') or contains(text(), 'Grade')]")
            print(f"   📋 Found {len(prediction_elements)} elements with prediction text")
        except:
            prediction_elements = []
        
        # Strategy 5: Look for elements with horizon text
        try:
            horizon_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '5min') or contains(text(), '15min') or contains(text(), '30min') or contains(text(), '60min')]")
            print(f"   📋 Found {len(horizon_elements)} elements with horizon text")
        except:
            horizon_elements = []
        
        # Strategy 6: Look for tabs
        try:
            tabs = self.driver.find_elements(By.CSS_SELECTOR, "button[class*='tab'], div[class*='tab']")
            print(f"   📋 Found {len(tabs)} tab elements")
        except:
            tabs = []
        
        return {
            'motion_divs': motion_divs,
            'bg_cards': bg_cards,
            'border_cards': border_cards,
            'prediction_elements': prediction_elements,
            'horizon_elements': horizon_elements,
            'tabs': tabs
        }
    
    def find_recommendations(self):
        """Find recommendation elements using multiple strategies"""
        print("   🔍 Searching for recommendations...")
        
        # Strategy 1: Look for recommendation buttons
        try:
            rec_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[class*='recommendation'], button[class*='action']")
            print(f"   💡 Found {len(rec_buttons)} recommendation buttons")
        except:
            rec_buttons = []
        
        # Strategy 2: Look for elements with recommendation text
        try:
            rec_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'recommendation') or contains(text(), 'suggestion') or contains(text(), 'action')]")
            print(f"   💡 Found {len(rec_elements)} elements with recommendation text")
        except:
            rec_elements = []
        
        # Strategy 3: Look for quick action buttons
        try:
            quick_actions = self.driver.find_elements(By.CSS_SELECTOR, "button[class*='quick'], button[class*='simulate']")
            print(f"   💡 Found {len(quick_actions)} quick action buttons")
        except:
            quick_actions = []
        
        # Strategy 4: Look for impact indicators
        try:
            impact_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'IMPACT') or contains(text(), 'HIGH') or contains(text(), 'MEDIUM') or contains(text(), 'LOW')]")
            print(f"   💡 Found {len(impact_elements)} impact elements")
        except:
            impact_elements = []
        
        return {
            'rec_buttons': rec_buttons,
            'rec_elements': rec_elements,
            'quick_actions': quick_actions,
            'impact_elements': impact_elements
        }
    
    def get_page_source_snippet(self):
        """Get a snippet of the page source to see what's actually there"""
        try:
            page_source = self.driver.page_source
            # Look for prediction-related content
            lines = page_source.split('\n')
            prediction_lines = [line for line in lines if any(keyword in line.lower() for keyword in ['prediction', 'pb', 'recovery', 'grade', 'horizon', 'recommendation'])]
            
            print(f"   📄 Found {len(prediction_lines)} lines with prediction-related content")
            if prediction_lines:
                print("   📄 Sample lines:")
                for i, line in enumerate(prediction_lines[:5]):  # Show first 5 lines
                    print(f"     {i+1}: {line.strip()[:100]}...")
            
            return prediction_lines
        except Exception as e:
            print(f"   ❌ Failed to get page source: {e}")
            return []
    
    def test_prediction_cards_detection(self):
        """Test detection of prediction cards and recommendations"""
        print("\n🧪 Testing Prediction Cards and Recommendations Detection")
        print("=" * 60)
        
        try:
            # Wait for dashboard to fully load
            print("   ⏳ Waiting for dashboard to load...")
            time.sleep(5)
            
            # Get initial state
            print("\n📊 Initial State Analysis:")
            initial_cards = self.find_prediction_cards()
            initial_recommendations = self.find_recommendations()
            initial_source = self.get_page_source_snippet()
            
            # Change sliders to trigger updates
            print("\n🎚️ Changing sliders to trigger updates...")
            kex_slider, sipx_slider = self.get_sliders()
            if kex_slider and sipx_slider:
                self.set_slider_value(kex_slider, 75)
                self.set_slider_value(sipx_slider, 45)
            
            # Wait for updates
            print("\n⏳ Waiting for UI updates...")
            time.sleep(8)  # Wait longer for all updates
            
            # Get updated state
            print("\n📊 Updated State Analysis:")
            updated_cards = self.find_prediction_cards()
            updated_recommendations = self.find_recommendations()
            updated_source = self.get_page_source_snippet()
            
            # Compare states
            print("\n📈 Comparison Results:")
            print(f"   📋 Prediction Cards:")
            print(f"     - Motion divs: {len(initial_cards['motion_divs'])} → {len(updated_cards['motion_divs'])}")
            print(f"     - Background cards: {len(initial_cards['bg_cards'])} → {len(updated_cards['bg_cards'])}")
            print(f"     - Border cards: {len(initial_cards['border_cards'])} → {len(updated_cards['border_cards'])}")
            print(f"     - Prediction elements: {len(initial_cards['prediction_elements'])} → {len(updated_cards['prediction_elements'])}")
            print(f"     - Horizon elements: {len(initial_cards['horizon_elements'])} → {len(updated_cards['horizon_elements'])}")
            print(f"     - Tabs: {len(initial_cards['tabs'])} → {len(updated_cards['tabs'])}")
            
            print(f"   💡 Recommendations:")
            print(f"     - Rec buttons: {len(initial_recommendations['rec_buttons'])} → {len(updated_recommendations['rec_buttons'])}")
            print(f"     - Rec elements: {len(initial_recommendations['rec_elements'])} → {len(updated_recommendations['rec_elements'])}")
            print(f"     - Quick actions: {len(initial_recommendations['quick_actions'])} → {len(updated_recommendations['quick_actions'])}")
            print(f"     - Impact elements: {len(initial_recommendations['impact_elements'])} → {len(updated_recommendations['impact_elements'])}")
            
            print(f"   📄 Page Source:")
            print(f"     - Prediction lines: {len(initial_source)} → {len(updated_source)}")
            
            # Check if any elements were found
            total_cards = sum(len(v) for v in updated_cards.values())
            total_recommendations = sum(len(v) for v in updated_recommendations.values())
            
            print(f"\n🎯 Summary:")
            print(f"   📋 Total card-related elements found: {total_cards}")
            print(f"   💡 Total recommendation-related elements found: {total_recommendations}")
            print(f"   📄 Prediction-related content in page source: {len(updated_source)} lines")
            
            if total_cards > 0 or total_recommendations > 0 or len(updated_source) > 0:
                print("   ✅ Elements found! The components are likely working but may need different selectors.")
                return True
            else:
                print("   ❌ No elements found. Components may not be rendering or may be using different selectors.")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    def run_test(self):
        """Run the complete test"""
        print("🧪 Prediction Cards and Recommendations Detection Test")
        print("=" * 60)
        
        if not self.setup_driver():
            return False
        
        try:
            if not self.login():
                return False
            
            success = self.test_prediction_cards_detection()
            
            print(f"\n🎯 Test Result: {'✅ PASS' if success else '❌ FAIL'}")
            return success
            
        finally:
            if self.driver:
                input("Press Enter to close the browser...")
                self.driver.quit()

def main():
    """Main function"""
    print("🔍 Prediction Cards and Recommendations Detection Test")
    print("This test will investigate why prediction cards aren't being detected")
    print()
    
    # Check if services are running
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        print("✅ Frontend is running")
    except:
        print("❌ Frontend is not running on port 3000")
        return False
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print("✅ Backend is running")
    except:
        print("❌ Backend is not running on port 8000")
        return False
    
    print()
    
    # Run test
    test = PredictionCardsTest()
    success = test.run_test()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
