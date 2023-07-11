import os
import re
import sys
import subprocess
import time
from io import StringIO

import pandas as pd
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.safari.options import Options

from selenium.webdriver.common.keys import Keys
from time import sleep

subprocess.check_call([sys.executable, '-m', 'pip', 'install',
                       'selenium'])

reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
print(installed_packages)

# pip install selenium

if webdriver.Firefox():
    usr = input("Please enter username: ")
    email = input("Please enter a valid email address: ")

    pwd = input('Please enter a password: ')
    pwd2 = input('Please re-type your password: ')

    while pwd2 != pwd:
        print("The passwords do not match. Please try again.")
        pwd = input("Please enter a password: ")
        pwd2 = input("Please re-type your password: ")

    #options = Options()
    #options.headless = True
    driver = webdriver.Firefox()
    driver.get("https://fallingstar-data.com/forcedphot/register/")
    print("Opened Atlas ForcedPhot Register Page")
    sleep(1)

    a = driver.find_element(By.ID, 'id_username')
    a.send_keys(usr)
    print("Username entered...")

    b = driver.find_element(By.ID, 'id_email')
    b.send_keys(email)
    print("Email entered...")

    c = driver.find_element(By.ID, 'id_password1')
    c.send_keys(pwd)
    print("Password entered...")

    d = driver.find_element(By.ID, 'id_password2')
    d.send_keys(pwd2)

    e = driver.find_element(By.XPATH, '//button[normalize-space()="Sign up"]')
    e.click()
    print("Done...")

    print("Please check your email address for further instructions.")

    sleep(10)
    driver.quit()

elif webdriver.Chrome():
    usr = input("Please enter username: ")
    email = input("Please enter a valid email address: ")

    pwd = input('Please enter a password: ')
    pwd2 = input('Please re-type your password: ')

    while pwd2 != pwd:
        print("The passwords do not match. Please try again.")
        pwd = input("Please enter a password: ")
        pwd2 = input("Please re-type your password: ")

    #options = Options()
    #options.headless = True
    driver = webdriver.Chrome()
    driver.get("https://fallingstar-data.com/forcedphot/register/")
    print("Opened Atlas ForcedPhot Register Page")
    sleep(1)

    a = driver.find_element(By.ID, 'id_username')
    a.send_keys(usr)
    print("Username entered...")

    b = driver.find_element(By.ID, 'id_email')
    b.send_keys(email)
    print("Email entered...")

    c = driver.find_element(By.ID, 'id_password1')
    c.send_keys(pwd)
    print("Password entered...")

    d = driver.find_element(By.ID, 'id_password2')
    d.send_keys(pwd2)

    e = driver.find_element(By.XPATH, '//button[normalize-space()="Sign up"]')
    e.click()
    print("Done...")

    print("Please check your email address for further instructions.")

    sleep(10)
    driver.quit()

elif webdriver.Safari():
    usr = input("Please enter username: ")
    email = input("Please enter a valid email address: ")

    pwd = input('Please enter a password: ')
    pwd2 = input('Please re-type your password: ')

    while pwd2 != pwd:
        print("The passwords do not match. Please try again.")
        pwd = input("Please enter a password: ")
        pwd2 = input("Please re-type your password: ")

    #options = Options
    #options.headless = True
    driver = webdriver.Safari()
    driver.get("https://fallingstar-data.com/forcedphot/register/")
    print("Opened Atlas ForcedPhot Register Page")
    sleep(1)

    a = driver.find_element(By.ID, 'id_username')
    a.send_keys(usr)
    print("Username entered...")

    b = driver.find_element(By.ID, 'id_email')
    b.send_keys(email)
    print("Email entered...")

    c = driver.find_element(By.ID, 'id_password1')
    c.send_keys(pwd)
    print("Password entered...")

    d = driver.find_element(By.ID, 'id_password2')
    d.send_keys(pwd2)

    e = driver.find_element(By.XPATH, '//button[normalize-space()="Sign up"]')
    e.click()
    print("Done...")

    print("Please check your email address for further instructions.")

    sleep(10)
    driver.quit()

USER = usr
PASS = pwd

RA = input("Please enter an RA in decimal format: ")
Dec = input("Please enter a Dec in decimal format: ")
mjd = input("Please enter a min MJD: ")

BASEURL = "https://fallingstar-data.com/forcedphot"
# BASEURL = "http://127.0.0.1:8000"

if os.environ.get("ATLASFORCED_SECRET_KEY"):
    token = os.environ.get("ATLASFORCED_SECRET_KEY")
    print("Using stored token")
else:
    data = {"username": USER, "password": PASS}

    resp = requests.post(url=f"{BASEURL}/api-token-auth/", data=data)

    if resp.status_code == 200:
        token = resp.json()["token"]
        print(f"Your token is {token}")
        print("Store this by running/adding to your .zshrc file:")
        print(f'export ATLASFORCED_SECRET_KEY="{token}"')
    else:
        print(f"ERROR {resp.status_code}")
        print(resp.text)
        sys.exit()

headers = {"Authorization": f"Token {token}", "Accept": "application/json"}

task_url = None  # mjd = 59310.64
while not task_url:
    with requests.Session() as s:
        # alternative to token auth
        # s.auth = ('USERNAME', 'PASSWORD')
        resp = s.post(
            f"{BASEURL}/queue/", headers=headers, data={"ra": RA, "dec": Dec, "mjd_min": mjd, "send_email": True}
        )

        if resp.status_code == 201:  # successfully queued
            task_url = resp.json()["url"]
            print(f"The task URL is {task_url}")
        elif resp.status_code == 429:  # throttled
            message = resp.json()["detail"]
            print(f"{resp.status_code} {message}")
            t_sec = re.findall(r"available in (\d+) seconds", message)
            t_min = re.findall(r"available in (\d+) minutes", message)
            if t_sec:
                waittime = int(t_sec[0])
            elif t_min:
                waittime = int(t_min[0]) * 60
            else:
                waittime = 10
            print(f"Waiting {waittime} seconds")
            time.sleep(waittime)
        else:
            print(f"ERROR {resp.status_code}")
            print(resp.text)
            sys.exit()

result_url = None
taskstarted_printed = False
while not result_url:
    with requests.Session() as s:
        resp = s.get(task_url, headers=headers)

        if resp.status_code == 200:  # HTTP OK
            if resp.json()["finishtimestamp"]:
                result_url = resp.json()["result_url"]
                print(f"Task is complete with results available at {result_url}")
            elif resp.json()["starttimestamp"]:
                if not taskstarted_printed:
                    print(f"Task is running (started at {resp.json()['starttimestamp']})")
                    taskstarted_printed = True
                time.sleep(2)
            else:
                print(f"Waiting for job to start (queued at {resp.json()['timestamp']})")
                time.sleep(4)
        else:
            print(f"ERROR {resp.status_code}")
            print(resp.text)
            sys.exit()

with requests.Session() as s:
    textdata = s.get(result_url, headers=headers).text

    # if we'll be making a lot of requests, keep the web queue from being
    # cluttered (and reduce server storage usage) by sending a delete operation
    # s.delete(task_url, headers=headers).json()

dfresult = pd.read_csv(StringIO(textdata.replace("###", "")), delim_whitespace=True)
print(dfresult)
