#!python3

import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from common import CHROMEDRIVER_PATH

SNOHOMISH_VACCINE_URL = 'https://snohomish-county-coronavirus-response-snoco-gis.hub.arcgis.com/pages/covid-19-vaccine'
ARLINGTON_LINK_TEXT = 'www.signupgenius.com/tabs/13577DF01A0CFEDC5AC5-vaccine3'
EXPECTED_SIGNUP_TITLE = '02/16/2021 - Arlington Additional(2) COVID-19 Vaccine Patient Sign Up'
EXPECTED_SIGNUP_STATUS = 'NO SLOTS AVAILABLE. SIGN UP IS FULL.'
SIGNUP_ENDED_MESSAGE = 'The sign up period for this event has ended'

POLL_WAIT_SECONDS = 5 * 60  # Wait between website checks
PAUSE_SECONDS = 5  # Wait between web page actions


def CheckSnohomish():
    driver = webdriver.Chrome(CHROMEDRIVER_PATH)

    print('INFO: OPENING SNOHOMISH COUNTY VACCINE PAGE')
    driver.get(SNOHOMISH_VACCINE_URL)
    time.sleep(PAUSE_SECONDS)  # Let the user actually see something!

    print('INFO: OPENING ARLINGTON VACCINE SIGNUP PAGE')
    try:
        element = driver.find_element_by_link_text(ARLINGTON_LINK_TEXT)
    except NoSuchElementException:
        print('ERROR: COULD NOT FIND ARLINGTON VACCINE SIGNUP LINK')
        return 1

    print('INFO: Linking to {0}'.format(element.get_property('href')))
    element.click()
    time.sleep(PAUSE_SECONDS)

    try:
        element = driver.find_element_by_link_text("Got it!")
    except NoSuchElementException:
        print('ERROR: COULD NOT FIND "Got it!" button')
        driver.quit()
        return 1

    print('INFO: Dimissing privacy notification')
    element.click()
    time.sleep(PAUSE_SECONDS)

    try:
        element = driver.find_element(
            By.XPATH, '//*[text()="{0}"]'.format(EXPECTED_SIGNUP_TITLE))
    except NoSuchElementException:
        print('INFO: SIGNUP HAS CHANGED')
        return 1

    print('INFO: SIGNUP TEXT "{0}"'.format(element.text))

    found_signup_status = False
    found_signup_ended = False
    try:
        element = driver.find_element(
            By.XPATH, '//*[text()="{0}"]'.format(EXPECTED_SIGNUP_STATUS))
        found_signup_status = True
    except NoSuchElementException:
        pass
    try:
        element = driver.find_element(
            By.XPATH, '//*[contains(text(),"{0}")]'.format(SIGNUP_ENDED_MESSAGE))
        found_signup_ended = True
    except NoSuchElementException:
        pass

    if found_signup_status or found_signup_ended:
        print('INFO: SIGNUP OVER "{0}"'.format(element.text))
        driver.stop_client()
        driver.quit()
        return 0
    else:
        print('INFO: NEW SIGNUP')
        return 1


def main():
    while CheckSnohomish() == 0:
        time.sleep(POLL_WAIT_SECONDS)


if __name__ == '__main__':
    main()
