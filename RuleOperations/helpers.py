from typing import Dict, Any, Tuple, List
from datetime import datetime, timedelta, timezone
from RuleOperations.interfaces import EmailOperation
from RuleOperations.interfaces import MarkAsReadOperation, MoveToLabelOperation


class RuleParser:
    @staticmethod
    def build_condition(condition: Dict[str, Any]) -> tuple:
        """
        Build an SQL condition from a rule condition.
        
        Args:
            condition: Dictionary containing field_name, predicate, value, and optional unit
            
        Returns:
            Tuple of (sql_condition, condition_value) or (None, None) if invalid
        """
        field_name = condition.get('field_name', '').title()
        predicate = condition.get('predicate')
        value = condition.get('value')
        unit = condition.get('unit')
        
        # Skip if any required field is missing
        if not all([field_name, predicate, value]):
            return None, None
        
        # Handle different predicates for string values
        if predicate == 'contains':
            return f"\"{field_name}\" LIKE ?", f"%{value}%"
        elif predicate == 'does not contain':
            return f"\"{field_name}\" NOT LIKE ?", f"%{value}%"
        elif predicate == 'equals':
            return f"\"{field_name}\" = ?", value
        elif predicate == 'does not equal':
            return f"\"{field_name}\" != ?", value
        # Handle datetime predicates
        elif predicate in ['is less than', 'is greater than'] and field_name == 'Date Received':
            try:
                value_int = int(value)
                current_date = datetime.now(timezone.utc)
                
                if unit == 'days':
                    if predicate == 'is less than':
                        # Emails received less than X days ago
                        target_date = current_date - timedelta(days=value_int)
                        return f"\"{field_name}\" > ?", target_date.strftime('%Y-%m-%d %H:%M:%S')
                    else:  # is greater than
                        # Emails received more than X days ago
                        target_date = current_date - timedelta(days=value_int)
                        return f"\"{field_name}\" < ?", target_date.strftime('%Y-%m-%d %H:%M:%S')
                elif unit == 'months':
                    # Calculate months by approximating 30 days per month
                    if predicate == 'is less than':
                        target_date = current_date - timedelta(days=30 * value_int)
                        return f"\"{field_name}\" > ?", target_date.strftime('%Y-%m-%d %H:%M:%S')
                    else:  # is greater than
                        target_date = current_date - timedelta(days=30 * value_int)
                        return f"\"{field_name}\" < ?", target_date.strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError) as e:
                print(f"Error processing datetime condition: {e}")
                return None, None
        
        return None, None

    @staticmethod
    def create_sql_query(rule: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """
        Create a SQL query for a given rule.
        
        Args:
            rule: Rule dictionary
            
        Returns:
            Tuple containing (SQL condition string, list of condition values)
        """
        rule_collection_predicate = rule.get('rule_collection_predicate', 'all')
        rule_conditions = rule.get('rules', [])
        
        sql_conditions = []
        condition_values = []
        
        # Build SQL conditions from rule conditions
        for condition in rule_conditions:
            sql_condition, value = RuleParser.build_condition(condition)
            if sql_condition and value is not None:
                sql_conditions.append(sql_condition)
                condition_values.append(value)
        
        # If no valid conditions, return empty query
        if not sql_conditions:
            return "", []
        
        # Combine conditions based on rule_collection_predicate
        if rule_collection_predicate.lower() == 'all':
            condition_str = " AND ".join(sql_conditions)
        else:  # 'any'
            condition_str = " OR ".join(sql_conditions)
        
        return condition_str, condition_values

class EmailOperationsBundler:
    @staticmethod
    def bundle_email_operations(rule_operations: List[Dict[str, Any]]) -> List[EmailOperation]:
        """
        Bundles email operations based on the rule operations.
        
        Args:
            rule_operations: List of operation dictionaries from the rule
            
        Returns:
            List of EmailOperation objects
        """
        email_operations = []
        
        for operation in rule_operations:
            action = operation.get('action')
            
            if action == 'Mark as Read':
                email_operations.append(MarkAsReadOperation())
                
            elif action == 'Move message':
                destination = operation.get('destination')
                if destination:
                    email_operations.append(MoveToLabelOperation(destination))
        
        return email_operations