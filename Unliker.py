from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time


def end_timer(start_time):
    end_time = time.time()
    elapsed = end_time - start_time
    mins, secs = divmod(int(elapsed), 60)
    millis = int((elapsed - int(elapsed)) * 1000)

    print(f"⏱️ Elapsed Time: {mins:02d}:{secs:02d}.{millis:03d}")
    print("🚪 Exiting...")
    
# --------------------
# Driver Setup
# --------------------
options = Options()
options.binary_location = "/usr/sbin/chromium"
options.add_argument("--start-maximized")

service = Service("/sbin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

# --------------------
# Step 1: Log in Manually
# --------------------
driver.get("https://www.instagram.com/accounts/login/")
print("⏳ Please log in manually within the next 20 seconds...")
time.sleep(30)

# --------------------
# Step 2: Go to Likes Activity Page
# -------------------- 

try:
    more_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//span[text()="More"]'))
    )
    more_button.click()
    print("✅ Clicked 'More'")

    time.sleep(1)

    # Click the "Your Activity" button
    activity_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//span[text()="Your activity"]'))
    )
    activity_button.click()
    print("✅ Clicked 'Your Activity'")

except Exception as e:
    print("❌ Failed to click 'More' or 'Your Activity':", e)
    driver.quit()
    exit()

time.sleep(1)

start_time = time.time()

while True: # Loop to unlike all posts
    # --------------------
    # ☑️ Step 3: Click the 'Select' Button
    # --------------------
    tries = 0
    while True:
        try:
            select_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Select"]'))
            )
            select_button.click()
            print("✅ Clicked 'Select' button.")
            break
        except TimeoutException:
            print("🔄 'Select' not found yet, retrying...")
            time.sleep(3)
        except WebDriverException as e:
            print("❌ WebDriver crashed or lost connection:", e)
            driver.quit()
            exit()
        except Exception as e:
            print("❌ Unexpected error:", e)
            driver.quit()
            exit()
        tries += 1
        if tries > 4:
            driver.get("https://www.instagram.com")
            time.sleep(1)
            try:
                # Click the "More" button
                more_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[text()="More"]'))
                )
                more_button.click()
                print("✅ Clicked 'More'")

                time.sleep(1)

                # Click the "Your Activity" button
                activity_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[text()="Your activity"]'))
                )
                activity_button.click()
                print("✅ Clicked 'Your Activity'")
                tries = 0
            except Exception as e:
                print("❌ Failed to click 'More' or 'Your Activity':", e)
                driver.quit()
                exit()
                        
    # --------------------
    # 🔄 Step 4: Scroll to Load More Posts
    # --------------------
    scrolls = 3 # Increase for more posts 
    for i in range(scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f"🔃 Scrolled ({i+1}/{scrolls})")
        time.sleep(0.2)

    # --------------------
    # 🖱️ Step 5: Select All Visible Liked Posts
    # --------------------
    try:
        post_buttons = driver.find_elements(By.XPATH, '//div[@role="button" and @aria-label="Image of Post"]')
        print(f"📌 Found {len(post_buttons)} posts to select...")

        for i, button in enumerate(post_buttons):
            try:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'})", button)
                time.sleep(0.2)
                button.click()
                print(f"✅ Selected post {i+1}")
            except Exception as e:
                end_timer(start_time)
                print(f"❌ Failed to select post {i+1}: {e}")
    except Exception as e:
        end_timer(start_time)
        print("⚠️ Error finding post buttons:", e)
        exit()

    # --------------------
    # ❌ Step 6: Click 'Unlike' or 'Remove from Likes'
    # --------------------
    try:
        unlike_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[text()="Unlike"] | //span[text()="Remove from likes"]'))
        )
        unlike_button.click()
        print("🗑️ Clicked 'Unlike' or 'Remove from likes' button.")
    except Exception as e:
        end_timer(start_time)
        print("⚠️ Could not find Unlike button (may need XPath tweak):", e)

    time.sleep(0.4)
    # --------------------
    # 👇 Step 7: Confirm 'Unlike' in the Modal
    # --------------------
    tries = 0
    while True:
        try:
            confirm_unlike = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[.//div[text()="Unlike"]]'))
            )
            confirm_unlike.click()
            print("✅ Confirmed 'Unlike' in modal.")
            break
        except Exception as e:
            # end_timer(start_time)
            print("⚠️ Could not confirm 'Unlike':", e)
        tries += 1
        if tries > 4:
            break # Exit loop if tries exceed 4

    # --------------------
    # ✅ Done
    # --------------------
    print("🎉 Finished unliking posts.")
    time.sleep(20)
