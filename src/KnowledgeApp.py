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
    error_text = StringProperty()
    pass


class Text2(Screen):
    error_text = StringProperty()
    pass


class Manager(Screen):
    def get_input(self, page: Any, type_info: str) -> Any:
        match type_info:
            case "radio":
                for child in page.ids.radio_group.children:
                    if hasattr(child, 'active') and child.active:
                        return child.value
            case "text":
                return page.ids.text_input.text
            case _:
                Logger.warning("Variable type_info could not be matched, is it missing in the provided data?")
        return None


class KnowledgeApp(App):
    """UI aspect of the knowledge base, accepts certain arguments which get passed by the DataProvider through a dictionary:
        "title": The title text
        "next_button": Text in the next button
        "previous_button": Text in the previous button
        "type_info", accepts: "text", "radio_buttons"
        "next_page", accepts: "starting_page", "radio_buttons", "text"
        "radio_text_i": The text for the i-th radio button, requires "next_page" to be "radio_buttons"

       There are some possible outputs:
        "output": The main output, this is either text input from the user, or "option_i" w.r.t. the radio buttons
    """
    title = StringProperty()
    next_button = StringProperty()
    previous_button = StringProperty()

    def build(self):
        self._provider = DataProvider()
        self._info = None
        self._first_variant_page = False
        return Manager()


    def switch_to_next_page(self):
        screen_manager = self.root.ids.screen_manager

        # Get info for next window
        info = self._provider.get_next_window()
        if info != self._info:
            Logger.debug(f"Received the following dictionary: {info}")
        self._info = info

        # Get page data for next page, implemented like this to allow switching between pages
        page_name = self._info["next_page"]
        if self._first_variant_page:
            self._first_variant_page = False
            page_name = "".join([page_name, "_2"])
        else:
            self._first_variant_page = True
            page_name = "".join([page_name, "_1"])
        page = screen_manager.get_screen(page_name)

        # Special case for starting_screen
        if screen_manager.current_screen.name == "starting_page":
            screen_manager.transition = SlideTransition(direction="left", duration=0.3)
            page = screen_manager.get_screen(page_name)
            self._switch_page(screen_manager, page)
            return

        # Get input and verify
        current_page = screen_manager.current_screen
        inputs = self.root.get_input(current_page, current_page.name.split("_")[0])
        correct_output = self._check_switch_allowed(inputs, current_page.name.split("_")[0], current_page)
        if correct_output == False:
            Logger.debug("Did not switch pages due to faulty output (ensure page to switch to and type_info is similar)")
            return
        info["output"] = inputs
        Logger.debug(f"Received following option: '{inputs}'")

        # Update provider class
        self._provider.update_data(self._info)

        # Switch screens
        screen_manager.transition = SlideTransition(direction="left", duration=0.3)
        self._switch_page(screen_manager, page)


    def switch_to_previous_page(self):
        screen_manager = self.root.ids.screen_manager

        # Get info for previous window
        info = self._provider.get_previous_window()
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
        self.previous_button = self._info["previous_button"]
        self.next_button = self._info["next_button"]
        page.radio_text_1 = self._info["radio_text_1"]
        page.radio_text_2 = self._info["radio_text_2"]

        # Switch to next page
        screen_manager.current = page.name


    def _check_switch_allowed(self, data: Any, type_info: str, page: Any):
        match type_info:
            case "text":
                if data == "" or data is None:
                    page.error_text = "Invalid input"
                    return False
            case "radio":
                pass
            case _:
                raise NotImplementedError(f"The type_info provided - {type_info} - is not implemented")
        return True


if __name__ == "__main__":
    Logger.setLevel(LOG_LEVELS["debug"])
    KnowledgeApp().run()
