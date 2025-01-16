import json
from .calculator import User


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
        """Read the knowledge base file"""
        with open(filename, "r") as file:
            return json.load(file)

    def _update_facts(self, fact, value):
        """Update the facts dictionary."""
        if fact == "advice":
            self._facts[fact].append(value)
        else:
            self._facts[fact] = value

    def _get_advice(self):
        """Get the advice given at the current step"""
        for rule in self._rules:
            if rule["description"] == self._current_step and "advice" in rule:
                if "fill in" in rule:
                    if type(rule["fill in"]) == str:
                        return rule["advice"].format(self._facts[rule["fill in"]])
                    else:
                        return rule["advice"].format(*[self._facts[key] for key in rule["fill in"]])
                return rule["advice"]
        return None
    
    def _conclusion(self):
        """Return the conclusion containing all advice."""
        conclusion = ""
        for advice in self._facts["advice"]:
            conclusion = conclusion + advice + "\n"
        return conclusion.rstrip()

    def _find_step(self):
        """Find a knowledge base item by description."""
        for kb_item in self._kb:
            if kb_item["description"] == self._current_step:
                self._kb_item = kb_item
                break

    def _condition(self, req):
        """Check a condition on a fact."""
        name, condition, value = req["name"], req["condition"], req["value"]
        fact_value = self._facts[name]
    
        if "minus" in req:
            for min in req["minus"]:
                if self._facts[min] is not None:
                    fact_value = self._facts[name] - self._facts[req["minus"]]
                else:
                    return None
        
        match condition:
            case "==":
                return fact_value == value
            case ">=":
                return fact_value >= value
            case "<=":
                return fact_value <= value
            case "!=":
                return fact_value != value
        return False

    def _rule_deduction(self):
        """Apply rules to deduce the next step."""
        for rule in self._rules:
            if rule["description"] == self._current_step:
                if "advice" in self._current_step:
                    self._current_step = rule["next_step"]
                    self._current_question_index = 0
                    return

                for req in rule["requirements"]:
                    if self._facts[req["name"]] == None:
                        return
                    
                    condition = self._condition(req)
                    if condition is None:
                        return
                    elif not condition:
                        self._current_step = rule["else"]
                        self._current_question_index = 0
                        return
                    
                self._current_step = rule["next_step"]
                self._current_question_index = 0
                return
    
    def _interest_bank(self):
        """Get the interest depending on the bank."""
        if "ING" in self._current_step:
            return 3.40
        elif "Vista" in self._current_step:
            return 3.34

    def _update_mortgage_facts(self):
        """Calculates the maximum mortgage."""
        costs_per_month = sum(self._facts[item] for item in ("family loan", "other loan", "mobile phone on credit", "private lease car") if type(self._facts[item]) == int)
        user = User(self._facts["income"], round(self._facts["interest"],1), 360, self._facts["energy label"], self._facts["property valuation"], costs_per_month, self._facts["student debt"])

        maximum_mortgage = user.find_max_mortgage()
        self._update_facts("maximum mortgage", maximum_mortgage)

        annuity_gross, annuity_net, linear_gross, linear_net = user.monthly_costs()
        self._update_facts("annuity gross monthly fees", annuity_gross)
        self._update_facts("linear gross monthly fees", linear_gross)
        self._update_facts("annuity net monthly fees", annuity_net)
        self._update_facts("linear net monthly fees", linear_net)

    def question_or_advice(self):
        """Infers which question to be asked or advice to be given to the user."""
        if self._current_question_index == 0:
            self._find_step()

        if "bank" | "buy possibility" in self._current_step:
            self._rule_deduction()

        while "advice" in self._current_step:
            if "bank" in self._current_step:
                self._update_facts("interest", self._interest_bank())
                if (self._facts["maximum mortgage"] is None
                    and all(self._facts[key] is not None for key in ["income", "interest", "energy label", "property valuation"])):
                    self._update_mortgage_facts()

            self._update_facts("advice", self._get_advice())

            if "end advice" in self._current_step:
                return "advice", self._conclusion(), None
            else:
                self._rule_deduction()
                self._find_step()         
        
        if self._current_question_index < len(self._kb_item["requirement questions"]):
            self._kb_requirement = self._kb_item["requirement questions"][self._current_question_index]

            question = self._kb_requirement["question"]
            if "fill in" in self._kb_requirement:
                question = question.format(self._facts[self._kb_requirement["fill in"]])
            answer_type = self._kb_requirement["answer_type"]

            self._current_question_index += 1  # Move to the next question
            return "question", question, answer_type
        
    def answer(self, answer):
        """Answer of the user is updated to the facts"""
        answer = (int(answer) if self._kb_requirement["answer_type"] == "integer" else answer)
        self._update_facts(self._kb_requirement["name"], answer)      

        if self._facts["max bid"] is None and self._facts["maximum mortgage"] is not None and self._facts["own money"] is not None:
            self._update_facts(self._kb_requirement["max bid"], answer)
        
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