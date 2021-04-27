from graph import Graph
from interface import LabInterfaceApp


class Main:

    def __init__(self):
        self.task_graph = Graph('Task')
        self.cs_graph = Graph('System')
        self.interface = LabInterfaceApp(self.task_graph, self.cs_graph)

    def run(self):
        self.interface.run()


if __name__ == '__main__':
    Main().run()
