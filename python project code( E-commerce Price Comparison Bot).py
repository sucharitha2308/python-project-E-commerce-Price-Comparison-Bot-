from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Take product name input from user
product_name = input("Enter the product name to search: ")

# Setup Chrome driver
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass bot detection
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")  # Set user agent

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

print("\n***************************************************************************")
print(f"Searching prices for: {product_name}")
print("***************************************************************************\n")

# Initialize variables
flipkart_price = "Unavailable"
amazon_price = "Unavailable"
croma_price = "Unavailable"

# Flipkart
print("Searching on Flipkart...")
try:
    driver.get("https://www.flipkart.com")
    
    # Handle login popup
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'✕')]")))
        close_btn = driver.find_element(By.XPATH, "//button[contains(text(),'✕')]")
        close_btn.click()
        print(" ---> Login popup closed")
    except:
        print(" ---> No login popup detected")

    # Wait for search box and search
    try:
        search_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(product_name)
        search_box.send_keys(Keys.RETURN)
        print(" ---> Search submitted")
    except Exception as e:
        print(f" ---> Search failed: {str(e)}")
        raise e

    # Wait for results and get price
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div._4rR01T, a.s1Q9rs"))
        )
        
        # Get product name
        product_element = driver.find_element(By.CSS_SELECTOR, "div._4rR01T, a.s1Q9rs")
        print(f" ---> Product found: {product_element.text[:50]}...")
        
        # Get price
        price_element = driver.find_element(By.CSS_SELECTOR, "div._30jeq3._1_WHN1, div._30jeq3")
        flipkart_price = price_element.text
        print(f" ---> Price found: {flipkart_price}")
    except Exception as e:
        print(f" ---> Couldn't extract price: {str(e)}")
        # Try alternative method if first attempt fails
        try:
            price_element = driver.find_element(By.XPATH, "//div[contains(text(),'₹')]")
            flipkart_price = price_element.text
            print(f" ---> Price found (alternative method): {flipkart_price}")
        except:
            print(" ---> All price extraction methods failed")

except Exception as e:
    print(f"Flipkart error: {str(e)}")
time.sleep(2)


# Amazon (updated to include rupee symbol)
print("Searching on Amazon...")
try:
    driver.get("https://www.amazon.in")
    driver.implicitly_wait(10)

    search_box = driver.find_element(By.ID, "twotabsearchtextbox")
    search_box.send_keys(product_name)
    search_box.send_keys(Keys.RETURN)
    time.sleep(10)

    try:
        price_element = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole")
        rupee_symbol = driver.find_element(By.CSS_SELECTOR, "span.a-price-symbol").text
        amazon_price = f"{rupee_symbol}{price_element.text}"
        print(f" ---> Successfully retrieved from Amazon: {amazon_price}")
    except:
        try:
            price_element = driver.find_element(By.CSS_SELECTOR, "span.a-price[data-a-size='xl'] span.a-price-whole")
            rupee_symbol = driver.find_element(By.CSS_SELECTOR, "span.a-price-symbol").text
            amazon_price = f"{rupee_symbol}{price_element.text}"
            print(f" ---> Successfully retrieved from Amazon (sponsored): {amazon_price}")
        except Exception as e:
            print("Amazon - Couldn't find product/price element:", e)
except Exception as e:
    print("Amazon - General error:", e)
time.sleep(2)

# Croma 
print("Searching on Croma...")
try:
    driver.get("https://www.croma.com")
    driver.implicitly_wait(10)

    search_box = driver.find_element(By.ID, "searchV2")
    search_box.send_keys(product_name)
    search_box.send_keys(Keys.RETURN)
    time.sleep(10)

    product_croma = driver.find_element(By.CSS_SELECTOR, "h3.product-title.plp-prod-title").text
    price_croma = driver.find_element(By.CSS_SELECTOR, "span.amount.plp-srp-new-amount").text
    croma_price = price_croma
    print(f" ---> Successfully retrieved from Croma: {price_croma}")
except Exception as e:
    print("Croma - Error:", e)
time.sleep(2)

# Final Output
print("\n#------------------------------------------------------------------------#")
print(f"Price comparison for [{product_name}] (Prices in INR):\n")
print(f"Flipkart: {flipkart_price}")
print(f"Amazon:   {amazon_price}")
print(f"Croma:    {croma_price}")

driver.quit()