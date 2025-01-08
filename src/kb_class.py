import json
import re
from calculator import User


class KnowledgeBase:
    def __init__(self, filename):
        self._data = self._read_file(filename)
        self._kb = self._data["knowledge base"]
        self._rules = self._data["rules"]
        self._facts = self._data["facts"]
        self._kb_requirement = None
        self._current_step = "check"
        self._current_question_index = 0
        self._kb_item = None

    def _read_file(self, filename):
        with open(filename, "r") as file:
            return json.load(file)

    def _update_facts(self, fact, value):
        """Update the facts dictionary."""
        self._facts[fact] = value

    def _get_advice(self):
        """Fetch the final advice if at the end step."""
        for rule in self._rules:
            if rule["description"] == self._current_step and "advice" in rule:
                if "fill in" in rule:
                    ls = []
                    for item in rule["fill in"]:
                        ls.append(self._facts[item])
                    return rule["advice"].format(*ls)
                return rule["advice"]
        return None

    def _find_step(self):
        """Find a knowledge base item by description."""
        for kb_item in self._kb:
            if kb_item["description"] == self._current_step:
                self._kb_item = kb_item
                self._current_question_index = 0
                break

    def _condition(self, req):
        """Check a condition on a fact."""
        name, condition, value = req["name"], req["condition"], req["value"]
        fact_value = self._facts[name]
    
        if "minus" in req:
            if self._facts[req["minus"]] is not None:
                fact_value = self._facts[name] - self._facts[req["minus"]]
            else:
                return None
        
        if condition == "==":
            return fact_value == value
        elif condition == ">=":
            return fact_value >= value
        elif condition == "<=":
            return fact_value <= value
        elif condition == "!=":
            return fact_value != value
        return False

    def _rule_deduction(self):
        """Apply rules to deduce the next step."""
        for rule in self._rules:
            if rule["description"] == self._current_step:
                for req in rule["requirements"]:
                    if self._facts[req["name"]] == None:
                        return
                    
                    condition = self._condition(req)
                    if condition is None:
                        return
                    elif not condition:
                        self._current_step = rule["else"]
                        self._find_step()
                        return
                    
                self._current_step = rule["next_step"]
                self._find_step()
                return
                
    def _check_requirements(self):
        """Check if all requirements of the current step are satisfied."""
        for rule in self._rules:
            if rule["description"] == self._current_step:
                for req in rule["requirements"]:
                    if not self._condition(req["name"], req["condition"], req["value"]):
                        self._current_step = rule["else"]
                        self._find_step()
                        return False
                self._current_step = rule["next_step"]
                self._find_step()
                return True
    
    def _calculate_mortgage(self):
        user = User(self._facts["income"], round(self._facts["interest"],1), 360)
        return user.find_max_mortgage()
        
    
    def question_or_advice(self):
        if self._current_question_index == 0:
            self._find_step()

        if "advice" in self._current_step:
            return "advice", self._get_advice(), None
        
        if self._current_question_index < len(self._kb_item["requirement questions"]):
            self._kb_requirement = self._kb_item["requirement questions"][self._current_question_index]
            question = self._kb_requirement["question"]
            answer_type = self._kb_requirement["answer_type"]

            self._current_question_index += 1  # Move to the next question
            return "question", question, answer_type
        
    def answer(self, answer):
        answer = (int(answer) if self._kb_requirement["answer_type"] == "integer" else answer)
        self._update_facts(self._kb_requirement["name"], answer)

        if self._facts["maximum mortgage"] is None and self._facts["income"] is not None and self._facts["interest"] is not None:
            maximum_mortgage = self._calculate_mortgage()
            self._update_facts("maximum mortgage", maximum_mortgage)

        self._rule_deduction()


def main():
    kb = KnowledgeBase("KnowledgeBase.json")
    q_or_a, item, answer_type = kb.question_or_advice()
    while q_or_a != "advice":
        print(item)
        answer = input()
        kb.answer(answer)
        q_or_a, item, answer_type = kb.question_or_advice()
    
    print(item)

if __name__ == "__main__":
    main()