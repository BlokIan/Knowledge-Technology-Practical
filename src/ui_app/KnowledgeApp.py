import kivy
kivy.require("2.3.0")
from kivy.metrics import dp
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.graphics import Color, Line
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.properties import StringProperty, NumericProperty, ListProperty
from .backend import DataProvider
from kivy.logger import Logger, LOG_LEVELS
from kivy.graphics import *
from typing import Any


class StartingPage(Screen):
    pass


class AdvicePage(Screen):
    pass


class RadioButtons1(Screen):
    radio_text_1 = StringProperty()
    radio_text_2 = StringProperty()
    options = ["Option 1", "Option 2", "Option 3", "Option 4"]

    def on_options(self):
        layout = self.ids.radio_group
        layout.clear_widgets()

        for i, option in enumerate(self.options):
            # Container for each label and checkbox pair
            container = GridLayout(cols=2, size_hint_y=None, height=50)
   
            # Multiline Label
            label = Label(
                text=option,
                text_size=(dp(200), None),  # Adjust text wrapping width
                halign="left",
                valign="middle",
                size_hint=(None, None),
                size=(dp(200), dp(50)),
                color=(0,0,0,1)
            )
            label.bind(size=lambda lbl, _: lbl.text_size)  # Dynamically adjust text_size
            container.add_widget(label)

            # CheckBox
            checkbox = CheckBox(
                group="answer_2",
                active=True if i == 0 else False
            )
            checkbox.value = option
            container.add_widget(checkbox)

            # Add container to layout
            layout.add_widget(container)

        # Ensure dynamic height of the GridLayout
        layout.height = layout.minimum_height


class RadioButtons2(Screen):
    radio_text_1 = StringProperty()
    radio_text_2 = StringProperty()
    options = ["Option 1", "Option 2", "Option 3", "Option 4"]

    def on_options(self):
        layout = self.ids.radio_group
        layout.clear_widgets()

        for i, option in enumerate(self.options):
            # Container for each label and checkbox pair
            container = GridLayout(cols=2, size_hint_y=None, height=50)

            # Multiline Label
            label = Label(
                text=option,
                text_size=(dp(200), None),  # Adjust text wrapping width
                halign="left",
                valign="middle",
                size_hint=(None, None),
                size=(dp(200), dp(50)),
                color=(0,0,0,1)
            )
            label.bind(size=lambda lbl, _: lbl.text_size)  # Dynamically adjust text_size
            container.add_widget(label)

            # CheckBox
            checkbox = CheckBox(
                group="answer_2",
                active=True if i == 0 else False
            )
            checkbox.value = option
            container.add_widget(checkbox)

            # Add container to layout
            layout.add_widget(container)

        # Ensure dynamic height of the GridLayout
        layout.height = layout.minimum_height


class Text1(Screen):
    error_text = StringProperty()
    pass


class Text2(Screen):
    error_text = StringProperty()
    pass


class YesNo1(Screen):
    yes_pressed = None
    error_text = StringProperty()

    def pressed_yes(self):
        self.yes_pressed = True

    def pressed_no(self):
        self.yes_pressed = False


class YesNo2(Screen):
    yes_pressed = None
    error_text = StringProperty()

    def pressed_yes(self):
        self.yes_pressed = True

    def pressed_no(self):
        self.yes_pressed = False


class Manager(Screen):
    def get_input(self, page: Any, type_info: str) -> Any:
        match type_info:
            case "radio":
                for child in page.ids.radio_group.children:
                    for child_2 in child.children:
                        if isinstance(child_2, CheckBox) and child_2.active:
                            return getattr(child_2, 'value', None)
            case "text":
                return page.ids.text_input.text
            case "yesno":
                return page.yes_pressed
            case "starting":
                pass
            case "advice":
                pass
            case _:
                Logger.warning("Variable type_info could not be matched, is it incorrect in the provided data?")
        return None

    def reset_page(self, page: Any, type_info: str) -> None:
        match type_info:
            case "radio":
                pass
            case "text":
                page.error_text = ""
                page.ids.text_input.text = ""
            case "yesno":
                page.error_text = ""
                page.yes_pressed = None
            case "starting":
                pass
            

class KnowledgeApp(App):
    """UI aspect of the knowledge base, accepts certain arguments which get passed by the DataProvider through a dictionary:
        "title": The title text
        "next_button": Text in the next button
        "next_page", accepts: "starting_page", "radio_buttons", "text", "yesno"
        "validate_function": A function which can be used to check the given output
        "radio_texts", list: A list of the different text options
        "radio_ammount", int: The ammount of radio button options on the page

       There are some possible outputs:
        "output": The main output, this is either text input from the user, or "option_i" w.r.t. the radio buttons
    """
    title = StringProperty()
    next_button = StringProperty()
    advice = StringProperty()


    def build(self):
        self._provider = DataProvider()
        self._info = {}
        self._first_variant_page = False
        return Manager()


    def switch_to_next_page(self):
        screen_manager = self.root.ids.screen_manager

        # Get input and verify
        current_page = screen_manager.current_screen
        inputs = self.root.get_input(current_page, current_page.name.split("_")[0])
        correct_output = self._check_switch_allowed(inputs, current_page.name.split("_")[0], current_page)
        if correct_output == False:
            Logger.debug(f"Did not switch pages due to faulty output: {inputs}")
            return
        self.root.reset_page(current_page, current_page.name.split("_")[0])
        self._info["output"] = inputs
        Logger.debug(f"Received following option from user: '{inputs}'")

        # Update provider class
        if current_page.name != "starting_page" and current_page.name != "advice_page":
            self._provider.update_data(self._info)

        # Get info for next window
        info = self._provider.get_next_window()
        if info != self._info:
            Logger.debug(f"Received the following dictionary: {info}")
        self._info = info

        # Special case for advice_screen
        if self._info["next_page"] == "advice_page":
            if current_page.name == "advice_page":
                super().stop()
            screen_manager.transition = SlideTransition(direction="left", duration=0.3)
            page = screen_manager.get_screen("advice_page")
            self.advice = self._info["advice"]
            self._switch_page(screen_manager, page)
            return

        # Get page data for next page, implemented like this to allow switching between pages
        page_name = self._info["next_page"]
        if self._first_variant_page:
            self._first_variant_page = not self._first_variant_page
            page_name = "".join([page_name, "_2"])
        else:
            self._first_variant_page = not self._first_variant_page
            page_name = "".join([page_name, "_1"])
        page = screen_manager.get_screen(page_name)

        # Special case for starting_screen
        if screen_manager.current_screen.name == "starting_page":
            screen_manager.transition = SlideTransition(direction="left", duration=0.3)
            page = screen_manager.get_screen(page_name)
            self._switch_page(screen_manager, page)
            return

        # Switch screens, first try updating 
        try:
            page.options = self._info["radio_texts"]
            page.rows = self._info["radio_ammount"]
            page.on_options()
        except KeyError:
            pass

        screen_manager.transition = SlideTransition(direction="left", duration=0.3)
        self._switch_page(screen_manager, page)


    def _switch_page(self, screen_manager: Any, page: Any):
        # Update page
        self.title = self._info["title"]
        # self.previous_button = self._info["previous_button"]
        self.next_button = self._info["next_button"]

        # Switch to next page
        screen_manager.current = page.name


    def _check_switch_allowed(self, data: Any, type_info: str, page: Any) -> bool:
        """Check whether you can switch to the next page w.r.t. the input given by the user

        Args:
            data (Any): The data / input to check
            type_info (str): What type of data was expected
            page (Any): The current page being displayed

        Raises:
            NotImplementedError: _description_

        Returns:
            _type_: _description_
        """        
        match type_info:
            case "text":
                if data == "" or data is None or not self._info["validate_function"](data):
                    page.error_text = "Invalid input"
                    return False
            case "radio":
                if data not in page.options:
                    return False
            case "yesno":
                if page.yes_pressed is None:
                    page.error_text = "Please press a button"
                    return False
            case "starting":
                pass
            case "advice":
                pass
            case _:
                raise NotImplementedError(f"The type_info provided - {type_info} - is not implemented")
        return True


if __name__ == "__main__":
    Logger.setLevel(LOG_LEVELS["debug"])
    KnowledgeApp().run()
