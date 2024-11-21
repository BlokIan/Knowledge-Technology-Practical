import kivy
kivy.require("2.3.0")
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox


class Chat(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    

class KnowledgeApp(App):
    def build(self):
        return Chat()


if __name__ == "__main__":
    KnowledgeApp().run()
