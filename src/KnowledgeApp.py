import kivy
kivy.require("2.3.0")
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty, NumericProperty
from backend import DataProvider
from kivy.logger import Logger, LOG_LEVELS
from kivy.graphics import *
from typing import Any

Logger.setLevel(LOG_LEVELS["debug"])


class StartingPage(Screen):
    pass


class FirstPage(Screen):
    title = StringProperty()
    status = StringProperty()
    previous_button = StringProperty()
    next_button = StringProperty()
    radio_text_1 = StringProperty()
    radio_text_2 = StringProperty()


class SecondPage(Screen):
    title = StringProperty()
    status = StringProperty()
    previous_button = StringProperty()
    next_button = StringProperty()
    radio_text_1 = StringProperty()
    radio_text_2 = StringProperty()


class Test(Screen):
    def get_selected_option(self, page: Any) -> Any:
        for child in page.ids.radio_group.children:
            if hasattr(child, 'active') and child.active:
                return child.value
        return None


class KnowledgeApp(App):
    def build(self):
        self._provider = DataProvider()
        self._info = None
        return Test()

    def switch_to_next_page(self):
        # Get info for next window
        self._info = self._provider.get_window()

        # Get page data for next page
        page = self.root.ids.screen_manager.get_screen(self._info["next_page"])
        
        # Get input from radio buttons
        selected_option = self.root.get_selected_option(page)
        print(selected_option)

        # Update page
        page.title = self._info["title"]
        page.status = self._info["status"]
        page.previous_button = self._info["previous_button"]
        page.next_button = self._info["next_button"]
        page.radio_text_1 = self._info["radio_text_1"]
        page.radio_text_2 = self._info["radio_text_2"]

        # Update provider class
        self._provider.update_data(self._info)

        # Switch to next page
        screen_manager = self.root.ids.screen_manager
        screen_manager.current = self._info["next_page"]


if __name__ == "__main__":
    KnowledgeApp().run()
