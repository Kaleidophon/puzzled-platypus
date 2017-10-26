# -*- coding: utf-8 -*-
"""
Module defining quantities.
"""

# CONST
GLOBAL_QUANTITY_SPACE = ("min", "-", "0", "+", "max")
QUANTITY_SPACE_INFLOW = ("0", "+")
QUANTITY_SPACE_OUTFLOW = QUANTITY_SPACE_VOLUME =\
    QUANTITY_SPACE_PRESSURE = QUANTITY_SPACE_HEIGHT = ("0", "+", "max")
QUANTITY_SPACE_DERIVATIVE = ("-", "0", "+")

QUANTITY_SPACES = {
    "inflow": QUANTITY_SPACE_INFLOW,
    "outflow": QUANTITY_SPACE_OUTFLOW,
    "volume": QUANTITY_SPACE_VOLUME,
    "pressure": QUANTITY_SPACE_PRESSURE,
    "height": QUANTITY_SPACE_HEIGHT
}

ADDITION_TABLE = {
    ("-", "-"): "-",
    ("-", "0"): "-",
    ("0", "-"): "-",
    ("-", "+"): "?",
    ("0", "0"): "0",
    ("0", "+"): "+",
    ("+", "+"): "+",
    ("+", "-"): "?",
    ("+", "0"): "+"
}


def get_global_quantity_index(quantity):
    assert quantity in GLOBAL_QUANTITY_SPACE
    return GLOBAL_QUANTITY_SPACE.index(quantity)


class Quantifiable:
    """
    Class to model a magnitude or a derivative.
    """
    def __init__(self, value, quantity_space, strict=True):
        self.init_stage = True  # Otherwise the assert-statement in __setattr__ will be triggered
        self.value = value
        self.init_stage = False

        self.strict = strict
        self.quantity_space = quantity_space
        self.space_ceil = len(quantity_space) - 1
        self.value_index = quantity_space.index(value)

    def is_max(self):
        return self.value_index == self.space_ceil

    def is_min(self):
        return self.value_index == 0

    @property
    def global_value_index(self):
        return GLOBAL_QUANTITY_SPACE.index(self.value)

    def __add__(self, other):
        assert other == 1, "You can only add one to a quantifiable."

        if self.value_index != self.space_ceil:
            self.value_index += 1
            self.value = self.quantity_space[self.value_index]

        return self

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        assert other == 1, "You can only subtract one to a quantifiable."
        if self.value_index != 0:
            self.value_index -= 1
            self.value = self.quantity_space[self.value_index]

        return self

    def __isub__(self, other):
        return self.__sub__(other)

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if type(other) == str:
            return str(self) == other
        return self == other

    def __setattr__(self, key, value):
        if key == "value" and not self.init_stage and self.strict:
            assert abs(self.global_value_index - GLOBAL_QUANTITY_SPACE.index(value)) < 2, \
                "Value assignment to Quantifiable would create a discontinuity"
        super().__setattr__(key, value)


class Quantity:
    """
    Class modeling a quantity of a inflow, outflow or volume.
    """
    magnitude = None
    derivative = None
    init_phase = True
    aggregations = {}
    aggregated = False

    def __init__(self, model, magnitude="0", derivative="0"):
        assert model in QUANTITY_SPACES.keys(), "Unknown model"

        self.model = model
        self.quantity_space = QUANTITY_SPACES[model]

        assert magnitude in self.quantity_space, "Invalid value for magnitude: {}".format(magnitude)
        assert derivative in QUANTITY_SPACE_DERIVATIVE, "Invalid value for derivative: {}".format(derivative)

        self.init_quantifiables(magnitude, derivative)

    def init_quantifiables(self, magnitude, derivative):
        # Wrap magnitude and derivative in Quantifiables for neat addition / subtraction functionalities
        self.magnitude = Quantifiable(value=magnitude, quantity_space=self.quantity_space)
        self.derivative = Quantifiable(value=derivative, quantity_space=QUANTITY_SPACE_DERIVATIVE)
        self.init_phase = False

    def aggregate(self, relationship, effect):
        self.aggregations[relationship] = effect
        self.aggregated = True

    def update(self):
        assert self.aggregated, "Aggregate step hasn't been performed recently"
        # TODO: Perform derivative calculus here [DU 26.10.17]
        pass

    def __copy__(self):
        return Quantity(self.model, str(self.magnitude), str(self.derivative))

    def __str__(self):
        return "{}, {}".format(self.magnitude, self.derivative)

    def __setattr__(self, key, value):
        if key == "magnitude" and not self.init_phase:
            self.magnitude.value = value
        elif key == "derivative" and not self.init_phase:
            self.derivative.value = value
        else:
            super().__setattr__(key, value)
