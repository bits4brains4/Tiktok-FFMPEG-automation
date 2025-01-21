import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

class TikTokDownloader:
    def __init__(self):
        self.driver = None
        
    def initialize_browser(self):
        print("Setting up Chrome...")
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        # Add performance options
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Chrome started successfully")
            
            print("Loading website...")
            self.driver.get("https://snaptik.app/en1")
            time.sleep(1)  # Reduced initial wait
            print("Website loaded")
            
        except Exception as e:
            print(f"Error initializing Chrome: {str(e)}")
            raise

    def close_ads(self):
        """Try to close any visible ads"""
        print("Checking for ads...")
        try:
            # Look for close buttons in iframes
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                try:
                    self.driver.switch_to.frame(iframe)
                    close_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Close') or contains(text(), 'close')]")
                    for button in close_buttons:
                        try:
                            button.click()
                            time.sleep(0.2)  # Reduced wait after closing ad
                        except:
                            pass
                    self.driver.switch_to.default_content()
                except:
                    self.driver.switch_to.default_content()
                    continue
            
            # Look for close buttons in main frame
            close_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Close') or contains(text(), 'close')]")
            for button in close_buttons:
                try:
                    button.click()
                    time.sleep(0.2)  # Reduced wait after closing ad
                except:
                    pass
                    
        except Exception as e:
            print(f"Error handling ads: {str(e)}")
            self.driver.switch_to.default_content()
    
    def wait_and_find(self, by, value, description, timeout=5):  # Reduced timeout
        print(f"Looking for {description}...")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            print(f"Error finding {description}: {str(e)}")
            return None
    
    def wait_and_click(self, by, value, description, timeout=5):  # Reduced timeout
        element = self.wait_and_find(by, value, description, timeout)
        if element:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.2)  # Reduced scroll wait
                self.driver.execute_script("arguments[0].click();", element)
                print(f"Clicked {description}")
                return True
            except Exception as e:
                print(f"Error clicking {description}: {str(e)}")
        return False
            
    def process_link(self, link, max_retries=3):
        for attempt in range(max_retries):
            print(f"\nProcessing link: {link} (Attempt {attempt + 1}/{max_retries})")
            try:
                # Close any ads first
                self.close_ads()
                
                # Find the input field and type the link directly
                input_field = self.wait_and_find(By.CSS_SELECTOR, "input.link-input", "input field")
                if not input_field:
                    print("Input field not found, refreshing...")
                    self.driver.refresh()
                    time.sleep(1)  # Reduced refresh wait
                    continue
                    
                print("Entering link...")
                input_field.clear()
                input_field.send_keys(link)
                time.sleep(0.2)  # Reduced wait after typing
                
                # Click the green Download button using multiple possible selectors
                print("Attempting to click download button...")
                download_clicked = False
                for selector in [
                    "button.btn-download",  # Try class
                    "button[type='submit']",  # Try button type
                    "//button[contains(text(), 'Download')]",  # Try text content
                    ".download",  # Try simple class
                    "[data-download]"  # Try data attribute
                ]:
                    try:
                        by = By.CSS_SELECTOR if not selector.startswith('//') else By.XPATH
                        if self.wait_and_click(by, selector, "download button"):
                            download_clicked = True
                            break
                    except:
                        continue
                
                if not download_clicked:
                    print("Failed to click download button, refreshing...")
                    self.driver.refresh()
                    time.sleep(1)  # Reduced refresh wait
                    continue
                    
                time.sleep(1)  # Reduced wait after first download click
                
                # Close any new ads that might have appeared
                self.close_ads()
                
                # Wait for the video preview to load and click the blue Download button
                download_clicked = False
                if self.wait_and_click(By.CSS_SELECTOR, "a.button.download", "blue download button"):
                    download_clicked = True
                elif self.wait_and_click(By.CSS_SELECTOR, "a.button.download-file", "alternative download button"):
                    download_clicked = True
                
                if not download_clicked:
                    print("Failed to click final download button, refreshing...")
                    self.driver.refresh()
                    time.sleep(1)  # Reduced refresh wait
                    continue
                
                time.sleep(0.5)  # Reduced wait after final download
                
                # Go back to main page
                print("Returning to main page...")
                self.driver.get("https://snaptik.app/en1")
                time.sleep(0.5)  # Reduced wait after page load
                
                return True
                
            except Exception as e:
                print(f"Error processing link: {str(e)}")
                print("Refreshing page...")
                self.driver.get("https://snaptik.app/en1")
                time.sleep(1)  # Reduced refresh wait
                continue
                
        print(f"Failed to process link after {max_retries} attempts")
        return False
            
    def process_links(self, links):
        try:
            self.initialize_browser()
            
            for index, link in enumerate(links, 1):
                print(f"\n{'='*50}")
                print(f"Processing link {index} of {len(links)}")
                print(f"{'='*50}")
                success = self.process_link(link)
                if success:
                    print(f"Successfully processed: {link}")
                else:
                    print(f"Failed to process: {link}")
                    
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            
        finally:
            self.driver.quit()

def main():
    print("TikTok Video Downloader")
    print("----------------------")
    print("Enter your TikTok links (one per line)")
    print("Press Enter twice when done")
    
    links = []
    while True:
        link = input()
        if link == "":
            break
        if link.strip():
            links.append(link.strip())
    
    if not links:
        print("No links provided.")
        return
        
    print(f"\nFound {len(links)} links to process")
    
    downloader = TikTokDownloader()
    downloader.process_links(links)

if __name__ == "__main__":
    main()