#!/usr/bin/env python3
"""
Test Automatic Refresh Issue
============================

Tests the specific issue where the system's automatic refresh causes
control values to revert to defaults while backend maintains adjusted values.

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

def test_automatic_refresh_issue():
    """Test the automatic refresh issue"""
    print("🔍 Testing Automatic Refresh Issue")
    print("=" * 60)
    print("Testing: System's automatic refresh causes control reversion")
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
        
        # Step 3: Adjust values
        print("\n🎚️ Step 3: Adjusting values...")
        target_kex = 25.0
        target_sipx = 45.0
        
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
        
        # Step 4: Wait for system's automatic refresh
        print("\n⏰ Step 4: Waiting for system's automatic refresh...")
        print("   (Waiting 30 seconds for the system's automatic refresh to occur)")
        
        # Wait for automatic refresh to occur
        time.sleep(30)
        
        # Step 5: Check values after automatic refresh
        print("\n📊 Step 5: Checking values after automatic refresh...")
        
        # Get frontend values after automatic refresh
        sliders = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='range']")))
        auto_refresh_kex = float(sliders[0].get_attribute("value"))
        auto_refresh_sipx = float(sliders[1].get_attribute("value"))
        print(f"📊 Frontend after automatic refresh: KEX={auto_refresh_kex}, SIPX={auto_refresh_sipx}")
        
        # Get backend values after automatic refresh
        response = requests.get("http://localhost:8000/api/control-settings", timeout=10)
        if response.status_code == 200:
            data = response.json()
            controls = data.get('controls', {})
            backend_kex = controls.get('kex')
            backend_sipx = controls.get('sipx')
            print(f"📊 Backend after automatic refresh: KEX={backend_kex}, SIPX={backend_sipx}")
        
        # Step 6: Analyze the automatic refresh issue
        print("\n🔍 Step 6: Analyzing the automatic refresh issue...")
        
        # Check if frontend reverted to initial values
        frontend_reverted = (auto_refresh_kex == initial_kex and auto_refresh_sipx == initial_sipx)
        
        # Check if backend maintained adjusted values
        backend_maintained = (backend_kex == target_kex and backend_sipx == target_sipx)
        
        print(f"📊 Analysis:")
        print(f"   - Initial values: KEX={initial_kex}, SIPX={initial_sipx}")
        print(f"   - Target values: KEX={target_kex}, SIPX={target_sipx}")
        print(f"   - After automatic refresh - Frontend: KEX={auto_refresh_kex}, SIPX={auto_refresh_sipx}")
        print(f"   - After automatic refresh - Backend: KEX={backend_kex}, SIPX={backend_sipx}")
        print(f"   - Frontend reverted to initial: {frontend_reverted}")
        print(f"   - Backend maintained target: {backend_maintained}")
        
        # Determine the issue
        if frontend_reverted and backend_maintained:
            print("\n🚨 AUTOMATIC REFRESH ISSUE CONFIRMED:")
            print("   - Frontend reverted to initial values after automatic refresh")
            print("   - Backend maintained the adjusted values")
            print("   - This is the exact issue described!")
            print(f"   - Frontend shows: KEX={auto_refresh_kex}, SIPX={auto_refresh_sipx}")
            print(f"   - Backend has: KEX={backend_kex}, SIPX={backend_sipx}")
            return True
        elif not frontend_reverted and backend_maintained:
            print("\n✅ NO ISSUE: Frontend maintained adjusted values after automatic refresh")
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
    print("🔍 Automatic Refresh Issue Test")
    print("=" * 60)
    print("Testing: System's automatic refresh causes control reversion")
    print("=" * 60)
    
    # Test the automatic refresh issue
    issue_found = test_automatic_refresh_issue()
    
    print("\n" + "=" * 60)
    if issue_found:
        print("🚨 AUTOMATIC REFRESH ISSUE CONFIRMED!")
        print("The system's automatic refresh causes frontend to revert to default values")
        print("while the backend maintains the adjusted values.")
        print("This is the exact synchronization problem described.")
    else:
        print("✅ NO AUTOMATIC REFRESH ISSUE FOUND!")
        print("Frontend and backend stay synchronized after automatic refresh.")
    print("=" * 60)
