from kivy.uix.popup import Popup


class InfoPopup(Popup):

    def __init__(self, title: str, info_msg: str, **kwargs):
        self.title = title
        self.info_msg = info_msg
        super().__init__(**kwargs)
