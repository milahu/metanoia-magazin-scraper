#!/usr/bin/env python3

r'''
{
  "email": "some.user@some.host.com",
  "password": "some_password"
}
'''
login_json_path = "login.json"

base_url = "https://www.metanoia-magazin.com"
login_url = f"{base_url}/account/login"
downloads_url = f"{base_url}/account/downloads"

downloads_dir = "downloads"

import os
import sys
import re
import sqlite3
import asyncio
import shutil
import datetime
import glob
import json

#import aiohttp
sys.path.insert(0, "aiohttp_chromium/src")
import aiohttp_chromium as aiohttp

# https://github.com/kaliiiiiiiiii/Selenium-Driverless/blob/master/src/selenium_driverless/scripts/switch_to.py
# https://github.com/kaliiiiiiiiii/Selenium-Driverless/blob/master/tests/html/test_relative_find_elem.py
# https://github.com/kaliiiiiiiiii/Selenium-Driverless/blob/master/tests/antibots/test_cloudfare.py
from selenium_driverless.types.by import By
from selenium_driverless.types.alert import Alert
from selenium_driverless.types.target import TargetInfo, Target
from selenium_driverless.types.target import NoSuchIframe
from selenium_driverless.types.webelement import WebElement, NoSuchElementException
from selenium_driverless.types import JSEvalException

from typing import Iterable, List
import urllib.parse
from urllib.parse import urlparse, urlunparse, parse_qs, parse_qsl, urlencode

from aiohttp_retry import RetryClient, ExponentialRetry



scraper_name = "metanoia-magazin-scraper"



def datetime_str():
    # https://stackoverflow.com/questions/2150739/iso-time-iso-8601-in-python#28147286
    return datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%S.%fZ")

datetime_str_regex = r"[0-9]{8}T[0-9]{6}\.[0-9]+Z"



# use tmpfs in RAM to avoid disk writes
# NOTE os.getuid only works on unix
tempdir = f"/run/user/{os.getuid()}"
tempdir_regex = re.escape(f"{tempdir}/{scraper_name}-") + datetime_str_regex
tempdir = tempdir + f"/{scraper_name}-{datetime_str()}"



with open(login_json_path) as f:
    login_data = json.load(f)



async def main():
    session_kwargs = dict(
        tempdir=tempdir,
        # _tempdir_regex=tempdir_regex,
    )
    async with aiohttp.ClientSession(**session_kwargs) as session:
        if 0:
            # FIXME RetryClient opens new tab for every retry
            retry_client = RetryClient(client_session=session)
            session = retry_client
        await main_inner(session)



async def main_inner(session):
    driver = None
    # done_torrents_id_set = set(map(lambda row: row[0], cur.fetchall()))
    # print(f"loaded {len(done_torrents_id_set)} done torrents")
    async def get_element(selector: str):
        nonlocal driver
        while True:
            # FIXME old version of selenium_driverless: target.find_elements(by=by, value=value, parent=parent)
            # elem_list = await driver.find_elements(By.CSS_SELECTOR, selector, timeout=10)
            elem_list = await driver.find_elements(By.CSS_SELECTOR, selector)
            if len(elem_list) > 0:
                return elem_list[0]
            await asyncio.sleep(1)
    async def get_elements(selector: str):
        nonlocal driver
        while True:
            # FIXME old version of selenium_driverless: target.find_elements(by=by, value=value, parent=parent)
            # elem_list = await driver.find_elements(By.CSS_SELECTOR, selector, timeout=10)
            elem_list = await driver.find_elements(By.CSS_SELECTOR, selector)
            if len(elem_list) > 0:
                return elem_list
            await asyncio.sleep(1)
    print("login ...")
    while True:
        async with session.get(login_url) as resp:
            print("status", resp.status)
            assert resp.status == 200
            html = await resp.text()
            # print(html); sys.exit()
            if 0:
                m = re.search(r'<form method="post" action="([^"]+)">', html)
                if not m:
                    print("error: not found login form in html:")
                    print(html)
            # example: "../takelogin.php"
            # TODO better
            print("waiting for login page to load")
            await asyncio.sleep(5)
            driver = resp._driver

            # accept cookies
            print("accepting cookies")
            # <span class="js-cookie-accept-all-button">
            #   <button type="submit" class="btn btn-primary">Alle Cookies akzeptieren</button>
            if 1:
                elem = await get_element("span.js-cookie-accept-all-button > button")
                await elem.click()

            # wait for modal: Newsletteranmeldung
            print("waiting for modal")
            # <a href="javascript:void(0)" class="iziModal-button iziModal-button-close" data-izimodal-close=""></a>
            if 1:
                elem = await get_element("a.iziModal-button-close")
                # close modal
                # TODO why 2 clicks
                for retry_idx in range(3):
                    print("closing modal... ", end="", flush=True)
                    try:
                        await elem.click()
                        print("done")
                    except TimeoutError:
                        print("timeout")
                        # Couldn't compute element location within 10 seconds
                        # modal was closed
                        if retry_idx > 0:
                            break
                    await asyncio.sleep(1)

            # enter username
            print("entering username")
            # <input type="email" class="form-control" id="loginMail" placeholder="E-Mail-Adresse" name="username" required="required">
            if 1:
                elem = await get_element("input#loginMail")
                await elem.write(login_data["email"])

            # enter password
            print("entering password")
            # <input type="password" class="form-control" id="loginPassword" placeholder="Passwort" name="password" required="required">
            if 1:
                elem = await get_element("input#loginPassword")
                await elem.write(login_data["password"])

            # click login
            print("submitting form")
            # <div class="login-submit">
            #   <button type="submit" class="btn btn-primary">Anmelden</button>
            if 1:
                elem = await get_element("div.login-submit > button[type=submit]")
                await elem.click()

            print("waiting for login done page to load")
            await asyncio.sleep(5)
            # StaleElementReferenceException
            # elem = await get_element("html")
            # html = elem.get_attribute("outerHTML")
            r'''
            html = await driver.execute_script('return document.querySelector("html").outerHTML')
            if not '<form method="post" action="../takelogin.php">' in html:
                break
            print("login failed -> retrying")
            '''
            # TODO check login status
            break # stop retry loop
        print("login done")

    print("opening downloads page")
    url = downloads_url
    href_list = []
    async with session.get(url) as resp:
        driver = resp._driver
        # original_window = driver.current_window_handle
        # driver.switch_to.window(original_window)
        print("status", resp.status)
        assert resp.status == 200
        # html = await resp.text()

        print("looping download links")
        # <p class="enno-downloads-link-rapper">
        #   <a class="enno-downloads-link"
        #     href="https://www.metanoia-magazin.com/enno/download?did=77cbb744e33e4ba9b86d01218d63423e&amp;oid=4072b8a57c3442228785beb4aa6380a1&amp;lid=067d7d8786a844438f032dc79fd139fa"
        #     target="_blank" rel="noopener nofollow"
        #   >Ausgabe 46</a>
        for elem in await get_elements("a.enno-downloads-link"):
            # print(f"elem {elem!r}")
            href = await elem.get_attribute("href")
            # print(f"href {href!r}")
            text = await elem.get_attribute("innerText")
            # print(f"text {text!r}")
            print(f"download link: {text!r} -> {href!r}")
            href_url = urllib.parse.urlparse(href)
            href_query = urllib.parse.parse_qs(href_url.query)
            href_id = href_query["did"][0] # download id
            href_dir = os.path.join(downloads_dir, href_id)
            existing_files = glob.glob(f"{href_dir}/*")
            if len(existing_files) >= 1:
                print(f"keeping downloads: {existing_files}")
                continue
            href_list.append(href)
            continue
            # print(f"downloading: {href}")
            # await elem.click()
            # print("TODO wait for download")
            # # TODO move downloaded file to href_dir
            # # /run/user/1000/metanoia-magazin-scraper-20251201T181226.893895Z/home/Downloads/59ac951e-b14a-4622-9e43-50978083ccd1
            # await asyncio.sleep(99999)

    for href in href_list:
        href_url = urllib.parse.urlparse(href)
        href_query = urllib.parse.parse_qs(href_url.query)
        href_id = href_query["did"][0] # download id
        href_dir = os.path.join(downloads_dir, href_id)
        os.makedirs(href_dir, exist_ok=True)
        print(f"downloading: {href}")
        async with session.get(href) as resp:
            driver = resp._driver
            print(f"waiting for download: path={resp._filepath!r}")
            await resp._wait_complete(timeout=9999)
            # assert resp._download_is_complete
            src_path = resp._filepath
            dst_path = f"{href_dir}/{resp._filename}"
            shutil.move(src_path, dst_path)
            print(f"done download: path={dst_path!r} size={os.path.getsize(dst_path)}")
            # await asyncio.sleep(99999)

    print("done")
    return

    await asyncio.sleep(99999)

asyncio.run(main())
