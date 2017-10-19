# -*- coding: utf-8 -*-
"""
Module defining the state graph.
"""

# STD
import copy

# PROJECT
from quantities import DiscontinuityException
from relationships import ConstraintEnforcementException


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
        states = {self.initial_state.readable_id: self.initial_state}
        transitions = {}
        state_stack = [self.initial_state]
        discontinuities, constraints = 0, 0

        if verbosity > 1:
            print(
                "\n{tspace}{tap:<4} | {cspace}{container:<16} | {drain} {relationship} {tap:>5}{tspace} | "
                "{container:>16}{cspace} | {drain}".format(
                    tap="tap", container="container", drain="drain", relationship=" "*12,
                    tspace=" "*2, cspace=" "*8
                )
            )
            print("{}+{}+{}{}{}+{}+{}".format("-"*7, "-"*26, "-"*7, " "*14, "-"*7, "-"*26, "-"*6))

        while len(state_stack) != 0:
            current_state = state_stack.pop(0)

            implied_state = self._apply_consequences(current_state)

            if current_state.readable_id != implied_state.readable_id:
                transitions[(current_state.readable_id, "C?")] = implied_state
                states[implied_state.readable_id] = implied_state

                if verbosity > 1:
                    print("{:<27} --({})-->   {}".format(current_state.readable_id, "C?", implied_state.readable_id))

            #if verbosity > 1:
            #    print("Current state: {}".format(current_state))

            # Branch out
            branches = implied_state.apply_rules(self.rules)
            branches = [branch for branch in branches if branch is not None]  # Clean up

            # Filter branches by applying constraints
            branches, local_constraint_counter = self._apply_constraints(branches)
            constraints += local_constraint_counter

            for rule, new_state in branches:
                transitions[(implied_state.readable_id, rule)] = new_state

                if verbosity > 1:
                    print("{:<27} --({})-->   {}".format(implied_state.readable_id, rule, new_state.readable_id))

                if new_state.readable_id not in states:
                    states[new_state.readable_id] = new_state
                    state_stack.append(new_state)

            discontinuities += implied_state.discontinuity_counter
            constraints += implied_state.constraint_counter

        if verbosity > 1:
            print("\n{pad} States found {pad}\n".format(pad="#"*14))
            print("{tspace}{tap:<4} | {cspace}{container:<16} | {drain}".format(
                    tap="tap", container="container", drain="drain", tspace=" "*2, cspace=" "*8
                )
            )
            print("{}+{}+{}".format("-"*7, "-"*26, "-"*7))
            for state_id in states.keys():
                print(state_id)

        if verbosity > 0:
            print("\n{} state(s) and {} transitions detected.".format(len(states), len(transitions)))
            print("{} state(s) were prohibited due to discontinuities.".format(discontinuities))
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
            enforcements = [constraint.apply(state) for constraint in self.constraints]

            if not any(enforcements):
                constrained_branches.append((rule, state))

            constraint_counter += enforcements.count(True)

        return constrained_branches, constraint_counter

    @property
    def edges(self):
        states, _ = self.envision()
        return states

    @property
    def nodes(self):
        self.envision()
        _, transitions = self.envision()
        return transitions


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

    def apply_rules(self, rules):
        branches = []

        for rule in rules:
            try:
                branches.append(rule.apply(self))
            except DiscontinuityException:
                self.discontinuity_counter += 1
            #except ConstraintEnforcementException:
            #    self.constraint_counter += 1

        return branches

    def __copy__(self):
        return State(**dict(zip(self.entity_names, [copy.copy(entity) for entity in self.entities])))


