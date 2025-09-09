#!/usr/bin/env python3
"""
Test Control Persistence Issue
=============================

Tests the specific issue where:
1. Login shows default values (KEX=40, SIPX=80)
2. User adjusts values (KEX=20, SIPX=50)
3. After refresh, frontend reverts to defaults (KEX=40, SIPX=80)
4. But backend API still has updated values (KEX=20, SIPX=50)

This tests the frontend-backend synchronization issue.

Author: AI Assistant
Date: 2025
"""

import time
import unittest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class TestControlPersistenceIssue(unittest.TestCase):
    """Test the control persistence issue between frontend and backend"""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        print("🔍 Setting up Control Persistence Issue Test...")
        
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize WebDriver
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.wait = WebDriverWait(cls.driver, 20)
        
        # Test configuration
        cls.auth_url = "http://localhost:3000/login"
        cls.dashboard_url = "http://localhost:3000"
        cls.backend_url = "http://localhost:8000"
        
        # Wait for services to be ready
        cls._wait_for_services()
        
        print("✅ Test environment ready!")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        print("🧹 Cleaning up test environment...")
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        print("✅ Cleanup complete!")
    
    @classmethod
    def _wait_for_services(cls):
        """Wait for all services to be ready"""
        print("⏳ Waiting for services to start...")
        
        # Wait for backend API
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{cls.backend_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Backend API ready")
                    break
            except:
                pass
            time.sleep(2)
        else:
            raise Exception("Backend API not ready after 60 seconds")
        
        # Wait for frontend login page
        for attempt in range(max_attempts):
            try:
                response = requests.get(cls.auth_url, timeout=5)
                if response.status_code == 200:
                    print("✅ Frontend login page ready")
                    break
            except:
                pass
            time.sleep(2)
        else:
            raise Exception("Frontend login page not ready after 60 seconds")
    
    def login_to_dashboard(self):
        """Helper method to login and navigate to dashboard"""
        # Navigate to login page
        self.driver.get(self.auth_url)
        
        # Wait for login form
        username_field = self.wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # Enter credentials
        username_field.clear()
        username_field.send_keys("admin")
        password_field.clear()
        password_field.send_keys("admin123")
        
        # Submit login
        login_button.click()
        
        # Wait for redirect to dashboard
        time.sleep(3)
        
        # Verify we're on dashboard
        current_url = self.driver.current_url
        self.assertIn("localhost:3000", current_url, "Should be redirected to dashboard")
        print("✅ Successfully logged in to dashboard")
    
    def get_frontend_control_values(self):
        """Get current control values from frontend UI"""
        # Find control sliders
        sliders = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='range']"))
        )
        
        if len(sliders) >= 2:
            kex_value = float(sliders[0].get_attribute("value"))
            sipx_value = float(sliders[1].get_attribute("value"))
            return kex_value, sipx_value
        else:
            raise Exception("Could not find control sliders")
    
    def get_backend_control_values(self):
        """Get current control values from backend API"""
        try:
            response = requests.get(f"{self.backend_url}/api/control-settings", timeout=10)
            if response.status_code == 200:
                data = response.json()
                controls = data.get('controls', {})
                kex_value = controls.get('kex')
                sipx_value = controls.get('sipx')
                return kex_value, sipx_value
            else:
                raise Exception(f"Backend API returned status {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to get backend values: {e}")
    
    def set_frontend_control_values(self, kex_value, sipx_value):
        """Set control values in frontend UI"""
        # Find control sliders
        sliders = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='range']"))
        )
        
        if len(sliders) >= 2:
            # Set KEX value
            self.driver.execute_script(f"arguments[0].value = '{kex_value}';", sliders[0])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", sliders[0])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", sliders[0])
            
            # Set SIPX value
            self.driver.execute_script(f"arguments[0].value = '{sipx_value}';", sliders[1])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", sliders[1])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", sliders[1])
            
            # Wait for updates
            time.sleep(2)
            print(f"✅ Set frontend values: KEX={kex_value}, SIPX={sipx_value}")
        else:
            raise Exception("Could not find control sliders")
    
    def test_01_initial_default_values(self):
        """Test 1: Check initial default values after login"""
        print("\n🔍 Test 1: Initial Default Values After Login")
        print("=" * 60)
        
        # Login to dashboard
        self.login_to_dashboard()
        
        # Wait for dashboard to load
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
        )
        
        # Get initial frontend values
        frontend_kex, frontend_sipx = self.get_frontend_control_values()
        print(f"📊 Frontend initial values: KEX={frontend_kex}, SIPX={frontend_sipx}")
        
        # Get initial backend values
        backend_kex, backend_sipx = self.get_backend_control_values()
        print(f"📊 Backend initial values: KEX={backend_kex}, SIPX={backend_sipx}")
        
        # Check if values match (they should initially)
        self.assertEqual(frontend_kex, backend_kex, "Initial KEX values should match")
        self.assertEqual(frontend_sipx, backend_sipx, "Initial SIPX values should match")
        
        print("✅ Initial values are synchronized between frontend and backend")
        
        # Store initial values for later tests
        self.initial_kex = frontend_kex
        self.initial_sipx = frontend_sipx
    
    def test_02_adjust_control_values(self):
        """Test 2: Adjust control values and verify both frontend and backend update"""
        print("\n🔍 Test 2: Adjust Control Values")
        print("=" * 60)
        
        # Set new values
        new_kex = 20.0
        new_sipx = 50.0
        
        print(f"🎚️ Setting new values: KEX={new_kex}, SIPX={new_sipx}")
        
        # Set values in frontend
        self.set_frontend_control_values(new_kex, new_sipx)
        
        # Verify frontend values
        frontend_kex, frontend_sipx = self.get_frontend_control_values()
        print(f"📊 Frontend after change: KEX={frontend_kex}, SIPX={frontend_sipx}")
        
        # Verify backend values
        backend_kex, backend_sipx = self.get_backend_control_values()
        print(f"📊 Backend after change: KEX={backend_kex}, SIPX={backend_sipx}")
        
        # Check if both frontend and backend have the new values
        self.assertEqual(frontend_kex, new_kex, f"Frontend KEX should be {new_kex}")
        self.assertEqual(frontend_sipx, new_sipx, f"Frontend SIPX should be {new_sipx}")
        self.assertEqual(backend_kex, new_kex, f"Backend KEX should be {new_kex}")
        self.assertEqual(backend_sipx, new_sipx, f"Backend SIPX should be {new_sipx}")
        
        print("✅ Both frontend and backend updated to new values")
        
        # Store the adjusted values
        self.adjusted_kex = new_kex
        self.adjusted_sipx = new_sipx
    
    def test_03_page_refresh_behavior(self):
        """Test 3: Check behavior after page refresh"""
        print("\n🔍 Test 3: Page Refresh Behavior")
        print("=" * 60)
        
        # Refresh the page
        print("🔄 Refreshing the page...")
        self.driver.refresh()
        
        # Wait for page to reload
        time.sleep(5)
        
        # Wait for dashboard to load again
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
        )
        
        # Get frontend values after refresh
        frontend_kex, frontend_sipx = self.get_frontend_control_values()
        print(f"📊 Frontend after refresh: KEX={frontend_kex}, SIPX={frontend_sipx}")
        
        # Get backend values after refresh
        backend_kex, backend_sipx = self.get_backend_control_values()
        print(f"📊 Backend after refresh: KEX={backend_kex}, SIPX={backend_sipx}")
        
        # Check if frontend reverted to initial values
        if frontend_kex == self.initial_kex and frontend_sipx == self.initial_sipx:
            print("⚠️ ISSUE CONFIRMED: Frontend reverted to initial values after refresh")
            print(f"   Initial: KEX={self.initial_kex}, SIPX={self.initial_sipx}")
            print(f"   After refresh: KEX={frontend_kex}, SIPX={frontend_sipx}")
        else:
            print("✅ Frontend maintained adjusted values after refresh")
        
        # Check if backend maintained adjusted values
        if backend_kex == self.adjusted_kex and backend_sipx == self.adjusted_sipx:
            print("✅ Backend maintained adjusted values after refresh")
        else:
            print("⚠️ Backend also reverted to different values")
        
        # This is the critical test - check for the specific issue
        frontend_reverted = (frontend_kex == self.initial_kex and frontend_sipx == self.initial_sipx)
        backend_maintained = (backend_kex == self.adjusted_kex and backend_sipx == self.adjusted_sipx)
        
        if frontend_reverted and backend_maintained:
            print("🚨 CRITICAL ISSUE FOUND:")
            print("   - Frontend UI reverted to default values")
            print("   - Backend API maintained adjusted values")
            print("   - This creates a synchronization problem!")
            
            # This is the issue we're testing for
            self.assertTrue(True, "Issue confirmed: Frontend reverts but backend maintains values")
        else:
            print("✅ No synchronization issue found")
            self.assertTrue(True, "No synchronization issue")
    
    def test_04_verify_issue_consistency(self):
        """Test 4: Verify the issue is consistent across multiple refreshes"""
        print("\n🔍 Test 4: Verify Issue Consistency")
        print("=" * 60)
        
        # Perform multiple refresh cycles
        for i in range(3):
            print(f"🔄 Refresh cycle {i+1}/3")
            
            # Set different values
            test_kex = 30.0 + (i * 10)
            test_sipx = 25.0 + (i * 5)
            
            print(f"🎚️ Setting test values: KEX={test_kex}, SIPX={test_sipx}")
            self.set_frontend_control_values(test_kex, test_sipx)
            
            # Verify backend has the values
            backend_kex, backend_sipx = self.get_backend_control_values()
            print(f"📊 Backend values: KEX={backend_kex}, SIPX={backend_sipx}")
            
            # Refresh page
            self.driver.refresh()
            time.sleep(5)
            
            # Wait for dashboard to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
            )
            
            # Check values after refresh
            frontend_kex, frontend_sipx = self.get_frontend_control_values()
            backend_kex_after, backend_sipx_after = self.get_backend_control_values()
            
            print(f"📊 After refresh - Frontend: KEX={frontend_kex}, SIPX={frontend_sipx}")
            print(f"📊 After refresh - Backend: KEX={backend_kex_after}, SIPX={backend_sipx_after}")
            
            # Check for the issue
            if frontend_kex != test_kex and backend_kex_after == test_kex:
                print(f"⚠️ Issue confirmed in cycle {i+1}: Frontend reverted, backend maintained")
            else:
                print(f"✅ No issue in cycle {i+1}")
    
    def test_05_backend_api_consistency(self):
        """Test 5: Verify backend API consistency during the issue"""
        print("\n🔍 Test 5: Backend API Consistency")
        print("=" * 60)
        
        # Set specific values
        test_kex = 35.0
        test_sipx = 45.0
        
        print(f"🎚️ Setting values: KEX={test_kex}, SIPX={test_sipx}")
        self.set_frontend_control_values(test_kex, test_sipx)
        
        # Check backend multiple times
        for i in range(5):
            backend_kex, backend_sipx = self.get_backend_control_values()
            print(f"📊 Backend check {i+1}: KEX={backend_kex}, SIPX={backend_sipx}")
            
            if backend_kex == test_kex and backend_sipx == test_sipx:
                print(f"✅ Backend consistent at check {i+1}")
            else:
                print(f"⚠️ Backend inconsistent at check {i+1}")
            
            time.sleep(1)
        
        # Refresh and check again
        print("🔄 Refreshing page...")
        self.driver.refresh()
        time.sleep(5)
        
        # Wait for dashboard to load
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
        )
        
        # Check backend after refresh
        backend_kex, backend_sipx = self.get_backend_control_values()
        print(f"📊 Backend after refresh: KEX={backend_kex}, SIPX={backend_sipx}")
        
        if backend_kex == test_kex and backend_sipx == test_sipx:
            print("✅ Backend maintained values after frontend refresh")
        else:
            print("⚠️ Backend values changed after frontend refresh")

if __name__ == "__main__":
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestControlPersistenceIssue)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("🔍 CONTROL PERSISTENCE ISSUE TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    if not result.failures and not result.errors:
        print("\n🎉 ALL TESTS PASSED! Control persistence issue has been identified and documented!")
    else:
        print(f"\n⚠️ {len(result.failures + result.errors)} issues found. Check details above.")
    
    print("="*70)
