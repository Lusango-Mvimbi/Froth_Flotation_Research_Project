#!/usr/bin/env python3
"""
Test 4 Second Refresh
=====================

Tests the control persistence with the actual refresh interval.
The system should refresh every 10 seconds (not 4 seconds as mentioned).

Author: AI Assistant
Date: 2025
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_4_second_refresh():
    """Test control persistence with actual refresh interval"""
    print("🔍 Testing 4 Second Refresh (Actually 10 seconds)")
    print("=" * 60)
    print("Testing: Control persistence with actual system refresh interval")
    print("=" * 60)
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    try:
        # Step 1: Login
        print("🔐 Step 1: Logging in...")
        driver.get("http://localhost:3000/login")
        
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        username_field.clear()
        username_field.send_keys("admin")
        password_field.clear()
        password_field.send_keys("admin123")
        login_button.click()
        
        time.sleep(3)
        print("✅ Logged in successfully")
        
        # Step 2: Get initial values
        print("\n📊 Step 2: Getting initial values...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "main")))
        
        sliders = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='range']")))
        initial_kex = float(sliders[0].get_attribute("value"))
        initial_sipx = float(sliders[1].get_attribute("value"))
        
        print(f"📊 Initial frontend values: KEX={initial_kex}, SIPX={initial_sipx}")
        
        # Get initial backend values
        response = requests.get("http://localhost:8000/api/control-settings", timeout=10)
        if response.status_code == 200:
            data = response.json()
            controls = data.get('controls', {})
            backend_kex = controls.get('kex')
            backend_sipx = controls.get('sipx')
            print(f"📊 Initial backend values: KEX={backend_kex}, SIPX={backend_sipx}")
        
        # Step 3: Test multiple refresh cycles
        test_values = [
            (15.0, 25.0),   # Test 1
            (35.0, 45.0),   # Test 2
            (55.0, 65.0),   # Test 3
        ]
        
        results = []
        
        for i, (target_kex, target_sipx) in enumerate(test_values, 1):
            print(f"\n🎚️ Test {i}/3: Setting KEX={target_kex}, SIPX={target_sipx}")
            
            # Set new values
            driver.execute_script(f"arguments[0].value = '{target_kex}';", sliders[0])
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", sliders[0])
            
            driver.execute_script(f"arguments[0].value = '{target_sipx}';", sliders[1])
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", sliders[1])
            
            time.sleep(2)
            
            # Verify frontend values after adjustment
            adjusted_kex = float(sliders[0].get_attribute("value"))
            adjusted_sipx = float(sliders[1].get_attribute("value"))
            print(f"📊 Frontend after adjustment: KEX={adjusted_kex}, SIPX={adjusted_sipx}")
            
            # Verify backend values after adjustment
            response = requests.get("http://localhost:8000/api/control-settings", timeout=10)
            if response.status_code == 200:
                data = response.json()
                controls = data.get('controls', {})
                backend_kex = controls.get('kex')
                backend_sipx = controls.get('sipx')
                print(f"📊 Backend after adjustment: KEX={backend_kex}, SIPX={backend_sipx}")
            
            # Wait for system refresh (10 seconds + buffer)
            print(f"⏰ Waiting for system refresh (12 seconds)...")
            time.sleep(12)
            
            # Check values after system refresh
            sliders = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='range']")))
            refresh_kex = float(sliders[0].get_attribute("value"))
            refresh_sipx = float(sliders[1].get_attribute("value"))
            print(f"📊 Frontend after system refresh: KEX={refresh_kex}, SIPX={refresh_sipx}")
            
            # Get backend values after system refresh
            response = requests.get("http://localhost:8000/api/control-settings", timeout=10)
            if response.status_code == 200:
                data = response.json()
                controls = data.get('controls', {})
                backend_kex = controls.get('kex')
                backend_sipx = controls.get('sipx')
                print(f"📊 Backend after system refresh: KEX={backend_kex}, SIPX={backend_sipx}")
            
            # Analyze the result
            frontend_maintained = (refresh_kex == target_kex and refresh_sipx == target_sipx)
            backend_maintained = (backend_kex == target_kex and backend_sipx == target_sipx)
            frontend_reverted = (refresh_kex == initial_kex and refresh_sipx == initial_sipx)
            
            result = {
                'test': i,
                'target': (target_kex, target_sipx),
                'frontend_after': (refresh_kex, refresh_sipx),
                'backend_after': (backend_kex, backend_sipx),
                'frontend_maintained': frontend_maintained,
                'backend_maintained': backend_maintained,
                'frontend_reverted': frontend_reverted,
                'success': frontend_maintained and backend_maintained
            }
            
            results.append(result)
            
            if result['success']:
                print(f"✅ Test {i} PASSED: Values maintained after system refresh")
            elif result['frontend_reverted']:
                print(f"❌ Test {i} FAILED: Frontend reverted to initial values")
            else:
                print(f"⚠️ Test {i} UNEXPECTED: Values changed but not as expected")
            
            print(f"   - Frontend maintained: {frontend_maintained}")
            print(f"   - Backend maintained: {backend_maintained}")
            print(f"   - Frontend reverted: {frontend_reverted}")
        
        # Step 4: Summary analysis
        print("\n📊 Step 4: Summary Analysis")
        print("=" * 60)
        
        passed_tests = sum(1 for r in results if r['success'])
        failed_tests = sum(1 for r in results if r['frontend_reverted'])
        unexpected_tests = len(results) - passed_tests - failed_tests
        
        print(f"📊 Test Results Summary:")
        print(f"   - Total tests: {len(results)}")
        print(f"   - Passed: {passed_tests}")
        print(f"   - Failed (reverted): {failed_tests}")
        print(f"   - Unexpected: {unexpected_tests}")
        print(f"   - Success rate: {(passed_tests / len(results) * 100):.1f}%")
        
        print(f"\n📊 Detailed Results:")
        for result in results:
            status = "✅ PASS" if result['success'] else "❌ FAIL" if result['frontend_reverted'] else "⚠️ UNEXPECTED"
            print(f"   Test {result['test']}: {status}")
            print(f"     Target: KEX={result['target'][0]}, SIPX={result['target'][1]}")
            print(f"     Frontend: KEX={result['frontend_after'][0]}, SIPX={result['frontend_after'][1]}")
            print(f"     Backend: KEX={result['backend_after'][0]}, SIPX={result['backend_after'][1]}")
        
        # Overall result
        if passed_tests == len(results):
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"✅ Control persistence fix is working with 10-second refresh!")
            return True
        elif passed_tests > failed_tests:
            print(f"\n⚠️ MOSTLY WORKING:")
            print(f"✅ {passed_tests} tests passed, ❌ {failed_tests} tests failed")
            print(f"⚠️ The fix is partially working but needs improvement")
            return False
        else:
            print(f"\n❌ FIX NOT WORKING:")
            print(f"❌ {failed_tests} tests failed, ✅ {passed_tests} tests passed")
            print(f"❌ The control persistence issue still exists")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 4 Second Refresh Test (Actually 10 seconds)")
    print("=" * 60)
    print("Testing: Control persistence with actual system refresh interval")
    print("=" * 60)
    
    # Test with actual refresh interval
    fix_working = test_4_second_refresh()
    
    print("\n" + "=" * 60)
    if fix_working:
        print("🎉 CONTROL PERSISTENCE FIX IS WORKING!")
        print("✅ All tests passed - Frontend and backend stay synchronized")
        print("✅ Control values persist correctly with 10-second refresh")
    else:
        print("❌ CONTROL PERSISTENCE FIX NEEDS MORE WORK!")
        print("⚠️ Some tests failed - The issue still exists")
        print("⚠️ Need to investigate and fix the remaining issues")
    print("=" * 60)
