import kivy
kivy.require("2.3.0")
from kivy.app import App
from kivy.uix.label import Label

class KnowledgeApp(App):
    def build(self):
        return Label(text ="Hello World !")
