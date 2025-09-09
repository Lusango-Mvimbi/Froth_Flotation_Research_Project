#!/usr/bin/env python3
"""
Fixed 10 Slider Test Cases - Proper timing for API calls
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class FixedSliderTestSuite:
    def __init__(self):
        self.driver = None
        self.base_url = "http://localhost:3000"
        self.login_url = f"{self.base_url}/login"
        self.dashboard_url = f"{self.base_url}/dashboard"
        self.backend_url = "http://localhost:8000"
        self.test_results = []
        
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
                return data.get('controls', {}).get('kex', 0), data.get('controls', {}).get('sipx', 0)
            else:
                print(f"❌ Backend API returned status {response.status_code}")
                return None, None
        except Exception as e:
            print(f"❌ Failed to get backend controls: {e}")
            return None, None
    
    def run_test(self, test_name, kex_value=None, sipx_value=None, expected_kex=None, expected_sipx=None):
        """Run a single test with proper timing"""
        print(f"\n🧪 {test_name}")
        print(f"   👀 Watch the browser - sliders should move to KEX={kex_value}, SIPX={sipx_value}")
        
        try:
            kex_slider, sipx_slider = self.get_sliders()
            if not kex_slider or not sipx_slider:
                return False
            
            # Set slider values
            if kex_value is not None:
                self.set_slider_value(kex_slider, kex_value)
            if sipx_value is not None:
                self.set_slider_value(sipx_slider, sipx_value)
            
            # Wait for API calls to complete
            print("   ⏳ Waiting for backend to update...")
            time.sleep(2)
            
            # Check values
            frontend_kex = self.get_slider_value(kex_slider)
            frontend_sipx = self.get_slider_value(sipx_slider)
            backend_kex, backend_sipx = self.get_backend_controls()
            
            # Determine expected values
            exp_kex = expected_kex if expected_kex is not None else kex_value
            exp_sipx = expected_sipx if expected_sipx is not None else sipx_value
            
            # Check success
            kex_success = (exp_kex is None or backend_kex == exp_kex)
            sipx_success = (exp_sipx is None or backend_sipx == exp_sipx)
            success = kex_success and sipx_success
            
            result = {
                'test': test_name,
                'frontend_kex': frontend_kex,
                'frontend_sipx': frontend_sipx,
                'backend_kex': backend_kex,
                'backend_sipx': backend_sipx,
                'expected_kex': exp_kex,
                'expected_sipx': exp_sipx,
                'success': success
            }
            self.test_results.append(result)
            
            print(f"   📊 Frontend: KEX={frontend_kex}, SIPX={frontend_sipx}")
            print(f"   📊 Backend: KEX={backend_kex}, SIPX={backend_sipx}")
            print(f"   🎯 Expected: KEX={exp_kex}, SIPX={exp_sipx}")
            print(f"   🎯 Result: {'✅ PASS' if success else '❌ FAIL'}")
            time.sleep(2)  # Pause to see result
            return success
            
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all 10 test cases"""
        print("🚀 Starting 10 Fixed Slider Test Cases")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            if not self.login():
                return False
            
            # Run all 10 tests
            tests = [
                ("Test 1: KEX minimum (0)", 0, None, 0, None),
                ("Test 2: KEX maximum (100)", 100, None, 100, None),
                ("Test 3: SIPX minimum (0)", None, 0, None, 0),
                ("Test 4: SIPX maximum (60)", None, 60, None, 60),
                ("Test 5: KEX middle (50)", 50, None, 50, None),
                ("Test 6: SIPX middle (30)", None, 30, None, 30),
                ("Test 7: Both low (KEX=20, SIPX=10)", 20, 10, 20, 10),
                ("Test 8: Both high (KEX=80, SIPX=50)", 80, 50, 80, 50),
                ("Test 9: Mixed values (KEX=35, SIPX=25)", 35, 25, 35, 25),
                ("Test 10: Edge case (KEX=1, SIPX=59)", 1, 59, 1, 59)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, kex_val, sipx_val, exp_kex, exp_sipx in tests:
                if self.run_test(test_name, kex_val, sipx_val, exp_kex, exp_sipx):
                    passed += 1
            
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
                input("Press Enter to close the browser...")
                self.driver.quit()

def main():
    """Main function to run the test suite"""
    print("🧪 10 Fixed Slider Test Cases - Froth Flotation Dashboard")
    print("Testing KEX and SIPX slider functionality with proper timing")
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
    
    # Run tests
    test_suite = FixedSliderTestSuite()
    success = test_suite.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
