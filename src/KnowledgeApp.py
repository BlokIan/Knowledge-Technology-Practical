import kivy
kivy.require("2.3.0")
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.properties import StringProperty, NumericProperty
from backend import DataProvider
from kivy.logger import Logger, LOG_LEVELS
from kivy.graphics import *
from typing import Any


class StartingPage(Screen):
    pass


class RadioButtons1(Screen):
    radio_text_1 = StringProperty()
    radio_text_2 = StringProperty()


class RadioButtons2(Screen):
    radio_text_1 = StringProperty()
    radio_text_2 = StringProperty()


class Text1(Screen):
    pass

class Text2(Screen):
    pass


class Manager(Screen):
    def get_input(self, page: Any, type_info: str) -> Any:
        match type_info:
            case "radio_buttons":
                for child in page.ids.radio_group.children:
                    if hasattr(child, 'active') and child.active:
                        return child.value
            case "text":
                pass
            case _:
                Logger.warning("Variable type_info could not be matched, is it missing in the provided data?")
        return None


class KnowledgeApp(App):
    status = StringProperty()
    title = StringProperty()
    next_button = StringProperty()
    previous_button = StringProperty()

    def build(self):
        self._provider = DataProvider()
        self._info = None
        return Manager()

    def switch_to_next_page(self):
        screen_manager = self.root.ids.screen_manager


        # Get info for next window
        info = self._provider.get_next_window()
        if info != self._info:
            Logger.debug(f"Received the following dictionary: {info}")
        self._info = info

        # Get page data for next page
        current_page = screen_manager.current_screen
        page = screen_manager.get_screen(self._info["next_page"])
        if page.ids == current_page.ids:
            Logger.warning("New page and old page are the same! Transitioning with animation will not work")

        # Get input from radio buttons
        selected_option = self.root.get_input(page, info["type_info"])
        info["output"] = selected_option
        Logger.debug(f"Received following option: '{selected_option}'")

        # Update provider class
        self._provider.update_data(self._info)

        screen_manager.transition = SlideTransition(direction="left", duration=0.3)
        self._switch_page(screen_manager, page)

    def switch_to_previous_page(self):
        screen_manager = self.root.ids.screen_manager

        # Get info for next window
        info = self._provider.get_next_window()
        if info != self._info:
            Logger.debug(f"Received the following dictionary: {info}")
        self._info = info

        # Get page data for next page
        current_page = screen_manager.current_screen
        page = screen_manager.get_screen(self._info["next_page"])
        if page.ids == current_page.ids:
            Logger.warning("New page and old page are the same! Transitioning with animation will not work")

        screen_manager.transition = SlideTransition(direction="right", duration=0.3)
        self._switch_page(screen_manager, page)

    def _switch_page(self, screen_manager: Any, page: Any):
        # Update page
        self.title = self._info["title"]
        self.status = self._info["status"]
        self.previous_button = self._info["previous_button"]
        self.next_button = self._info["next_button"]
        page.radio_text_1 = self._info["radio_text_1"]
        page.radio_text_2 = self._info["radio_text_2"]

        # Switch to next page
        screen_manager.current = self._info["next_page"]


if __name__ == "__main__":
    Logger.setLevel(LOG_LEVELS["debug"])
    KnowledgeApp().run()
