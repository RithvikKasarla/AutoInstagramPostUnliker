from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time


class InstagramUnliker:
    # Configuration constants
    LOGIN_URL = "https://www.instagram.com/accounts/login/"
    HOME_URL = "https://www.instagram.com/"
    TIMEOUT = 15
    SCROLL_ATTEMPTS = 5
    
    # XPATH constants
    MORE_BUTTON_XPATH = '//span[text()="More"]'
    ACTIVITY_BUTTON_XPATH = '//span[text()="Your activity"]'
    SELECT_BUTTON_XPATH = '//span[text()="Select"]'
    POST_BUTTON_XPATH = '//div[@role="button" and @aria-label="Image of Post"]'
    UNLIKE_BUTTON_XPATH = '//span[text()="Unlike"] | //span[text()="Remove from likes"]'
    CONFIRM_UNLIKE_XPATH = '//button[.//div[text()="Unlike"]]'

    def __init__(self, chrome_binary, driver_path):
        self.chrome_binary = chrome_binary
        self.driver_path = driver_path
        self.driver = None
        self.start_time = None

    def __enter__(self):
        self._initialize_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()
            print("🚪 Driver closed successfully")
        if self.start_time:
            self._print_elapsed_time()

    def _initialize_driver(self):
        options = Options()
        options.binary_location = self.chrome_binary
        options.add_argument("--start-maximized")
        
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        print("🚀 Chrome driver initialized")

    def _print_elapsed_time(self):
        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)
        millis = int((elapsed - int(elapsed)) * 1000)
        print(f"⏱️ Total elapsed time: {mins:02d}:{secs:02d}.{millis:03d}")

    def manual_login(self):
        self.driver.get(self.LOGIN_URL)
        print("⏳ Please complete manual login within 30 seconds...")
        time.sleep(30)
        print("✅ Assuming login successful")

    def navigate_to_activity(self):
        self._safe_get(self.HOME_URL)
        self._click_element(self.MORE_BUTTON_XPATH, "More button")
        self._click_element(self.ACTIVITY_BUTTON_XPATH, "Activity button")
        print("✅ Successfully navigated to activity page")

    def run_unlike_cycle(self):
        self.start_time = time.time()
        while True:
            try:
                if not self._handle_select_button():
                    continue
                
                self._scroll_page()
                selected = self._select_posts()
                
                if selected:
                    self._process_unlike()
                else:
                    print("ℹ️ No posts found to unlike")
                
                time.sleep(20)
                
            except KeyboardInterrupt:
                print("\n🛑 User interrupted process")
                return
            except Exception as e:
                print(f"⚠️ Unexpected error: {str(e)}")
                self.navigate_to_activity()

    def _handle_select_button(self, max_retries=5):
        for attempt in range(max_retries):
            try:
                self._click_element(self.SELECT_BUTTON_XPATH, "Select button", timeout=5)
                return True
            except TimeoutException:
                print(f"🔄 Select button not found (attempt {attempt+1}/{max_retries})")
        
        print("🔁 Resetting to activity page...")
        self.navigate_to_activity()
        return False

    def _scroll_page(self):
        for i in range(self.SCROLL_ATTEMPTS):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"🔃 Scrolled page ({i+1}/{self.SCROLL_ATTEMPTS})")
            time.sleep(0.2)

    def _select_posts(self):
        posts = self.driver.find_elements(By.XPATH, self.POST_BUTTON_XPATH)
        print(f"📌 Found {len(posts)} posts to select")
        
        for idx, post in enumerate(posts, 1):
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});",
                    post
                )
                post.click()
                print(f"✅ Selected post {idx}/{len(posts)}")
                time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ Failed to select post {idx}: {str(e)}")
        
        return len(posts) > 0

    def _process_unlike(self):
        self._click_element(self.UNLIKE_BUTTON_XPATH, "Unlike button")
        self._confirm_unlike()
        print("✅ Successfully processed unlike action")

    def _confirm_unlike(self, max_retries=5):
        for attempt in range(max_retries):
            try:
                self._click_element(self.CONFIRM_UNLIKE_XPATH, "Confirm unlike", timeout=3)
                return
            except TimeoutException:
                print(f"🔄 Confirm dialog not found (attempt {attempt+1}/{max_retries})")
                time.sleep(0.5)
        print("⚠️ Failed to confirm unlike after multiple attempts")

    def _click_element(self, xpath, element_name, timeout=TIMEOUT):
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()
        print(f"✅ Clicked {element_name}")

    def _safe_get(self, url):
        try:
            self.driver.get(url)
        except WebDriverException as e:
            print(f"⚠️ Failed to navigate to {url}: {str(e)}")
            raise


def main():
    CHROME_BINARY = "/usr/sbin/chromium"
    CHROMEDRIVER_PATH = "/sbin/chromedriver"

    try:
        with InstagramUnliker(CHROME_BINARY, CHROMEDRIVER_PATH) as unliker:
            unliker.manual_login()
            unliker.navigate_to_activity()
            unliker.run_unlike_cycle()
    except Exception as e:
        print(f"❌ Critical error occurred: {str(e)}")
    finally:
        print("🏁 Program execution completed")


if __name__ == "__main__":
    main()