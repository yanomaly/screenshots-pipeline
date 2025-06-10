import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

class UIDocumentationScreenshots:

    def __init__(self, options: dict = None):
        options = options or {}
        self.browser = None
        self.context = None
        self.page = None
        self.output_dir = Path(options.get('outputDir', './screenshots'))
        self.base_url = options.get('baseUrl', '')
        self.auth_config = options.get('auth', {})


    async def initialize(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False, slow_mo=10000)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=2,
            is_mobile=False,
            has_touch=False
        )
        self.page = await self.context.new_page()
        self.output_dir.mkdir(parents=True, exist_ok=True)


    async def authenticate(self):
        ...


    async def find_element(self, selector: dict):

        if selector.get('type') == 'text':
            return await self.find_by_text(selector)
        elif selector.get('type') == 'locator':
            return self.page.locator(selector.get('expression', '')).first
        elif selector.get('type') == 'complex':
            return await self.find_element_by_complex_selector(selector)

        raise ValueError('Invalid selector type')


    async def find_by_text(self, text_selector: dict):
        text = text_selector.get('text', '')
        options = text_selector.get('options', {})

        match = options.get('match')
        if match == 'exact':
            return self.page.get_by_text(text, exact=True)
        elif match == 'partial':
            return self.page.get_by_text(text).first
        else:
            raise ValueError('Invalid text selector mode')


    async def find_element_by_complex_selector(self, complex_selector: dict):
        text_selector = complex_selector.get('text_selector', {})
        locator_selector = complex_selector.get('locator_selector', {})

        find_by_text = await self.find_by_text(text_selector)
        return find_by_text.locator(locator_selector.get('expression', '')).first


    async def take_element_screenshot(self, selector: dict, filename: str, options: dict = None):
        options = options or {}
        element = await self.find_element(selector)
        await element.wait_for(state='visible')

        padding = options.get('padding', 20)
        screenshot_path = self.output_dir / filename
        screenshot_options = {'path': str(screenshot_path)}

        if options.get('crop') == 'element':
            box = await element.bounding_box()
            screenshot_options['clip'] = {
                'x': max(0, box['x'] - padding),
                'y': max(0, box['y'] - padding),
                'width': box['width'] + 2 * padding,
                'height': box['height'] + 2 * padding
            }

        await self.page.screenshot(**screenshot_options)
        print(f"Screenshot saved: {filename}")


    async def take_full_page_screenshot(self, filename: str):
        screenshot_path = self.output_dir / filename
        await self.page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"Full page screenshot saved: {filename}")


    async def navigate_and_actions(self, url: str, actions: dict = None):
        actions = actions or []
        if not url or not actions:
            raise ValueError("You should specify navigation URL and desired actions")
        print(f"Navigating to: {url}")
        await self.page.goto(self.base_url + url)
        await self.page.wait_for_load_state('networkidle')

        for action in actions:
            await self.execute_action(action)


    async def execute_action(self, action: dict):
        selector = action.get('selector', action.get('element'))
        action_type = action.get('type', '')

        print(f"Executing {action['type']}")
        if action_type == 'click':
            el = await self.find_element(selector)
            await el.click()
            if 'waitFor' in action:
                await self.page.wait_for_selector(action['waitFor'])

        elif action_type == 'fill':
            el = await self.find_element(selector)
            await el.fill(action['value'])

        elif action_type == 'hover':
            el = await self.find_element(selector)
            await el.hover()

        elif action_type == 'screenshot':
            if 'element' in action:
                await self.take_element_screenshot(action.get('element', {}), action.get('filename'), action.get('options', {}))
            else:
                await self.take_full_page_screenshot(action.get('filename', ''))


    async def run_documentation_flow(self, flow):
        coroutines = [self.navigate_and_actions(step.get('url', ''), step.get('actions', [])) for step in flow]
        await asyncio.gather(*coroutines)


    async def cleanup(self):
        if self.browser:
            await self.browser.close()

config = {
    'outputDir': './documentation-screenshots',
}

documentation_flow = [
    {
        'name': 'Test exception button',
        'url': 'https://app.writer.com/login',
        'actions': [
            {
                'type': 'screenshot',
                'filename': 'test/login.png',
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'text',
                    'text': 'Sign in',
                    'options': {'match': 'exact'}
                },
                'filename': 'sign-in-button.png',
                'options': {'padding': 25, 'crop': 'element'}
            },
            {
                'type': 'click',
                'element': {
                    'type': 'text',
                    'text': 'Sign in',
                    'options': {'match': 'exact'}
                },
            },
            {
                'type': 'screenshot',
                'filename': 'test/login2.png'
            },
            {
                'type': 'screenshot',
                'element': {
                    'type': 'text',
                    'text': 'Email is',
                    'options': {'match': 'partial'}
                },
                'filename': 'exception.png',
                'options': {'padding': 25, 'crop': 'element'}
            },
        ]
    },
]

async def run_step(step):
    screenshotter = UIDocumentationScreenshots(config)
    try:
        await screenshotter.initialize()
        await screenshotter.navigate_and_actions(step['url'], step['actions'])
        print('\n✅ Documentation screenshots completed!')
    except Exception as e:
        print('❌ Error generating screenshots:', e)
    finally:
        await screenshotter.cleanup()

async def main():
    await asyncio.gather(*[run_step(step) for step in documentation_flow])


if __name__ == "__main__":
    asyncio.run(main())
