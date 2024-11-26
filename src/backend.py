class DataProvider():
    def __init__(self, dictionary: dict = None,  **kwargs):
        if dictionary is not None:
            raise NotImplementedError()
        # self.get_starting_data() needs to be implemented still, get starting data from knowledge system
        self._dict = {
            "title": "This is a question", 
            "status": "Status: Good", 
            "previous_button": "Previous", 
            "next_button": "Next", 
            "radio_buttons": True, 
            "radio_text_1": "This is one answer",
            "radio_text_2": "This is another answer"
        }
    
    def update_data(self, information: dict) -> dict:
        return self.get_window()
    
    def get_window(self):
        return self._dict


if __name__ == "__main__":
    data = DataProvider(title = "This is a question", 
                        status = "Status: Good", 
                        button_left = "Previous", 
                        button_right = "Next", 
                        radio_buttons = True, 
                        radio_text_1 = "This is one answer",
                        radio_text_2 = "This is another answer")