import json

class KnowledgeBase:
    def __init__(self, filename):
        self.data = self._read_file(filename)
        self.kb = self.data["knowledge base"]
        self.rules = self.data["rules"]
        self.facts = self.data["facts"]
        self.current_step = "bkr registration"

    def _read_file(self, filename):
        with open(filename, "r") as file:
            return json.load(file)

    def get_current_step(self):
        """Retrieve the current step's requirements and questions."""
        kb_item = self._find_step(self.current_step)
        if kb_item:
            return kb_item["requirements"]
        return []

    def update_facts(self, name, value):
        """Update the facts dictionary."""
        self.facts[name] = value

    def next_step(self):
        """Determine the next step based on rules."""
        self.current_step = self._rule_deduction()

    def get_advice(self):
        """Fetch the final advice if at the end step."""
        for rule in self.rules:
            if rule["description"] == self.current_step and "advice" in rule:
                return rule["advice"]
        return None

    def _find_step(self, description):
        """Find a knowledge base item by description."""
        for kb_item in self.kb:
            if kb_item["description"] == description:
                return kb_item
        return None

    def _condition(self, name, condition, value):
        """Check a condition on a fact."""
        fact_value = self.facts.get(name)
        if condition == "==":
            return fact_value == value
        elif condition == ">=":
            return fact_value >= value
        return False

    def _rule_deduction(self):
        """Apply rules to deduce the next step."""
        for rule in self.rules:
            if rule["description"] == self.current_step:
                reqs = rule["requirements"]
                for req in reqs:
                    if not self._condition(req["name"], req["condition"], req["value"]):
                        return rule["else"]
                return rule["next_step"]
        return self.current_step