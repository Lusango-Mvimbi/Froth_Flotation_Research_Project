#!/usr/bin/env python3
"""
Test to check if frontend is making API calls when sliders change
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_frontend_api_calls():
    """Test if frontend makes API calls when sliders change"""
    
    # Setup Chrome driver (visible)
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🔐 Logging in...")
        driver.get("http://localhost:3000/login")
        
        # Login
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        login_button.click()
        
        # Wait for dashboard
        WebDriverWait(driver, 15).until(
            EC.url_contains("/dashboard")
        )
        
        print("✅ Logged in successfully")
        
        # Get initial backend values
        print("\n📊 Initial backend values:")
        response = requests.get("http://localhost:8000/api/control-settings")
        initial_data = response.json()
        print(f"   KEX: {initial_data['controls']['kex']}")
        print(f"   SIPX: {initial_data['controls']['sipx']}")
        
        # Find sliders
        sliders = driver.find_elements(By.CSS_SELECTOR, "input[type='range']")
        if len(sliders) >= 2:
            kex_slider = sliders[0]
            sipx_slider = sliders[1]
            
            print(f"\n🎚️ Initial frontend values:")
            print(f"   KEX: {kex_slider.get_attribute('value')}")
            print(f"   SIPX: {sipx_slider.get_attribute('value')}")
            
            # Change KEX slider
            print(f"\n🔄 Changing KEX slider to 75...")
            driver.execute_script(f"""
                arguments[0].value = 75;
                arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                arguments[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
            """, kex_slider)
            
            # Wait a bit for the API call
            time.sleep(2)
            
            # Check if backend was updated
            print(f"\n📊 Backend values after KEX change:")
            response = requests.get("http://localhost:8000/api/control-settings")
            after_data = response.json()
            print(f"   KEX: {after_data['controls']['kex']}")
            print(f"   SIPX: {after_data['controls']['sipx']}")
            
            # Check frontend values
            print(f"\n🎚️ Frontend values after change:")
            print(f"   KEX: {kex_slider.get_attribute('value')}")
            print(f"   SIPX: {sipx_slider.get_attribute('value')}")
            
            # Check browser console for errors
            print(f"\n🔍 Checking browser console for errors...")
            logs = driver.get_log('browser')
            for log in logs:
                if log['level'] == 'SEVERE':
                    print(f"   ❌ Error: {log['message']}")
                elif 'error' in log['message'].lower():
                    print(f"   ⚠️ Warning: {log['message']}")
            
            if not logs:
                print("   ✅ No console errors found")
            
        else:
            print("❌ Could not find sliders")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_frontend_api_calls()
