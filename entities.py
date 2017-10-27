# -*- coding: utf-8 -*-
"""
Module defining entities for the causal graph.
"""

# STD
import copy
import itertools


class Entity:
    def __init__(self, **quantities):
        self.quantity_names = quantities
        self.quantities = list(quantities.values())
        self.__dict__.update(quantities)

    def update(self):
        """
        Update quantities based on the aggregated effects.
        """
        branches = {quantity: set() for quantity in self.quantities}

        for quantity in self.quantities:
            quantity_branches = quantity.update()

            branches[quantity] = quantity_branches if len(quantity_branches) > 0 else {
                (quantity.magnitude, quantity.derivative)
            }

        return [el[0] for el in list(itertools.product(*list(branches.values())))]

    @property
    def fancy_repr(self):
        return " | ".join(
            ["M: {}, d: {}".format(quantity.magnitude, quantity.derivative) for quantity in self.quantities]
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
