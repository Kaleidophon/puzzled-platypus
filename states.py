# -*- coding: utf-8 -*-
"""
Module defining the state graph.
"""

# STD
import copy
import itertools
import collections

# PROJECT
from quantities import get_global_quantity_index
from relationships import Consequence, ValueCorrespondence


class StateGraph:
    """
    Class to model a state graph, i.e. a graph with states as nodes and transitions between those same nodes as edges.
    """
    def __init__(self, initial_state, inter_state, intra_state):
        self.initial_state = initial_state
        self.entities = initial_state.entities
        self.inter_state = inter_state  # Inter-state relationships
        self.intra_state = intra_state  # Intra-state relationships
        self.states, self.transitions = None, None

    def envision(self, verbosity=0):
        if not (self.states or self.transitions):  # Do some caching of results
            self.states, self.transitions = self._envision(verbosity=verbosity)
        return self.states, self.transitions

    def _envision(self, verbosity=0):
        states = {self.initial_state.uid: self.initial_state}
        transitions = collections.defaultdict(list)
        state_stack = [self.initial_state]

        self._print_transition_table_header(verbosity)

        while len(state_stack) != 0:
            current_state = state_stack.pop(0)
            print(current_state.readable_id)

            # Step 1: Apply consequences
            implied_state = self._apply_consequences(current_state)

            # Step 2: Apply value correspondences if possible
            implied_state = self._apply_vcs(implied_state)

            # Step 3: Aggregate incoming influences and proportionalities for every entity
            implied_state.apply_rules(self.inter_state)

            # Step 4: Perform derivative calculus and update quantities
            # Step 5: Branch if necessary
            raw_branches = implied_state.update()
            # print("{:<27} --({})-->   {}".format(current_state.readable_id, "C?", implied_state.readable_id))
            branches = [self.construct_state_from_raw_quantities(current_state, branch) for branch in raw_branches]
            new_branches = [state for state in branches if state.uid not in states]

            for new_state in new_branches:
                # Step 6: Apply value correspondences again if possible
                new_state = self._apply_vcs(new_state)
                transitions[current_state.uid].append(new_state.uid)
                states[new_state.uid] = new_state
                state_stack.append(new_state)

                if verbosity > 1:
                    print("{:<27} --({})-->   {}".format(current_state.readable_id, rule, new_state.readable_id))

        self._print_state_table_header(verbosity, states)

        if verbosity > 0:
            print("\n{} state(s) and {} transitions detected.".format(len(states), len(transitions)))
            #print("{} state(s) were prohibited due to discontinuities.".format(discontinuities))

        return states, transitions

    def _apply_consequences(self, state):
        state = copy.copy(state)

        for consequence in self.consequences:
            state = consequence.apply(state)

        return state

    def _apply_vcs(self, state):
        state = copy.copy(state)

        for value_correspondence in self.value_correspondences:
            state = value_correspondence.apply(state)

        return state


    @property
    def consequences(self):
        return [relationship for relationship in self.intra_state if isinstance(relationship, Consequence)]

    @property
    def value_correspondences(self):
        return [relationship for relationship in self.intra_state if isinstance(relationship, ValueCorrespondence)]

    @property
    def nodes(self):
        states, _ = self.envision()
        return [(state.uid, state) for state in states.values()]

    @property
    def edges(self):
        self.envision()
        _, transitions = self.envision()

        for start in transitions:
            ends = transitions[start]
            for end in ends:
                yield (start, end)

    def construct_state_from_raw_quantities(self, state, raw_quantities):
        new_state = copy.copy(state)
        raw_quantities = list(raw_quantities)

        flattened_quantities = self.flatten_quantity_list(raw_quantities)

        for entity in new_state.entities:
            for quantity in entity.quantities:
                raw_quantity = flattened_quantities.pop(0)
                quantity.magnitude.replace(raw_quantity[0])
                quantity.derivative.replace(raw_quantity[1])

        return new_state

    def flatten_quantity_list(self, quantity_list):
        el = quantity_list[0]
        if type(el) == tuple and type(el[0]) == str:
            return quantity_list

        flatter_list = []
        for element in quantity_list:
            for ele in element:
                flatter_list.append(ele)

        return self.flatten_quantity_list(flatter_list)

    def _print_transition_table_header(self, verbosity):
        if verbosity > 1:
            # Not beautiful but still in the scope of this project
            if len(self.initial_state.container.quantities) == 3:
                print(
                    "\n{tspace}{tap:<4} | {cspace}{container:<16} | {drain} {relationship} {tap:>5}{tspace} | "
                    "{container:>16}{cspace} | {drain}".format(
                        tap="tap", container="container", drain="drain", relationship=" "*12,
                        tspace=" "*2, cspace=" "*8
                    )
                )
                print("{}+{}+{}{}{}+{}+{}".format("-"*7, "-"*26, "-"*7, " "*14, "-"*7, "-"*26, "-"*6))

            if len(self.initial_state.container.quantities) == 1:
                print(
                    "\n{tspace}{tap:<4} | {cspace}{container} | {drain} {relationship} {tap:>7}{tspace} | "
                    "{container}{cspace} | {drain}".format(
                        tap="tap", container="cont.", drain="drain", relationship=" "*12,
                        tspace=" "*2, cspace=" "*1
                    )
                )
                print("{}+{}+{}{}{}+{}+{}".format("-" * 7, "-" * 8, "-" * 7, " " * 14, "-" * 9, "-" * 8, "-" * 6))

    def _print_state_table_header(self, verbosity, states):
        if verbosity > 1:
            # Not beautiful but still in the scope of this project
            if len(self.initial_state.container.quantities) == 3:
                print("\n{pad} States found {pad}\n".format(pad="#"*14))
                print("{tspace}{tap:<4} | {cspace}{container:<16} | {drain}".format(
                        tap="tap", container="container", drain="drain", tspace=" "*2, cspace=" "*8
                    )
                )
                print("{}+{}+{}".format("-"*7, "-"*26, "-"*7))

            if len(self.initial_state.container.quantities) == 1:
                print("\n{pad} States found {pad}\n".format(pad="#" * 5))
                print("{tspace}{tap:<4} | {cspace}{container} | {drain}".format(
                    tap="tap", container="cont.", drain="drain", tspace=" " * 2, cspace=" " * 1
                    )
                )
                print("{}+{}+{}".format("-" * 7, "-" * 8, "-" * 7))

        for state in states.values():
            print(state.readable_id)


class State:
    """
    Class to model a state in the state graph.
    """
    def __init__(self, **entities):
        self.entity_names = entities.keys()
        self.entities = list(entities.values())
        vars(self).update(entities)

    def update(self):
        entity_branches = [entity.update() for entity in self.entities]

        return list(itertools.product(*entity_branches))

    def apply_rules(self, rules):
        return [rule.apply(self) for rule in rules]

    def __repr__(self):
        return "<State: {}>".format(self.readable_id)

    @property
    def uid(self):
        return "".join(
            [
                "".join([
                    "{}{}".format(
                        get_global_quantity_index(quantity.magnitude),
                        get_global_quantity_index(quantity.derivative)
                    )
                    for quantity in entity.quantities
                ])
                for entity in self.entities
            ]
        )

    @property
    def readable_id(self):
        return "| ".join(
            [
                "; ".join(
                    [
                        "{:<3} {:<3}".format(str(quantity.magnitude), str(quantity.derivative))
                        for quantity in entity.quantities
                    ]
                )
                for entity in self.entities
            ]
        )

    def __str__(self):
        return "\n".join(
            [
                "({}) {}".format(entity.__class__.__name__, entity.fancy_repr)
                for entity in self.entities
            ]
        )

    def __copy__(self):
        return State(**dict(zip(self.entity_names, [copy.copy(entity) for entity in self.entities])))


