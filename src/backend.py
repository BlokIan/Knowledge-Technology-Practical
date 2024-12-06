class DataProvider():
    def __init__(self, dictionary: dict = None,  **kwargs):
        if dictionary is not None:
            raise NotImplementedError()
        # self.get_starting_data() needs to be implemented still, get starting data from knowledge system
        self._dict = {
            "title": "This is a question", 
            "previous_button": "Previous", 
            "next_button": "Next", 
            "radio_buttons": True, 
            "radio_text_1": "This is one answer",
            "radio_text_2": "This is another answer",
            "next_page": "text",
        }
        self.count = 0
    
    def update_data(self, information: dict) -> None:
        if not isinstance(information, dict):
            raise TypeError(f"Expected dict, received {type(information)}")
        self._dict = information
    
    def get_next_window(self) -> dict:
        if self.count < 2:
            self.count += 1
            return self._dict

        self._dict["next_page"] = "radio_buttons"
        return self._dict

    def get_previous_window(self) -> dict:
        return self._dict


if __name__ == "__main__":
    data = DataProvider(title = "This is a question", 
                        status = "Status: Good", 
                        button_left = "Previous", 
                        button_right = "Next", 
                        radio_buttons = True, 
                        radio_text_1 = "This is one answer",
                        radio_text_2 = "This is another answer")