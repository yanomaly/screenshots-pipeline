import asyncio
import json
import os
import random
from pathlib import Path

from playwright.async_api import async_playwright, Locator, expect, TimeoutError as PlaywrightTimeoutError


class UIDocumentationScreenshots:

    def __init__(self, options: dict = None) -> None:
        options = options or {}
        self.browser = None
        self.context = None
        self.page = None
        self.output_dir = Path(options.get('outputDir', './screenshots'))
        self.base_url = options.get('baseUrl', '')
        self.auth_config = options.get('authConfig', {})
        self.cookies = options.get('cookies', [])


    async def initialize(self) -> None:
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False, slow_mo=3_000)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=2,
            is_mobile=False,
            has_touch=False,
        )
        self.cookies = self.fetch_auth_cookies()
        await self.context.add_cookies(self.cookies)
        self.page = await self.context.new_page()
        self.output_dir.mkdir(parents=True, exist_ok=True)


    async def authenticate(self) -> None:
        if not self.cookies:
            if not self.auth_config.get('loginUrl', ''):
                raise ValueError("Auth config should contain 'loginUrl'.")

            print('Authenticating...')
            await self.page.goto(self.base_url + self.auth_config.get('loginUrl', ''))

            await asyncio.sleep(random.random() * 3)
            await self.page.fill(self.auth_config.get('emailSelector', ''), self.auth_config.get('email', ''))
            await asyncio.sleep(random.random() * 3)
            await self.page.click(self.auth_config.get('submitSelector', ''))
            await asyncio.sleep(random.random() * 3)
            await self.page.fill(self.auth_config.get('passwordSelector', ''), self.auth_config.get('password', ''))
            await asyncio.sleep(random.random() * 3)
            await self.page.click(self.auth_config.get('submitSelector', ''))

            try:
                await self.page.wait_for_load_state('networkidle', timeout=15_000)
            except PlaywrightTimeoutError:
                print("Timeout error on waiting for load status. Continue chain execution.")

            await asyncio.sleep(10)
            await self.save_auth_cookies()


    async def save_auth_cookies(self) -> None:
        with open("cookies.json", "w") as f:
            f.write(json.dumps(await self.context.cookies()))


    def fetch_auth_cookies(self) -> list:
        if os.path.exists("cookies.json"):
            with open("cookies.json", "r") as f:
                try:
                    return json.loads(f.read())
                except json.decoder.JSONDecodeError:
                    return []
        else:
            return []


    # async def emulate_auth_human_click(self, element_selector: str) -> None:
    #     await asyncio.sleep(random.random() * 3)
    #
    #     element = self.page.locator(element_selector)
    #     await expect(element, "Locator has more or less than one element.").to_have_count(1)
    #     box = await element.bounding_box()
    #
    #     death_zone_x_pixels = 40
    #     death_zone_y_pixels = 10 #to avoid miss clicks caused by rounded borders, padding, etc
    #     await element.click(position={
    #         "x": death_zone_x_pixels + random.random() * (box["width"] - death_zone_x_pixels),
    #         "y": death_zone_y_pixels + random.random() * (box["height"] - death_zone_y_pixels)
    #     })


    async def find_element(self, selector: dict) -> Locator:
        if selector.get('type') == 'text':
            return await self.find_by_text(selector)
        elif selector.get('type') == 'locator':
            element = self.page.locator(selector.get('expression', ''))
            await expect(element, "Locator has more or less than one element.").to_have_count(1)
            return element
        elif selector.get('type') == 'complex':
            return await self.find_element_by_complex_selector(selector)
        else:
            raise ValueError('Invalid selector type.')


    async def find_by_text(self, text_selector: dict) -> Locator:
        text = text_selector.get('text', '')
        options = text_selector.get('options', {})
        match = options.get('match', 'exact')

        if match == 'exact':
            element = self.page.get_by_text(text, exact=True)
        elif match == 'partial':
            element = self.page.get_by_text(text)
        else:
            raise ValueError('Invalid text selector mode.')

        await expect(element, "Locator has more or less than one element. ").to_have_count(1)
        return element

    async def find_element_by_complex_selector(self, complex_selector: dict) -> Locator:
        text_selector = complex_selector.get('text_selector', {})
        locator_selector = complex_selector.get('locator_selector', {})

        find_by_locator = self.page.locator(locator_selector.get('expression', ''))

        text = text_selector.get('text', '')
        options = text_selector.get('options', {})
        match = options.get('match', 'exact')

        if match == 'exact':
            element = find_by_locator.get_by_text(text, exact=True)
        elif match == 'partial':
            element = find_by_locator.get_by_text(text)
        else:
            raise ValueError('Invalid text selector mode.')

        await expect(element, "Locator has more or less than one element.").to_have_count(1)
        return element


    async def take_element_screenshot(self, selector: dict, filename: str, options: dict = None) -> None:
        options = options or {}
        element = await self.find_element(selector)
        await element.wait_for(state='visible')

        padding = options.get('padding', 20)
        screenshot_path = self.output_dir / filename
        screenshot_options = {'path': str(screenshot_path)}

        box = await element.bounding_box()
        screenshot_options['clip'] = {
            'x': max(0, box['x'] - padding),
            'y': max(0, box['y'] - padding),
            'width': box['width'] + 2 * padding,
            'height': box['height'] + 2 * padding
        }

        await self.page.screenshot(**screenshot_options)
        print(f"Screenshot saved: {filename}.")


    async def take_full_page_screenshot(self, filename: str) -> None:
        screenshot_path = self.output_dir / filename
        await self.page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"Full page screenshot saved: {filename}.")


    async def navigate_and_actions(self, url: str, actions: dict = None) -> None:
        actions = actions or []
        if not url or not actions:
            raise ValueError("You should specify navigation URL and desired actions.")

        print(f"Navigating to: {url}.")
        await self.page.goto(self.base_url + url)

        try:
            await self.page.wait_for_load_state('networkidle', timeout=15_000)
        except PlaywrightTimeoutError:
            print("Timeout error on waiting for load status. Continue chain execution.")

        for action in actions:
            await self.execute_action(action)


    async def execute_action(self, action: dict) -> None:
        selector = action.get('selector', action.get('element'))
        action_type = action.get('type', '')

        print(f"Executing {action.get('type', '')}.")
        if action_type == 'click':
            el = await self.find_element(selector)
            await el.click(**action.get('kwargs', {}))

        elif action_type == 'db_click':
            el = await self.find_element(selector)
            await el.dblclick(**action.get('kwargs', {}))

        elif action_type == 'hover':
            el = await self.find_element(selector)
            await el.hover(**action.get('kwargs', {}))
            await self.page.mouse.down()

        elif action_type == 'fill':
            el = await self.find_element(selector)
            await el.fill(action.get('value', ''))

        elif action_type == 'check':
            el = await self.find_element(selector)
            await el.check()

        elif action_type == 'select_option':
            el = await self.find_element(selector)
            await el.select_option(action.get('value', ''))

        elif action_type == 'upload_file':
            el = await self.find_element(selector)
            await el.set_input_files(action.get('value', ''))

        elif action_type == 'focus':
            el = await self.find_element(selector)
            await el.focus()

        #TODO implement drag and drop & test files upload

        elif action_type == 'screenshot':
            if 'element' in action:
                await self.take_element_screenshot(action.get('element', {}), action.get('filename'), action.get('options', {}))
            else:
                await self.take_full_page_screenshot(action.get('filename', ''))

        try:
            await self.page.wait_for_load_state('networkidle', timeout=15_000)
        except PlaywrightTimeoutError:
            print("Timeout error on waiting for load status. Continue chain execution.")


    async def cleanup(self) -> None:
        # await self.save_auth_cookies()

        if self.browser:
            await self.browser.close()
