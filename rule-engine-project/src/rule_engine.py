import re
import json
import os

# Load configuration from JSON file in the project root
def load_config():
    # Construct path to `config.json` in the project root, relative to `src`
    config_path = os.path.join(os.path.dirname(__file__), "../config.json")
    config_path = os.path.abspath(config_path)  # Get the absolute path
    with open(config_path, 'r') as file:
        config= json.load(file)
    return config


# Load JSON config
config = load_config()
VALID_ATTRIBUTES = set(config["valid_attributes"])

# Node class to represent the AST
class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.type = node_type  # "operator" or "operand"
        self.left = left       # Left child (another Node)
        self.right = right     # Right child (another Node)
        self.value = value     # For operands (e.g., condition: age > 30)


# Custom exceptions for error handling
class InvalidRuleError(Exception):
    pass

class InvalidAttributeError(Exception):
    pass


# Function to create the AST from a rule string
def create_rule(rule_string):
    try:
        tokens = re.split(r'(\s+AND\s+|\s+OR\s+|\(|\))', rule_string)
        stack = []
        operators = []  # Stack to manage operators and parentheses

        # Helper function to process the stack into an AST
        def process_stack():
            if len(stack) < 2 or not operators:
                raise InvalidRuleError("Invalid rule structure or missing operator.")
            right = stack.pop()
            operator = operators.pop()
            left = stack.pop()
            stack.append(Node(node_type='operator', left=left, right=right, value=operator.strip()))

        # Parse tokens into AST using a stack-based approach
        for token in tokens:
            token = token.strip()
            if not token:
                continue

            if token in ['AND', 'OR']:
                operators.append(token)
            elif token == '(':
                operators.append('(')  # Push opening parenthesis
            elif token == ')':
                while operators and operators[-1] != '(':
                    process_stack()  # Process until opening parenthesis
                operators.pop()  # Pop the '(' from the stack
            else:
                # Validate the attribute in the condition
                attribute, operator, value = re.split(r'\s*(>|<|=)\s*', token)
                if attribute not in VALID_ATTRIBUTES:
                    raise InvalidAttributeError(f"Invalid attribute '{attribute}' in rule.")
                stack.append(Node(node_type='operand', value=token))  # Operand nodes

            # Handle operator precedence
            while len(stack) > 1 and operators and operators[-1] not in ['(']:
                process_stack()

        if not stack:
            raise InvalidRuleError("Rule string did not result in a valid AST.")
        return stack[0]  # The root of the AST

    except (ValueError, IndexError):
        raise InvalidRuleError("Invalid comparison or malformed rule string.")


# Function to combine multiple rules into one AST
def combine_rules(rule_strings):
    combined_root = None
    for rule_string in rule_strings:
        root = create_rule(rule_string)
        if combined_root is None:
            combined_root = root
        else:
            combined_root = Node(node_type='operator', left=combined_root, right=root, value='AND')
    return combined_root


# Function to evaluate the AST against user data
def evaluate_rule(node, data):
    if node.type == 'operand':
        # Split the operand to extract attribute, operator, and value
        attribute, operator, value = re.split(r'\s*(>|<|=)\s*', node.value)
        if attribute not in data:
            return False  # Handle missing data attributes

        # Convert the value for comparison
        value = int(value) if value.isdigit() else value.strip("'")

        # Perform the comparison
        if operator == '>':
            return data[attribute] > value
        elif operator == '<':
            return data[attribute] < value
        elif operator == '=':
            return str(data[attribute]) == value
        else:
            raise ValueError(f"Invalid operator: {operator}")

    elif node.type == 'operator':
        # Recursively evaluate left and right branches
        left_result = evaluate_rule(node.left, data)
        right_result = evaluate_rule(node.right, data)

        # Combine results based on the operator (AND/OR)
        if node.value == 'AND':
            return left_result and right_result
        elif node.value == 'OR':
            return left_result or right_result
        else:
            raise ValueError(f"Invalid operator in AST: {node.value}")


# Function to modify an existing rule (replace operator, operand values, etc.)
def modify_rule(node, old_value, new_value):
    if node.type == 'operand' and node.value == old_value:
        node.value = new_value
    elif node.type == 'operator':
        modify_rule(node.left, old_value, new_value)
        modify_rule(node.right, old_value, new_value)


# Example of combining rules into a single AST
def run_combined_rule_example():
    # Load rules and user data from config
    rules = config["rules"]
    user_data = config["user_data"]

    try:
        # Create and combine rules
        combined_root = combine_rules(rules)

        # Evaluate the combined rule AST with user data from config
        result = evaluate_rule(combined_root, user_data)
        print(f"Result of evaluating combined rules: {result}")  # Expected output: True or False

        # Modify an existing rule (e.g., change age > 30 to age > 40)
        modify_rule(combined_root, "age > 30", "age > 40")
        result_after_modification = evaluate_rule(combined_root, user_data)
        print(f"Result after modifying rule: {result_after_modification}")  # Expected output after modification

    except (InvalidRuleError, InvalidAttributeError) as e:
        print(f"Error: {str(e)}")


# Run examples
if __name__ == "__main__":
    print("Evaluating combined rules example:")
    run_combined_rule_example()
