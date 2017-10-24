# -*- coding: utf-8 -*-
"""
Module defining the state graph.
"""

# STD
import copy

# PROJECT
from quantities import get_global_quantity_index


class StateGraph:
    """
    Class to model a state graph, i.e. a graph with states as nodes and transitions between those same nodes as edges.
    """
    states = None
    transitions = None

    def __init__(self, initial_state, rules, consequences, constraints):
        self.initial_state = initial_state
        self.rules = rules
        self.consequences = consequences
        self.constraints = constraints

    def envision(self, verbosity=0):
        if not (self.states or self.transitions):
            self.states, self.transitions = self._envision(verbosity=verbosity)
        return self.states, self.transitions

    def _envision(self, verbosity=0):
        states = {self.initial_state.uid: self.initial_state}
        transitions = {}
        state_stack = [self.initial_state]
        discontinuities, constraints = 0, 0

        self._print_transition_table_header(verbosity)

        while len(state_stack) != 0:
            current_state = state_stack.pop(0)

            implied_state = self._apply_consequences(current_state)

            if implied_state.uid != current_state.uid:
                # Check if state resulting from a consequence is still a valid state

                if all(self._get_constraint_feedback(implied_state)):
                    transitions[(current_state.uid, "C?")] = implied_state.uid
                    states[implied_state.uid] = implied_state
                else:
                    # The state that was created by applying the consequences is invalid; proceed with original state
                    implied_state = current_state

            if verbosity > 1:
                print("{:<27} --({})-->   {}".format(current_state.readable_id, "C?", implied_state.readable_id))

            # Branch out
            branches = implied_state.apply_rules(self.rules)
            branches = [branch for branch in branches if branch is not None]  # Clean up

            # Filter branches by applying constraints
            branches, local_constraint_counter = self._apply_constraints(branches)
            constraints += local_constraint_counter

            for rule, new_state in branches:
                transitions[(implied_state.uid, rule)] = new_state.uid

                if verbosity > 1:
                    print("{:<27} --({})-->   {}".format(implied_state.readable_id, rule, new_state.readable_id))

                if new_state.uid not in states:
                    states[new_state.uid] = new_state
                    state_stack.append(new_state)

            discontinuities += implied_state.discontinuity_counter
            constraints += implied_state.constraint_counter

        self._print_state_table_header(verbosity, states)

        if verbosity > 0:
            print("\n{} state(s) and {} transitions detected.".format(len(states), len(transitions)))
            #print("{} state(s) were prohibited due to discontinuities.".format(discontinuities))
            print("Constraints were enforced {} times.".format(constraints))

        return states, transitions

    def _apply_consequences(self, state):

        for consequence in self.consequences:
            applied_consequence = consequence.apply(state)
            if applied_consequence is not None:
                state = applied_consequence

        return state

    def _apply_constraints(self, branches):
        constrained_branches = []
        constraint_counter = 0

        for rule, state in branches:
            feedbacks = self._get_constraint_feedback(state)

            if all(feedbacks):
                constrained_branches.append((rule, state))

            constraint_counter += feedbacks.count(False)

        return constrained_branches, constraint_counter

    def _get_constraint_feedback(self, state):
        return [constraint.holds(state) for constraint in self.constraints]

    @property
    def nodes(self):
        states, _ = self.envision()
        return [(state.uid, state) for state in states.values()]

    @property
    def edges(self):
        self.envision()
        _, transitions = self.envision()
        return [(start, label, end) for (start, label), end in transitions.items()]

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
    discontinuity_counter = 0
    constraint_counter = 0

    def __init__(self, **entities):
        self.entity_names = entities.keys()
        self.entities = list(entities.values())
        vars(self).update(entities)

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

    def apply_rules(self, rules):
        return [rule.apply(self) for rule in rules]

    def __copy__(self):
        return State(**dict(zip(self.entity_names, [copy.copy(entity) for entity in self.entities])))


