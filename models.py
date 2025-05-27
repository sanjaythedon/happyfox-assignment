from typing import List, Literal, Optional
from pydantic import BaseModel


class Rule(BaseModel):
    field_name: Literal["From", "Subject", "Message", "Date Received"]
    predicate: Literal["contains", "equals", "does not contain", "does not equal", 
                      "is greater than", "is less than"]
    value: str
    unit: Optional[Literal["days", "months"]] = None


class Operation(BaseModel):
    action: Literal["Mark as Read", "Move message"]
    destination: Optional[str] = None


class EmailRule(BaseModel):
    rule_name: str
    rule_collection_predicate: Literal["all", "any"]
    rules: List[Rule]
    operations: List[Operation]


if __name__ == "__main__":

    def load_rules_from_json(file_path: str) -> List[EmailRule]:
        """Load rules from a JSON file."""
        import json
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return [EmailRule.model_validate(rule) for rule in data]
    
    rules = load_rules_from_json("rules.json")
    print(rules)
