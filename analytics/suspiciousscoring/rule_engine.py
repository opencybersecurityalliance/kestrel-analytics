"""Dynamically generating business-rules variables when the rules operate on a dict."""


from business_rules.actions import rule_action, BaseActions
from business_rules.engine import run_all
from business_rules.fields import FIELD_TEXT, FIELD_NUMERIC
from business_rules.operators import NumericType
from business_rules.operators import StringType
from business_rules.utils import fn_name_to_pretty_label
from business_rules.variables import BaseVariables


# internal ctor to be used by RuleVariables class
def __RuleVariables__init__(self, d):
    # d is a dict
    self.d = d


# Automagically build a method that creates a rule variable
def _add_method(cls, key, vtype):
    func = lambda slf: slf.d.get(key)  # d is a dict; return key's value

    # This is the stuff that business-rules does to rule variable methods
    func.field_type = vtype
    func.is_rule_variable = True
    func.label = fn_name_to_pretty_label(key)
    func.options = []

    # Now add func to class as a method
    setattr(cls, key, func)


# Automagically build methods that create rule variables
def _build_rule_variables(rule_vars):
    cls = type('RuleVariables',
               (BaseVariables,),
               {'__init__': __RuleVariables__init__})
    for name, vtype in rule_vars.items():
        # need to do this in a separate func due to python scoping rules
        _add_method(cls, name, vtype)
    return cls


def _read_rule(conds, rule_vars):
    if 'any' in conds:
        for cond in conds['any']:
            _read_rule(cond, rule_vars)
    elif 'all' in conds:
        for cond in conds['all']:
            _read_rule(cond, rule_vars)
    else:
        name = conds['name']
        value = conds['value']
        if isinstance(value, int) or isinstance(value, float):
            val_type = NumericType
        elif isinstance(value, str):
            val_type = StringType
        else:
            raise TypeError
        if name not in rule_vars:
            rule_vars[name] = val_type


class RuleActions(BaseActions):
    def __init__(self, properties, state):
        self.properties = properties
        self.state = state

    # These are the "actions" a rule can trigger

    @rule_action(params={"name": FIELD_TEXT, "value": FIELD_NUMERIC})
    def set_property(self, name, value):
        self.properties[name] = value

    @rule_action(params={"name": FIELD_TEXT, "value": FIELD_NUMERIC})
    def increment_property(self, name, value):
        val = self.properties.get(name, 0)
        self.properties[name] = val + value

    @rule_action(params={"name": FIELD_TEXT, "value": FIELD_NUMERIC})
    def decrement_property(self, name, value):
        val = self.properties.get(name, 0)
        self.properties[name] = val - value

    @rule_action(params={"name": FIELD_TEXT, "value": FIELD_NUMERIC})
    def set_state(self, name, value):
        self.state[name] = value

    @rule_action(params={"name": FIELD_TEXT, "value": FIELD_NUMERIC})
    def increment_state(self, name, value):
        val = self.state.get(name, 0)
        self.state[name] = val + value

    @rule_action(params={"name": FIELD_TEXT, "value": FIELD_NUMERIC})
    def decrement_state(self, name, value):
        val = self.state.get(name, 0)
        self.state[name] = val - value

    @rule_action(params={"name": FIELD_TEXT, "value": FIELD_TEXT})
    def append_to_property(self, name, value):
        vals = set(self.properties.get(name, '').split(' '))
        vals.add(value)
        self.properties[name] = ' '.join(list(vals))


class RuleEngine:
    def __init__(self, rules):
        self.state = {}
        self.rules = rules
        self.rule_vars = {}
        for rule in rules:
            rule_conds = rule['conditions']
            _read_rule(rule_conds, self.rule_vars)

        # Build the RulesVariables class (not object!) with a list of variables
        # Variables are learned by reading the rule list
        # They should also appear in the items (dicts) the rules act upon
        self.RuleVariables = _build_rule_variables(self.rule_vars)

    def apply_rules(self, obj: dict):
        run_all(
            rule_list=self.rules,
            defined_variables=self.RuleVariables(obj),
            defined_actions=RuleActions(obj, self.state),
        )


if __name__ == '__main__':
    import json
    import sys

    rulefile = sys.argv[1]
    with open(rulefile, 'r') as fp:
        rules = json.load(fp)
    engine = RuleEngine(rules)

    infile = sys.argv[2]
    with open(infile, 'r') as fp:
        objects = json.load(fp)

    for obj in objects:
        engine.apply_rules(obj)

    outfile = sys.argv[3]
    with open(outfile, 'w') as fp:
        json.dump(objects, fp)
