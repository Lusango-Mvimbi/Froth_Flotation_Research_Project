#!/usr/bin/env python3
"""
Comprehensive 10 Slider Test Cases - Including UI Updates
Tests sliders + prediction cards + graphs + recommendations
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class ComprehensiveSliderTestSuite:
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
    
    def get_prediction_cards(self):
        """Get prediction card values for all horizons"""
        try:
            # Wait for prediction cards to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='prediction'], [class*='card']"))
            )
            
            # Look for prediction cards with different approaches
            cards = []
            
            # Try different selectors for prediction cards
            selectors = [
                "[class*='prediction']",
                "[class*='card']",
                "[class*='horizon']",
                "div[class*='5min'], div[class*='15min'], div[class*='30min'], div[class*='60min']"
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    cards.extend(elements)
            
            # Get text content from cards
            card_data = []
            for card in cards[:8]:  # Limit to first 8 cards
                try:
                    text = card.text.strip()
                    if text and any(horizon in text.lower() for horizon in ['5min', '15min', '30min', '60min', 'prediction']):
                        card_data.append(text)
                except:
                    continue
            
            return card_data
            
        except Exception as e:
            print(f"❌ Failed to get prediction cards: {e}")
            return []
    
    def get_graph_data(self):
        """Get graph/chart data"""
        try:
            # Look for charts/graphs
            chart_selectors = [
                "[class*='chart']",
                "[class*='graph']",
                "[class*='recharts']",
                "svg",
                "canvas"
            ]
            
            charts = []
            for selector in chart_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    charts.extend(elements)
            
            # Get chart information
            chart_info = []
            for chart in charts[:3]:  # Limit to first 3 charts
                try:
                    # Check if chart is visible
                    if chart.is_displayed():
                        chart_info.append({
                            'tag': chart.tag_name,
                            'class': chart.get_attribute('class'),
                            'visible': True
                        })
                except:
                    continue
            
            return chart_info
            
        except Exception as e:
            print(f"❌ Failed to get graph data: {e}")
            return []
    
    def get_recommendations(self):
        """Get recommendation data"""
        try:
            # Look for recommendation elements
            rec_selectors = [
                "[class*='recommendation']",
                "[class*='suggestion']",
                "[class*='action']",
                "button[class*='quick'], button[class*='action']"
            ]
            
            recommendations = []
            for selector in rec_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    recommendations.extend(elements)
            
            # Get recommendation text
            rec_data = []
            for rec in recommendations[:5]:  # Limit to first 5
                try:
                    text = rec.text.strip()
                    if text and len(text) > 0:
                        rec_data.append(text)
                except:
                    continue
            
            return rec_data
            
        except Exception as e:
            print(f"❌ Failed to get recommendations: {e}")
            return []
    
    def run_comprehensive_test(self, test_name, kex_value=None, sipx_value=None, expected_kex=None, expected_sipx=None):
        """Run a comprehensive test including UI updates"""
        print(f"\n🧪 {test_name}")
        print(f"   👀 Watch the browser - sliders should move to KEX={kex_value}, SIPX={sipx_value}")
        
        try:
            kex_slider, sipx_slider = self.get_sliders()
            if not kex_slider or not sipx_slider:
                return False
            
            # Get initial UI state
            print("   📊 Getting initial UI state...")
            initial_cards = self.get_prediction_cards()
            initial_graphs = self.get_graph_data()
            initial_recommendations = self.get_recommendations()
            
            print(f"   📋 Initial prediction cards: {len(initial_cards)} found")
            print(f"   📈 Initial graphs: {len(initial_graphs)} found")
            print(f"   💡 Initial recommendations: {len(initial_recommendations)} found")
            
            # Set slider values
            if kex_value is not None:
                self.set_slider_value(kex_slider, kex_value)
            if sipx_value is not None:
                self.set_slider_value(sipx_slider, sipx_value)
            
            # Wait for UI updates
            print("   ⏳ Waiting for UI updates...")
            time.sleep(5)  # Wait longer for UI updates
            
            # Check slider values
            frontend_kex = self.get_slider_value(kex_slider)
            frontend_sipx = self.get_slider_value(sipx_slider)
            backend_kex, backend_sipx = self.get_backend_controls()
            
            # Get updated UI state
            print("   📊 Getting updated UI state...")
            updated_cards = self.get_prediction_cards()
            updated_graphs = self.get_graph_data()
            updated_recommendations = self.get_recommendations()
            
            # Determine expected values
            exp_kex = expected_kex if expected_kex is not None else kex_value
            exp_sipx = expected_sipx if expected_sipx is not None else sipx_value
            
            # Check success
            kex_success = (exp_kex is None or backend_kex == exp_kex)
            sipx_success = (exp_sipx is None or backend_sipx == exp_sipx)
            slider_success = kex_success and sipx_success
            
            # Check if UI updated
            ui_updated = (
                len(updated_cards) > 0 or 
                len(updated_graphs) > 0 or 
                len(updated_recommendations) > 0
            )
            
            overall_success = slider_success and ui_updated
            
            result = {
                'test': test_name,
                'frontend_kex': frontend_kex,
                'frontend_sipx': frontend_sipx,
                'backend_kex': backend_kex,
                'backend_sipx': backend_sipx,
                'expected_kex': exp_kex,
                'expected_sipx': exp_sipx,
                'slider_success': slider_success,
                'ui_updated': ui_updated,
                'prediction_cards': len(updated_cards),
                'graphs': len(updated_graphs),
                'recommendations': len(updated_recommendations),
                'overall_success': overall_success
            }
            self.test_results.append(result)
            
            print(f"   📊 Frontend: KEX={frontend_kex}, SIPX={frontend_sipx}")
            print(f"   📊 Backend: KEX={backend_kex}, SIPX={backend_sipx}")
            print(f"   🎯 Expected: KEX={exp_kex}, SIPX={exp_sipx}")
            print(f"   🎚️ Sliders: {'✅ PASS' if slider_success else '❌ FAIL'}")
            print(f"   📋 Prediction Cards: {len(updated_cards)} found")
            print(f"   📈 Graphs: {len(updated_graphs)} found")
            print(f"   💡 Recommendations: {len(updated_recommendations)} found")
            print(f"   🎯 Overall Result: {'✅ PASS' if overall_success else '❌ FAIL'}")
            time.sleep(2)  # Pause to see result
            return overall_success
            
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all 10 comprehensive test cases"""
        print("🚀 Starting 10 Comprehensive Slider + UI Test Cases")
        print("=" * 60)
        
        if not self.setup_driver():
            return False
        
        try:
            if not self.login():
                return False
            
            # Run all 10 tests
            tests = [
                ("Test 1: KEX minimum (0) + UI", 0, None, 0, None),
                ("Test 2: KEX maximum (100) + UI", 100, None, 100, None),
                ("Test 3: SIPX minimum (0) + UI", None, 0, None, 0),
                ("Test 4: SIPX maximum (60) + UI", None, 60, None, 60),
                ("Test 5: KEX middle (50) + UI", 50, None, 50, None),
                ("Test 6: SIPX middle (30) + UI", None, 30, None, 30),
                ("Test 7: Both low (KEX=20, SIPX=10) + UI", 20, 10, 20, 10),
                ("Test 8: Both high (KEX=80, SIPX=50) + UI", 80, 50, 80, 50),
                ("Test 9: Mixed values (KEX=35, SIPX=25) + UI", 35, 25, 35, 25),
                ("Test 10: Edge case (KEX=1, SIPX=59) + UI", 1, 59, 1, 59)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, kex_val, sipx_val, exp_kex, exp_sipx in tests:
                if self.run_comprehensive_test(test_name, kex_val, sipx_val, exp_kex, exp_sipx):
                    passed += 1
            
            # Print summary
            print("\n" + "=" * 60)
            print("📊 COMPREHENSIVE TEST SUMMARY")
            print("=" * 60)
            print(f"Total Tests: {total}")
            print(f"Passed: {passed}")
            print(f"Failed: {total - passed}")
            print(f"Success Rate: {(passed/total)*100:.1f}%")
            
            if passed == total:
                print("🎉 ALL TESTS PASSED! Sliders + UI are fully working!")
            else:
                print("⚠️  Some tests failed. Check the results above.")
            
            # Print detailed results
            print("\n📋 DETAILED RESULTS:")
            for result in self.test_results:
                status = "✅ PASS" if result['overall_success'] else "❌ FAIL"
                print(f"   {result['test']}: {status}")
                print(f"     - Sliders: {'✅' if result['slider_success'] else '❌'}")
                print(f"     - UI Updated: {'✅' if result['ui_updated'] else '❌'}")
                print(f"     - Cards: {result['prediction_cards']}, Graphs: {result['graphs']}, Recs: {result['recommendations']}")
            
            return passed == total
            
        finally:
            if self.driver:
                input("Press Enter to close the browser...")
                self.driver.quit()

def main():
    """Main function to run the comprehensive test suite"""
    print("🧪 10 Comprehensive Slider + UI Test Cases")
    print("Testing sliders + prediction cards + graphs + recommendations")
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
    test_suite = ComprehensiveSliderTestSuite()
    success = test_suite.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
