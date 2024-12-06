import json

class KnowledgeBase:
    def __init__(self, filename):
        self._data = self._read_file(filename)
        self._kb = self._data["knowledge base"]
        self._rules = self._data["rules"]
        self._facts = self._data["facts"]
        self._requirement = None
        self._current_step = "bkr registration"

    def _read_file(self, filename):
        with open(filename, "r") as file:
            return json.load(file)

    def _get_current_step(self):
        """Retrieve the current step's requirements and questions."""
        kb_item = self._find_step(self._current_step)
        if kb_item:
            return kb_item["requirements"]
        return []

    def _update_facts(self, value):
        """Update the facts dictionary."""
        self._facts[self._requirement["name"]] = value

    def _get_advice(self):
        """Fetch the final advice if at the end step."""
        for rule in self._rules:
            if rule["description"] == self._current_step and "advice" in rule:
                return rule["advice"]
        return None

    def _find_step(self):
        """Find a knowledge base item by description."""
        for kb_item in self._kb:
            if kb_item["description"] == self._current_step:
                return kb_item
        return None

    def _condition(self, name, condition, value):
        """Check a condition on a fact."""
        fact_value = self._facts[name]
        if condition == "==":
            return fact_value == value
        elif condition == ">=":
            return fact_value >= value
        return False

    def _rule_deduction(self):
        """Apply rules to deduce the next step."""
        for rule in self._rules:
            if rule["description"] == self._current_step:
                reqs = rule["requirements"]
                for req in reqs:
                    if not self._condition(req["name"], req["condition"], req["value"]):
                        self._current_step = rule["next_step"]
                        return
                    self._current_step = rule["else"]
                    return

    
    def question_or_advice(self):
        if "advice" in self._current_step:
            return "advice", self._get_advice()
        
        kb_item = self._find_step()
        for req in kb_item["requirements"]:
            self._requirement = req
            return "question", req["question"]
        
    def answer(self, answer):
        answer = (int(answer) if self._requirement["answer_type"] == "integer" else answer)
        self._update_facts(answer)
        self._rule_deduction()


def main():
    kb = KnowledgeBase("version.json")
    q_or_a, item = kb.question_or_advice()
    while q_or_a != "advice":
        print(item)
        answer = input()
        kb.answer(answer)
        q_or_a, item = kb.question_or_advice()
    
    print(item)

if __name__ == "__main__":
    main()