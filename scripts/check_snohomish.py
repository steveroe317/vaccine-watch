#!python3

import argparse
import logging
import optparse
import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from twilio.rest import Client as TwilioClient

SNOHOMISH_VACCINE_URL = 'https://snohomish-county-coronavirus-response-snoco-gis.hub.arcgis.com/pages/covid-19-vaccine'
ARLINGTON_LINK_TEXT = 'www.signupgenius.com/tabs/13577DF01A0CFEDC5AC5-vaccine3'
EXPECTED_SIGNUP_BANNER = '02/16/2021 - Arlington Additional(2) COVID-19 Vaccine Patient Sign Up'
EXPECTED_SIGNUP_STATUS = 'NO SLOTS AVAILABLE. SIGN UP IS FULL.'
SIGNUP_ENDED_MESSAGE = 'The sign up period for this event has ended'

POLL_WAIT_SECONDS = 5 * 60  # Wait between website checks
PAUSE_SECONDS = 5  # Wait between web page actions


def send_sms(sms_targets, message_body):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    sms_source = os.environ['TWILIO_ACCOUNT_PHONE']

    for sms_target in sms_targets:
        client = TwilioClient(account_sid, auth_token)
        message = client.messages.create(
            body=message_body, from_=sms_source, to=sms_target)
        print(message.sid)


def CheckSnohomish(chromedriver_path):
    driver = webdriver.Chrome(chromedriver_path)

    logging.info('Opening Snohomish county vaccine page')
    driver.get(SNOHOMISH_VACCINE_URL)
    time.sleep(PAUSE_SECONDS)  # Let the user actually see something!

    logging.info('Opening Arlington vaccine signup page')
    try:
        element = driver.find_element_by_link_text(ARLINGTON_LINK_TEXT)
    except NoSuchElementException:
        logging.error('Could not find Arlington vaccine signup link')
        return 1

    logging.info('Linking to {0}'.format(element.get_property('href')))
    element.click()
    time.sleep(PAUSE_SECONDS)

    try:
        element = driver.find_element_by_link_text("Got it!")
    except NoSuchElementException:
        logging.warning('Could not find "Got it!" button')
        driver.stop_client()
        driver.quit()
        return 0

    logging.info('Dimissing privacy notification')
    element.click()
    time.sleep(PAUSE_SECONDS)

    try:
        element = driver.find_element(
            By.XPATH, '//*[text()="{0}"]'.format(EXPECTED_SIGNUP_BANNER))
    except NoSuchElementException:
        logging.error('Signup banner has changed')
        return 1
    logging.info('Signup banner "{0}"'.format(element.text))

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
        logging.info('Signup over "{0}"'.format(element.text))
        driver.stop_client()
        driver.quit()
        return 0
    else:
        logging.error('New signup!!!')
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Check Snohomish County Arlington Vaccine web site for updates.')
    parser.add_argument('--chromedriver', required=True,
                        help='Path to chromedriver binary')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    sms_admin_target = os.environ['VACCINE_WATCH_ADMIN_PHONE']
    sms_alert_target = os.environ['VACCINE_WATCH_ALERT_PHONE']

    send_sms(
        [sms_admin_target],
        'Beginning Snohomish County Arlington site watch.')

    while CheckSnohomish(args.chromedriver) == 0:
        time.sleep(POLL_WAIT_SECONDS)

    send_sms(
        [sms_admin_target, sms_alert_target],
        'The Snohomish Arlington vaccine page changed % s, please check it.'
        % SNOHOMISH_VACCINE_URL)

    send_sms(
        [sms_admin_target],
        'Ending Snohomish County Arlington site watch.')


if __name__ == '__main__':
    main()
