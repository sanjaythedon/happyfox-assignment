from singleton import rule_operations

def main(rule_operations):
    """
    Applies rules to the emails. 
    """
    
    count = rule_operations.run_operations()
    return count

if __name__ == "__main__":
    print("Applying rules to emails...")
    count = main(rule_operations)
    print(f"Successfully applied operations to {count} matching emails")