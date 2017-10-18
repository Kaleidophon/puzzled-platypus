# -*- coding: utf-8 -*-
"""
Module defining quantities.
"""

# STD
from functools import wraps

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


class DiscontinuityException(Exception):
    pass


def enforce_continuity(func):
    """
    Decorate a Quantifiable's in such a way that operations that would create discontinuities throw an error.
    """
    @wraps(func)
    def function_wrapper(*args, **kwargs):
        self = args[0]
        res = func(*args, **kwargs)
        self.quantity.check_consistency()
        return res
    return function_wrapper


class Quantifiable:
    """
    Class to model a magnitude or a derivative.
    """
    def __init__(self, value, quantity_space, quantity):
        self.value = value
        self.quantity_space = quantity_space
        self.space_ceil = len(quantity_space) - 1
        self.value_index = quantity_space.index(value)
        self.quantity = quantity

    def is_max(self):
        return self.value_index == self.space_ceil

    def is_min(self):
        return self.value_index == 0

    @property
    def global_value_index(self):
        return GLOBAL_QUANTITY_SPACE.index(self.value)

    @enforce_continuity
    def __add__(self, other):
        assert other == 1, "You can only add one to a quantifiable."

        if self.value_index != self.space_ceil:
            self.value_index += 1
            self.value = self.quantity_space[self.value_index]

        return self

    @enforce_continuity
    def __iadd__(self, other):
        return self.__add__(other)

    @enforce_continuity
    def __sub__(self, other):
        assert other == 1, "You can only subtract one to a quantifiable."
        if self.value_index != 0:
            self.value_index -= 1
            self.value = self.quantity_space[self.value_index]

        return self

    @enforce_continuity
    def __isub__(self, other):
        return self.__sub__(other)

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if type(other) == str:
            return str(self) == other
        return self == other


class FrozenQuantifiable(Quantifiable):
    """
    Quantifiable that has an immutable value.
    """
    def __setattr__(self, key, value):
        if key == "value":
            raise KeyError("Cannot set value for an immutable quantity.")
        super().__setattr__(key, value)


class Quantity:
    """
    Class modeling a quantity of a inflow, outflow or volume.
    """
    magnitude = None
    derivative = None

    def __init__(self, model, magnitude="0", derivative="0"):
        assert model in QUANTITY_SPACES.keys(), "Unknown model"

        self.model = model
        self.quantity_space = QUANTITY_SPACES[model]

        assert magnitude in self.quantity_space, "Invalid value for magnitude: {}".format(magnitude)
        assert derivative in QUANTITY_SPACE_DERIVATIVE, "Invalid value for derivative: {}".format(derivative)

        self.init_quantifiables(magnitude, derivative)
        self.check_consistency()

    def init_quantifiables(self, magnitude, derivative):
        # Wrap magnitude and derivative in Quantifiables for neat addition / subtraction functionalities
        self.magnitude = Quantifiable(value=magnitude, quantity_space=self.quantity_space, quantity=self)
        self.derivative = Quantifiable(value=derivative, quantity_space=QUANTITY_SPACE_DERIVATIVE, quantity=self)

    def check_consistency(self):
        if abs(self.magnitude.global_value_index - self.derivative.global_value_index) > 1:
            raise DiscontinuityException(
                "Discontinuity detected! Magnitude: {} Derivative: {}".format(self.magnitude, self.derivative)
            )

    def __copy__(self):
        return Quantity(self.model, str(self.magnitude), str(self.derivative))

    def __str__(self):
        return "{}, {}".format(self.magnitude, self.derivative)


class FrozenQuantity(Quantity):
    """
    Quantity that is immutable.
    """
    def init_quantifiables(self, magnitude, derivative):
        # Wrap magnitude and derivative in Quantifiables for neat addition / subtraction functionalities
        self.magnitude = FrozenQuantifiable(value=magnitude, quantity_space=self.quantity_space)
        self.derivative = FrozenQuantifiable(value=derivative, quantity_space=QUANTITY_SPACE_DERIVATIVE)

