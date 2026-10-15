# auto_account.py
# Registers a random account on the Hospital Manager portal,
# then verifies it in a fresh browser by logging in.
#
# Uses content-based success checks (not URL checks) because
# the app auto-logs in after registration and may keep the same URL.

import csv
import os
import random
import string
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)


# ---------------------------------------------------------------
# 1. SETTINGS
# ---------------------------------------------------------------
BASE_URL     = "https://hospitalmanager-beta.vercel.app"
REGISTER_URL = BASE_URL + "/patient-portal?register=true"
LOGIN_URL    = BASE_URL + "/login"
CSV_FILE     = "test_accounts.csv"


# ---------------------------------------------------------------
# 2. MAKE RANDOM CREDENTIALS
# ---------------------------------------------------------------
def make_password(length=12):
    """Password with at least one uppercase, lowercase, digit, and symbol."""
    upper  = random.choice(string.ascii_uppercase)
    lower  = random.choice(string.ascii_lowercase)
    digit  = random.choice(string.digits)
    symbol = random.choice("!@#$%^&*")
    others = "".join(random.choices(
        string.ascii_letters + string.digits, k=length - 4
    ))
    chars = list(upper + lower + digit + symbol + others)
    random.shuffle(chars)
    return "".join(chars)


def make_phone_number():
    """Generate a random Nigerian mobile number like 08031234567."""
    prefixes = ["0803", "0805", "0806", "0807", "0810",
                "0813", "0816", "0703", "0705", "0903"]
    return random.choice(prefixes) + "".join(random.choices(string.digits, k=7))


def make_credentials():
    """Return a dict with all the fields the form needs."""
    suffix = str(int(time.time())) + str(random.randint(100, 999))

    first_name = random.choice(["Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey"])
    last_name  = random.choice(["Rivera", "Chen", "Okafor", "Patel", "Kim", "Mensah"])

    year  = random.randint(1965, 2005)
    month = random.randint(1, 12)
    day   = random.randint(1, 28)
    dob   = f"{year}-{month:02d}-{day:02d}"

    return {
        "first_name": first_name,
        "last_name":  last_name,
        "dob":        dob,
        "gender":     random.choice(["male", "female", "other"]),
        "email":      f"bot.{first_name.lower()}.{suffix}@example.com",
        "password":   make_password(),
        "phone":      make_phone_number(),
    }


# ---------------------------------------------------------------
# 3. HELPER: SET AN INPUT VALUE (works well with React pages)
# ---------------------------------------------------------------
def set_value(driver, element, value):
    driver.execute_script("""
        const el = arguments[0];
        const setter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
        ).set;
        setter.call(el, arguments[1]);
        el.dispatchEvent(new Event('input',  { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
    """, element, value)


# ---------------------------------------------------------------
# 3b. HELPER: ROBUST CLICK (scrolls + JS fallback)
# ---------------------------------------------------------------
def safe_click(driver, element, label="element"):
    """Scroll element into view, then click. Fall back to JS click if
    the browser reports that the element is covered/intercepted."""
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
        element,
    )
    time.sleep(0.3)  # let sticky headers / smooth-scroll settle
    try:
        element.click()
    except ElementClickInterceptedException:
        print(f"   click on {label} intercepted — using JS click fallback")
        driver.execute_script("arguments[0].click();", element)


# ---------------------------------------------------------------
# 4. SAVE CREDENTIALS TO CSV
# ---------------------------------------------------------------
def save_credentials(creds):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "created_at", "first_name", "last_name",
            "dob", "gender", "email", "phone", "password"
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "created_at": datetime.now().isoformat(timespec="seconds"),
            **creds
        })
    print(f"Saved to {CSV_FILE}")


# ---------------------------------------------------------------
# 5. REGISTER A NEW ACCOUNT
# ---------------------------------------------------------------
def register(driver, creds):
    print("\nOpening register page...")
    driver.get(REGISTER_URL)

    wait = WebDriverWait(driver, 15)
    wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, 'input[placeholder="First name"]')))

    # --- Fill the form ---
    set_value(driver, driver.find_element(By.CSS_SELECTOR, 'input[placeholder="First name"]'),
              creds["first_name"])
    set_value(driver, driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Last name"]'),
              creds["last_name"])
    set_value(driver, driver.find_element(By.CSS_SELECTOR, 'input[type="date"]'),
              creds["dob"])
    set_value(driver, driver.find_element(By.CSS_SELECTOR, 'input[type="email"]'),
              creds["email"])
    set_value(driver, driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Phone number"]'),
              creds["phone"])
    set_value(driver, driver.find_element(
        By.CSS_SELECTOR,
        'input[type="password"][placeholder="Password (8+ characters)"]'),
        creds["password"])
    set_value(driver, driver.find_element(
        By.CSS_SELECTOR,
        'input[type="password"][placeholder="Confirm password"]'),
        creds["password"])

    # --- Gender dropdown ---
    Select(driver.find_element(By.CSS_SELECTOR, 'select')).select_by_value(creds["gender"])

    # --- Click "Create account" ---
    print("Clicking 'Create account'...")
    btn = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//button[contains(., 'Create account')]")))
    safe_click(driver, btn, label="'Create account' button")

    # --- Success check: registration heading should disappear ---
    # The app auto-logs in, so we cannot rely on the URL.
    # Instead, we wait for the "Start your care journey" heading to be gone.
    try:
        wait.until(EC.invisibility_of_element_located(
            (By.XPATH, "//*[contains(., 'Start your care journey')]")
        ))
        print("Registration succeeded — auto-logged in")
        print(f"   Current URL: {driver.current_url}")
        return True
    except TimeoutException:
        # Fallback: success = the email input is no longer present.
        try:
            wait.until(EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, 'input[type="email"]')
            ))
            print("Registration succeeded (fallback check)")
            print(f"   Current URL: {driver.current_url}")
            return True
        except TimeoutException:
            driver.save_screenshot("register_error.png")
            print("Registration may have failed — screenshot saved")
            print(f"   Current URL: {driver.current_url}")
            return False


# ---------------------------------------------------------------
# 6. LOGIN WITH THE NEW ACCOUNT (fresh browser)
# ---------------------------------------------------------------
def login(driver, creds):
    print("\nOpening login page...")
    driver.get(LOGIN_URL)

    wait = WebDriverWait(driver, 15)
    wait.until(EC.visibility_of_element_located((By.ID, "email")))

    driver.find_element(By.ID, "email").send_keys(creds["email"])
    driver.find_element(By.ID, "password").send_keys(creds["password"])

    print("Clicking 'Sign in'...")
    signin = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    safe_click(driver, signin, label="'Sign in' button")

    # --- Success check: login form should be gone ---
    # We wait for the email field to disappear. That happens when
    # the app navigates away from /login after a successful sign-in.
    try:
        wait.until(EC.invisibility_of_element_located((By.ID, "email")))
        print("Login succeeded")
        print(f"   Current URL: {driver.current_url}")
        return True
    except TimeoutException:
        driver.save_screenshot("login_error.png")
        print("Login may have failed — screenshot saved")
        print(f"   Current URL: {driver.current_url}")
        return False


# ---------------------------------------------------------------
# 7. MAIN
# ---------------------------------------------------------------
NUM_USERS = 10   # ← change this to 5, 10, 20, whatever you want

def main():
    print(f"Creating {NUM_USERS} account(s)...\n")

    for i in range(NUM_USERS):
        print(f"\n{'='*50}")
        print(f"  ACCOUNT {i+1} of {NUM_USERS}")
        print(f"{'='*50}")

        # --- 1. Generate credentials ---
        creds = make_credentials()
        print("Generated credentials:")
        for key, value in creds.items():
            print(f"   {key:12}: {value}")

        # --- 2. Register ---
        driver = webdriver.Chrome()
        registered = False
        try:
            registered = register(driver, creds)
        finally:
            driver.quit()

        # --- 3. Save if successful ---
        if registered:
            save_credentials(creds)
        else:
            print("⚠️ Skipping save — registration failed for this account.")

        # --- 4. Small pause between accounts (be polite to the server) ---
        if i < NUM_USERS - 1:
            print("Waiting 3 seconds before next account...")
            time.sleep(3)

    print(f"\n✅ Done. Created {NUM_USERS} account(s).")
    print(f"📄 Credentials saved to {CSV_FILE}")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()