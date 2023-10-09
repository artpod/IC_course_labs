class KnowledgeBase:
    def __init__(self):
        self.facts = []
        self.rules = []

    def add(self, item):
        if isinstance(item, Fact):
            self.add_logical_fact(item)
        elif isinstance(item, Rule):
            self.add_logical_rule(item)

    def add_logical_fact(self, fact):
        if fact not in self.facts:
            self.facts.append(fact)
            # Derive all the rules based on this fact
            for rule in self.rules:
                self.derive(fact, rule)
        else:
            # If the fact already relies on something, add it to the list
            if fact.relies_on:
                ind = self.facts.index(fact)
                for f in fact.relies_on:
                    self.facts[ind].relies_on.append(f)
            else:
                ind = self.facts.index(fact)
                # The fact is just a statement that does not rely on anything
                self.facts[ind].asserted = True

    def add_facts(self, facts):
        for fact in facts:
            self.add_logical_fact(fact)

    def add_logical_rule(self, rule):
        if rule not in self.rules:
            # Try to derive the rule based on each fact that we already have
            self.rules.append(rule)
            for fact in self.facts:
                self.derive(fact, rule)
        else:
            # If the rule already relies on something, add it to the list
            if rule.relies_on:
                ind = self.rules.index(rule)
                for f in rule.relies_on:
                    self.rules[ind].relies_on.append(f)
            else:
                ind = self.rules.index(rule)
                # The rule is just a statement that does not rely on anyything
                self.rules[ind].asserted = True

    def add_rules(self, rules):
        for rule in rules:
            self.add_logical_rule(rule)

    def query(self, fact):
        if isinstance(fact, Fact):
            f = Fact(fact.predicate)
            bindings_lst = []
            # Looking through previously derived facts
            for fact in self.facts:
                binding = match(f.predicate, fact.predicate)
                if binding:
                    bindings_lst.append(binding)

            return bindings_lst

        else:
            print("Invalid question:", fact.predicate)
            return []

    def derive(self, fact, rule):
        # Try to derive the first conditiion for the rule
        bindings = match(rule.lhs[0], fact.predicate)
        if not bindings:
            return None

        # If that is the only condition in the rule, stop
        if len(rule.lhs) == 1:
            new_fact = Fact(instantiate(rule.rhs, bindings), [[rule, fact]])
            rule.relied_facts.append(new_fact)
            fact.relied_facts.append(new_fact)
            self.add(new_fact)
        else:
            # Otherwise, derive the rest of the rule assumign that the parameters are bound
            # to the first rule.
            local_lhs = []
            local_rule = []
            for i in range(1, len(rule.lhs)):
                local_lhs.append(instantiate(rule.lhs[i], bindings))
            local_rule.append(local_lhs)
            local_rule.append(instantiate(rule.rhs, bindings))
            new_rule = Rule(local_rule, [[rule, fact]])
            rule.relied_rules.append(new_rule)
            fact.relied_rules.append(new_rule)
            # Add the new rule (it will recursively derived into new facts later)
            self.add(new_rule)


class Fact:
    def __init__(self, predicate, relies_on=None):
        if relies_on is None:
            relies_on = []
        # Fact is provided in the form of predicate
        self.predicate = predicate if isinstance(predicate, Predicate) else Predicate(predicate)
        self.asserted = not relies_on
        self.relies_on = []
        self.relied_facts = []
        self.relied_rules = []
        for pair in relies_on:
            self.relies_on.append(pair)

    def __eq__(self, other):
        return isinstance(other, Fact) and self.predicate == other.predicate


class Rule:
    def __init__(self, rule, relies_on=None):
        if relies_on is None:
            relies_on = []

        # The rule is provided in the form of a list of predicates, separate by `&` operation
        self.lhs = [p if isinstance(p, Predicate) else Predicate(p) for p in rule[0]]

        # The right side is the predicate that is derived from the rule
        self.rhs = rule[1] if isinstance(rule[1], Predicate) else Predicate(rule[1])
        self.asserted = not relies_on
        self.relies_on = []
        self.relied_facts = []
        self.relied_rules = []
        for pair in relies_on:
            self.relies_on.append(pair)


class Predicate:
    def __init__(self, predicates_list=None):
        if predicates_list is None:
            predicates_list = []
        self.terms = []
        self.predicate = ""

        # Predicate consists of a name and a list of terms
        if predicates_list:
            self.predicate = predicates_list[0]
            self.terms = [t if isinstance(t, Term) else Term(t) for t in predicates_list[1:]]

    def __eq__(self, other):
        if self.predicate != other.predicate:
            return False

        for self_term, other_term in zip(self.terms, other.terms):
            if self_term != other_term:
                return False

        return True


class Term:
    def __init__(self, term):
        # Term is either a variable or a constant
        is_var_or_value = isinstance(term, Variable) or isinstance(term, Constant)
        self.term = term if is_var_or_value else (Variable(term) if Variable.is_variable(term) else Constant(term))

    def __eq__(self, other):
        return (self is other
                or isinstance(other, Term) and self.term.element == other.term.element
                or ((isinstance(other, Variable) or isinstance(other, Constant))
                    and self.term.element == other.element))


class Variable:
    def __init__(self, element):
        self.term = None
        self.element = element

    def __eq__(self, other):
        return (self is other
                or isinstance(other, Term) and self.term.element == other.term.element
                or ((isinstance(other, Variable) or isinstance(other, Constant))
                    and self.term.element == other.element))

    @staticmethod
    def is_variable(var):
        if type(var) == str:
            return var[0] == '?'
        if isinstance(var, Term):
            return isinstance(var.term, Variable)

        return isinstance(var, Variable)


class Constant:
    def __init__(self, element):
        self.term = None
        self.element = element

    def __eq__(self, other):
        return (self is other
                or isinstance(other, Term) and self.term.element == other.term.element
                or ((isinstance(other, Variable) or isinstance(other, Constant))
                    and self.term.element == other.element))


# Struct used to build assignments for quering the knowledge base
class Assignment:
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

    def __str__(self):
        return self.variable.element + " : " + self.value.element


class Assignments:
    def __init__(self):
        self.assignments = []
        self.mapping = {}

    def __str__(self):
        if not self.assignments:
            return ''
        return ", ".join((str(binding) for binding in self.assignments))

    def __getitem__(self, key):
        return self.mapping[key] if (self.mapping and key in self.mapping) else None

    def assign(self, variable, value):
        self.mapping[variable.element] = value.element
        self.assignments.append(Assignment(variable, value))

    def is_assigned_to(self, variable):
        if variable.element in self.mapping.keys():
            value = self.mapping[variable.element]
            if value:
                return Variable(value) if Variable.is_variable(value) else Constant(value)
        return False

    def test_and_bind(self, variable_term, value_term):
        bound = self.is_assigned_to(variable_term.term)
        if bound:
            return value_term.term == bound

        self.assign(variable_term.term, value_term.term)
        return True


def match(state1, state2, bindings=None):
    if len(state1.terms) != len(state2.terms) or state1.predicate != state2.predicate:
        return False
    if not bindings:
        bindings = Assignments()
    return match_recursive(state1.terms, state2.terms, bindings)


def match_recursive(terms1, terms2, bindings):
    if len(terms1) == 0:
        return bindings
    if Variable.is_variable(terms1[0]):
        if not bindings.test_and_bind(terms1[0], terms2[0]):
            return False
    elif Variable.is_variable(terms2[0]):
        if not bindings.test_and_bind(terms2[0], terms1[0]):
            return False
    elif terms1[0] != terms2[0]:
        return False
    return match_recursive(terms1[1:], terms2[1:], bindings)


def instantiate(statement, bindings):
    def handle_term(term):
        if Variable.is_variable(term):
            bound_value = bindings.is_assigned_to(term.term)
            return Term(bound_value) if bound_value else term
        else:
            return term

    new_terms = [handle_term(t) for t in statement.terms]
    return Predicate([statement.predicate] + new_terms)
