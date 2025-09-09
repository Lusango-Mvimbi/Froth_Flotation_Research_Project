#!/usr/bin/env python3
"""
Simple Test for Control Refresh Issue
====================================

Tests the specific issue where frontend reverts to defaults after refresh
but backend maintains the adjusted values.

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

def test_control_refresh_issue():
    """Test the control refresh issue"""
    print("🔍 Testing Control Refresh Issue")
    print("=" * 50)
    
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
        new_kex = 25.0
        new_sipx = 40.0
        
        # Set new values
        driver.execute_script(f"arguments[0].value = '{new_kex}';", sliders[0])
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", sliders[0])
        
        driver.execute_script(f"arguments[0].value = '{new_sipx}';", sliders[1])
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", sliders[1])
        
        time.sleep(2)
        
        # Verify frontend values
        updated_kex = float(sliders[0].get_attribute("value"))
        updated_sipx = float(sliders[1].get_attribute("value"))
        print(f"📊 Frontend after adjustment: KEX={updated_kex}, SIPX={updated_sipx}")
        
        # Verify backend values
        response = requests.get("http://localhost:8000/api/control-settings", timeout=10)
        if response.status_code == 200:
            data = response.json()
            controls = data.get('controls', {})
            backend_kex = controls.get('kex')
            backend_sipx = controls.get('sipx')
            print(f"📊 Backend after adjustment: KEX={backend_kex}, SIPX={backend_sipx}")
        
        # Step 4: Refresh page
        print("\n🔄 Step 4: Refreshing page...")
        driver.refresh()
        time.sleep(5)
        
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "main")))
        
        # Step 5: Check values after refresh
        print("\n📊 Step 5: Checking values after refresh...")
        
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
        
        # Step 6: Analyze the issue
        print("\n🔍 Step 6: Analyzing the issue...")
        
        frontend_reverted = (refresh_kex == initial_kex and refresh_sipx == initial_sipx)
        backend_maintained = (backend_kex == new_kex and backend_sipx == new_sipx)
        
        if frontend_reverted and backend_maintained:
            print("🚨 ISSUE CONFIRMED:")
            print("   - Frontend reverted to initial values after refresh")
            print("   - Backend maintained the adjusted values")
            print("   - This creates a synchronization problem!")
            print(f"   - Initial: KEX={initial_kex}, SIPX={initial_sipx}")
            print(f"   - Adjusted: KEX={new_kex}, SIPX={new_sipx}")
            print(f"   - After refresh - Frontend: KEX={refresh_kex}, SIPX={refresh_sipx}")
            print(f"   - After refresh - Backend: KEX={backend_kex}, SIPX={backend_sipx}")
            return True
        elif not frontend_reverted and backend_maintained:
            print("✅ NO ISSUE: Frontend maintained values after refresh")
            return False
        else:
            print("⚠️ PARTIAL ISSUE: Both frontend and backend changed")
            return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 Simple Control Refresh Issue Test")
    print("=" * 50)
    
    issue_found = test_control_refresh_issue()
    
    print("\n" + "=" * 50)
    if issue_found:
        print("🚨 CONTROL REFRESH ISSUE CONFIRMED!")
        print("The frontend reverts to default values after refresh")
        print("but the backend maintains the adjusted values.")
        print("This creates a synchronization problem.")
    else:
        print("✅ NO CONTROL REFRESH ISSUE FOUND!")
        print("Frontend and backend stay synchronized after refresh.")
    print("=" * 50)
