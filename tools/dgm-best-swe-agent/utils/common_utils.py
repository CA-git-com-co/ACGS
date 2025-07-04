import json

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



def read_file(file_path):
    """
    Read a file and return its contents as a string.
    """
    with open(file_path) as f:
        content = f.read().strip()
    return content


def load_json_file(file_path):
    """
    Load a JSON file and return its contents as a dictionary.
    """
    with open(file_path) as file:
        return json.load(file)
