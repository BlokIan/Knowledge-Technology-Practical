import kivy
kivy.require("2.3.0")
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty, NumericProperty
from backend import DataProvider
from kivy.uix.gridlayout import GridLayout

class Manager(Screen):
    pass

class StartingPage(Screen):
    pass

class SecondKnowledgeApp(App):
    def build(self):
        return Manager()

if __name__ == '__main__':
    SecondKnowledgeApp().run()
