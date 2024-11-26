import kivy
kivy.require("2.3.0")
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty, NumericProperty
from backend import DataProvider
from kivy.logger import Logger, LOG_LEVELS
from kivy.graphics import *

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
    pass


class KnowledgeApp(App):
    def build(self):
        self._provider = DataProvider()
        self._info = None
        return Test()

    def switch_to_next_page(self, page_name):
        self._info = self._provider.update_data(self._info)

        page = self.root.ids.screen_manager.get_screen(page_name)
        page.title = self._info["title"]
        page.status = self._info["status"]
        page.previous_button = self._info["previous_button"]
        page.next_button = self._info["next_button"]
        page.radio_text_1 = self._info["radio_text_1"]
        page.radio_text_2 = self._info["radio_text_2"]

        screen_manager = self.root.ids.screen_manager
        screen_manager.current = page_name
        

if __name__ == "__main__":
    KnowledgeApp().run()
