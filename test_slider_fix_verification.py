#!/usr/bin/env python3
"""
Simple test to verify slider functionality is working
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_slider_fix():
    """Test that sliders properly update the backend"""
    
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
        
        # Test 1: Set KEX to 25
        print("\n🧪 Test 1: Set KEX to 25")
        sliders = driver.find_elements(By.CSS_SELECTOR, "input[type='range']")
        kex_slider = sliders[0]
        
        # Get initial backend value
        response = requests.get("http://localhost:8000/api/control-settings")
        initial_kex = response.json()['controls']['kex']
        print(f"   Initial backend KEX: {initial_kex}")
        
        # Change slider
        driver.execute_script(f"""
            arguments[0].value = 25;
            arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
            arguments[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
        """, kex_slider)
        
        print("   ⏳ Waiting for API call...")
        time.sleep(3)  # Wait for debounced API call
        
        # Check backend
        response = requests.get("http://localhost:8000/api/control-settings")
        new_kex = response.json()['controls']['kex']
        print(f"   New backend KEX: {new_kex}")
        
        if new_kex == 25.0:
            print("   ✅ Test 1 PASSED - Backend updated correctly")
        else:
            print(f"   ❌ Test 1 FAILED - Expected 25.0, got {new_kex}")
        
        # Test 2: Set SIPX to 40
        print("\n🧪 Test 2: Set SIPX to 40")
        sipx_slider = sliders[1]
        
        # Get initial backend value
        response = requests.get("http://localhost:8000/api/control-settings")
        initial_sipx = response.json()['controls']['sipx']
        print(f"   Initial backend SIPX: {initial_sipx}")
        
        # Change slider
        driver.execute_script(f"""
            arguments[0].value = 40;
            arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
            arguments[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
        """, sipx_slider)
        
        print("   ⏳ Waiting for API call...")
        time.sleep(3)  # Wait for debounced API call
        
        # Check backend
        response = requests.get("http://localhost:8000/api/control-settings")
        new_sipx = response.json()['controls']['sipx']
        print(f"   New backend SIPX: {new_sipx}")
        
        if new_sipx == 40.0:
            print("   ✅ Test 2 PASSED - Backend updated correctly")
        else:
            print(f"   ❌ Test 2 FAILED - Expected 40.0, got {new_sipx}")
        
        # Test 3: Set both values
        print("\n🧪 Test 3: Set both KEX=60, SIPX=20")
        
        # Change both sliders
        driver.execute_script(f"""
            arguments[0].value = 60;
            arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
            arguments[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
        """, kex_slider)
        
        driver.execute_script(f"""
            arguments[0].value = 20;
            arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
            arguments[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
        """, sipx_slider)
        
        print("   ⏳ Waiting for API calls...")
        time.sleep(4)  # Wait longer for both API calls
        
        # Check backend
        response = requests.get("http://localhost:8000/api/control-settings")
        final_data = response.json()['controls']
        print(f"   Final backend KEX: {final_data['kex']}")
        print(f"   Final backend SIPX: {final_data['sipx']}")
        
        if final_data['kex'] == 60.0 and final_data['sipx'] == 20.0:
            print("   ✅ Test 3 PASSED - Both values updated correctly")
        else:
            print(f"   ❌ Test 3 FAILED - Expected KEX=60.0, SIPX=20.0")
        
        print("\n🎉 Slider functionality test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        input("Press Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    test_slider_fix()
