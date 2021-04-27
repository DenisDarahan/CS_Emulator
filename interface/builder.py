from kivy.app import App
from kivy.core.window import Window

from CS_Emulator.interface import Container


class LabInterfaceApp(App):

    def __init__(self, task_graph, cs_graph, **kwargs):
        self.task_graph = task_graph
        self.cs_graph = cs_graph
        super().__init__(**kwargs)

    def build(self):
        Window.fullscreen = 'auto'
        return Container(self.task_graph, self.cs_graph)
