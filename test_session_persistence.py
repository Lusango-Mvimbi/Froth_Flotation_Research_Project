#!/usr/bin/env python3
"""
Test Session Persistence Fix
============================

Tests that the dashboard maintains login session after page refresh.

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

def test_session_persistence():
    """Test that login session persists after page refresh"""
    print("🔍 Testing Session Persistence Fix")
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
        
        # Step 2: Verify we're on dashboard
        print("\n📊 Step 2: Verifying dashboard access...")
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        if "localhost:3000" in current_url and "login" not in current_url:
            print("✅ Successfully on dashboard")
        else:
            print("❌ Not on dashboard")
            return False
        
        # Step 3: Check for dashboard elements
        print("\n🎛️ Step 3: Checking dashboard elements...")
        try:
            # Wait for dashboard to load
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "main")))
            print("✅ Dashboard main content loaded")
            
            # Check for control sliders
            sliders = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='range']")))
            print(f"✅ Found {len(sliders)} control sliders")
            
            # Check for prediction cards
            cards = driver.find_elements(By.CSS_SELECTOR, ".bg-gradient-to-br.from-dark-800.to-dark-700")
            print(f"✅ Found {len(cards)} prediction cards")
            
        except Exception as e:
            print(f"❌ Dashboard elements not found: {e}")
            return False
        
        # Step 4: Refresh the page
        print("\n🔄 Step 4: Refreshing the page...")
        driver.refresh()
        time.sleep(5)
        
        # Step 5: Check if we're still logged in
        print("\n🔍 Step 5: Checking if still logged in after refresh...")
        current_url = driver.current_url
        print(f"Current URL after refresh: {current_url}")
        
        if "login" in current_url:
            print("❌ ISSUE: Redirected to login page after refresh")
            print("   This means session persistence is NOT working")
            return False
        elif "localhost:3000" in current_url:
            print("✅ SUCCESS: Still on dashboard after refresh")
            print("   Session persistence is working!")
            
            # Verify dashboard elements are still there
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "main")))
                sliders = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='range']")))
                print(f"✅ Dashboard elements still present: {len(sliders)} sliders")
                return True
            except Exception as e:
                print(f"❌ Dashboard elements missing after refresh: {e}")
                return False
        else:
            print(f"⚠️ Unexpected URL after refresh: {current_url}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 Session Persistence Test")
    print("=" * 50)
    
    # Test the fix
    session_works = test_session_persistence()
    
    print("\n" + "=" * 50)
    if session_works:
        print("🎉 SESSION PERSISTENCE FIXED!")
        print("✅ Dashboard maintains login session after page refresh")
        print("✅ No need to login again when refreshing the page")
    else:
        print("❌ SESSION PERSISTENCE ISSUE STILL EXISTS")
        print("⚠️ Dashboard still requires login after page refresh")
    print("=" * 50)
