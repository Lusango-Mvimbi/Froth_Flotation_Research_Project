#!/usr/bin/env python3
"""
Final Comprehensive Test - Using Correct Selectors Based on Investigation
Tests sliders + prediction cards + graphs + recommendations with proper detection
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class FinalComprehensiveTest:
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
    
    def count_prediction_cards(self):
        """Count prediction cards using correct selectors"""
        try:
            # Use the selectors we discovered work
            bg_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='bg-dark-800']")
            border_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='border-dark-600']")
            prediction_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Pb') or contains(text(), 'Recovery') or contains(text(), 'Grade')]")
            horizon_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '5min') or contains(text(), '15min') or contains(text(), '30min') or contains(text(), '60min')]")
            
            return {
                'bg_cards': len(bg_cards),
                'border_cards': len(border_cards),
                'prediction_elements': len(prediction_elements),
                'horizon_elements': len(horizon_elements),
                'total_cards': len(bg_cards) + len(border_cards) + len(prediction_elements) + len(horizon_elements)
            }
        except Exception as e:
            print(f"❌ Failed to count prediction cards: {e}")
            return {'total_cards': 0}
    
    def count_recommendations(self):
        """Count recommendation elements using correct selectors"""
        try:
            # Use the selectors we discovered work
            rec_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'recommendation') or contains(text(), 'suggestion') or contains(text(), 'action')]")
            impact_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'IMPACT') or contains(text(), 'HIGH') or contains(text(), 'MEDIUM') or contains(text(), 'LOW')]")
            
            return {
                'rec_elements': len(rec_elements),
                'impact_elements': len(impact_elements),
                'total_recommendations': len(rec_elements) + len(impact_elements)
            }
        except Exception as e:
            print(f"❌ Failed to count recommendations: {e}")
            return {'total_recommendations': 0}
    
    def count_graphs(self):
        """Count graph elements"""
        try:
            # Look for Recharts elements (we know these work)
            recharts_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='recharts']")
            svg_elements = self.driver.find_elements(By.CSS_SELECTOR, "svg")
            
            return {
                'recharts_elements': len(recharts_elements),
                'svg_elements': len(svg_elements),
                'total_graphs': len(recharts_elements) + len(svg_elements)
            }
        except Exception as e:
            print(f"❌ Failed to count graphs: {e}")
            return {'total_graphs': 0}
    
    def run_comprehensive_test(self, test_name, kex_value=None, sipx_value=None, expected_kex=None, expected_sipx=None):
        """Run a comprehensive test with correct selectors"""
        print(f"\n🧪 {test_name}")
        print(f"   👀 Watch the browser - sliders should move to KEX={kex_value}, SIPX={sipx_value}")
        
        try:
            kex_slider, sipx_slider = self.get_sliders()
            if not kex_slider or not sipx_slider:
                return False
            
            # Get initial UI state
            print("   📊 Getting initial UI state...")
            initial_cards = self.count_prediction_cards()
            initial_recommendations = self.count_recommendations()
            initial_graphs = self.count_graphs()
            
            print(f"   📋 Initial prediction cards: {initial_cards['total_cards']} found")
            print(f"   💡 Initial recommendations: {initial_recommendations['total_recommendations']} found")
            print(f"   📈 Initial graphs: {initial_graphs['total_graphs']} found")
            
            # Set slider values
            if kex_value is not None:
                self.set_slider_value(kex_slider, kex_value)
            if sipx_value is not None:
                self.set_slider_value(sipx_slider, sipx_value)
            
            # Wait for UI updates
            print("   ⏳ Waiting for UI updates...")
            time.sleep(5)  # Wait for all updates
            
            # Check slider values
            frontend_kex = self.get_slider_value(kex_slider)
            frontend_sipx = self.get_slider_value(sipx_slider)
            backend_kex, backend_sipx = self.get_backend_controls()
            
            # Get updated UI state
            print("   📊 Getting updated UI state...")
            updated_cards = self.count_prediction_cards()
            updated_recommendations = self.count_recommendations()
            updated_graphs = self.count_graphs()
            
            # Determine expected values
            exp_kex = expected_kex if expected_kex is not None else kex_value
            exp_sipx = expected_sipx if expected_sipx is not None else sipx_value
            
            # Check success
            kex_success = (exp_kex is None or backend_kex == exp_kex)
            sipx_success = (exp_sipx is None or backend_sipx == exp_sipx)
            slider_success = kex_success and sipx_success
            
            # Check if UI components are present
            ui_components_present = (
                updated_cards['total_cards'] > 0 and 
                updated_recommendations['total_recommendations'] > 0 and 
                updated_graphs['total_graphs'] > 0
            )
            
            overall_success = slider_success and ui_components_present
            
            result = {
                'test': test_name,
                'frontend_kex': frontend_kex,
                'frontend_sipx': frontend_sipx,
                'backend_kex': backend_kex,
                'backend_sipx': backend_sipx,
                'expected_kex': exp_kex,
                'expected_sipx': exp_sipx,
                'slider_success': slider_success,
                'ui_components_present': ui_components_present,
                'prediction_cards': updated_cards['total_cards'],
                'recommendations': updated_recommendations['total_recommendations'],
                'graphs': updated_graphs['total_graphs'],
                'overall_success': overall_success
            }
            self.test_results.append(result)
            
            print(f"   📊 Frontend: KEX={frontend_kex}, SIPX={frontend_sipx}")
            print(f"   📊 Backend: KEX={backend_kex}, SIPX={backend_sipx}")
            print(f"   🎯 Expected: KEX={exp_kex}, SIPX={exp_sipx}")
            print(f"   🎚️ Sliders: {'✅ PASS' if slider_success else '❌ FAIL'}")
            print(f"   📋 Prediction Cards: {updated_cards['total_cards']} found")
            print(f"   💡 Recommendations: {updated_recommendations['total_recommendations']} found")
            print(f"   📈 Graphs: {updated_graphs['total_graphs']} found")
            print(f"   🎯 Overall Result: {'✅ PASS' if overall_success else '❌ FAIL'}")
            time.sleep(2)  # Pause to see result
            return overall_success
            
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all 10 comprehensive test cases with correct selectors"""
        print("🚀 Starting Final Comprehensive Test - All Components")
        print("=" * 60)
        
        if not self.setup_driver():
            return False
        
        try:
            if not self.login():
                return False
            
            # Run all 10 tests
            tests = [
                ("Test 1: KEX minimum (0) + All UI Components", 0, None, 0, None),
                ("Test 2: KEX maximum (100) + All UI Components", 100, None, 100, None),
                ("Test 3: SIPX minimum (0) + All UI Components", None, 0, None, 0),
                ("Test 4: SIPX maximum (60) + All UI Components", None, 60, None, 60),
                ("Test 5: KEX middle (50) + All UI Components", 50, None, 50, None),
                ("Test 6: SIPX middle (30) + All UI Components", None, 30, None, 30),
                ("Test 7: Both low (KEX=20, SIPX=10) + All UI Components", 20, 10, 20, 10),
                ("Test 8: Both high (KEX=80, SIPX=50) + All UI Components", 80, 50, 80, 50),
                ("Test 9: Mixed values (KEX=35, SIPX=25) + All UI Components", 35, 25, 35, 25),
                ("Test 10: Edge case (KEX=1, SIPX=59) + All UI Components", 1, 59, 1, 59)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, kex_val, sipx_val, exp_kex, exp_sipx in tests:
                if self.run_comprehensive_test(test_name, kex_val, sipx_val, exp_kex, exp_sipx):
                    passed += 1
            
            # Print summary
            print("\n" + "=" * 60)
            print("📊 FINAL COMPREHENSIVE TEST SUMMARY")
            print("=" * 60)
            print(f"Total Tests: {total}")
            print(f"Passed: {passed}")
            print(f"Failed: {total - passed}")
            print(f"Success Rate: {(passed/total)*100:.1f}%")
            
            if passed == total:
                print("🎉 ALL TESTS PASSED! Complete system is fully working!")
            else:
                print("⚠️  Some tests failed. Check the results above.")
            
            # Print detailed results
            print("\n📋 DETAILED RESULTS:")
            for result in self.test_results:
                status = "✅ PASS" if result['overall_success'] else "❌ FAIL"
                print(f"   {result['test']}: {status}")
                print(f"     - Sliders: {'✅' if result['slider_success'] else '❌'}")
                print(f"     - UI Components: {'✅' if result['ui_components_present'] else '❌'}")
                print(f"     - Cards: {result['prediction_cards']}, Recs: {result['recommendations']}, Graphs: {result['graphs']}")
            
            return passed == total
            
        finally:
            if self.driver:
                input("Press Enter to close the browser...")
                self.driver.quit()

def main():
    """Main function to run the final comprehensive test suite"""
    print("🧪 Final Comprehensive Test - All UI Components")
    print("Testing sliders + prediction cards + graphs + recommendations with correct selectors")
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
    test_suite = FinalComprehensiveTest()
    success = test_suite.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
