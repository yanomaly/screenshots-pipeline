import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, Locator, expect


class UIDocumentationScreenshots:

    def __init__(self, options: dict = None):
        options = options or {}
        self.browser = None
        self.context = None
        self.page = None
        self.output_dir = Path(options.get('outputDir', './screenshots'))
        self.base_url = options.get('baseUrl', '')
        self.auth_config = options.get('authConfig', {})


    async def initialize(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.firefox.launch(headless=False, slow_mo=1000)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=2,
            is_mobile=False,
            has_touch=False
        )
        self.page = await self.context.new_page()
        self.output_dir.mkdir(parents=True, exist_ok=True)


    async def authenticate(self) -> None:
        if not self.auth_config.get('loginUrl', ''):
            raise ValueError("Auth config should contain 'loginUrl'.")

        print('Authenticating...')
        await self.page.goto(self.auth_config.get('loginUrl', ''))

        if self.auth_config['type'] == 'form':
            await self.page.fill(self.auth_config.get('emailSelector', ''), self.auth_config.get('email', ''))
            await self.page.click(self.auth_config.get('submitSelector', ''))
            await self.page.fill(self.auth_config.get('passwordSelector', ''), self.auth_config.get('password', ''))
            await self.page.click(self.auth_config.get('submitSelector', ''))
            await self.page.wait_for_load_state('domcontentloaded')

    async def find_element(self, selector: dict) -> Locator:

        if selector.get('type') == 'text':
            return await self.find_by_text(selector)
        elif selector.get('type') == 'locator':
            element = self.page.locator(selector.get('expression', ''))
            await expect(element, "Locator has more or less than one element.").to_have_count(1)
            return element
        elif selector.get('type') == 'complex':
            return await self.find_element_by_complex_selector(selector)

        raise ValueError('Invalid selector type.')


    async def find_by_text(self, text_selector: dict) -> Locator:
        text = text_selector.get('text', '')
        options = text_selector.get('options', {})

        match = options.get('match')
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

        match = options.get('match')
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
        await element.wait_for(state='visible', timeout=10_000)

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

        await self.page.screenshot(**screenshot_options, timeout=10_000)
        print(f"Screenshot saved: {filename}.")


    async def take_full_page_screenshot(self, filename: str) -> None:
        screenshot_path = self.output_dir / filename
        await self.page.screenshot(path=str(screenshot_path), full_page=True, timeout=10_000)
        print(f"Full page screenshot saved: {filename}.")


    async def navigate_and_actions(self, url: str, actions: dict = None) -> None:
        actions = actions or []
        if not url or not actions:
            raise ValueError("You should specify navigation URL and desired actions.")
        print(f"Navigating to: {url}.")
        await self.page.goto(self.base_url + url)
        await self.page.wait_for_load_state('networkidle')

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
            await el.click(**action.get('kwargs', {}))

        elif action_type == 'hover':
            el = await self.find_element(selector)
            await el.hover(**action.get('kwargs', {}))

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

        #TODO implement drag and drop

        elif action_type == 'screenshot':
            if 'element' in action:
                await self.take_element_screenshot(action.get('element', {}), action.get('filename'), action.get('options', {}))
            else:
                await self.take_full_page_screenshot(action.get('filename', ''))


    async def run_documentation_flow(self, flow: dict) -> None:
        coroutines = [self.navigate_and_actions(step.get('url', ''), step.get('actions', [])) for step in flow]
        await asyncio.gather(*coroutines)


    async def cleanup(self) -> None:
        if self.browser:
            await self.browser.close()