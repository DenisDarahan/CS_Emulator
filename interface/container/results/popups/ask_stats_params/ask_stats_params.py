from decimal import Decimal

from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty

from interface.popups import ErrorPopup


class AskStatsParams(Popup):
    nodes_min_count: TextInput = ObjectProperty()
    nodes_max_count: TextInput = ObjectProperty()
    nodes_step: TextInput = ObjectProperty()
    correlation_min: TextInput = ObjectProperty()
    correlation_max: TextInput = ObjectProperty()
    correlation_step: TextInput = ObjectProperty()
    nodes_min_weight: TextInput = ObjectProperty()
    nodes_max_weight: TextInput = ObjectProperty()
    graphs_count: TextInput = ObjectProperty()

    DEFAULT_N_MIN_COUNT: int
    DEFAULT_N_MAX_COUNT: int
    DEFAULT_N_STEP: int = 1
    DEFAULT_C_MIN: float = 0.1
    DEFAULT_C_MAX: float = 0.9
    DEFAULT_C_STEP: float = 0.1
    DEFAULT_N_MIN_WEIGHT: int = 1
    DEFAULT_N_MAX_WEIGHT: int = 9
    DEFAULT_G_COUNT: int = 5

    def __init__(self, parent_tab: TabbedPanelItem, **kwargs):
        self.parent_tab = parent_tab
        super().__init__(**kwargs)
        self._init_default_values()

    def _init_default_values(self):
        self.DEFAULT_N_MIN_COUNT = len(self.parent_tab.cs_tab.processors)
        self.DEFAULT_N_MAX_COUNT = 4 * len(self.parent_tab.cs_tab.processors)

        self.nodes_min_count.text = str(self.DEFAULT_N_MIN_COUNT)
        self.nodes_max_count.text = str(self.DEFAULT_N_MAX_COUNT)
        self.nodes_step.text = str(self.DEFAULT_N_STEP)
        self.correlation_min.text = str(self.DEFAULT_C_MIN)
        self.correlation_max.text = str(self.DEFAULT_C_MAX)
        self.correlation_step.text = str(self.DEFAULT_C_STEP)
        self.nodes_min_weight.text = str(self.DEFAULT_N_MIN_WEIGHT)
        self.nodes_max_weight.text = str(self.DEFAULT_N_MAX_WEIGHT)
        self.graphs_count.text = str(self.DEFAULT_G_COUNT)

    def set_params(self):
        self.dismiss()

        try:
            n_min_count = int(self.nodes_min_count.text) if self.nodes_min_count.text else self.DEFAULT_N_MIN_COUNT
            if n_min_count < self.DEFAULT_N_MIN_COUNT:
                raise ValueError('Nodes min count must be 1 or greater')

            n_max_count = int(self.nodes_max_count.text) if self.nodes_max_count.text else self.DEFAULT_N_MAX_COUNT
            if n_max_count < n_min_count or n_max_count > self.DEFAULT_N_MAX_COUNT:
                raise ValueError(f'Nodes max count must be {n_min_count} or greater')

            n_step = abs(int(self.nodes_step.text)) * (n_max_count - n_min_count) // abs(n_max_count - n_min_count) \
                if self.nodes_step.text else self.DEFAULT_N_STEP
            if n_step == 0:
                raise ValueError('Step cannot be 0')

            c_min = Decimal(self.correlation_min.text) if self.correlation_min.text else self.DEFAULT_C_MIN
            if c_min < 0 or c_min > 1:
                raise ValueError('Correlation must be between 0 and 1')

            c_max = Decimal(self.correlation_max.text) if self.correlation_max.text else self.DEFAULT_C_MAX
            if c_max < 0 or c_max > 1:
                raise ValueError('Correlation must be between 0 and 1')

            c_step = (abs(Decimal(self.correlation_step.text)) * (c_max - c_min) / abs(c_max - c_min)) \
                if self.correlation_step.text else self.DEFAULT_C_STEP

            n_min_weight = int(self.nodes_min_weight.text) if self.nodes_min_weight.text else self.DEFAULT_N_MIN_WEIGHT
            if n_min_weight < 1:
                raise ValueError('Nodes min weight must be 1 or greater')

            n_max_weight = int(self.nodes_max_weight.text) if self.nodes_max_weight.text else self.DEFAULT_N_MAX_WEIGHT
            if n_max_weight < n_min_weight:
                raise ValueError(f'Nodes max weight must be {n_min_weight} or greater')

            g_count = int(self.graphs_count.text) if self.graphs_count.text else self.DEFAULT_G_COUNT
            if g_count < 1:
                raise ValueError('Graphs count must be 1 or greater')

        except ValueError as ve:
            ErrorPopup(f'Not correct value!\n{" ".join(ve.args)}').open()

        else:
            self.parent_tab.run_stats(n_min_count, n_max_count, n_step, c_min, c_max, c_step,
                                      n_min_weight, n_max_weight, g_count)
