#!/usr/bin/env python3
"""
Comprehensive test suite for slider functionality - 10 test cases
Tests KEX and SIPX slider controls with various values and persistence scenarios
"""

import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys

class SliderTestSuite:
    def __init__(self):
        self.driver = None
        self.base_url = "http://localhost:3000"
        self.login_url = f"{self.base_url}/login"
        self.dashboard_url = f"{self.base_url}/dashboard"
        self.backend_url = "http://localhost:8000"
        self.auth_url = "http://localhost:8051"
        self.test_results = []
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        # Remove --headless to make browser visible
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
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
            
            # Wait for login form
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            # Enter credentials
            username_field.clear()
            username_field.send_keys("admin")
            password_field.clear()
            password_field.send_keys("admin123")
            
            # Click login
            login_button.click()
            
            # Wait for redirect to dashboard
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
            # Wait for dashboard to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='range']"))
            )
            
            sliders = self.driver.find_elements(By.CSS_SELECTOR, "input[type='range']")
            if len(sliders) >= 2:
                kex_slider = sliders[0]  # First slider is KEX
                sipx_slider = sliders[1]  # Second slider is SIPX
                return kex_slider, sipx_slider
            else:
                print(f"❌ Expected 2 sliders, found {len(sliders)}")
                return None, None
                
        except Exception as e:
            print(f"❌ Failed to find sliders: {e}")
            return None, None
    
    def set_slider_value(self, slider, value):
        """Set slider value using proper Selenium actions"""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            from selenium.webdriver.common.keys import Keys
            
            print(f"   🎚️ Setting slider to value: {value}")
            
            # First, try the simple JavaScript approach
            self.driver.execute_script(f"""
                arguments[0].value = {value};
                arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                arguments[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
            """, slider)
            
            time.sleep(2)  # Wait longer so you can see the change
            print(f"   ✅ Slider set to {value}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set slider value: {e}")
            return False
    
    def get_slider_value(self, slider):
        """Get current slider value"""
        try:
            return float(slider.get_attribute('value'))
        except Exception as e:
            print(f"❌ Failed to get slider value: {e}")
            return None
    
    def get_backend_controls(self):
        """Get current control values from backend API"""
        try:
            response = requests.get(f"{self.backend_url}/api/control-settings", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('kex', 0), data.get('sipx', 0)
            else:
                print(f"❌ Backend API returned status {response.status_code}")
                return None, None
        except Exception as e:
            print(f"❌ Failed to get backend controls: {e}")
            return None, None
    
    def wait_for_backend_update(self, expected_kex=None, expected_sipx=None, timeout=10):
        """Wait for backend to be updated with expected values"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            backend_kex, backend_sipx = self.get_backend_controls()
            
            # Check if expected values match (None means don't check that value)
            kex_match = expected_kex is None or backend_kex == expected_kex
            sipx_match = expected_sipx is None or backend_sipx == expected_sipx
            
            if kex_match and sipx_match:
                return True
            time.sleep(0.5)
        
        return False
    
    def test_case_1_kex_minimum(self):
        """Test 1: KEX slider minimum value (0)"""
        print("\n🧪 Test 1: KEX slider minimum value (0)")
        print("   👀 Watch the browser - KEX slider should move to 0")
        try:
            kex_slider, sipx_slider = self.get_sliders()
            if not kex_slider:
                return False
            
            # Set KEX to minimum using proper Selenium interaction
            self.set_slider_value(kex_slider, 0)
            
            print("   ⏳ Waiting for backend to update...")
            # Wait longer for the API call to complete
            time.sleep(3)
            # Wait for backend to be updated
            backend_updated = self.wait_for_backend_update(0, None, timeout=5)
            
            # Check frontend value
            frontend_value = self.get_slider_value(kex_slider)
            
            # Check backend value
            backend_kex, backend_sipx = self.get_backend_controls()
            
            success = (frontend_value == 0.0 and backend_kex == 0.0)
            result = {
                'test': 'KEX Minimum (0)',
                'frontend_value': frontend_value,
                'backend_value': backend_kex,
                'backend_updated': backend_updated,
                'success': success
            }
            self.test_results.append(result)
            
            print(f"   📊 Frontend: {frontend_value}, Backend: {backend_kex}")
            print(f"   🔄 Backend Updated: {'✅' if backend_updated else '❌'}")
            print(f"   🎯 Result: {'✅ PASS' if success else '❌ FAIL'}")
            time.sleep(3)  # Pause so you can see the result
            return success
            
        except Exception as e:
            print(f"❌ Test 1 failed: {e}")
            return False
    
    def test_case_2_kex_maximum(self):
        """Test 2: KEX slider maximum value (100)"""
        print("\n🧪 Test 2: KEX slider maximum value (100)")
        print("   👀 Watch the browser - KEX slider should move to 100")
        try:
            kex_slider, sipx_slider = self.get_sliders()
            if not kex_slider:
                return False
            
            # Set KEX to maximum
            self.set_slider_value(kex_slider, 100)
            
            print("   ⏳ Waiting for backend to update...")
            # Wait longer for the API call to complete
            time.sleep(3)
            # Wait for backend to be updated
            backend_updated = self.wait_for_backend_update(100, None, timeout=5)
            
            # Check frontend value
            frontend_value = self.get_slider_value(kex_slider)
            
            # Check backend value
            backend_kex, backend_sipx = self.get_backend_controls()
            
            success = (frontend_value == 100.0 and backend_kex == 100.0)
            result = {
                'test': 'KEX Maximum (100)',
                'frontend_value': frontend_value,
                'backend_value': backend_kex,
                'backend_updated': backend_updated,
                'success': success
            }
            self.test_results.append(result)
            
            print(f"   📊 Frontend: {frontend_value}, Backend: {backend_kex}")
            print(f"   🔄 Backend Updated: {'✅' if backend_updated else '❌'}")
            print(f"   🎯 Result: {'✅ PASS' if success else '❌ FAIL'}")
            time.sleep(2)  # Pause so you can see the result
            return success
            
        except Exception as e:
            print(f"❌ Test 2 failed: {e}")
            return False
    
    def test_case_3_sipx_minimum(self):
        """Test 3: SIPX slider minimum value (0)"""
        print("\n🧪 Test 3: SIPX slider minimum value (0)")
        try:
            kex_slider, sipx_slider = self.get_sliders()
            if not sipx_slider:
                return False
            
            # Set SIPX to minimum
            self.set_slider_value(sipx_slider, 0)
            time.sleep(1)
            
            # Check frontend value
            frontend_value = self.get_slider_value(sipx_slider)
            
            # Check backend value
            backend_kex, backend_sipx = self.get_backend_controls()
            
            success = (frontend_value == 0.0 and backend_sipx == 0.0)
            result = {
                'test': 'SIPX Minimum (0)',
                'frontend_value': frontend_value,
                'backend_value': backend_sipx,
                'success': success
            }
            self.test_results.append(result)
            
            print(f"   Frontend: {frontend_value}, Backend: {backend_sipx}")
            print(f"   Result: {'✅ PASS' if success else '❌ FAIL'}")
            return success
            
        except Exception as e:
            print(f"❌ Test 3 failed: {e}")
            return False
    
    def test_case_4_sipx_maximum(self):
        """Test 4: SIPX slider maximum value (60)"""
        print("\n🧪 Test 4: SIPX slider maximum value (60)")
        try:
            kex_slider, sipx_slider = self.get_sliders()
            if not sipx_slider:
                return False
            
            # Set SIPX to maximum
            self.set_slider_value(sipx_slider, 60)
            time.sleep(1)
            
            # Check frontend value
            frontend_value = self.get_slider_value(sipx_slider)
            
            # Check backend value
            backend_kex, backend_sipx = self.get_backend_controls()
            
            success = (frontend_value == 60.0 and backend_sipx == 60.0)
            result = {
                'test': 'SIPX Maximum (60)',
                'frontend_value': frontend_value,
                'backend_value': backend_sipx,
                'success': success
            }
            self.test_results.append(result)
            
            print(f"   Frontend: {frontend_value}, Backend: {backend_sipx}")
            print(f"   Result: {'✅ PASS' if success else '❌ FAIL'}")
            return success
            
        except Exception as e:
            print(f"❌ Test 4 failed: {e}")
            return False
    
    def test_case_5_kex_middle(self):
        """Test 5: KEX slider middle value (50)"""
        print("\n🧪 Test 5: KEX slider middle value (50)")
        try:
            kex_slider, sipx_slider = self.get_sliders()
            if not kex_slider:
                return False
            
            # Set KEX to middle
            self.set_slider_value(kex_slider, 50)
            time.sleep(1)
            
            # Check frontend value
            frontend_value = self.get_slider_value(kex_slider)
            
            # Check backend value
            backend_kex, backend_sipx = self.get_backend_controls()
            
            success = (frontend_value == 50.0 and backend_kex == 50.0)
            result = {
                'test': 'KEX Middle (50)',
                'frontend_value': frontend_value,
                'backend_value': backend_kex,
                'success': success
            }
            self.test_results.append(result)
            
            print(f"   Frontend: {frontend_value}, Backend: {backend_kex}")
            print(f"   Result: {'✅ PASS' if success else '❌ FAIL'}")
            return success
            
        except Exception as e:
            print(f"❌ Test 5 failed: {e}")
            return False
    
    def test_case_6_sipx_middle(self):
        """Test 6: SIPX slider middle value (30)"""
        print("\n🧪 Test 6: SIPX slider middle value (30)")
        try:
            kex_slider, sipx_slider = self.get_sliders()
            if not sipx_slider:
                return False
            
            # Set SIPX to middle
            self.set_slider_value(sipx_slider, 30)
            time.sleep(1)
            
            # Check frontend value
            frontend_value = self.get_slider_value(sipx_slider)
            
            # Check backend value
            backend_kex, backend_sipx = self.get_backend_controls()
            
            success = (frontend_value == 30.0 and backend_sipx == 30.0)
            result = {
                'test': 'SIPX Middle (30)',
                'frontend_value': frontend_value,
                'backend_value': backend_sipx,
                'success': success
            }
            self.test_results.append(result)
            
            print(f"   Frontend: {frontend_value}, Backend: {backend_sipx}")
            print(f"   Result: {'✅ PASS' if success else '❌ FAIL'}")
            return success
            
        except Exception as e:
            print(f"❌ Test 6 failed: {e}")
            return False
    
    def test_case_7_both_low(self):
        """Test 7: Both sliders at low values (KEX=20, SIPX=10)"""
        print("\n🧪 Test 7: Both sliders at low values (KEX=20, SIPX=10)")
        try:
            kex_slider, sipx_slider = self.get_sliders()
            if not kex_slider or not sipx_slider:
                return False
            
            # Set both sliders to low values
            self.set_slider_value(kex_slider, 20)
            self.set_slider_value(sipx_slider, 10)
            time.sleep(1)
            
            # Check frontend values
            frontend_kex = self.get_slider_value(kex_slider)
            frontend_sipx = self.get_slider_value(sipx_slider)
            
            # Check backend values
            backend_kex, backend_sipx = self.get_backend_controls()
            
            success = (frontend_kex == 20.0 and frontend_sipx == 10.0 and 
                      backend_kex == 20.0 and backend_sipx == 10.0)
            result = {
                'test': 'Both Low (KEX=20, SIPX=10)',
                'frontend_kex': frontend_kex,
                'frontend_sipx': frontend_sipx,
                'backend_kex': backend_kex,
                'backend_sipx': backend_sipx,
                'success': success
            }
            self.test_results.append(result)
            
            print(f"   Frontend: KEX={frontend_kex}, SIPX={frontend_sipx}")
            print(f"   Backend: KEX={backend_kex}, SIPX={backend_sipx}")
            print(f"   Result: {'✅ PASS' if success else '❌ FAIL'}")
            return success
            
        except Exception as e:
            print(f"❌ Test 7 failed: {e}")
            return False
    
    def test_case_8_both_high(self):
        """Test 8: Both sliders at high values (KEX=80, SIPX=50)"""
        print("\n🧪 Test 8: Both sliders at high values (KEX=80, SIPX=50)")
        try:
            kex_slider, sipx_slider = self.get_sliders()
            if not kex_slider or not sipx_slider:
                return False
            
            # Set both sliders to high values
            self.set_slider_value(kex_slider, 80)
            self.set_slider_value(sipx_slider, 50)
            time.sleep(1)
            
            # Check frontend values
            frontend_kex = self.get_slider_value(kex_slider)
            frontend_sipx = self.get_slider_value(sipx_slider)
            
            # Check backend values
            backend_kex, backend_sipx = self.get_backend_controls()
            
            success = (frontend_kex == 80.0 and frontend_sipx == 50.0 and 
                      backend_kex == 80.0 and backend_sipx == 50.0)
            result = {
                'test': 'Both High (KEX=80, SIPX=50)',
                'frontend_kex': frontend_kex,
                'frontend_sipx': frontend_sipx,
                'backend_kex': backend_kex,
                'backend_sipx': backend_sipx,
                'success': success
            }
            self.test_results.append(result)
            
            print(f"   Frontend: KEX={frontend_kex}, SIPX={frontend_sipx}")
            print(f"   Backend: KEX={backend_kex}, SIPX={backend_sipx}")
            print(f"   Result: {'✅ PASS' if success else '❌ FAIL'}")
            return success
            
        except Exception as e:
            print(f"❌ Test 8 failed: {e}")
            return False
    
    def test_case_9_page_refresh_persistence(self):
        """Test 9: Control persistence after page refresh"""
        print("\n🧪 Test 9: Control persistence after page refresh")
        try:
            kex_slider, sipx_slider = self.get_sliders()
            if not kex_slider or not sipx_slider:
                return False
            
            # Set specific values
            self.set_slider_value(kex_slider, 35)
            self.set_slider_value(sipx_slider, 25)
            time.sleep(1)
            
            # Get values before refresh
            before_kex = self.get_slider_value(kex_slider)
            before_sipx = self.get_slider_value(sipx_slider)
            
            # Refresh the page
            self.driver.refresh()
            time.sleep(3)  # Wait for page to reload
            
            # Get sliders again after refresh
            kex_slider, sipx_slider = self.get_sliders()
            if not kex_slider or not sipx_slider:
                return False
            
            # Get values after refresh
            after_kex = self.get_slider_value(kex_slider)
            after_sipx = self.get_slider_value(sipx_slider)
            
            # Check backend values
            backend_kex, backend_sipx = self.get_backend_controls()
            
            success = (after_kex == 35.0 and after_sipx == 25.0 and 
                      backend_kex == 35.0 and backend_sipx == 25.0)
            result = {
                'test': 'Page Refresh Persistence',
                'before_kex': before_kex,
                'before_sipx': before_sipx,
                'after_kex': after_kex,
                'after_sipx': after_sipx,
                'backend_kex': backend_kex,
                'backend_sipx': backend_sipx,
                'success': success
            }
            self.test_results.append(result)
            
            print(f"   Before refresh: KEX={before_kex}, SIPX={before_sipx}")
            print(f"   After refresh: KEX={after_kex}, SIPX={after_sipx}")
            print(f"   Backend: KEX={backend_kex}, SIPX={backend_sipx}")
            print(f"   Result: {'✅ PASS' if success else '❌ FAIL'}")
            return success
            
        except Exception as e:
            print(f"❌ Test 9 failed: {e}")
            return False
    
    def test_case_10_automatic_refresh_persistence(self):
        """Test 10: Control persistence after automatic refresh (4s)"""
        print("\n🧪 Test 10: Control persistence after automatic refresh (4s)")
        try:
            kex_slider, sipx_slider = self.get_sliders()
            if not kex_slider or not sipx_slider:
                return False
            
            # Set specific values
            self.set_slider_value(kex_slider, 45)
            self.set_slider_value(sipx_slider, 35)
            time.sleep(1)
            
            # Get values before waiting for automatic refresh
            before_kex = self.get_slider_value(kex_slider)
            before_sipx = self.get_slider_value(sipx_slider)
            
            # Wait for automatic refresh (5 seconds to be safe)
            print("   Waiting for automatic refresh (5 seconds)...")
            time.sleep(5)
            
            # Get values after automatic refresh
            after_kex = self.get_slider_value(kex_slider)
            after_sipx = self.get_slider_value(sipx_slider)
            
            # Check backend values
            backend_kex, backend_sipx = self.get_backend_controls()
            
            success = (after_kex == 45.0 and after_sipx == 35.0 and 
                      backend_kex == 45.0 and backend_sipx == 35.0)
            result = {
                'test': 'Automatic Refresh Persistence',
                'before_kex': before_kex,
                'before_sipx': before_sipx,
                'after_kex': after_kex,
                'after_sipx': after_sipx,
                'backend_kex': backend_kex,
                'backend_sipx': backend_sipx,
                'success': success
            }
            self.test_results.append(result)
            
            print(f"   Before auto-refresh: KEX={before_kex}, SIPX={before_sipx}")
            print(f"   After auto-refresh: KEX={after_kex}, SIPX={after_sipx}")
            print(f"   Backend: KEX={backend_kex}, SIPX={backend_sipx}")
            print(f"   Result: {'✅ PASS' if success else '❌ FAIL'}")
            return success
            
        except Exception as e:
            print(f"❌ Test 10 failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all 10 test cases"""
        print("🚀 Starting 10 Slider Test Cases")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            if not self.login():
                return False
            
            # Run all test cases
            tests = [
                self.test_case_1_kex_minimum,
                self.test_case_2_kex_maximum,
                self.test_case_3_sipx_minimum,
                self.test_case_4_sipx_maximum,
                self.test_case_5_kex_middle,
                self.test_case_6_sipx_middle,
                self.test_case_7_both_low,
                self.test_case_8_both_high,
                self.test_case_9_page_refresh_persistence,
                self.test_case_10_automatic_refresh_persistence
            ]
            
            passed = 0
            total = len(tests)
            
            for i, test in enumerate(tests, 1):
                try:
                    if test():
                        passed += 1
                    else:
                        pass  # Test failed but continue
                except Exception as e:
                    print(f"❌ Test {i} crashed: {e}")
            
            # Print summary
            print("\n" + "=" * 50)
            print("📊 TEST SUMMARY")
            print("=" * 50)
            print(f"Total Tests: {total}")
            print(f"Passed: {passed}")
            print(f"Failed: {total - passed}")
            print(f"Success Rate: {(passed/total)*100:.1f}%")
            
            if passed == total:
                print("🎉 ALL TESTS PASSED! Sliders are fully working!")
            else:
                print("⚠️  Some tests failed. Check the results above.")
            
            # Print detailed results
            print("\n📋 DETAILED RESULTS:")
            for result in self.test_results:
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                print(f"   {result['test']}: {status}")
            
            return passed == total
            
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main function to run the test suite"""
    print("🧪 10 Slider Test Cases - Froth Flotation Dashboard")
    print("Testing KEX and SIPX slider functionality and persistence")
    print()
    
    # Check if services are running
    try:
        # Check frontend
        response = requests.get("http://localhost:3000", timeout=5)
        print("✅ Frontend is running")
    except:
        print("❌ Frontend is not running on port 3000")
        return False
    
    try:
        # Check backend
        response = requests.get("http://localhost:8000/health", timeout=5)
        print("✅ Backend is running")
    except:
        print("❌ Backend is not running on port 8000")
        return False
    
    try:
        # Check auth service
        response = requests.get("http://localhost:8051/health", timeout=5)
        print("✅ Auth service is running")
    except:
        print("❌ Auth service is not running on port 8051")
        return False
    
    print()
    
    # Run tests
    test_suite = SliderTestSuite()
    success = test_suite.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
