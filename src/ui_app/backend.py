from src.kb.kb_class import KnowledgeBase
from kivy.logger import Logger, LOG_LEVELS

import os
KB_FILEPATH = os.path.join(os.getcwd(), "src", "kb", "KnowledgeBase.json")


class DataProvider():
    def __init__(self):
        self._kb = KnowledgeBase(filename=KB_FILEPATH)
    
    
    def update_data(self, information: dict) -> None:
        if not isinstance(information, dict):
            raise TypeError(f"Expected dict, received {type(information)}")
        match information["next_page"]:
            case "yesno":
                information["output"] = "yes" if information["output"] else "no"
            case _:
                pass
        Logger.debug(f"Returned the following output to kb: {information["output"]}")
        self._kb.answer(information["output"])


    def get_next_window(self) -> dict:
        try:
            result = self._kb.question_or_advice()
            q_or_a, item, answer_type = result
        except TypeError:
            raise ValueError(f"Received the following items from question_or_advice(), expected three different outputs: {result}")
        new_page = {}
        if q_or_a != "advice":
            Logger.info("Asking another question")
            Logger.debug(f"Item received from kb: {item}\tAnswer_type: {answer_type}")

            # Transform item and answer type into page information dict
            match answer_type:
                case "yes/no":
                    new_page["next_page"] = "yesno"
                case "integer":
                    new_page["next_page"] = "text"
                    new_page["validate_function"] = lambda output : not isinstance(output, int)
                case _: # Assume multiple choice
                    new_page["next_page"] = "radio_buttons"

                    # Generate radio buttons options
                    answer_type: str
                    choices = answer_type.split("/")
                    new_page["radio_texts"] = choices
                    new_page["radio_ammount"] = len(choices)

            new_page["title"] = item
            new_page["next_button"] = "next"
        else:
            Logger.info("Giving advice")

        return new_page


    # DEPRECATED FUNCTION MAY RETURN LATER
    # def get_previous_window(self) -> dict:
    #     return self._dict


if __name__ == "__main__":
    data = DataProvider(title = "This is a question", 
                        status = "Status: Good", 
                        button_left = "Previous", 
                        button_right = "Next", 
                        radio_buttons = True, 
                        radio_text_1 = "This is one answer",
                        radio_text_2 = "This is another answer")
    print(DataProvider.get_next_window())