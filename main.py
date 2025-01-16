from src.ui_app.KnowledgeApp import KnowledgeApp
from kivy.logger import Logger, LOG_LEVELS


if __name__ == "__main__":
    Logger.setLevel(LOG_LEVELS["info"])
    KnowledgeApp().run()