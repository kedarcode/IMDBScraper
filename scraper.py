from selenium import webdriver
from selenium_stealth import stealth
import os
from dotenv import load_dotenv
import traceback
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
load_dotenv()


class CreateDriver:
    def __new__(self, visibility: bool = True, niche: str = 'default' ,download='Download',userdata:bool=False):
        try:
            niche = str(niche).replace(' ', '_')
            folder = f'userdata/{niche}_userdata'
            if not os.path.exists(folder):
                os.makedirs(folder)
            PATH = os.path.abspath('Driver/chromedriver.exe')
            options = webdriver.ChromeOptions()
            options.add_argument("start-maximized")
            prefs = {"download.default_directory": os.path.abspath(download)}
            options.add_experimental_option("prefs", prefs)
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/90.0.4430.212 Safari/537.36")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-blink-features=AutomationControlled')
            if userdata:
                options.add_argument("--user-data-dir=" + os.path.abspath(folder))

            if not visibility: options.add_argument('--headless')
            options.add_experimental_option("detach", True)
            driver = webdriver.Chrome(options=options)
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win64",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    )

            return driver
        except Exception as e:
            traceback.print_exc()

            print(e)



