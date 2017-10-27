# -*- coding: utf-8 -*-
"""
Module defining quantities.
"""

# STD
import itertools

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
    def __init__(self, value, quantity_space, quant_type, strict=True):
        assert quant_type in ("magnitude", "derivative"), "Invalid type for quantifiable"
        self.init_stage = True  # Otherwise the assert-statement in __setattr__ will be triggered
        self.value = value
        self.init_stage = False
        self.type = quant_type
        self.delta = 0  # Rate of change since last update

        self.strict = strict
        self.quantity_space = quantity_space
        self.space_ceil = len(quantity_space) - 1
        self.value_index = quantity_space.index(value)
        self.aggregations = []

    def is_max(self):
        return self.value_index == self.space_ceil

    def is_min(self):
        return self.value_index == 0

    def replace(self, new_value):
        self.init_stage = True
        self.value = new_value
        self.init_stage = False

    def update(self):
        branches = set()

        if self.type == "derivative" and len(self.aggregations) > 0:
            initial_effect, initial_value = self.aggregations[0]
            current_value = initial_value

            if len(self.aggregations) != 1:
                for effect, value in self.aggregations[1:]:
                    new_value = ADDITION_TABLE[(current_value, value)]

                    if new_value == "?":
                        branches.add(self.value)
                        branches.add(current_value)
                        branches.add(value)
                        current_value = new_value
                        break

                    current_value = new_value

            self.value = current_value

        self.aggregations = []  # Reset aggregations
        self.delta = 0  # Reset change since last update
        return branches

    @property
    def global_value_index(self):
        return GLOBAL_QUANTITY_SPACE.index(self.value)

    def __add__(self, other):
        # Just add a number
        if type(other) == int:
            assert other == 1, "You can only add one to a quantifiable."

            if self.value_index != self.space_ceil:
                self.value_index += 1
                self.value = self.quantity_space[self.value_index]
                self.delta += 1

        # Add a number and origin of effect (influence, proportionality)
        elif type(other) == tuple:
            effect, value = other
            assert value == 1, "You can only add one to a quantifiable."

            if self.value_index != self.space_ceil:
                self.delta += 1
                self.aggregations.append((effect, self.quantity_space[self.value_index + 1]))

        return self

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        # Just subtract a number
        if type(other) == int:
            assert other == 1, "You can only subtract one to a quantifiable."
            if self.value_index != 0:
                self.value_index -= 1
                self.value = self.quantity_space[self.value_index]
                self.delta -= 1

        # Subtract a number and origin of effect (influence, proportionality)
        elif type(other) == tuple:
            effect, value = other
            assert value == 1, "You can only subtract one to a quantifiable."

            if self.value_index != 0:
                self.delta -= 1
                self.aggregations.append((effect, self.quantity_space[self.value_index - 1]))

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
            assert value == "?" or abs(self.global_value_index - GLOBAL_QUANTITY_SPACE.index(value)) < 2, \
                "Value assignment to Quantifiable would create a discontinuity"

            if type(value) == tuple:
                value_, effect = value
                self.aggregations.append((effect, value_))
                return
            elif type(value) == int:
                self.delta += GLOBAL_QUANTITY_SPACE.index(value) - self.global_value_index

        super().__setattr__(key, value)


class Quantity:
    """
    Class modeling a quantity of a inflow, outflow or volume.
    """
    def __init__(self, model, magnitude="0", derivative="0"):
        assert model in QUANTITY_SPACES.keys(), "Unknown model"

        self.init_phase = True
        self.model = model
        self.quantity_space = QUANTITY_SPACES[model]

        assert magnitude in self.quantity_space, "Invalid value for magnitude: {}".format(magnitude)
        assert derivative in QUANTITY_SPACE_DERIVATIVE, "Invalid value for derivative: {}".format(derivative)

        self.init_quantifiables(magnitude, derivative)

    def init_quantifiables(self, magnitude, derivative):
        # Wrap magnitude and derivative in Quantifiables for neat addition / subtraction functionalities
        self.magnitude = Quantifiable(
            value=magnitude, quantity_space=self.quantity_space, quant_type="magnitude"
        )
        self.derivative = Quantifiable(
            value=derivative, quantity_space=QUANTITY_SPACE_DERIVATIVE, quant_type="derivative"
        )
        self.init_phase = False

    def update(self):
        branches = set()

        branches_magnitude = {self.magnitude.value}
        branches_derivative = self.derivative.update()
        branches_derivative = branches_derivative if len(branches_derivative) > 0 else {self.derivative.value}

        for mag, der in itertools.product(branches_magnitude, branches_derivative):
            branches.add((mag, der))

        return branches

    def __copy__(self):
        return Quantity(self.model, str(self.magnitude), str(self.derivative))

    def __str__(self):
        return "{}, {}".format(self.magnitude, self.derivative)

    def __setattr__(self, key, value):
        if key == "magnitude" and not self.init_phase:
            self.init_phase = True
            if type(value) == Quantifiable:
                self.magnitude = value
            else:
                self.magnitude.value = value
        elif key == "derivative" and not self.init_phase:
            self.init_phase = True
            if type(value) == Quantifiable:
                self.derivative = value
            else:
                self.derivative.value = value
        elif key != "init_phase":
            super().__setattr__(key, value)
            self.init_phase = False
        else:
            super().__setattr__(key, value)

if __name__ == "__main__":
    quant = Quantity("inflow")
    print(quant)
    quant.derivative -= ("I+", 1)
    quant.derivative += ("I-", 1)
    print(quant.update())
