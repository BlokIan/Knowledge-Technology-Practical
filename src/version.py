import json


def read_file(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return data


def find_step(current_step, kb):
    for kb_item in kb:
        if kb_item["description"] == current_step:
            return kb_item
        
def condition(name, condition, value, facts):
    if condition == "==":
        if facts[name] == value:
            return True
    elif condition == ">=":
        if facts[name] >= value:
            return True
        
    return False
        
def rule_deduction(rules, facts, current_step):
    for rule in rules:
        if rule["description"] == current_step:
            reqs = rule["requirements"]
            for req in reqs:
                if not condition(req["name"], req["condition"], req["value"], facts):
                    return rule["next_step"]
                
            return rule["else"]

def main():
    filename = 'version.json'
    data = read_file(filename)
    current_step = "bkr registration"
    kb = data["knowledge base"]
    facts = data["facts"]
    rules = data["rules"]
    
    while "advice" not in current_step:
        kb_item = find_step(current_step, kb)

        for req in kb_item["requirements"]:
            print(req["question"])
            answer = input()
            answer = (int(answer) if req["answer_type"] == "integer" else answer)
            facts[req["name"]] = answer

        current_step = rule_deduction(rules, facts, current_step)

    for rule in rules:
        if rule["description"] == current_step:
            print(rule["advice"])

        
            




if __name__ == "__main__":
    main()


