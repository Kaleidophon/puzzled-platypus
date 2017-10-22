# -*- coding: utf-8 -*-
"""
Module defining entities for the causal graph.
"""

# STD
import copy


class Entity:
    def __init__(self, **quantities):
        self.quantity_names = quantities
        self.quantities = list(quantities.values())
        self.__dict__.update(quantities)

    @property
    def fancy_repr(self):
        return " | ".join(
            [
                "M: {}, d: {}".format(quantity.magnitude, quantity.derivative)
                for quantity in self.quantities
            ]
        )

    def __copy__(self):
        return type(self)(
            **dict(zip(self.quantity_names, [copy.copy(quantity) for quantity in self.quantities]))
        )


class Container(Entity):
    """
    Class representing a container.
    """
    def __init__(self, **quantities):
        assert all([quantity in {"volume", "height", "pressure"} for quantity in quantities])
        super().__init__(**quantities)


class Drain(Entity):
    """
    Class representing the drain, removing water from a container.
    """
    def __init__(self, **quantities):
        assert "outflow" in quantities
        super().__init__(**quantities)


class Tap(Entity):
    """
    Class representing the tap, feeding water into a container.
    """
    def __init__(self, **quantities):
        assert "inflow" in quantities
        super().__init__(**quantities)
