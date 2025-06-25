import os
import random
from typing import Optional

from playwright.async_api import Frame, FrameLocator, Locator, Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright, expect

from schemas.config import Config
from schemas.flow import Action, ActionType, Chain, ScreenshotAction
from schemas.selectors import (
    ComplexElementSelector,
    LocatorElementSelector,
    MatchMode,
    SelectorType,
    TextElementSelector,
)


class ChainExecutor:

    def __init__(self, config: Config, chain_name: str = "N/D") -> None:
        self.browser = None
        self.context = None
        self.page = None
        self.output_dir = config.base_output_dir
        self.base_url = config.base_url
        self.auth_config = config.auth_config
        self.running_chain = chain_name

        os.makedirs(self.output_dir, exist_ok=True)

    async def initialize(self, additional_context_params: dict = None) -> None:
        print(f"{self.running_chain} | Initializing browser.")

        context_params = {
            "viewport": {"width": 1920, "height": 1080},
            "device_scale_factor": 2,
            "is_mobile": False,
            "has_touch": False,
        }

        if additional_context_params:
            context_params.update(additional_context_params)

        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context(**context_params)
        self.page = await self.context.new_page()

    async def authenticate(self) -> None:
        print(f"{self.running_chain} | Authenticating.")

        if self.auth_config is None:
            raise ValueError("'auth_config' is required for authentication.")

        if os.path.exists(self.auth_config.storage_state_path):
            await self.initialize(
                {"storage_state": self.auth_config.storage_state_path}
            )
            await self._authenticate_with_cache()
        else:
            print(
                f"{self.running_chain} | Can't find auth.json. Authenticating without cache."
            )
            await self.initialize()
            await self._authenticate_with_cache()

    async def _authenticate_with_cache(self) -> None:
        await self.page.goto(self.base_url + "/organization")
        await self.page.wait_for_load_state()

        print(f"{self.running_chain} | Authenticating with cache.")
        try:
            await self.page.wait_for_url("**/organization")
        except PlaywrightTimeoutError:
            print(
                f"{self.running_chain} | Can't authenticate with existing cache. Overriding it."
            )
            await self._authenticate_with_credentials()

    async def _authenticate_with_credentials(self) -> None:
        print(f"{self.running_chain} | Authenticating with credentials.")

        await self.page.goto(self.base_url + self.auth_config.login_url)
        await self.page.wait_for_load_state()

        await self.page.mouse.move(*self.generate_random_2d_coordinates(0, 0, 800, 800))
        await self.page.mouse.down()

        await self.page.wait_for_timeout(self.generate_random_1d_coordinate(500, 2000))
        await self.page.fill(self.auth_config.email_selector, self.auth_config.email)
        await self.page.wait_for_timeout(self.generate_random_1d_coordinate(500, 2000))
        await self.page.click(self.auth_config.submit_selector)
        await self.page.wait_for_timeout(self.generate_random_1d_coordinate(500, 2000))
        await self.page.fill(
            self.auth_config.password_selector,
            self.auth_config.password,
        )
        await self.page.wait_for_timeout(self.generate_random_1d_coordinate(500, 2000))
        await self.page.click(self.auth_config.submit_selector)

        await self.page.wait_for_load_state()
        await self.page.wait_for_url("**/organization/**")

        await self.page.context.storage_state(path=self.auth_config.storage_state_path)

    @staticmethod
    def generate_random_1d_coordinate(offset: float, range: float) -> float:
        return offset + random.random() * range

    @staticmethod
    def generate_random_2d_coordinates(
        offset_x: float, offset_y: float, range_x: float, range_y: float
    ) -> tuple[float, float]:
        return ChainExecutor.generate_random_1d_coordinate(
            offset_x, range_x
        ), ChainExecutor.generate_random_1d_coordinate(offset_y, range_y)

    async def find_element(
        self,
        selector: TextElementSelector | LocatorElementSelector | ComplexElementSelector,
    ) -> Optional[Locator]:
        match selector.type:

            case SelectorType.text:
                element = await self._find_by_text(selector)

            case SelectorType.locator:
                element = self.page.locator(selector.expression)

            case SelectorType.complex:
                element = await self._find_element_by_complex_selector(selector)

            case _:
                raise ValueError("Invalid selector type.")

        return await self._verify_found_element(element)

    async def _find_by_text(
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

        return element

    async def _find_element_by_complex_selector(
        self, complex_selector: ComplexElementSelector
    ) -> Optional[Locator]:
        find_by_locator = self.page.locator(
            complex_selector.locator_selector.expression
        )
        return await self._find_by_text(complex_selector.text_selector, find_by_locator)

    @staticmethod
    async def _verify_found_element(element: Locator) -> Locator:
        try:
            await element.wait_for(state="visible", timeout=10_000)
            await expect(
                element, "Locator has more or less than one element."
            ).to_have_count(1)
            return element
        except PlaywrightTimeoutError:
            raise TimeoutError("Element not found or invisible.")

    async def process_chain(self, chain: Chain) -> None:
        self.running_chain = chain.name

        print(f"{self.running_chain} | Navigating to: {chain.url}.")
        await self.page.goto(self.base_url + chain.url)
        await self.page.wait_for_load_state()

        for action in chain.actions:
            try:
                await self.handle_action(action)
            except Exception as e:
                raise type(e)(str(e) + f"| Action note: {action.note}. |")

    async def handle_action(self, action: Action | ScreenshotAction) -> None:
        if action.type == ActionType.screenshot:
            if not isinstance(action, ScreenshotAction):
                raise TypeError(
                    "Action with 'type = screenshot' "
                    "must be instance of 'ScreenshotAction'"
                )

            action.action_kwargs["path"] = self.output_dir + action.filename

            if action.element_selector:
                element = await self.find_element(action.element_selector[0])

                box = await element.bounding_box()
                action.action_kwargs["clip"] = {
                    "x": max(0, box["x"] - action.padding),
                    "y": max(0, box["y"] - action.padding),
                    "width": box["width"] + 2 * action.padding,
                    "height": box["height"] + 2 * action.padding,
                }
            else:
                action.action_kwargs["full_page"] = True

            await self._execute_action(
                "screenshot",
                action.action_kwargs,
                self.page,
                new_page_handling_required=action.new_page_handling_required,
                new_page_handling_timeout=action.new_page_handling_timeout,
            )

        elif action.type in ActionType:
            if len(action.element_selector) == 1:
                el = await self.find_element(action.element_selector[0])
                await self._execute_action(
                    action.type,
                    action.action_kwargs,
                    el,
                    new_page_handling_required=action.new_page_handling_required,
                    new_page_handling_timeout=action.new_page_handling_timeout,
                )
            elif len(action.element_selector) == 2:
                el_from = await self.find_element(action.element_selector[0])
                el_to = await self.find_element(action.element_selector[-1])
                await self._execute_action(
                    action.type,
                    action.action_kwargs,
                    el_from,
                    el_to,
                    new_page_handling_required=action.new_page_handling_required,
                    new_page_handling_timeout=action.new_page_handling_timeout,
                )
            else:
                raise ValueError("Incorrect number of element selectors.")

        else:
            raise ValueError("Unknown action type.")

        await self.page.wait_for_load_state()

        if timeout := action.post_action_timeout:
            await self.page.wait_for_timeout(timeout * 1000)

    async def _execute_action(
        self,
        action: str,
        action_args: dict,
        element_to_call_action_on: Page | Frame | FrameLocator | Locator,
        element_to_pass_into_action: Page | Frame | FrameLocator | Locator = None,
        new_page_handling_required: bool = False,
        new_page_handling_timeout: float = 10,
    ) -> None:
        print(f"{self.running_chain} | Executing {action}.")

        method = getattr(element_to_call_action_on, action)

        if new_page_handling_required:
            try:
                async with self.context.expect_page(
                    timeout=(new_page_handling_timeout * 1000)
                ) as new_page_info:
                    if element_to_pass_into_action:
                        await method(element_to_pass_into_action, **action_args)
                    else:
                        await method(**action_args)

                print(f"{self.running_chain} | Switching to the new page.")
                self.page = await new_page_info.value
            except PlaywrightTimeoutError:
                raise TimeoutError("No new page was opened before timeout.")
        else:
            if element_to_pass_into_action:
                await method(element_to_pass_into_action, **action_args)
            else:
                await method(**action_args)

    async def cleanup(self) -> None:
        if self.browser:
            await self.browser.close()

        if self.running_chain:
            self.running_chain = "N/D"
