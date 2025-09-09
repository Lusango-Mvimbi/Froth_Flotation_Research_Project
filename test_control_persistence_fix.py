#!/usr/bin/env python3
"""
Test Control Persistence Fix
============================

Tests if the control persistence fix is working by using different values
to clearly see if the frontend reverts or maintains values.

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

def test_control_persistence_fix():
    """Test if the control persistence fix is working"""
    print("🔍 Testing Control Persistence Fix")
    print("=" * 60)
    print("Testing: Different values to clearly see if persistence works")
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
        
        # Step 3: Adjust to clearly different values
        print("\n🎚️ Step 3: Adjusting to clearly different values...")
        target_kex = 70.0  # Clearly different from initial
        target_sipx = 15.0  # Clearly different from initial
        
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
        print("   (Waiting 35 seconds for the system's automatic refresh to occur)")
        
        # Wait for automatic refresh to occur
        time.sleep(35)
        
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
        
        # Step 6: Analyze the results
        print("\n🔍 Step 6: Analyzing the results...")
        
        # Check if frontend reverted to initial values
        frontend_reverted = (auto_refresh_kex == initial_kex and auto_refresh_sipx == initial_sipx)
        
        # Check if frontend maintained adjusted values
        frontend_maintained = (auto_refresh_kex == target_kex and auto_refresh_sipx == target_sipx)
        
        # Check if backend maintained adjusted values
        backend_maintained = (backend_kex == target_kex and backend_sipx == target_sipx)
        
        print(f"📊 Analysis:")
        print(f"   - Initial values: KEX={initial_kex}, SIPX={initial_sipx}")
        print(f"   - Target values: KEX={target_kex}, SIPX={target_sipx}")
        print(f"   - After automatic refresh - Frontend: KEX={auto_refresh_kex}, SIPX={auto_refresh_sipx}")
        print(f"   - After automatic refresh - Backend: KEX={backend_kex}, SIPX={backend_sipx}")
        print(f"   - Frontend reverted to initial: {frontend_reverted}")
        print(f"   - Frontend maintained target: {frontend_maintained}")
        print(f"   - Backend maintained target: {backend_maintained}")
        
        # Determine the result
        if frontend_reverted and backend_maintained:
            print("\n🚨 ISSUE STILL EXISTS:")
            print("   - Frontend reverted to initial values after automatic refresh")
            print("   - Backend maintained the adjusted values")
            print("   - The fix did not work")
            return False
        elif frontend_maintained and backend_maintained:
            print("\n✅ FIX WORKING:")
            print("   - Frontend maintained adjusted values after automatic refresh")
            print("   - Backend maintained the adjusted values")
            print("   - Frontend and backend are synchronized")
            return True
        else:
            print("\n⚠️ UNEXPECTED RESULT:")
            print("   - Frontend and backend values don't match expected patterns")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 Control Persistence Fix Test")
    print("=" * 60)
    print("Testing: Different values to clearly see if persistence works")
    print("=" * 60)
    
    # Test the fix
    fix_working = test_control_persistence_fix()
    
    print("\n" + "=" * 60)
    if fix_working:
        print("🎉 CONTROL PERSISTENCE FIX IS WORKING!")
        print("✅ Frontend and backend stay synchronized after automatic refresh")
        print("✅ Control values persist correctly")
    else:
        print("❌ CONTROL PERSISTENCE FIX NOT WORKING!")
        print("⚠️ Frontend still reverts to default values after automatic refresh")
        print("⚠️ The issue still exists")
    print("=" * 60)
