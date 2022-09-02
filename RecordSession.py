#!/usr/bin/env python3

"""
Firefox session recording demo script.

Requirements:
- playwright
- lz4
- tldextract

Make sure to run "playwright install chromium" after installing the requirements!
"""

from playwright.async_api import async_playwright, Error
from pathlib import Path
from time import time
import lz4.block
import tldextract
import json
import asyncio

session_path = Path.cwd() / str(int(time()))
session_file_path = session_path / 'Session.txt'

# Default firefox session store file.
ff_session = Path.home() / '.mozilla' / 'firefox'
ff_session = list(ff_session.glob('*default*/sessionstore-backups/recovery.jsonlz4'))[0]
opened_urls = set()


async def save_page_helper(server_response):
    if server_response.ok:
        response_url = server_response.url
        response_url_fragments = response_url.split('/')[3:]
        website_domain_name = tldextract.extract(response_url).fqdn

        # The 'if' here is to prevent proceeding with blank / invalid fqdns.
        if website_domain_name:
            website_folder = session_path / website_domain_name
            website_folder.mkdir(exist_ok=True)
            for fragment in response_url_fragments[:-1]:
                website_folder /= fragment
                website_folder.mkdir(exist_ok=True)
            try:
                filename = response_url_fragments[-1]
            except IndexError:
                filename = ''
            if filename == '':
                filename = 'index.html'

            try:
                with open(website_folder / filename, "wb") as file_to_write:
                    contents = await server_response.body()
                    file_to_write.write(contents)
            except (OSError, Error):
                # Do not save resources whose URLs cause exceptions.
                pass


async def record_session(page_object):
    # Re-read session file contents
    session_file_bytes = ff_session.read_bytes()
    if session_file_bytes[:8] == b'mozLz40\0':
        session_file_bytes = lz4.block.decompress(session_file_bytes[8:])
    session_json = json.loads(session_file_bytes)

    # Re-read all the URLs open in browser, and save any new ones.
    for browser_window in session_json['windows']:
        for browser_tab in browser_window['tabs']:
            for browser_entry in browser_tab['entries']:
                # Everything after the '#' in a URL is used to specify what element the browser should focus on.
                # This could result in us saving the same page multiple times, so we strip that stuff out.
                url = browser_entry['url'].split('#')[0]
                # Ignore firefox built-in configuration pages
                if not url.startswith('about:'):
                    if url not in opened_urls:
                        opened_urls.add(url)
                        with open(session_path / 'Session.txt', 'a') as session_urls:
                            session_urls.write(url + '\n')
                        print('New URL:', url)
                        try:
                            await page_object.goto(url)
                            screenshot_name = tldextract.extract(page_object.url).fqdn + ' ' + str(time()) + '.png'
                            screenshot_path = session_path / screenshot_name
                            # Save screenshot of page.
                            await page_object.screenshot(path=str(screenshot_path), full_page=True)
                        except Error:
                            # If we ever navigate to a page that does not resolve, we don't want the script to crash.
                            # If we try to screenshot a page that causes issues, just continue.
                            pass


async def main():
    # Create the session folder & file.
    session_path.mkdir()
    session_file_path.touch()

    async with async_playwright() as ap:
        # Chromium tends to be a bit more stable.
        browser = await ap.chromium.launch()
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        # Run the 'save_page_helper' function whenever we receive a response from a server.
        page.on("response", save_page_helper)
        while True:
            try:
                await record_session(page)
                # Wait for the session file to be updated.
                await asyncio.sleep(30)
            except KeyboardInterrupt:
                break
            except FileNotFoundError:
                print('No running Firefox session detected!')
                break


if __name__ == '__main__':
    asyncio.run(main())
