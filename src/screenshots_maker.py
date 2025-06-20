import os
import random
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Locator, expect, TimeoutError as PlaywrightTimeoutError, Page


class UIDocumentationScreenshots:

    def __init__(self, options: dict = None) -> None:
        options = options or {}
        self.browser = None
        self.context = None
        self.page = None
        self.output_dir = Path(options.get('outputDir', ''))
        self.base_url = options.get('baseUrl', '')
        self.auth_config = options.get('authConfig', {})


    async def initialize(self) -> None:
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)

        context_params = {
            'viewport': {'width': 1920, 'height': 1080},
            'device_scale_factor': 2,
            'is_mobile': False,
            'has_touch': False,
        }

        if os.path.exists('auth.json'):
            context_params['storage_state'] = 'auth.json'

            self.context = await self.browser.new_context(
               **context_params
            )
            self.page = await self.context.new_page()
            await self.authenticate_with_cache()
        else:
            print('Can\'t find auth.json. Authenticating without cache.')
            self.context = await self.browser.new_context(
               **context_params
            )
            self.page = await self.context.new_page()
            await self.authenticate()

        self.output_dir.mkdir(parents=True, exist_ok=True)


    async def authenticate_with_cache(self) -> None:
        await self.page.goto(self.base_url + '/organization')
        await self.page.wait_for_load_state()

        try:
            await self.page.wait_for_url('**/organization')
        except PlaywrightTimeoutError:
            print('Can\'t authenticate with existing cache. Overriding it')
            await self.authenticate()


    async def authenticate(self) -> None:
        if not self.auth_config.get('loginUrl', ''):
            raise ValueError('Auth config should contain \'loginUrl\'.')

        print('Authenticating...')

        await self.page.goto(self.base_url + self.auth_config.get('loginUrl', ''))
        await self.page.wait_for_load_state()

        await self.page.mouse.move(random.random() * 800, random.random() * 800)
        await self.page.mouse.down()

        await self.page.wait_for_timeout(random.random() * 2000 + 500)
        await self.page.fill(self.auth_config.get('emailSelector', ''), self.auth_config.get('email', ''))
        await self.page.wait_for_timeout(random.random() * 2000 + 500)
        await self.page.click(self.auth_config.get('submitSelector', ''))
        await self.page.wait_for_timeout(random.random() * 2000 + 500)
        await self.page.fill(self.auth_config.get('passwordSelector', ''), self.auth_config.get('password', ''))
        await self.page.wait_for_timeout(random.random() * 2000 + 500)
        await self.page.click(self.auth_config.get('submitSelector', ''))

        await self.page.wait_for_load_state()
        await self.page.wait_for_url('**/organization/**')

        await self.page.context.storage_state(path='auth.json')


    async def find_element(self, selector: dict) -> Optional[Locator]:
        if selector.get('type') == 'text':
            return await self.find_by_text(selector)
        elif selector.get('type') == 'locator':
            element = self.page.locator(selector.get('expression', ''))

            try:
                await element.wait_for(state='visible', timeout=10_000)
                await expect(element, 'Locator has more or less than one element. ').to_have_count(1)
                return element
            except PlaywrightTimeoutError:
                raise ValueError('Element not found or invisible.')

        elif selector.get('type') == 'complex':
            return await self.find_element_by_complex_selector(selector)
        else:
            raise ValueError('Invalid selector type.')


    async def find_by_text(self, text_selector: dict) -> Optional[Locator]:
        text = text_selector.get('text', '')
        options = text_selector.get('options', {})
        match = options.get('match', 'exact')

        if match == 'exact':
            element = self.page.get_by_text(text, exact=True)
        elif match == 'partial':
            element = self.page.get_by_text(text)
        else:
            raise ValueError('Invalid text selector mode.')

        try:
            await element.wait_for(state='visible', timeout=10_000)
            await expect(element, 'Locator has more or less than one element.').to_have_count(1)
            return element
        except PlaywrightTimeoutError:
            raise ValueError('Element not found or invisible.')


    async def find_element_by_complex_selector(self, complex_selector: dict) -> Optional[Locator]:
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

        try:
            await element.wait_for(state='visible', timeout=10_000)
            await expect(element, 'Locator has more or less than one element.').to_have_count(1)
            return element
        except PlaywrightTimeoutError:
            raise ValueError('Element not found or invisible.')


    async def take_element_screenshot(
        self,
        selector: dict,
        filename: str,
        options: dict = None,
        action_kwargs: dict = None,
    ) -> None:
        options = options or {}
        element = await self.find_element(selector)

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

        screenshot_options.update(action_kwargs)

        await self.page.screenshot(**screenshot_options)
        print(f'Screenshot saved: {filename}.')


    async def take_full_page_screenshot(self, filename: str, action_kwargs: dict = None) -> None:
        screenshot_path = self.output_dir / filename
        await self.page.screenshot(path=str(screenshot_path), full_page=True, **action_kwargs)
        print(f'Full page screenshot saved: {filename}.')


    async def navigate_and_actions(self, url: str, actions: dict = None, name: str = None) -> None:
        actions = actions or []
        if not url or not actions:
            raise ValueError('You should specify navigation URL and desired actions.')

        print(f'Navigating to: {url}.')
        await self.page.goto(self.base_url + url)
        await self.page.wait_for_load_state()

        for action in actions:
            await self.execute_action(action)


    async def execute_action(self, action: dict) -> None:
        selector = action.get('element', {})
        action_type = action.get('type', '')

        print(f'Executing {action_type}.')

        if action_type == 'click':
            el = await self.find_element(selector)

            if action.get('new_page_handling_required', False):
                try:
                    async with (self.context.expect_page(
                            timeout=(action.get('new_page_handling_timeout', 30)) * 1000)
                                as new_page_info):
                        await el.click(**action.get('action_kwargs', {}))

                    print('Switching to the new page.')
                    self.page = await new_page_info.value
                except PlaywrightTimeoutError:
                    raise ValueError('No new page was opened before timeout.')
            else:
                await el.click(**action.get('action_kwargs', {}))

        elif action_type == 'db_click':
            el = await self.find_element(selector)
            await el.dblclick(**action.get('action_kwargs', {}))

        elif action_type == 'hover':
            el = await self.find_element(selector)
            await el.hover(**action.get('action_kwargs', {}))
            await self.page.mouse.down()

        elif action_type == 'fill':
            el = await self.find_element(selector)
            await el.fill(**action.get('action_kwargs', {}))

        elif action_type == 'check':
            el = await self.find_element(selector)
            await el.check(**action.get('action_kwargs', {}))

        elif action_type == 'select_option':
            el = await self.find_element(selector)
            await el.select_option(**action.get('action_kwargs', {}))

        elif action_type == 'upload_file':
            el = await self.find_element(selector)
            await el.set_input_files(**action.get('action_kwargs', {}))

        elif action_type == 'focus':
            el = await self.find_element(selector)
            await el.focus(**action.get('action_kwargs', {}))

        elif action_type == 'drag_and_drop':
            el_from = await self.find_element(selector.get('from', {}))
            el_to = await self.find_element(selector.get('to', {}))
            await el_from.drag_to(el_to, **action.get('action_kwargs', {}))

        elif action_type == 'screenshot':
            if selector:
                await self.take_element_screenshot(
                    selector, action.get('filename', ''),
                    action.get('options', {}),
                    action.get('action_kwargs', {})
                )
            else:
                await self.take_full_page_screenshot(
                    action.get('filename', ''),
                    action.get('action_kwargs', {})
                )

        else:
            raise ValueError("Unknown action type.")

        await self.page.wait_for_load_state()

        if timeout := action.get('post_action_timeout'):
            await self.page.wait_for_timeout(timeout * 1000)


    async def cleanup(self) -> None:
        if self.browser:
            await self.browser.close()
