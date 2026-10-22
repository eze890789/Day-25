from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
driver = webdriver.Chrome()
try:
    driver.get("https://hospitalmanager-beta.vercel.app/login")
    wait = WebDriverWait(driver, 15)
    email_input = wait.until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    email_input.clear()
    email_input.send_keys("botaccount1@gmail.com")
    password_input = driver.find_element(By.ID, "password")
    password_input.clear()
    password_input.send_keys("StrongPass123!")
    sign_in_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    sign_in_btn.click()

    import time
    time.sleep(5)
    print("Current URL:", driver.current_url)
    print("Page title:", driver.title)
    if "login" not in driver.current_url:
        print("✅ login appears successful!")
    else:
        print("⚠️ Still on login page -- check credentials or error message.")

finally:
    driver.quit()
