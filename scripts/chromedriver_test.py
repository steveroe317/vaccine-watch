#!python3

import time
from selenium import webdriver

from common import CHROMEDRIVER_PATH

# Optional argument, if not specified will search path.
driver = webdriver.Chrome(CHROMEDRIVER_PATH)
driver.get('http://www.google.com/')
time.sleep(5)  # Let the user actually see something!
search_box = driver.find_element_by_name('q')
search_box.send_keys('ChromeDriver')
search_box.submit()
time.sleep(5)  # Let the user actually see something!
driver.quit()
