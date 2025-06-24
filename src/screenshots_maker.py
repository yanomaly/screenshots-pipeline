import os
import random
from pathlib import Path
from typing import Optional

from playwright.async_api import Frame, FrameLocator, Locator, Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright, expect

from schemas.config import Config
from schemas.flow import Action, Chain, ScreenshotAction
from schemas.selectors import (
    ComplexElementSelector,
    LocatorElementSelector,
    MatchMode,
    SelectorType,
    TextElementSelector,
)


class UIDocumentationScreenshots:

    def __init__(self, config: Config) -> None:
        self.browser = None
        self.context = None
        self.page = None
        self.output_dir = Path(config.base_output_dir)
        self.base_url = config.base_url
        self.auth_config = config.auth_config
        self.running_chain = ""

    async def initialize(self, with_authentication: bool = True) -> None:
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)

        context_params = {
            "viewport": {"width": 1920, "height": 1080},
            "device_scale_factor": 2,
            "is_mobile": False,
            "has_touch": False,
        }

        if os.path.exists(self.auth_config.storage_state_path):
            context_params["storage_state"] = self.auth_config.storage_state_path

            self.context = await self.browser.new_context(**context_params)
            self.page = await self.context.new_page()
            await self.authenticate_with_cache()
        else:
            print(
                f"{self.running_chain} | Can't find auth.json. Authenticating without cache."
            )
            self.context = await self.browser.new_context(**context_params)
            self.page = await self.context.new_page()
            await self.authenticate()

        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def authenticate_with_cache(self) -> None:
        await self.page.goto(self.base_url + "/organization")
        await self.page.wait_for_load_state()

        try:
            await self.page.wait_for_url("**/organization")
        except PlaywrightTimeoutError:
            print(
                f"{self.running_chain} | Can't authenticate with existing cache. Overriding it"
            )
            await self.authenticate()

    async def authenticate(self) -> None:
        print(f"{self.running_chain} | Authenticating...")

        await self.page.goto(self.base_url + self.auth_config.login_url)
        await self.page.wait_for_load_state()

        await self.page.mouse.move(random.random() * 800, random.random() * 800)
        await self.page.mouse.down()

        await self.page.wait_for_timeout(random.random() * 2000 + 500)
        await self.page.fill(self.auth_config.email_selector, self.auth_config.email)
        await self.page.wait_for_timeout(random.random() * 2000 + 500)
        await self.page.click(self.auth_config.submit_selector)
        await self.page.wait_for_timeout(random.random() * 2000 + 500)
        await self.page.fill(
            self.auth_config.password_selector,
            self.auth_config.password,
        )
        await self.page.wait_for_timeout(random.random() * 2000 + 500)
        await self.page.click(self.auth_config.submit_selector)

        await self.page.wait_for_load_state()
        await self.page.wait_for_url("**/organization/**")

        await self.page.context.storage_state(path=self.auth_config.storage_state_path)

    async def find_element(
        self,
        selector: TextElementSelector | LocatorElementSelector | ComplexElementSelector,
    ) -> Optional[Locator]:
        match selector.type:

            case SelectorType.text:
                return await self.find_by_text(selector)

            case SelectorType.locator:
                element = self.page.locator(selector.expression)

                try:
                    await element.wait_for(state="visible", timeout=10_000)
                    await expect(
                        element, "Locator has more or less than one element. "
                    ).to_have_count(1)
                    return element
                except PlaywrightTimeoutError:
                    raise TimeoutError("Element not found or invisible.")

            case SelectorType.complex:
                return await self.find_element_by_complex_selector(selector)

            case _:
                raise ValueError("Invalid selector type.")

    async def find_by_text(
        self,
        text_selector: TextElementSelector,
        searching_area: Page | Frame | FrameLocator | Locator = None,
    ) -> Optional[Locator]:
        if searching_area is None:
            searching_area = self.page

        match text_selector.match:

            case MatchMode.exact:
                element = searching_area.get_by_text(text_selector.text, exact=True)

            case MatchMode.partial:
                element = searching_area.get_by_text(text_selector.text)

            case _:
                raise ValueError("Invalid text selector mode.")

        try:
            await element.wait_for(state="visible", timeout=10_000)
            await expect(
                element, "Locator has more or less than one element."
            ).to_have_count(1)
            return element
        except PlaywrightTimeoutError:
            raise TimeoutError("Element not found or invisible.")

    async def find_element_by_complex_selector(
        self, complex_selector: ComplexElementSelector
    ) -> Optional[Locator]:
        find_by_locator = self.page.locator(
            complex_selector.locator_selector.expression
        )
        return await self.find_by_text(complex_selector.text_selector, find_by_locator)

    async def take_element_screenshot(
        self,
        screenshot_action: ScreenshotAction,
    ) -> None:
        element = await self.find_element(screenshot_action.element_selector[0])

        screenshot_path = self.output_dir / screenshot_action.filename
        screenshot_options = {"path": str(screenshot_path)}

        box = await element.bounding_box()
        screenshot_options["clip"] = {
            "x": max(0, box["x"] - screenshot_action.padding),
            "y": max(0, box["y"] - screenshot_action.padding),
            "width": box["width"] + 2 * screenshot_action.padding,
            "height": box["height"] + 2 * screenshot_action.padding,
        }

        screenshot_options.update(screenshot_action.action_kwargs)

        await self.page.screenshot(**screenshot_options)
        print(f"{self.running_chain} | Screenshot saved: {screenshot_path}.")

    async def take_full_page_screenshot(
        self, screenshot_action: ScreenshotAction
    ) -> None:
        screenshot_path = self.output_dir / screenshot_action.filename
        await self.page.screenshot(
            path=str(screenshot_path),
            full_page=True,
            **screenshot_action.action_kwargs,
        )
        print(
            f"{self.running_chain} | Full page screenshot was saved: {screenshot_path}."
        )

    async def process_chain(self, chain: Chain) -> None:
        self.running_chain = chain.name

        print(f"{self.running_chain} | Initializing environment.")
        await self.initialize()

        print(f"{self.running_chain} | Navigating to: {chain.url}.")
        await self.page.goto(self.base_url + chain.url)
        await self.page.wait_for_load_state()

        for action in chain.actions:
            try:
                await self.execute_action(action)
            except Exception as e:
                raise type(e)(str(e) + f"| Action note: {action.note}. |")

    async def execute_action(self, action: Action | ScreenshotAction) -> None:
        print(f"{self.running_chain} | Executing {action.type}.")

        match action.type:

            case "click":
                el = await self.find_element(action.element_selector[0])

                if action.new_page_handling_required:
                    try:
                        async with self.context.expect_page(
                            timeout=(action.new_page_handling_timeout * 1000)
                        ) as new_page_info:
                            await el.click(**action.action_kwargs)

                        print(f"{self.running_chain} | Switching to the new page.")
                        self.page = await new_page_info.value
                    except PlaywrightTimeoutError:
                        raise TimeoutError("No new page was opened before timeout.")
                else:
                    await el.click(**action.action_kwargs)

            case "db_click":
                el = await self.find_element(action.element_selector[0])
                await el.dblclick(**action.action_kwargs)

            case "hover":
                el = await self.find_element(action.element_selector[0])
                await el.hover(**action.action_kwargs)
                await self.page.mouse.down()

            case "fill":
                el = await self.find_element(action.element_selector[0])
                await el.fill(**action.action_kwargs)

            case "check":
                el = await self.find_element(action.element_selector[0])
                await el.check(**action.action_kwargs)

            case "select_option":
                el = await self.find_element(action.element_selector[0])
                await el.select_option(**action.action_kwargs)

            case "upload_file":
                el = await self.find_element(action.element_selector[0])
                await el.set_input_files(**action.action_kwargs)

            case "focus":
                el = await self.find_element(action.element_selector[0])
                await el.focus(**action.action_kwargs)

            case "drag_and_drop":
                el_from = await self.find_element(action.element_selector[0])
                el_to = await self.find_element(action.element_selector[-1])
                await el_from.drag_to(el_to, **action.action_kwargs)

            case "screenshot":
                if not isinstance(action, ScreenshotAction):
                    raise TypeError("Action with 'type = screenshot' "
                                    "must be instance of 'ScreenshotAction'")

                if action.element_selector:
                    await self.take_element_screenshot(action)
                else:
                    await self.take_full_page_screenshot(action)

            case _:
                raise ValueError("Unknown action type.")

        await self.page.wait_for_load_state()

        if timeout := action.post_action_timeout:
            await self.page.wait_for_timeout(timeout * 1000)

    async def cleanup(self) -> None:
        if self.browser:
            await self.browser.close()

        if self.running_chain:
            self.running_chain = ""
