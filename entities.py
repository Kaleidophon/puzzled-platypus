# -*- coding: utf-8 -*-
"""
Module defining entities for the causal graph.
"""


class Entity:
    def __init__(self, **quantities):
        self.quantities = list(quantities.values())
        self.__dict__.update(quantities)
        #vars(self).update(quantities)


class Container(Entity):
    """
    Class representing a container.
    """
    def __init__(self, **quantities):
        assert all([quantity in quantities for quantity in {"volume", "height", "pressure"}])
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
