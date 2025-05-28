from singleton import rule_operations

def main(rule_operations):
    """
    Applies rules to the emails. 
    """
    
    rule_operations.run_operations()

if __name__ == "__main__":
    print("Applying rules to emails...")
    main(rule_operations)
    print("Successfully applied operations for all rules")