from playwright.sync_api import Page
from regression_tests.pages.base_page import BasePage


class MistralChatPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        self.model_selector_input = self.page.locator("#model-selector-0-button")
        self.chat_input = self.page.locator("#chat-input")
        self.send_prompt_button = self.page.locator("#send-message-button")
        self.prompt_response_field = self.page.locator("#response-content-container")

    def send_prompt(self, prompt: str):
        self.chat_input.fill(prompt)
        self.send_prompt_button.click()