from typing import List, Literal, Union, Annotated
from pydantic import BaseModel, Field


class StringFieldRule(BaseModel):
    field_name: Literal["From", "Subject", "Message"]
    predicate: Literal["contains", "equals", "does not contain", "does not equal"]
    value: str


class DateReceivedRule(BaseModel):
    field_name: Literal["Date Received"]
    predicate: Literal["is greater than", "is less than"]
    value: str
    unit: Literal["days", "months"]


Rule = Union[StringFieldRule, DateReceivedRule]


class MarkAsReadOperation(BaseModel):
    action: Literal["Mark as Read"]


class MoveMessageOperation(BaseModel):
    action: Literal["Move message"]
    destination: str


Operation = Union[MarkAsReadOperation, MoveMessageOperation]


class EmailRule(BaseModel):
    rule_name: str
    rule_collection_predicate: Literal["all", "any"]
    rules: List[Rule]
    operations: List[Operation]
    


def load_rules_from_json(file_path: str) -> List[EmailRule]:
    """Load rules from a JSON file."""
    import json
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    email_rules = [EmailRule.model_validate(rule) for rule in data]
    
    return email_rules


if __name__ == "__main__":
    rules = load_rules_from_json("rules.json")
    print(rules)
