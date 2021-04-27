from kivy.uix.popup import Popup


class ErrorPopup(Popup):

    def __init__(self, error_msg: str, **kwargs):
        self.error_msg = error_msg
        super().__init__(**kwargs)
