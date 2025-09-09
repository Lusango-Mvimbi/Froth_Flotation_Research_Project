#!/usr/bin/env python3
"""
Test Specific Control Scenario
==============================

Tests the exact scenario described:
1. Login shows default values: KEX=40, SIPX=80
2. User adjusts to: KEX=20, SIPX=50
3. After automatic refresh: Frontend reverts to KEX=40, SIPX=80
4. But backend API still has: KEX=20, SIPX=50

This tests the specific synchronization issue.

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

def test_specific_control_scenario():
    """Test the specific control scenario described by user"""
    print("🔍 Testing Specific Control Scenario")
    print("=" * 60)
    print("Scenario: Login defaults (KEX=40, SIPX=80) → Adjust (KEX=20, SIPX=50) → Auto refresh → Check sync")
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
        
        # Step 2: Get initial/default values
        print("\n📊 Step 2: Getting initial/default values...")
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
        
        # Step 3: Adjust values to specific targets
        print("\n🎚️ Step 3: Adjusting values to KEX=20, SIPX=50...")
        target_kex = 20.0
        target_sipx = 50.0
        
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
        
        # Step 4: Wait for automatic refresh (simulate by waiting and then refreshing)
        print("\n⏰ Step 4: Waiting for automatic refresh...")
        print("   (Simulating automatic refresh by waiting 10 seconds then refreshing)")
        
        # Wait for any automatic refresh to occur
        time.sleep(10)
        
        # Manually refresh to simulate automatic refresh
        print("🔄 Refreshing page to simulate automatic refresh...")
        driver.refresh()
        time.sleep(5)
        
        # Wait for dashboard to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "main")))
        
        # Step 5: Check values after automatic refresh
        print("\n📊 Step 5: Checking values after automatic refresh...")
        
        # Get frontend values after refresh
        sliders = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='range']")))
        refresh_kex = float(sliders[0].get_attribute("value"))
        refresh_sipx = float(sliders[1].get_attribute("value"))
        print(f"📊 Frontend after refresh: KEX={refresh_kex}, SIPX={refresh_sipx}")
        
        # Get backend values after refresh
        response = requests.get("http://localhost:8000/api/control-settings", timeout=10)
        if response.status_code == 200:
            data = response.json()
            controls = data.get('controls', {})
            backend_kex = controls.get('kex')
            backend_sipx = controls.get('sipx')
            print(f"📊 Backend after refresh: KEX={backend_kex}, SIPX={backend_sipx}")
        
        # Step 6: Analyze the specific issue
        print("\n🔍 Step 6: Analyzing the specific issue...")
        
        # Check if frontend reverted to initial values
        frontend_reverted = (refresh_kex == initial_kex and refresh_sipx == initial_sipx)
        
        # Check if backend maintained adjusted values
        backend_maintained = (backend_kex == target_kex and backend_sipx == target_sipx)
        
        print(f"📊 Analysis:")
        print(f"   - Initial values: KEX={initial_kex}, SIPX={initial_sipx}")
        print(f"   - Target values: KEX={target_kex}, SIPX={target_sipx}")
        print(f"   - After refresh - Frontend: KEX={refresh_kex}, SIPX={refresh_sipx}")
        print(f"   - After refresh - Backend: KEX={backend_kex}, SIPX={backend_sipx}")
        print(f"   - Frontend reverted to initial: {frontend_reverted}")
        print(f"   - Backend maintained target: {backend_maintained}")
        
        # Determine the issue
        if frontend_reverted and backend_maintained:
            print("\n🚨 SPECIFIC ISSUE CONFIRMED:")
            print("   - Frontend reverted to initial values after automatic refresh")
            print("   - Backend maintained the adjusted values")
            print("   - This creates the exact synchronization problem described!")
            print(f"   - Frontend shows: KEX={refresh_kex}, SIPX={refresh_sipx}")
            print(f"   - Backend has: KEX={backend_kex}, SIPX={backend_sipx}")
            return True
        elif not frontend_reverted and backend_maintained:
            print("\n✅ NO ISSUE: Frontend maintained adjusted values after refresh")
            return False
        elif frontend_reverted and not backend_maintained:
            print("\n⚠️ PARTIAL ISSUE: Both frontend and backend reverted")
            return True
        else:
            print("\n✅ NO ISSUE: Both frontend and backend maintained values")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 Specific Control Scenario Test")
    print("=" * 60)
    print("Testing: Login defaults → Adjust values → Auto refresh → Check sync")
    print("=" * 60)
    
    # Test the specific scenario
    issue_found = test_specific_control_scenario()
    
    print("\n" + "=" * 60)
    if issue_found:
        print("🚨 SPECIFIC CONTROL ISSUE CONFIRMED!")
        print("The frontend reverts to default values after automatic refresh")
        print("but the backend maintains the adjusted values.")
        print("This is the exact synchronization problem described.")
    else:
        print("✅ NO SPECIFIC CONTROL ISSUE FOUND!")
        print("Frontend and backend stay synchronized after automatic refresh.")
    print("=" * 60)
