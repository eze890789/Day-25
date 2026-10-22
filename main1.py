# Selenium => is a browser automation framework. It controls a real browser programmatically


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# driver = webdriver.Chrome()
# driver.get("https://example.com")
# print(driver.title)
# driver.quit()


# driver = webdriver.Chrome()
#
# driver.get("https://learncompletefrontend.vercel.app/")
#
# element = driver.find_element(By.CSS_SELECTOR, "h1")
# print(element.text)
#
# driver.quit()

# driver = webdriver.Chrome()
#
# driver.get("https://hospitalmanager-beta.vercel.app/")
#
# element = driver.find_element(By.CSS_SELECTOR, "h1")
# print(element.text)
#
# driver.quit()

# driver = webdriver.Chrome()
#
# try:
#     driver.get("https://hospitalmanager-beta.vercel.app/")
#     print(f"The page is: {driver.title}")
#
#     element = WebDriverWait(driver, 10).until(
#          EC.visibility_of_element_located((By.CSS_SELECTOR, "h1"))
#     )
#     print("These are the h1 element text on the page:")
#     print(element.text)
# finally:
#     driver.quit()

# driver = webdriver.Chrome()
#
# driver.get("https://learncompletefrontend.vercel.app/")
#
#
# element = driver.find_element(By.CLASS_NAME, "course_desc")
# print(element.text)
#
# driver.quit()

